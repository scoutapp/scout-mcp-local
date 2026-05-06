import { vi, beforeEach } from 'vitest';

// Mock global fetch
global.fetch = vi.fn();

// Don't mock crypto - we need real crypto for the implementation
// The tests will check URL patterns instead of exact hashes

vi.mock('node:child_process', () => {
  const mocks = {
    // eslint-disable-next-line
    exec: vi.fn((cmd: string, cb: Function) => {
      cb(null, 'Successfully added MCP server', '');
      return {} as any;
    }),
  };
  return { ...mocks, default: mocks };
});

vi.mock('node:fs', () => {
  const mocks = {
    existsSync: vi.fn(),
    readFileSync: vi.fn(),
    writeFileSync: vi.fn(),
    mkdirSync: vi.fn(),
  };
  return { ...mocks, default: mocks };
});

vi.mock('node:path', () => {
  const mocks = {
    join: vi.fn((...paths: string[]) => paths.join('/')),
    dirname: vi.fn((path: string) => path.split('/').slice(0, -1).join('/')),
    resolve: vi.fn((...paths: string[]) => paths.join('/')),
    sep: '/',
  };
  return { ...mocks, default: mocks };
});

vi.mock('node:os', () => {
  const mocks = {
    platform: vi.fn(() => 'darwin'),
    homedir: vi.fn(() => '/Users/testuser'),
    tmpdir: vi.fn(() => '/tmp'),
  };
  return { ...mocks, default: mocks };
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
