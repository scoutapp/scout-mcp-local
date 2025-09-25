import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [tsconfigPaths()],
  build: {
    target: 'node18',
    outDir: 'dist',
    lib: {
      entry: 'bin.ts',
      formats: ['es'],
    },
    rollupOptions: {
      external: [
        'node:process',
        'node:buffer',
        'node:path', 
        'node:url',
        'node:util',
        'node:child_process',
        'node:fs/promises',
        'node:fs',
        'node:os',
        'node:crypto',
        'chalk',
        '@clack/core',
        '@clack/prompts',
        'open'
      ],
    },
  },
});