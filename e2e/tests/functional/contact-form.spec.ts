import { test, expect, type Page } from "@playwright/test";

import { dismissTorWarning } from "../helpers/tor-warning";

// Contact form tests, originating with our QA checklist item:
//
//  "Verify contact form submission works as expected (functionality may be
//   limited in staging)"

const HELP_FORM = "/help/";

// Skip a test that submits the form when running against a deployed environment
function skipWhenDeployed() {
  test.skip(
    Boolean(process.env.E2E_ENV),
    "submissions from a deployed environment reach the real help desk",
  );
}

// Open the form, with the Tor Browser warning dismissed (by setting
// torWarningDismissed in session storage) so it can't cover the form
async function openForm(page: Page) {
  await dismissTorWarning(page);
  const response = await page.goto(HELP_FORM);
  expect(response?.ok(), `${HELP_FORM} should load`).toBe(true);
  return page.locator("form.basic-form");
}

test.describe("contact form", { tag: ["@qa", "@forms"] }, () => {

  test("renders", async ({ page }) => {
    const form = await openForm(page);
    const submit = form.getByRole("button", { name: /submit|send/i });

    await expect(form).toBeVisible();
    await expect(form.locator(".basic-form__field").first()).toBeVisible();
    await expect(submit).toBeVisible();
  });

  test("blocks an incomplete submission in the browser", async ({ page }) => {
    skipWhenDeployed();

    const form = await openForm(page);
    const submit = form.getByRole("button", { name: /submit|send/i });
    await submit.click();

    // The browser flags the required fields, and doesn't send it
    await expect(form.locator("input:invalid, textarea:invalid, select:invalid")).not.toHaveCount(0);
    await expect(form).toBeVisible();
  });

  test("accepts a submission", async ({ page }, testInfo) => {
    // Only accept a submission when running the QA stack, not on a deployed
    // environment.
    skipWhenDeployed();

    // Generous, as it waits out the form's honeypot interval (below)
    test.setTimeout(60_000);

    // Fill in the form's required fields
    const form = await openForm(page);
    await form.getByRole("textbox", { name: "Name of your organization" }).fill("QA test");
    await form.getByRole("textbox", { name: "Subject of your request" }).fill("QA test request.");
    await form.getByRole("textbox", { name: "Email address" }).fill("qa@example.com");

    // The form's honeypot silently discards submissions made within 3 seconds
    // of the form being served, as likely spam, so  we have to wait that out.
    await page.waitForTimeout(4_500);

    await form.getByRole("button", { name: /submit|send/i }).click();
    await expect(page.locator(".thanks"), "the thank you page should show").toBeVisible();
  });
});
