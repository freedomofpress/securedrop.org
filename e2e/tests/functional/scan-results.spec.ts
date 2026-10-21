import { test, expect } from "@playwright/test";

import { adminLogin } from "../helpers/admin";

// Directory scan result admin tests, originating with our QA checklist item:
//
//  "Verify that the directory scan result page in the admin interface loads
//   as expected"
const SCAN_RESULTS = "/admin/scanresult/";

test.describe("directory scan results admin", { tag: ["@qa", "@admin", "@directory"] }, () => {
  test.beforeEach(async ({ page }, testInfo) => {
    // These verify the scan results admin works, not that the Wagtail admin
    // works cross-browser, so this skips them for all but the first
    // configured browser.
    const [firstBrowser] = testInfo.config.projects;
    test.skip(
      testInfo.project.name !== firstBrowser.name,
      `the admin specs run in one browser only (${firstBrowser.name})`,
    );

    // Either log in with the dev user admin credentials or via pre-captured session
    test.skip(
      !(await adminLogin(page)),
      "no Wagtail admin session; capture one with `just qa-auth ENV` or set E2E_ADMIN_USER/E2E_ADMIN_PASSWORD",
    );
  });

  test("lists scan results", async ({ page }) => {
    // Get to the listing from the admin menu
    await page.getByRole("link", { name: "Scan results" }).click();
    await expect(page).toHaveURL(new RegExp(`${SCAN_RESULTS}$`));
    await expect(page.getByRole("heading", { level: 1, name: "Scan results" })).toBeVisible();

    // It has the columns we expect, and some results in them
    for (const column of ["Securedrop", "Landing page URL", "Result last seen", "Live", "Grade"]) {
      await expect(page.getByRole("columnheader", { name: column })).toBeVisible();
    }
    await expect(page.locator("table tbody tr")).not.toHaveCount(0);
  });

  test("inspects a scan result", async ({ page }) => {
    await page.goto(SCAN_RESULTS);

    // Each listed result links to its inspect page
    const inspectLink = page.locator(`a[href*="${SCAN_RESULTS}inspect/"]`).first();
    await expect(inspectLink, "scan results should link to their inspect pages").toBeAttached();
    const response = await page.goto((await inspectLink.getAttribute("href")) ?? "");
    expect(response?.status(), "the inspect page should load").toBe(200);

    // Which shows the scan result's details, headed by its name, e.g.
    // "Inspect: Scan result for https://example.org/securedrop"
    await expect(
      page.getByRole("heading", { level: 1, name: /^Inspect: Scan result for / }),
    ).toBeVisible();
    for (const field of ["Landing page URL", "Live", "Grade"]) {
      await expect(page.getByText(field, { exact: true }).first()).toBeVisible();
    }
  });
});
