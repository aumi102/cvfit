import { describe, expect, it } from 'vitest';
import { safeFrontendBuildMetadata } from './route';


describe('frontend build metadata', () => {
  it('exposes only allowlisted deployment identity', () => {
    const metadata = safeFrontendBuildMetadata({
      RENDER_GIT_COMMIT: '1099396339a24e9b3d1387301a2c57f397f1bb55',
      RENDER: 'true',
      BUILD_TIME: '2026-07-22T08:30:00Z',
      OPENAI_API_KEY: 'must-not-leak',
      DATABASE_URL: 'must-not-leak',
    });

    expect(metadata).toEqual({
      service: 'frontend',
      commit_sha: '1099396339a24e9b3d1387301a2c57f397f1bb55',
      environment: 'production',
      build_time: '2026-07-22T08:30:00Z',
    });
    expect(JSON.stringify(metadata)).not.toContain('must-not-leak');
  });
});
