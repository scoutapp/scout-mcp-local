import chalk from 'chalk';
import clack from "@/lib/utils/clack";

/**
 * Prompts the user to confirm opening a URL and optionally opens it
 * @param message - The confirmation message to show the user
 * @param url - The URL to open if confirmed
 * @param fallbackMessage - Message to show if user declines to open the URL
 * @returns Promise<void>
 */
export const promptAndOpenUrl = async (message: string, url: string, fallbackMessage: string): Promise<void> => {
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

export const openUrl = async (url: string): Promise<void> => {
  const open = (await import('open')).default;
  await open(url);
};

export const getBaseUrl = (): string => {
  return process.env.SCOUT_HOST || 'https://scoutapm.com';
};
