import clack from "./utils/clack";
import chalk from 'chalk';
import { exec } from 'node:child_process';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';

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

const setupClaudeCLI = async (agentKey: string): Promise<void> => {
  console.log(chalk.blue('Setting up Scout MCP with Claude CLI...'));
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
    console.log(chalk.blue('Adding Scout MCP server to Claude CLI...'));
    const { stdout, stderr } = await execAsync(command);
    
    if (stdout) {
      console.log(chalk.green('✓ Scout MCP successfully configured with Claude CLI!'));
      console.log(stdout);
    }
    
    if (stderr) {
      console.log(chalk.yellow('Warning:'), stderr);
    }
  } catch (error: any) {
    console.log(chalk.red('✗ Failed to configure Scout MCP with Claude CLI'));
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
  console.log(chalk.yellow('Opening Cursor deeplink to install Scout MCP...'));
  
  // Generate the dynamic Cursor deeplink with the actual API key
  const deeplink = generateCursorDeeplink(agentKey);
  
  await openUrl(deeplink);
  
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
      await openUrl(`${baseUrl}/users/sign_up?utm_source=mcp-setup&utm_medium=setup-wizard&utm_campaign=scout-mcp-local`);
      await collectKey();
      break;
      
    case 'exit':
      console.log(chalk.yellow('Goodbye!'));
      break;
      
    default:
      console.log(chalk.red('Invalid selection'));
  }

  // Only configure AI assistant if we have an API key
  if (agentKey) {
    const aiAssistant = await clack.select({
      message: 'Which AI assistant are you using?',
      options: [
        { value: 'cursor', label: 'Cursor' },
        { value: 'claude-cli', label: 'Claude CLI' },
        { value: 'claude-desktop', label: 'Claude Desktop' },
        { value: 'manual', label: 'Manual setup (show JSON config)' }
      ]
    });

    switch (aiAssistant) {
      case 'cursor':
        await setupCursor(agentKey);
        break;
        
      case 'claude-cli':
        await setupClaudeCLI(agentKey);
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
