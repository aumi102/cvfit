const COMMIT_SHA = /^[0-9a-f]{7,40}$/i;
const ENVIRONMENTS = new Set(['development', 'test', 'staging', 'production']);

export function safeFrontendBuildMetadata(environment = process.env) {
  const rawSha = environment.RENDER_GIT_COMMIT || environment.NEXT_PUBLIC_BUILD_SHA || '';
  const commitSha = COMMIT_SHA.test(rawSha) ? rawSha.toLowerCase() : 'unknown';
  const rawEnvironment = environment.APP_ENVIRONMENT
    || (String(environment.RENDER).toLowerCase() === 'true' ? 'production' : environment.NODE_ENV)
    || '';
  const publicEnvironment = ENVIRONMENTS.has(rawEnvironment) ? rawEnvironment : 'unknown';
  const rawBuildTime = environment.BUILD_TIME || '';
  const buildTime = rawBuildTime.length <= 40 && !Number.isNaN(Date.parse(rawBuildTime))
    ? rawBuildTime
    : null;
  return {
    service: 'frontend',
    commit_sha: commitSha,
    environment: publicEnvironment,
    build_time: buildTime,
  };
}

export async function GET() {
  return Response.json(safeFrontendBuildMetadata(), {
    headers: { 'Cache-Control': 'no-store' },
  });
}
