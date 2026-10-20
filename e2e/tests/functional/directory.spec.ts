import { test, expect, type Page } from "@playwright/test";

import { dismissTorWarning } from "../helpers/tor-warning";

// Directory tests, originating with our QA checklist items:
//
//  "Verify directory filters (country/topic/language) work as expected"
//  "Verify directory search works as expected"
//
// These take their filter and search values from the listing itself, so they
// work against the QA data and deployed environments alike.

const DIRECTORY = "/directory/";

// Unlikely to appear in any entry title anywhere, hopefully?
const NO_MATCH = "zqxjkvw-no-such-instance";

// Selector for instance listing table rows
const ROWS = "tr.instance-table__row";

// The titles of the entries currently listed
async function listedTitles(page: Page): Promise<string[]> {
  return page
    .locator(`${ROWS} .instance-table__org-name`)
    .evaluateAll((names) => names.map((name) => name.textContent?.trim() ?? ""));
}

// Submit the filter form, with whichever submit button the viewport shows
async function submitFilters(page: Page) {
  await page
    .locator("form.filter-form")
    .getByRole("button", { name: "submit" })
    .filter({ visible: true })
    .click();
  await page.waitForLoadState("domcontentloaded");
}

// Common function to check a particular filter using the filter dropdown.
async function checkFilter(page: Page, param: string, label: string) {
  await dismissTorWarning(page);

  await page.goto(DIRECTORY, { waitUntil: "domcontentloaded" });
  const rows = page.locator(ROWS);

  // Each instance lists its languages, countries and topics in its hidden
  // tag-list,with their link parameters being the only distinction.
  // So first we select the tag links for this specific parameter.
  const tagLinks = `a.tag-list__link[href*="?${param}="]`;

  // Then get the link text of the first match (i.e. "English" for the
  // "language" parameter).
  const tagName = (await rows.first().locator(tagLinks).first().textContent())?.trim() ?? "";

  // Then make a locator for tag links for this parameter whose text exactly
  // matches the tag name. This is used below to find any instance listed
  // without the tag.
  const tag = page.locator(tagLinks).getByText(tagName, { exact: true });

  // Look up the filter for the given label, and filter by the tag name
  const select = page.getByLabel(label, { exact: true });
  await select.selectOption({ label: tagName });
  await submitFilters(page);

  // The filter should stay selected
  await expect(select.locator("option:checked")).toHaveText(tagName);

  // There should be results
  await expect(rows).not.toHaveCount(0);

  // Every row should have the tag... this tests the negative though, that
  // there are zero rows that do NOT have the tag
  await expect(rows.filter({ hasNot: tag })).toHaveCount(0);
}

// Test each directory filter in turn.
test.describe("directory filters", { tag: ["@qa", "@directory"] }, () => {
  test("filters by language", async ({ page }) => {
    await checkFilter(page, "language", "Language Accepted");
  });

  test("filters by country", async ({ page }) => {
    await checkFilter(page, "country", "Country");
  });

  test("filters by topic", async ({ page }) => {
    await checkFilter(page, "topic", "Topic");
  });
});

test.describe("directory search", { tag: ["@qa", "@directory", "@search"] }, () => {
  test("finds instances by title", async ({ page }) => {
    await dismissTorWarning(page);

    await page.goto(DIRECTORY, { waitUntil: "domcontentloaded" });
    const [title] = await listedTitles(page);
    expect(title, "the directory should list entries").toBeTruthy();

    // Select the last word of the first entry's title as our search term.
    // This will give us at least one search result.
    const word = title.split(/\s+/).at(-1) ?? title;
    const query = word.toUpperCase();

    // Search!
    const search = page.getByPlaceholder("Search instances...");
    await search.fill(query);
    await search.press("Enter");
    await page.waitForLoadState("domcontentloaded");

    // The search term is in the query string and the search box
    await expect(page).toHaveURL(new RegExp(`[?&]search=${encodeURIComponent(query)}(&|$)`));
    await expect(search).toHaveValue(query);

    // The entry is found, and every result includes the query term
    const results = await listedTitles(page);
    expect(results, `searching "${query}" should find "${title}"`).toContain(title);
    for (const result of results) {
      expect(result.toLowerCase(), `"${result}" should match "${query}"`).toContain(
        word.toLowerCase(),
      );
    }
  });

  test("tells the user when no instances matches", async ({ page }) => {
    await dismissTorWarning(page);

    await page.goto(`${DIRECTORY}?search=${NO_MATCH}`, { waitUntil: "domcontentloaded" });

    await expect(page.getByText("No instances match those filter criteria")).toBeVisible();
    await expect(page.locator(ROWS)).toHaveCount(0);
    await expect(page.getByPlaceholder("Search instances...")).toHaveValue(NO_MATCH);
  });
});
