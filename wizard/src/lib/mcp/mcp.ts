import chalk from 'chalk';
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import clack from '@/lib/utils/clack';
import { execAsync } from '@/lib/utils/execAsync';
import { promptAndOpenUrl } from '@/lib/utils/shared';

/**
 * Generates the MCP configuration object for Claude Desktop
 * @param agentKey - The Scout APM agent key
 * @returns The MCP configuration object
 */
export const mcpConfig = (agentKey: string = 'your_scout_api_key_here') => {
  return {
    mcpServers: {
      'scout-apm': {
        command: 'docker',
        args: ['run', '--rm', '-i', '--env', 'SCOUT_API_KEY', 'scoutapp/scout-mcp-local:latest'],
        env: { SCOUT_API_KEY: agentKey },
      },
    },
  };
};

const getClaudeDesktopConfigPath = (): string => {
  const platform = os.platform();
  if (platform === 'darwin') {
    return path.join(
      os.homedir(),
      'Library',
      'Application Support',
      'Claude',
      'claude_desktop_config.json'
    );
  } else if (platform === 'win32') {
    return path.join(process.env.APPDATA || '', 'Claude', 'claude_desktop_config.json');
  } else {
    // Linux or other platforms - Claude Desktop may not be available
    throw new Error('Claude Desktop config path not supported on this platform');
  }
};

/**
 * Set up Scout MCP for Claude Code using the `claude` CLI
 * @param agentKey - The Scout APM agent key
 * @returns void
 */
export const setupClaudeCode = async (agentKey: string): Promise<void> => {
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
    command: 'docker',
    args: ['run', '--rm', '-i', '--env', 'SCOUT_API_KEY', 'scoutapp/scout-mcp-local:latest'],
    env: { SCOUT_API_KEY: agentKey },
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
export const setupCursor = async (agentKey: string): Promise<void> => {
  console.log(chalk.blue('Setting up Scout MCP for Cursor...'));
  console.log(chalk.yellow("We'll open a Cursor deeplink to install Scout MCP."));

  // Generate the dynamic Cursor deeplink with the actual API key
  const deeplink = generateCursorDeeplink(agentKey);

  await promptAndOpenUrl(
    'Press enter to open the Cursor deeplink',
    deeplink,
    'Please manually open Cursor and add the Scout MCP server configuration.'
  );

  console.log(
    chalk.yellow(
      'After clicking "Add Server" in Cursor, the Scout MCP will be configured with your API key automatically.'
    )
  );
  console.log(chalk.blue('No further manual configuration should be needed!'));
};
/**
 * Set up Scout MCP for Claude Desktop by updating the config file
 * @param agentKey - The Scout APM agent key
 * @returns void
 */
export const setupClaudeDesktop = async (agentKey: string): Promise<void> => {
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
      } catch (_) {
        console.log(
          chalk.yellow('Warning: Could not parse existing Claude config, will create new one')
        );
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
        ...config.mcpServers,
      },
    };

    // Write the config
    fs.writeFileSync(configPath, JSON.stringify(finalConfig, null, 2));

    console.log(chalk.green('✓ Scout MCP configuration added to Claude Desktop!'));
    console.log(chalk.blue(`Config file updated: ${configPath}`));
    console.log(chalk.yellow('Please restart Claude Desktop for the changes to take effect.'));
  } catch (error: any) {
    console.log(chalk.red('✗ Failed to update Claude Desktop config'));
    console.log(chalk.red('Error:'), error.message);

    console.log(
      chalk.yellow('Please manually add this configuration to your Claude Desktop config:')
    );
    console.log(JSON.stringify(mcpConfig(agentKey), null, 2));
  }
};
