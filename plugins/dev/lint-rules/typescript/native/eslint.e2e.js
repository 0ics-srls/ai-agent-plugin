import { defineConfig } from "eslint/config";
import playwright from "eslint-plugin-playwright";

// The end-to-end code: the rules of eslint-plugin-playwright that find a test that does not test —
// a call nobody awaits, an assertion that cannot fail, a `.only` left behind — and only them.
export default defineConfig({
  files: ["e2e/**/*.ts"],
  plugins: { playwright },
  rules: {
    // Enforce assertion to be made in a test body.
    "playwright/expect-expect": "error",
    // Identify false positives when async Playwright APIs are not properly awaited.
    "playwright/missing-playwright-await": "error",
    // Disallow calling `expect` conditionally.
    "playwright/no-conditional-expect": "error",
    // Prevent usage of `.only()` focus test annotation.
    "playwright/no-focused-test": "error",
    // Prevent usage of page.pause().
    "playwright/no-page-pause": "error",
    // Disallow assertions on a Locator that can never fail.
    "playwright/no-unnecessary-assertions": "error",
    // Prevent unsafe variable references in page.evaluate() and page.addInitScript().
    "playwright/no-unsafe-references": "error",
    // Disallow usage of page locators that are not used.
    "playwright/no-unused-locators": "error",
    // Prevent usage of page.waitForTimeout().
    "playwright/no-wait-for-timeout": "error",
    // Prefer web first assertions.
    "playwright/prefer-web-first-assertions": "error",
    // Enforce valid `expect()` usage.
    "playwright/valid-expect": "error",
    // Require promises that have expectations in their chain to be valid.
    "playwright/valid-expect-in-promise": "error",
  },
});
