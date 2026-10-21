import path from "path";

import { defineConfig, devices } from "@playwright/test";

// The base site URL to test against. Defaults to http://localhost:8000.
// When running locally, this will need to be the e2e django service with
// data already seeded.
const baseURL = process.env.E2E_BASE_URL ?? "http://localhost:8000";

// Optional per-environment visual baseline folder.
// By default, screenshots are stored in __screenshots__/.
// If E2E_ENV is set, it creates a subdirectory, __screenshots__/{E2E_ENV}
// (i.e. with E2E_ENV=staging, __screenshots__/staging/), to store
// environment-specific screenshots separately.
const envSeg = process.env.E2E_ENV ? `${process.env.E2E_ENV}/` : "";

// Optional saved auth state, captured with npx playwright open --save-storage
const storageState = process.env.E2E_STORAGE_STATE || undefined;

export default defineConfig({
  // The suite itself lives in e2e/, alongside its compose overlay; only this
  // config sits at the root, where playwright finds it by default.
  testDir: "./e2e/tests",
  // Snapshots live next to the specs, committed to the repo, one dir per spec.
  snapshotPathTemplate: `{testDir}/__screenshots__/${envSeg}{testFilePath}/{arg}-{projectName}{ext}`,
  // Test results go in e2e/test-results instead of the root
  outputDir: path.join(__dirname, "e2e", "test-results"),
  // Test files and projects will still be parallelized, but tests within a
  // single file will share one worker.
  fullyParallel: false,
  // Playwright defaults to half of available CPUs for its number of workers.
  // On GitHub Actions, runners have 4 vCPUs, which means Playwright will use
  // 2 workers. For consistency and to avoid CI-specific flakiness, we'll set
  // the same everywhere.
  workers: 2,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI
    ? [
        [
          "html",
          { outputFolder: path.join(__dirname, "e2e", "playwright-report"), open: "never" },
        ],
        ["list"],
      ]
    : "list",
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,
      animations: "disabled",
    },
  },
  use: {
    baseURL,
    storageState,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    reducedMotion: "reduce",
  },
  // Adding a project browser not already used below will require a
  // corresponding change to install that browser in the `playwright` target
  // of ci/containers/Containerfile.
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "mobile-chrome",
      use: { ...devices["Pixel 7"] },
    },
  ],
});
