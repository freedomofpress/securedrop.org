import type { Page } from "@playwright/test";

// Sign into the admin with stored credentials
// If they're not provided as env vars, it's expected that captured session
// data will allow admin access.
export async function adminLogin(page: Page): Promise<boolean> {
  const isDeployed = Boolean(process.env.E2E_ENV?.trim());
  const username = process.env.E2E_ADMIN_USER ?? (isDeployed ? undefined : "test");
  const password = process.env.E2E_ADMIN_PASSWORD ?? (isDeployed ? undefined : "test");

  await page.goto("/admin/");

  const loginForm = page.locator("form#login-form, form[action*='/admin/login']");
  if (!(await loginForm.count())) {
    // Already authenticated by the stored session.
    return true;
  }

  if (!username || !password) {
    return false;
  }

  await page.getByLabel(/username/i).fill(username);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.waitForURL(/\/admin\//);

  return (await loginForm.count()) === 0;
}
