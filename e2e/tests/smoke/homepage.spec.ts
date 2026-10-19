import { test, expect } from "@playwright/test";

test.describe("homepage", () => {
  test("renders", { tag: ["@smoke"] }, async ({ page }) => {
    const response = await page.goto("/");
    expect(response?.ok()).toBe(true);

    // Has the page hero
    const hero = page.locator(".hero");
    await expect(hero).toBeVisible();

    // Has navigation
    await expect(page.getByRole("navigation").first()).toBeAttached();
  });
});
