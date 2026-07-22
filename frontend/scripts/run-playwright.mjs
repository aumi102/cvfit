import { spawn } from 'node:child_process';
import { once } from 'node:events';
import process from 'node:process';

const SERVER_URL = 'http://127.0.0.1:3000';
const STARTUP_TIMEOUT_MS = 120_000;
const SHUTDOWN_TIMEOUT_MS = 5_000;

const children = new Set();
let shuttingDown = false;

function launch(command, args, options = {}) {
  const child = spawn(command, args, {
    ...options,
    detached: process.platform !== 'win32',
  });
  children.add(child);
  child.once('exit', () => children.delete(child));
  return child;
}

async function waitForServer(server) {
  const deadline = Date.now() + STARTUP_TIMEOUT_MS;
  while (Date.now() < deadline) {
    if (server.exitCode !== null) {
      throw new Error(`Next.js test server exited with code ${server.exitCode}`);
    }
    try {
      const response = await fetch(SERVER_URL, { signal: AbortSignal.timeout(2_000) });
      if (response.ok) return;
    } catch {
      // The server may still be compiling or binding the port.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error('Timed out while starting the Next.js test server');
}

async function stopProcessTree(child) {
  if (!child || child.exitCode !== null || child.signalCode !== null) return;

  if (process.platform === 'win32') {
    const killer = spawn('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'], {
      stdio: 'ignore',
      windowsHide: true,
    });
    await once(killer, 'exit');
    return;
  }

  try {
    process.kill(-child.pid, 'SIGTERM');
  } catch (error) {
    if (error.code !== 'ESRCH') throw error;
    return;
  }

  const exited = once(child, 'exit').then(() => true);
  const timedOut = new Promise((resolve) => {
    setTimeout(() => resolve(false), SHUTDOWN_TIMEOUT_MS).unref();
  });
  if (await Promise.race([exited, timedOut])) return;

  try {
    process.kill(-child.pid, 'SIGKILL');
  } catch (error) {
    if (error.code !== 'ESRCH') throw error;
  }
}

async function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  await Promise.allSettled([...children].map(stopProcessTree));
}

async function main() {
  const server = launch(process.execPath, [
    './node_modules/next/dist/bin/next',
    'start',
    '--hostname',
    '127.0.0.1',
    '--port',
    '3000',
  ], { stdio: ['ignore', 'inherit', 'inherit'] });

  await waitForServer(server);

  const playwright = launch(process.execPath, [
    './node_modules/@playwright/test/cli.js',
    'test',
    ...process.argv.slice(2),
  ], { stdio: 'inherit' });
  const [code, signal] = await once(playwright, 'exit');
  if (signal) return 1;
  return code ?? 1;
}

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.once(signal, async () => {
    await shutdown();
    process.exit(1);
  });
}

let exitCode = 1;
try {
  exitCode = await main();
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
} finally {
  await shutdown();
}
// The startup probe uses Node's global fetch, whose pooled socket may remain
// referenced on Windows after the owned server and Playwright child exit.
// Cleanup above is complete, so terminate the test runner deterministically.
process.exit(exitCode);
