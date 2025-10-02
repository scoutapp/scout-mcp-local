import chalk from 'chalk';
import ora from 'ora';
import { createHash, randomBytes } from 'node:crypto';
import clack from "@/lib/utils/clack";
import { getBaseUrl, openUrl } from '@/lib/utils/shared';

interface UatOrgResponse {
  orgs: Array<{ id: number; name: string; }>;
}

interface UatAuthCheckResponse {
  has_authenticated: boolean;
}

export interface UatKeyResponse {
  org_key: string;
  api_key: string;
}

interface VerifierChallenge {
  verifier: string;
  challenge: string;
}

const createVerifierAndChallenge = (): VerifierChallenge => {
  const verifier = randomBytes(32).toString('hex');
  const challenge = createHash('sha256').update(verifier).digest('hex');
  return { verifier, challenge };
};

const sleep = (ms: number): Promise<void> => 
  new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Fetch with retry.
 *
 * @param url - The URL to fetch
 * @param opts - Fetch options
 * @param tries - How many times to try
 * @param delayMs - Delay in ms between retries
 */
const fetchWithRetry = async (url: string, opts?: RequestInit, tries: number = 2, delayMs: number = 1000): Promise<Response> => {
  for (let i = 0; i < tries; i++) {
    try {
      return await fetch(url, opts);
    } catch (err) {
      if (i < tries - 1) {
        console.log(`retrying in ${delayMs}ms...`);
        await sleep(delayMs);
      } else {
        throw err; // last attempt, rethrow immediately
      }
    }
  }

  // TS wants a return here.
  throw new Error("Unreachable");
}

/**
 * Post UAT form data to the given URL. If we fail, fallback to manual.
 * @param url - The URL to post the form data to
 * @param data - The form data as a record of key-value pairs
 * @returns Promise<UatKeyResponse | null>
 */
const postForm = async (url: string, data: Record<string, any> = {}): Promise<Response> => {
  const formData = new URLSearchParams();
  Object.entries(data).forEach(([key, value]) => {
    formData.append(key, value.toString());
  });

  return await fetchWithRetry(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  });
};

/**
 * Authenticate with UAT endpoints using OAuth/PKCE-like flow (single use, short lived tokens)
 * @param authType - 'sign_in' or 'sign_up'
 * @returns Promise<UatKeyResponse | null>
 */
export const authenticateWithUat = async (authType: string): Promise<UatKeyResponse | null> => {
  try {
    const baseUrl = getBaseUrl();
    console.log(chalk.blue('Starting authentication flow...'));

    // Step 1: Create first verifier, challenge token and open browser for auth
    const { verifier: firstVerifier, challenge: firstChallenge } = createVerifierAndChallenge();
    const firstChallengeB64 = Buffer.from(firstChallenge).toString('base64url');

    const authUrl = `${baseUrl}/uat/auth/${authType}/${firstChallengeB64}`;

    await openUrl(authUrl);

    // Step 2: Poll for authentication completion / if the challenge token has been created.
    console.log(chalk.yellow('Please complete authentication in your browser... \n'));
    const spinner = ora('Waiting for authentication...').start();

    const startTime = Date.now();
    const timeoutMs = 300 * 1000; // 300 seconds
    let authenticated = false;

    try {
      while (Date.now() - startTime < timeoutMs) {
        const checkResponse = await fetchWithRetry(`${baseUrl}/uat/auth/check/${firstChallengeB64}`);

        if (checkResponse.ok) {
          const checkData = await checkResponse.json() as UatAuthCheckResponse;

          if (checkData.has_authenticated) {
            spinner.succeed('Authentication successful! \n');
            authenticated = true;
            break;
          }
        }
        
        await sleep(5000); // Poll every 5 seconds
      }
    } catch (error) {
      spinner.fail('Authentication failed');
      throw error;
    }

    if (!authenticated) {
      spinner.fail('Authentication timed out after 5 minutes \n');
      throw new Error('Authentication timeout');
    }

    // Step 3: Get orgs using the first verifier and create a second challenge which will be used
    // for getting the keys.
    const { verifier: secondVerifier, challenge: secondChallenge } = createVerifierAndChallenge();
    const firstVerifierB64 = Buffer.from(firstVerifier).toString('base64url');
    const secondChallengeB64 = Buffer.from(secondChallenge).toString('base64url');

    console.log(chalk.blue('Getting organizations...'));
    const orgsResponse = await postForm(`${baseUrl}/uat/get_orgs`, {
      verify_token: firstVerifierB64,
      challenge_token: secondChallengeB64
    });

    if (!orgsResponse.ok) {
      throw new Error(`Failed to get organizations: ${orgsResponse.status}`);
    }

    const orgsData = await orgsResponse.json() as UatOrgResponse;

    if (!orgsData.orgs || orgsData.orgs.length === 0) {
      throw new Error('No organizations found');
    }

    // Step 4: Let user select organization. If only one org, select it automatically.
    let selectedOrgId: number;
    if (orgsData.orgs.length === 1) {
      selectedOrgId = orgsData.orgs[0].id;
    } else {
      const orgChoice = await clack.select({
        message: 'Select an organization:',
        options: orgsData.orgs.map(org => ({
          value: org.id.toString(),
          label: org.name
        }))
      });
      selectedOrgId = parseInt(orgChoice as string);
    }
    console.log(chalk.green(`Using organization: ${orgsData.orgs[0].name} \n`));

    // Step 5: Get the keys using second verifier and selected org
    const secondVerifierB64 = Buffer.from(secondVerifier).toString('base64url');
    console.log(chalk.blue('Getting keys...'));

    const keysResponse = await postForm(`${baseUrl}/uat/get_keys`, {
      verify_token: secondVerifierB64,
      org_id: selectedOrgId
    });

    if (!keysResponse.ok) {
      throw new Error(`Failed to get keys: ${keysResponse.status}`);
    }

    const keysData = await keysResponse.json() as UatKeyResponse;

    if (!keysData.api_key) {
      throw new Error('No API key received');
    }

    console.log(chalk.green('Gathering keys successful!'));
    return keysData;

  } catch (error: any) {
    console.log(chalk.red('✗ Authentication failed:'), error.message);
    console.log(chalk.yellow('Falling back to manual API key entry...'));
    return null;
  }
};
