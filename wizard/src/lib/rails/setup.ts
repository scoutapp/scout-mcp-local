import chalk from 'chalk';
import clack from '@/lib/utils/clack';
import { readFileSync, writeFileSync, existsSync, mkdirSync, accessSync, constants } from 'node:fs';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Check if a directory is a Rails project root
 */
export function isRailsProject(path: string): boolean {
  try {
    const hasGemfile = existsSync(join(path, 'Gemfile'));
    const hasConfigDir = existsSync(join(path, 'config'));
    return hasGemfile && hasConfigDir;
  } catch {
    return false;
  }
}

/**
 * Validate that a path exists and is writable
 */
function validateProjectPath(path: string): { valid: boolean; error?: string } {
  if (!existsSync(path)) {
    return { valid: false, error: 'Path does not exist' };
  }

  try {
    accessSync(path, constants.W_OK);
    return { valid: true };
  } catch {
    return { valid: false, error: 'Path is not writable' };
  }
}

/**
 * Main Rails setup function
 */
export async function setupRails(orgKey: string, detectedPath?: string): Promise<void> {
  let projectPath: string;

  if (detectedPath) {
    // Rails project was auto-detected
    const confirm = await clack.confirm({
      message: `Use current directory for Rails setup? (${detectedPath})`,
    });

    if (confirm) {
      projectPath = detectedPath;
    } else {
      const customPath = await clack.text({
        message: 'Enter your Rails project path:',
        placeholder: '/path/to/rails/project',
      });
      projectPath = resolve(customPath.toString());
    }
  } else {
    // No auto-detection, prompt for path
    const customPath = await clack.text({
      message: 'Enter your Rails project path:',
      placeholder: '/path/to/rails/project',
    });
    projectPath = resolve(customPath.toString());
  }

  // Validate the project path
  const validation = validateProjectPath(projectPath);
  if (!validation.valid) {
    console.log(chalk.red(`✗ Error: ${validation.error}`));
    return;
  }

  // Verify it's a Rails project
  if (!isRailsProject(projectPath)) {
    console.log(
      chalk.yellow(
        '⚠ Warning: This does not appear to be a Rails project (missing Gemfile or config/ directory)'
      )
    );
    const proceed = await clack.confirm({
      message: 'Continue anyway?',
    });

    if (!proceed) {
      console.log(chalk.yellow('Setup cancelled.'));
      return;
    }
  }

  // Ensure config directory exists
  const configDir = join(projectPath, 'config');
  if (!existsSync(configDir)) {
    console.log(chalk.blue('Creating config/ directory...'));
    try {
      mkdirSync(configDir, { recursive: true });
    } catch (error: any) {
      console.log(chalk.red(`✗ Failed to create config/ directory: ${error.message}`));
      return;
    }
  }

  // Check if config file already exists
  let configPath = join(configDir, 'scout_apm.yml');
  if (existsSync(configPath)) {
    console.log(chalk.yellow('⚠ scout_apm.yml already exists.'));
    const action = await clack.select({
      message: 'What would you like to do?',
      options: [
        { value: 'new', label: 'Create scout_apm.wizard.yml' },
        { value: 'overwrite', label: 'Overwrite existing scout_apm.yml' },
        { value: 'cancel', label: 'Cancel' },
      ],
    });

    if (action === 'cancel') {
      console.log(chalk.yellow('Setup cancelled.'));
      return;
    }

    if (action === 'new') {
      configPath = join(configDir, 'scout_apm.wizard.yml');
      console.log(chalk.blue(`Creating ${configPath} instead...`));
    }
  }

  // Read template and replace placeholder
  try {
    const templatePath = resolve(__dirname, 'lib/templates/scout_apm.yml.template');
    const template = readFileSync(templatePath, 'utf-8');
    const configContent = template.replace('{{SCOUT_KEY}}', orgKey);

    // Write the configuration file
    writeFileSync(configPath, configContent, 'utf-8');

    console.log(chalk.green(`\n✓ Successfully created ${configPath}`));

    // If we created a .wizard.yml file, add a note about reviewing it
    if (configPath.endsWith('.wizard.yml')) {
      console.log(
        chalk.yellow('\n⚠ Note: Review the generated file and rename to scout_apm.yml when ready.')
      );
    }

    console.log(chalk.blue('\nNext steps:'));
    console.log(chalk.white('  1. Add scout_apm gem to your Gemfile:'));
    console.log(chalk.gray("     gem 'scout_apm'"));
    console.log(chalk.white('  2. Run bundle install:'));
    console.log(chalk.gray('     bundle install'));
    console.log(chalk.white('  3. Deploy your application'));
    console.log(
      chalk.white('\n  Your data should appear in Scout APM within ~5 minutes of deployment.\n')
    );
    console.log(chalk.blue('For more info: https://scoutapm.com/docs/ruby/configuration\n'));
  } catch (error: any) {
    console.log(chalk.red(`✗ Failed to create configuration file: ${error.message}`));
    throw error;
  }
}
