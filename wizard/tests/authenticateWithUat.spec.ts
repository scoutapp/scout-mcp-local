import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as clack from '@clack/prompts'
import ora from 'ora'
import { authenticateWithUat } from '@/lib/setup'

// Get mocked open function
const mockOpen = vi.hoisted(() => vi.fn().mockResolvedValue(undefined))

vi.mock('open', () => ({
  default: mockOpen
}))

describe('authenticateWithUat', () => {
  const mockSpinner = {
    start: vi.fn().mockReturnThis(),
    succeed: vi.fn().mockReturnThis(),
    fail: vi.fn().mockReturnThis(),
    stop: vi.fn().mockReturnThis()
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(ora).mockReturnValue(mockSpinner as any)
    process.env.SCOUT_HOST = 'https://test.scoutapm.com'
  })

  it('should complete full authentication flow successfully', async () => {
    // Mock successful authentication check
    vi.mocked(fetch)
      .mockResolvedValueOnce(new Response(JSON.stringify({ has_authenticated: true }), { status: 200 })) // auth check
      .mockResolvedValueOnce(new Response(JSON.stringify({
        orgs: [{ id: 123, name: 'Test Org' }]
      }), { status: 200 })) // get orgs
      .mockResolvedValueOnce(new Response(JSON.stringify({
        org_key: 'test-org-key',
        api_key: 'test-api-key'
      }), { status: 200 })) // get keys

    const result = await authenticateWithUat('sign_in')

    expect(result).toEqual({
      org_key: 'test-org-key',
      api_key: 'test-api-key'
    })

    expect(mockOpen).toHaveBeenCalled()
    expect(mockOpen.mock.calls[0][0]).toMatch(/^https:\/\/test\.scoutapm\.com\/uat\/auth\/sign_in\/[A-Za-z0-9_-]+$/)
    expect(mockSpinner.start).toHaveBeenCalled()
    expect(mockSpinner.succeed).toHaveBeenCalledWith('Authentication successful! \n')
  })

  it('should handle multiple organizations and prompt for selection', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(new Response(JSON.stringify({ has_authenticated: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        orgs: [
          { id: 123, name: 'Test Org 1' },
          { id: 456, name: 'Test Org 2' }
        ]
      }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        org_key: 'selected-org-key',
        api_key: 'selected-api-key'
      }), { status: 200 }))

    vi.mocked(clack.select).mockResolvedValueOnce('456')

    const result = await authenticateWithUat('sign_in')

    expect(clack.select).toHaveBeenCalledWith({
      message: 'Select an organization:',
      options: [
        { value: '123', label: 'Test Org 1' },
        { value: '456', label: 'Test Org 2' }
      ]
    })

    expect(result).toEqual({
      org_key: 'selected-org-key',
      api_key: 'selected-api-key'
    })
  })

  it('should handle network errors gracefully', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('Network error'))

    const result = await authenticateWithUat('sign_in')

    expect(result).toBeNull()
    expect(mockSpinner.fail).toHaveBeenCalledWith('Authentication failed')
  })

  it('should handle API errors during org retrieval', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(new Response(JSON.stringify({ has_authenticated: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response('Server Error', { status: 500 }))

    const result = await authenticateWithUat('sign_in')

    expect(result).toBeNull()
  })

  it('should handle empty organizations list', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(new Response(JSON.stringify({ has_authenticated: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ orgs: [] }), { status: 200 }))

    const result = await authenticateWithUat('sign_in')

    expect(result).toBeNull()
  })

  it('should handle missing API key in response', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(new Response(JSON.stringify({ has_authenticated: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        orgs: [{ id: 123, name: 'Test Org' }]
      }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        org_key: 'test-org-key'
        // Missing api_key
      }), { status: 200 }))

    const result = await authenticateWithUat('sign_in')

    expect(result).toBeNull()
  })

  it('should use correct auth type in URL', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(new Response(JSON.stringify({ has_authenticated: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        orgs: [{ id: 123, name: 'Test Org' }]
      }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        org_key: 'test-org-key',
        api_key: 'test-api-key'
      }), { status: 200 }))

    await authenticateWithUat('sign_up')

    expect(mockOpen).toHaveBeenCalled()
    expect(mockOpen.mock.calls[0][0]).toMatch(/^https:\/\/test\.scoutapm\.com\/uat\/auth\/sign_up\/[A-Za-z0-9_-]+$/)
  })
})
