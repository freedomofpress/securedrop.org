import type { Page } from "@playwright/test";

export async function dismissTorWarning(page: Page) {
  // On mobile, the full-page warning about using Tor Browser covers the
  // entire page. This sets it as dismissed in session storage.
  await page.addInitScript(() => {
    window.sessionStorage.setItem("torWarningDismissed", "1");
  });
}
