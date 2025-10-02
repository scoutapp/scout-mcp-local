import { vi, beforeEach } from 'vitest';

// Mock global fetch
global.fetch = vi.fn();

// Don't mock crypto - we need real crypto for the implementation
// The tests will check URL patterns instead of exact hashes

vi.mock('node:child_process', async () => {
  const actual = await vi.importActual<typeof import('node:child_process')>('node:child_process');
  return {
    ...actual,
    // eslint-disable-next-line
    exec: vi.fn((cmd: string, cb: Function) => {
      cb(null, 'Successfully added MCP server', '');
      return {} as any;
    }),
  };
});

vi.mock('node:fs', async () => {
  const actual = await vi.importActual<typeof import('node:fs')>('node:fs');
  return {
    ...actual,
    existsSync: vi.fn(),
    readFileSync: vi.fn(),
    writeFileSync: vi.fn(),
    mkdirSync: vi.fn(),
  };
});

vi.mock('node:path', async () => {
  const actual = await vi.importActual<typeof import('node:path')>('node:path');
  return {
    ...actual,
    join: vi.fn((...paths) => paths.join('/')),
    dirname: vi.fn(path => path.split('/').slice(0, -1).join('/')),
  };
});

vi.mock('node:os', async () => {
  const actual = await vi.importActual<typeof import('node:os')>('node:os');
  return {
    ...actual,
    platform: vi.fn(() => 'darwin'),
    homedir: vi.fn(() => '/Users/testuser'),
  };
});

// Mock external dependencies
vi.mock('open', () => ({
  default: vi.fn(),
}));

vi.mock('ora', () => ({
  default: vi.fn(() => ({
    start: vi.fn().mockReturnThis(),
    succeed: vi.fn().mockReturnThis(),
    fail: vi.fn().mockReturnThis(),
    stop: vi.fn().mockReturnThis(),
  })),
}));

vi.mock('chalk', () => ({
  default: {
    blue: vi.fn(text => text),
    yellow: vi.fn(text => text),
    green: vi.fn(text => text),
    red: vi.fn(text => text),
    gray: vi.fn(text => text),
  },
}));

vi.mock('@clack/prompts', () => ({
  select: vi.fn(),
  text: vi.fn(),
  confirm: vi.fn(),
}));

// Reset all mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
  // Mock console.log to reduce noise in tests
  vi.spyOn(console, 'log').mockImplementation(() => {});
});
