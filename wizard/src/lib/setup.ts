import clack from "./utils/clack";
import chalk from 'chalk';
import { exec } from 'node:child_process';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import { createHash, randomBytes } from 'node:crypto';
import ora from 'ora';

interface UatOrgResponse {
  orgs: Array<{ id: number; name: string; }>;
}

interface UatKeyResponse {
  org_key: string;
  api_key: string;
}

interface UatAuthCheckResponse {
  has_authenticated: boolean;
}

interface VerifierChallenge {
  verifier: string;
  challenge: string;
}

const getBaseUrl = (): string => {
  return process.env.SCOUT_HOST || 'https://scoutapm.com';
};

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
const authenticateWithUat = async (authType: string): Promise<UatKeyResponse | null> => {
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

const openUrl = async (url: string): Promise<void> => {
  const open = (await import('open')).default;
  await open(url);
};

/**
 * Prompts the user to confirm opening a URL and optionally opens it
 * @param message - The confirmation message to show the user
 * @param url - The URL to open if confirmed
 * @param fallbackMessage - Message to show if user declines to open the URL
 * @returns Promise<void>
 */
const promptAndOpenUrl = async (message: string, url: string, fallbackMessage: string): Promise<void> => {
  const shouldOpen = await clack.confirm({
    message,
    initialValue: true
  });
  
  if (shouldOpen) {
    await openUrl(url);
  } else {
    console.log(chalk.yellow(fallbackMessage));
  }
};


const mcpConfig = (agentKey: string = "your_scout_api_key_here") => {
  return {
    "mcpServers": {
      "scout-apm": {
        "command": "docker",
        "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY", "scoutapp/scout-mcp-local:latest"],
        "env": { "SCOUT_API_KEY": agentKey }
      }
    }
  };
};

const execAsync = (command: string): Promise<{ stdout: string; stderr: string }> => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
};

const getClaudeDesktopConfigPath = (): string => {
  const platform = os.platform();
  if (platform === 'darwin') {
    return path.join(os.homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  } else if (platform === 'win32') {
    return path.join(process.env.APPDATA || '', 'Claude', 'claude_desktop_config.json');
  } else {
    // Linux or other platforms - Claude Desktop may not be available
    throw new Error('Claude Desktop config path not supported on this platform');
  }
};

const setupClaudeCode = async (agentKey: string): Promise<void> => {
  console.log(chalk.blue('Setting up Scout MCP with Claude Code...'));
  const command = `claude mcp add scout-apm -e SCOUT_API_KEY=${agentKey} -- docker run --rm -i -e SCOUT_API_KEY scoutapp/scout-mcp-local:latest`;
  
  console.log(chalk.yellow('This will run the following command:'));
  console.log(chalk.gray(command));
  
  const shouldRun = await clack.confirm({
    message: 'Do you want to run this now?',
  });
  
  if (!shouldRun) {
    console.log(chalk.yellow('No problem! You can run this command later:'));
    console.log(chalk.gray(command));
    return;
  }
  
  try {
    console.log(chalk.blue('Adding Scout MCP server to Claude Code...'));
    const { stdout, stderr } = await execAsync(command);
    
    if (stdout) {
      console.log(chalk.green('✓ Scout MCP successfully configured with Claude Code!'));
      console.log(stdout);
    }
    
    if (stderr) {
      console.log(chalk.yellow('Warning:'), stderr);
    }
  } catch (error: any) {
    console.log(chalk.red('✗ Failed to configure Scout MCP with Claude Code'));
    console.log(chalk.red('Error:'), error.message);
    console.log(chalk.yellow('You can manually run this command:'));
    console.log(chalk.gray(command));
  }
};

const generateCursorDeeplink = (agentKey: string): string => {
  // TODO: This is seemingly broken in the Arc browser, which exits out of the cursor site quickly after opening. 
  // Needs further investigation, but seems like a bug with Arc rather than an issue with the deeplink.
  const config = {
    "command": "docker",
    "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY", "scoutapp/scout-mcp-local:latest"],
    "env": { "SCOUT_API_KEY": agentKey }
  };
  
  const configJson = JSON.stringify(config);
  const configBase64 = Buffer.from(configJson).toString('base64');
  
  return `https://cursor.com/en/install-mcp?name=scout-apm&config=${encodeURIComponent(configBase64)}`;
};

/**
 * Set up Scout MCP for Cursor using a deeplink. Allowing the link to open in Cursor will prompt the user for confirmation and 
 * show the available tools. 
 * @param agentKey - The Scout APM agent key
 * @returns void
 */
const setupCursor = async (agentKey: string): Promise<void> => {
  console.log(chalk.blue('Setting up Scout MCP for Cursor...'));
  console.log(chalk.yellow('We\'ll open a Cursor deeplink to install Scout MCP.'));
  
  // Generate the dynamic Cursor deeplink with the actual API key
  const deeplink = generateCursorDeeplink(agentKey);
  
  await promptAndOpenUrl(
    'Press enter to open the Cursor deeplink',
    deeplink,
    'Please manually open Cursor and add the Scout MCP server configuration.'
  );
  
  console.log(chalk.yellow('After clicking "Add Server" in Cursor, the Scout MCP will be configured with your API key automatically.'));
  console.log(chalk.blue('No further manual configuration should be needed!'));
};
/**
 * Set up Scout MCP for Claude Desktop by updating the config file 
 * @param agentKey - The Scout APM agent key
 * @returns void
 */
const setupClaudeDesktop = async (agentKey: string): Promise<void> => {
  try {
    console.log(chalk.blue('Setting up Scout MCP for Claude Desktop...'));
    
      const configPath = getClaudeDesktopConfigPath();
      const config = mcpConfig(agentKey);
    

    let existingConfig = {};
    
    // Try to read existing config
    if (fs.existsSync(configPath)) {
      try {
        const existingConfigData = fs.readFileSync(configPath, 'utf8');
        existingConfig = JSON.parse(existingConfigData);
      } catch (error) {
        console.log(chalk.yellow('Warning: Could not parse existing Claude config, will create new one'));
      }
    } else {
      // Create directory if it doesn't exist
      const configDir = path.dirname(configPath);
      fs.mkdirSync(configDir, { recursive: true });
    }

    // Merge configs
    const finalConfig = {
      ...existingConfig,
      mcpServers: {
        ...(existingConfig as any).mcpServers,
        ...config.mcpServers
      }
    };

    // Write the config
    fs.writeFileSync(configPath, JSON.stringify(finalConfig, null, 2));
    
    console.log(chalk.green('✓ Scout MCP configuration added to Claude Desktop!'));
    console.log(chalk.blue(`Config file updated: ${configPath}`));
    console.log(chalk.yellow('Please restart Claude Desktop for the changes to take effect.'));
    
  } catch (error: any) {
    console.log(chalk.red('✗ Failed to update Claude Desktop config'));
    console.log(chalk.red('Error:'), error.message);
    
    console.log(chalk.yellow('Please manually add this configuration to your Claude Desktop config:'));
    console.log(JSON.stringify(mcpConfig(agentKey), null, 2));
  }
};

export async function setup(): Promise<void> {
  const action = await clack.select({
    message: 'Are you currently a Scout APM customer?',
    options: [
      { value: 'sign_in', label: 'Yes' },
      { value: 'sign_up', label: 'No' },
      { value: 'exit', label: 'Exit' }
    ]
  });

  if (action === 'exit') {
    console.log(chalk.yellow('Goodbye!'));
    return;
  }

  const baseUrl = getBaseUrl();
  let keys: UatKeyResponse | null = null;

  // Try UAT authentication first. Fallback if it fails.
  keys = await authenticateWithUat(action as string);
  let agentKey = keys ? keys.api_key : null;

  // Fall back to manual key entry if UAT fails
  // TODO: Implement fallback for org key.
  if (!agentKey) {
    const collectKey = async (): Promise<string> => {
      const key = await clack.text({
        message: 'Please paste your API key below:',
        placeholder: 'API key',
      });
      return key.toString();
    };

    console.log(chalk.blue('We\'ll open the Scout APM settings page where you can copy your API key.'));
    await promptAndOpenUrl(
      'Press enter to open the Scout APM settings page',
      `${baseUrl}/settings`,
      `Please visit ${baseUrl}/settings to get your API key.`
    );
    agentKey = await collectKey();
  }

  // Only configure AI assistant if we have an API key
  if (agentKey) {
    const aiAssistant = await clack.select({
      message: 'Which AI assistant are you using?',
      options: [
        { value: 'cursor', label: 'Cursor' },
        { value: 'claude-code', label: 'Claude Code (CLI)' },
        { value: 'claude-desktop', label: 'Claude Desktop' },
        { value: 'manual', label: 'Manual setup (show JSON config)' }
      ]
    });

    switch (aiAssistant) {
      case 'cursor':
        await setupCursor(agentKey);
        break;
        
      case 'claude-code':
        await setupClaudeCode(agentKey);
        break;
        
      case 'claude-desktop':
        await setupClaudeDesktop(agentKey);
        break;
        
      case 'manual':
        console.log(chalk.green('Please paste the following into your MCP config to complete setup:'));
        console.log(JSON.stringify(mcpConfig(agentKey), null, 2));
        break;
        
      default:
        console.log(chalk.red('Invalid selection'));
    }
  }
}
