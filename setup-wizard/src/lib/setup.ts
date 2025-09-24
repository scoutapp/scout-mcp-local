import clack from "./utils/clack";
import chalk from 'chalk';
import { createHash, randomBytes } from 'crypto';

const getBaseUrl = (): string => {
  return process.env.SCOUT_HOST || 'https://scoutapm.com';
};

const openUrl = async (url: string): Promise<void> => {
  const open = (await import('open')).default;
  await open(url);
};

const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

export async function setup(): Promise<void> {
  const action = await clack.select({
    message: 'Are you currently a Scout APM customer?',
    options: [
      { value: 'signin', label: 'Yes' },
      { value: 'signup', label: 'No' },
      { value: 'exit', label: 'Exit' }
    ]
  });

  const collectKey = async (): Promise<void> => {
    const key = await clack.text({
      message: 'Please paste your Agent Key below:',
      placeholder: 'Agent Key',
    });
    agentKey = key.toString();
  };

  const baseUrl = getBaseUrl();
  let agentKey: string | null = null;

  switch (action) {
    case 'signin':
      console.log(chalk.blue(`Opening Scout APM settings page...`))
      console.log(chalk.blue('Please copy your Agent Key before continuing.'));
      // wait two seconds before opening the url 
      await delay(2000);
      openUrl(`${baseUrl}/settings`);
      await collectKey();
      break;
      
    case 'signup':
      console.log(chalk.blue('Opening Scout APM sign up page...'));

      console.log(chalk.blue('After completing signup, please visit your settings page to get your Agent Key.'));
      console.log(chalk.blue('Then return here to continue setup.'));
      await delay(2000);
      await collectKey();
      break;
      
    case 'exit':
      console.log(chalk.yellow('Goodbye!'));
      break;
      
    default:
      console.log(chalk.red('Invalid selection'));
  }

  // Only generate config if we have an API key
  if (agentKey) {
    // TODO: Determine if the user is using claude or cursor, automatically add the mcp config file to the correct location
    const mcpConfig = {
      "mcpServers": {
        "scout-apm": {
          "command": "docker",
          "args": ["run", "--rm", "-i", "--env", "SCOUT_API_KEY", "scoutapp/scout-mcp-local:latest"],
          "env": { "SCOUT_API_KEY": agentKey }
        }
      }
    }
    
    console.log(chalk.green('Please paste the following into your MCP config to complete setup.'));
    console.log(JSON.stringify(mcpConfig, null, 2));
  }
}
