import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { isRailsProject } from '@/lib/rails/setup';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

vi.mock('node:fs');

describe('Rails Setup', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('isRailsProject', () => {
    it('should return true when both Gemfile and config directory exist', () => {
      vi.mocked(existsSync).mockImplementation((path: any) => {
        const pathStr = path.toString();
        return pathStr.includes('Gemfile') || pathStr.includes('config');
      });

      const result = isRailsProject('/test/rails/project');

      expect(result).toBe(true);
      expect(existsSync).toHaveBeenCalledWith(join('/test/rails/project', 'Gemfile'));
      expect(existsSync).toHaveBeenCalledWith(join('/test/rails/project', 'config'));
    });

    it('should return false when Gemfile is missing', () => {
      vi.mocked(existsSync).mockImplementation((path: any) => {
        const pathStr = path.toString();
        return pathStr.includes('config'); // Only config exists
      });

      const result = isRailsProject('/test/rails/project');

      expect(result).toBe(false);
    });

    it('should return false when config directory is missing', () => {
      vi.mocked(existsSync).mockImplementation((path: any) => {
        const pathStr = path.toString();
        return pathStr.includes('Gemfile'); // Only Gemfile exists
      });

      const result = isRailsProject('/test/rails/project');

      expect(result).toBe(false);
    });

    it('should return false when both Gemfile and config directory are missing', () => {
      vi.mocked(existsSync).mockReturnValue(false);

      const result = isRailsProject('/test/rails/project');

      expect(result).toBe(false);
    });

    it('should handle errors gracefully and return false', () => {
      vi.mocked(existsSync).mockImplementation(() => {
        throw new Error('File system error');
      });

      const result = isRailsProject('/test/rails/project');

      expect(result).toBe(false);
    });
  });
});
