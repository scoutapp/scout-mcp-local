import { exec } from 'node:child_process';

/**
 * Executes a shell command and returns a promise that resolves with the command's stdout and stderr.
 * In a separate module, as exec has been found to be tricky to mock directly in tests.
 * @param command The command to execute
 * @returns Promise resolving to an object with stdout and stderr
 */
export const execAsync = (command: string): Promise<{ stdout: string; stderr: string }> => {
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
