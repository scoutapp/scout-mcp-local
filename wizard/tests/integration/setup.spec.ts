import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as clack from '@clack/prompts';
import ora from 'ora';
import open from 'open';

const mockExecAsync = vi.hoisted(() => vi.fn().mockResolvedValue({ stdout: 'mocked', stderr: '' }));

vi.mock('@/lib/utils/execAsync', () => ({
  execAsync: mockExecAsync,
}));

import { setup } from '@/lib/setup';

describe('setup - integration test', () => {
  const mockSpinner = {
    start: vi.fn().mockReturnThis(),
    succeed: vi.fn().mockReturnThis(),
    fail: vi.fn().mockReturnThis(),
    stop: vi.fn().mockReturnThis(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(ora).mockReturnValue(mockSpinner as any);
    process.env.SCOUT_HOST = 'https://test.scoutapm.com';
  });

  it('should complete full setup flow with multiple orgs and Claude Code selection', async () => {
    // Mock user selections through the setup flow
    vi.mocked(clack.select)
      .mockResolvedValueOnce('mcp') // What would you like to set up? -> MCP
      .mockResolvedValueOnce('sign_in') // Are you a Scout APM customer? -> Yes
      .mockResolvedValueOnce('456') // Select org -> Claude Code Org
      .mockResolvedValueOnce('claude-code'); // Which AI assistant? -> Claude Code

    // Mock confirm for running the claude mcp add command
    vi.mocked(clack.confirm).mockResolvedValueOnce(true);

    // Mock successful authentication check
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ has_authenticated: true }), { status: 200 })
      ) // auth check
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            orgs: [
              { id: 123, name: 'Scout APM Org' },
              { id: 456, name: 'Claude Code Org' },
              { id: 789, name: 'Another Org' },
            ],
          }),
          { status: 200 }
        )
      ) // get orgs
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            org_key: 'claude-code-org-key',
            api_key: 'claude-code-api-key',
          }),
          { status: 200 }
        )
      ); // get keys

    await setup();

    // Verify browser was opened for authentication
    expect(open).toHaveBeenCalled();
    expect(vi.mocked(open).mock.calls[0][0]).toMatch(
      /^https:\/\/test\.scoutapm\.com\/uat\/auth\/sign_in\/[A-Za-z0-9_-]+\?utm_source=scout_wizard$/
    );

    // Verify spinner lifecycle
    expect(mockSpinner.start).toHaveBeenCalled();
    expect(mockSpinner.succeed).toHaveBeenCalledWith('Authentication successful! \n');

    // Verify first selection: What would you like to set up?
    expect(clack.select).toHaveBeenNthCalledWith(1, {
      message: 'What would you like to set up?',
      options: [
        { value: 'mcp', label: 'Scout MCP (AI assistant integration)' },
        { value: 'rails', label: 'Scout APM for Rails (specify project path)' },
        { value: 'exit', label: 'Exit' },
      ],
    });

    // Verify second selection: Are you a Scout APM customer?
    expect(clack.select).toHaveBeenNthCalledWith(2, {
      message: 'Are you currently a Scout APM customer?',
      options: [
        { value: 'sign_in', label: 'Yes' },
        { value: 'sign_up', label: 'No' },
        { value: 'exit', label: 'Exit' },
      ],
    });

    // Verify org selection was prompted with all orgs
    expect(clack.select).toHaveBeenNthCalledWith(3, {
      message: 'Select an organization:',
      options: [
        { value: '123', label: 'Scout APM Org' },
        { value: '456', label: 'Claude Code Org' },
        { value: '789', label: 'Another Org' },
      ],
    });

    // Verify AI assistant selection
    expect(clack.select).toHaveBeenNthCalledWith(4, {
      message: 'Which AI assistant are you using?',
      options: [
        { value: 'cursor', label: 'Cursor' },
        { value: 'claude-code', label: 'Claude Code (CLI)' },
        { value: 'claude-desktop', label: 'Claude Desktop' },
        { value: 'manual', label: 'Manual setup (show JSON config)' },
      ],
    });

    // Verify confirm prompt for running the command
    expect(clack.confirm).toHaveBeenCalledWith({
      message: 'Do you want to run this now?',
    });

    expect(mockExecAsync).toHaveBeenCalledWith(
      'claude mcp add scout-apm -e SCOUT_API_KEY=claude-code-api-key -- docker run --rm -i -e SCOUT_API_KEY scoutapp/scout-mcp-local:latest'
    );
  });
});
