import { test, expect } from "@playwright/test";

// Directory API tests, originating with our QA checklist item:
//
//  "Verify that the API at /api/v1/directory/ returns directory entries and
//   scan results as expected"
//
// These check the API's shape, rather than look for particular entries, so
// they work against the QA data and deployed environments alike.

const API = "/api/v1/directory/";
const DIRECTORY = "/directory/";

type Entry = {
  title: string;
  slug: string;
  directory_url: string;
  onion_address: string;
  languages: string[];
  topics: string[];
  countries: string[];
  latest_scan: Record<string, unknown> | null;
};

test.describe("directory API", { tag: ["@qa", "@api", "@directory"] }, () => {
  test.beforeEach(async ({}, testInfo) => {
    // We don't need to browser-test the API, skip for all but the first
    // configured browser.
    const [firstBrowser] = testInfo.config.projects;
    test.skip(
      testInfo.project.name !== firstBrowser.name,
      `the API specs run in one browser only (${firstBrowser.name})`,
    );
  });

  test("directory is listed at the API root", async ({ request }) => {
    const response = await request.get("/api/v1/");
    expect(response.ok(), "the API root should respond").toBe(true);
    expect(await response.json()).toHaveProperty("directory");
  });

  test("returns directory entries", async ({ request }) => {
    const response = await request.get(API);
    expect(response.ok(), `${API} should respond`).toBe(true);
    expect(response.headers()["content-type"]).toContain("application/json");

    const entries: Entry[] = await response.json();
    expect(entries.length, "the API should list entries").toBeGreaterThan(0);

    for (const entry of entries) {
      // Ensure DirectoryEntrySerializer fields are present
      expect(Object.keys(entry).sort(), `"${entry.title}" fields`).toEqual([
        "countries",
        "directory_url",
        "first_published_at",
        "landing_page_url",
        "languages",
        "latest_scan",
        "onion_address",
        "onion_name",
        "organization_description",
        "organization_logo",
        "organization_url",
        "slug",
        "title",
        "topics",
      ]);

      // Each entry links to its own page in the directory. decode the path
      // when comparing to preserve non-ASCII slugs.
      expect(decodeURIComponent(new URL(entry.directory_url).pathname)).toBe(
        `${DIRECTORY}${entry.slug}/`,
      );
      expect(entry.onion_address).toMatch(/\.onion$/);

      // Has languages, topics, and countries taxonomy
      for (const field of ["languages", "topics", "countries"] as const) {
        expect(Array.isArray(entry[field]), `"${entry.title}" ${field}`).toBe(true);
        for (const name of entry[field]) expect(typeof name).toBe("string");
      }
    }
  });

  test("returns the latest scan results", async ({ request }) => {
    const entries: Entry[] = await (await request.get(API)).json();

    // The first entry with a scan result
    const scanned = entries.find((entry) => entry.latest_scan !== null);
    expect(scanned, "there should be scan results").toBeDefined();
    const { title, latest_scan: scan } = scanned!;

    // The latest scan is the most recent one that reached the landing page
    expect(scan?.live, `"${title}" latest scan should be live`).toBe(true);
    // And has some data that seems reasonable
    expect(scan?.grade, `"${title}" latest scan grade`).toMatch(/^[ABCDF?]$/);
    expect(
      Date.parse(String(scan?.result_last_seen)),
      `"${title}" latest scan should have a date`,
    ).not.toBeNaN();
  });
});
