import {
  test,
  expect,
  type Browser,
  type BrowserContextOptions,
  type Page,
} from "@playwright/test";

import { adminLogin } from "../helpers/admin";

// CMS lifecycle tests, originating with our QA checklist item:
//
//  "Verify basic CMS functionality (saving drafts, publishing changes)
//   across content types".
//
// The intent is to verify that the CMS is functional, not that the Wagtail
// admin works.
test.describe("CMS content lifecycle", () => {
  test.beforeEach(async ({ page }, testInfo) => {
    // Because these are intended to verify that CMS content lifecycle
    // functionality works as expected (and NOT that the Wagtail admin itself
    // works cross-browser) we don't actually need to run these in the full
    // browser matrix. This has the advantage of reducing the load on the
    // running target environment too.
    //
    // So, this skips these tests for all but the first configured browser.
    const [firstBrowser] = testInfo.config.projects;
    test.skip(
      testInfo.project.name !== firstBrowser.name,
      `the CMS specs run in one browser only (${firstBrowser.name})`,
    );

    // Either log in with the dev user admin credentials or via pre-captured session
    test.skip(
      !(await adminLogin(page)),
      "no Wagtail admin session; capture one with `just qa-auth ENV` or set E2E_ADMIN_USER/E2E_ADMIN_PASSWORD",
    );
  });

  // Test a simple page's lifecycle
  test.describe("simple page", { tag: ["@qa", "@cms", "@simple"] }, () => {
    // The tests in this scope have to be run serially
    test.describe.configure({ mode: "serial" });

    const suffix = Date.now();
    const title = `QA test simple page ${suffix}`;
    const editedTitle = `${title} (edited)`;
    const slug = `qa-test-simple-page-${suffix}`;
    const publicPath = `/${slug}/`;

    // The page this test builds, passed along from the step that creates it.
    let created: number | null = null;

    test.afterAll(async ({ browser }, workerInfo) => {
      await deletePage(browser, workerInfo.project.use, created);
    });

    test("saves a draft", async ({ page }) => {
      // Let this run a little bit long if it needs to, since it interacts
      // with the page explorer to find where to create the new page, and
      // the page editor widgets to give it content.
      test.setTimeout(60_000);

      // Get the home page ("SecureDrop") via the page explorer. Its link name
      // also carries any status tag, e.g. "SecureDrop LIVE + DRAFT".
      await page.getByRole("button", { name: "Pages" }).click();
      const explorer = page.getByRole("dialog", { name: "Page explorer" });
      await explorer.getByRole("link", { name: /^SecureDrop\b/ }).click();

      // Add a child page
      await page.getByRole("link", { name: "Add child page" }).click();

      await page.getByRole("link", { name: "Simple page", exact: true }).click();
      await expect(
        page.locator("#id_title"),
        "a simple page should be creatable under the home page",
      ).toBeVisible();
      await page.locator("#id_title").fill(title);

      // Body is required, add a Heading 1 block (a single CharBlock)
      const body = page.locator("[data-contentpath='body']");
      await body.getByRole("button", { name: "Insert a block" }).click();
      await page.getByRole("option", { name: "Heading 1", exact: true }).click();
      await body.getByRole("textbox").fill("QA test body copy.");

      // Go to the "Promote" tab and edit the slug
      await page.getByRole("tab", { name: /promote/i }).click();
      await page.locator("#id_slug").fill(slug);

      // Save the draft
      await page.getByRole("button", { name: "Save draft" }).click();
      await expect(page.locator(".messages li.success")).toContainText(/created/i);

      // Capture the page id from the URL, for the steps that follow
      created = Number(page.url().match(/\/pages\/(\d+)\//)?.[1]);
      expect(created, "the editor URL should carry the new page id").not.toBeNaN();

      const draft = await page.request.get(publicPath);
      expect(draft.status(), `${publicPath} should 404 while it is a draft`).toBe(404);

      const preview = await page.request.get(`/admin/pages/${created}/view_draft/`);
      expect(preview.status(), "draft preview should render").toBe(200);
    });

    test("publishes", async ({ page }) => {
      await page.goto(`/admin/pages/${created}/edit/`);
      await publish(page);

      const live = await page.goto(publicPath, { waitUntil: "domcontentloaded" });
      expect(live?.status(), `${publicPath} should be live after publishing`).toBe(200);
      expect(await page.title()).toContain(title);
    });

    test("publishes an edit", async ({ page }) => {
      await page.goto(`/admin/pages/${created}/edit/`);
      await page.locator("#id_title").fill(editedTitle);
      await publish(page);

      await page.goto(publicPath, { waitUntil: "domcontentloaded" });
      expect(
        await page.title(),
        "the published edit should be visible on the live page",
      ).toContain(editedTitle);
    });

    test("unpublishes", async ({ page }) => {
      await page.goto(`/admin/pages/${created}/unpublish/`);
      await page.getByRole("button", { name: /yes, unpublish it/i }).click();
      await expect(page.locator(".messages li.success")).toContainText(/unpublished/i);

      const unpublished = await page.request.get(publicPath);
      expect(unpublished.status(), `${publicPath} should 404 once unpublished`).toBe(404);
    });
  });
});

// Perform a page deletion, used at the end of the lifecycle tests to remove
// the test page they created
async function deletePage(
  browser: Browser,
  use: BrowserContextOptions,
  created: number | null,
) {
  if (created === null || Number.isNaN(created)) return;

  // A context of our own, carrying the same base URL and stored session the
  // tests ran with.
  const context = await browser.newContext({
    baseURL: use.baseURL,
    storageState: use.storageState,
  });
  const page = await context.newPage();

  if (await adminLogin(page)) {
    await page.goto(`/admin/pages/${created}/delete/`);
    const confirm = page.getByRole("button", { name: /yes, delete it/i });
    if (await confirm.count()) await confirm.click();
  }

  await context.close();
}

// Perform the actions needed to publish a page, and if it fails try to provide
// helpful error messaging
async function publish(page: Page) {
  //  "Publish" is under the "More actions" toggle
  const publishButton = page.locator("button[name='action-publish']");
  if (!(await publishButton.isVisible())) {
    await page.getByRole("button", { name: /more actions/i }).click();
  }
  await publishButton.click();

  // Check for success or failure
  const success = page.locator(".messages li.success");
  const failure = page.locator(".messages li.error");
  await expect(success.or(failure).first()).toBeVisible({ timeout: 30_000 });

  if (await failure.count()) {
    // Determine which field might've failed validation and report it out
    const invalid = await page.locator(".w-field--error").evaluateAll((fields) =>
      fields.map((field) => {
        const path = field.closest("[data-contentpath]")?.getAttribute("data-contentpath");
        const message = field.querySelector(".error-message")?.textContent ?? "";
        return `  ${path ?? "unknown field"}: ${message.trim()}`;
      }),
    );
    throw new Error(`publishing failed on validation errors:\n${invalid.join("\n")}`);
  }

  await expect(success).toContainText(/published/i);
}
