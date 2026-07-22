import os from 'node:os';
import path from 'node:path';
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  outputDir: path.join(os.tmpdir(), 'cvfit-playwright-results'),
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:3000',
    browserName: 'chromium',
    channel: process.env.CI ? undefined : 'msedge',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
});
