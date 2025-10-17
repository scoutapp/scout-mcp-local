import chalk from 'chalk';
import clack from '@/lib/utils/clack';
import { promptAndOpenUrl, getBaseUrl } from '@/lib/utils/shared';
import { setupClaudeCode, setupCursor, setupClaudeDesktop, mcpConfig } from './mcp/mcp';
import { authenticateWithUat } from './uat/authenticate';
import type { UatKeyResponse } from './uat/authenticate';
import { setupRails, isRailsProject } from './rails/setup';

/**
 * Main setup function to guide user through configuration
 */
export async function setup(): Promise<void> {
  // Auto-detect Rails project
  const cwd = process.cwd();
  const railsDetected = isRailsProject(cwd);

  // Show context-aware setup type prompt
  let setupTypeMessage: string;
  let setupTypeOptions: Array<{ value: string; label: string }>;

  if (railsDetected) {
    setupTypeMessage = '✓ Detected Rails project! What would you like to set up?';
    setupTypeOptions = [
      { value: 'rails', label: 'Scout APM for this Rails app (auto-configure)' },
      { value: 'mcp', label: 'Scout MCP (AI assistant integration)' },
      { value: 'exit', label: 'Exit' },
    ];
  } else {
    setupTypeMessage = 'What would you like to set up?';
    setupTypeOptions = [
      { value: 'mcp', label: 'Scout MCP (AI assistant integration)' },
      { value: 'rails', label: 'Scout APM for Rails (specify project path)' },
      { value: 'exit', label: 'Exit' },
    ];
  }

  const setupType = await clack.select({
    message: setupTypeMessage,
    options: setupTypeOptions,
  });

  if (setupType === 'exit') {
    console.log(chalk.yellow('Goodbye!'));
    return;
  }

  // Show info note about Python support
  console.log(
    chalk.gray(
      'Note: Scout APM also supports Python and other languages/frameworks. The MCP can help you configure Scout APM for your project.\n'
    )
  );

  const action = await clack.select({
    message: 'Are you currently a Scout APM customer?',
    options: [
      { value: 'sign_in', label: 'Yes' },
      { value: 'sign_up', label: 'No' },
      { value: 'exit', label: 'Exit' },
    ],
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

    console.log(
      chalk.blue("We'll open the Scout APM settings page where you can copy your API key.")
    );
    await promptAndOpenUrl(
      'Press enter to open the Scout APM settings page',
      `${baseUrl}/settings`,
      `Please visit ${baseUrl}/settings to get your API key.`
    );
    agentKey = await collectKey();
  }

  // Route to appropriate setup based on user selection
  if (setupType === 'rails') {
    // Rails setup flow - requires org_key
    const orgKey = keys ? keys.org_key : null;

    if (!orgKey) {
      console.log(chalk.red('✗ Failed to retrieve organization key. Please try again.'));
      return;
    }

    await setupRails(orgKey, railsDetected ? cwd : undefined);
  } else if (setupType === 'mcp') {
    // MCP setup flow - requires api_key
    if (!agentKey) {
      console.log(chalk.red('✗ Failed to retrieve API key. Please try again.'));
      return;
    }

    const aiAssistant = await clack.select({
      message: 'Which AI assistant are you using?',
      options: [
        { value: 'cursor', label: 'Cursor' },
        { value: 'claude-code', label: 'Claude Code (CLI)' },
        { value: 'claude-desktop', label: 'Claude Desktop' },
        { value: 'manual', label: 'Manual setup (show JSON config)' },
      ],
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
        console.log(
          chalk.green('Please paste the following into your MCP config to complete setup:')
        );
        console.log(JSON.stringify(mcpConfig(agentKey), null, 2));
        break;

      default:
        console.log(chalk.red('Invalid selection'));
    }
  }
}
