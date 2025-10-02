import chalk from 'chalk';
import clack from "@/lib/utils/clack";
import { promptAndOpenUrl, getBaseUrl } from '@/lib/utils/shared';
import { setupClaudeCode, setupCursor, setupClaudeDesktop, mcpConfig } from './mcp/mcp';
import { authenticateWithUat } from './uat/authenticate';
import type { UatKeyResponse } from './uat/authenticate';

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
