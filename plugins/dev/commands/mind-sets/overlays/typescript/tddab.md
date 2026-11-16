# TypeScript — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in a TypeScript frontend:
the tests by level and the reference code of a block. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a TypeScript frontend; a plan
copies them into its blocks (`tddab-planner.md`, "The commands, by level").

| Key | Angular | React, Vue |
|---|---|---|
| `@test-focused-frontend` | `npx ng test --watch=false --include {file} --filter "{test}"` | `npx vitest run {file} -t "{test}"` |
| `@test-block-frontend` | `npm run check && npm test` (both regenerate the client first) | the same |
| `@test-fast`, the frontend's part | `npm test` | the same |
| `@test-slow`, the frontend's part | `npm test` | the same |
| `@test-e2e` | `npm run e2e`, whose `playwright.config.ts` starts the backend and the application (`testing.md`) | the same |
| `@gate-final`, the frontend's part | `npm run check`, `npm run build`, `npm run e2e` | the same |

A block that changes a page adds the end-to-end tests of that page to its success, as a criterion
before the three lines: `@test-e2e` narrowed to the page's tag — `npx playwright test --grep @orders`.
`--include` and the file argument take the
test's file, `--filter` and `-t` a pattern of its name. A type expectation fails in `npm run check`
(the compiler), not in the test run: a block whose RED is a type is red in the gate. Vitest fails a
run that finds no test file: the application's first block writes its first test.

## 2. Each part's block, at its level

The RED of a block runs at the level of its part: a converter, the loader, the reading of a problem as
unit tests on a fake of the generated call; a page as an end-to-end test against the backend
(`testing.md`).

## 3. Reference RED — a converter block

```ts
// src/shared/load/primereact.test.ts
import { type TableState, requestOf } from "./primereact";
import { describe, expect, expectTypeOf, test } from "vitest";
import type { Order } from "../../api/model";

const FIELDS = ["Id", "Amount", "Customer.Name"] as const;
const FIRST = 10;
const ROWS = 5;
const DESCENDING = -1;
const START: TableState = { filters: {}, first: FIRST, rows: ROWS, sortField: "", sortOrder: null };

describe("the request of a PrimeReact lazy table", () => {
  test("the page, the sort and a text filter on the declared fields", () => {
    const request = requestOf<Order, typeof FIELDS>(
      { ...START, filters: { "Customer.Name": { matchMode: "contains", value: "Bo" } }, sortField: "Amount", sortOrder: DESCENDING },
      FIELDS,
    );

    expectTypeOf(request.Select).toEqualTypeOf<typeof FIELDS>();
    expect(request).toEqual({
      Filter: ["Customer.Name", "contains", "Bo"],
      RequireTotalCount: true,
      Select: FIELDS,
      Skip: FIRST,
      Sort: [{ Desc: true, Selector: "Amount" }],
      Take: ROWS,
    });
  });

  test("a field the columns do not declare is dropped, an empty filter too", () => {
    const request = requestOf<Order, typeof FIELDS>(
      { ...START, filters: { Amount: { matchMode: "contains", value: "" }, Status: { matchMode: "contains", value: "Open" } }, sortField: "Status" },
      FIELDS,
    );

    expect(request).not.toHaveProperty("Sort");
    expect(request).not.toHaveProperty("Filter");
  });
});
```

## 4. Reference GREEN — the converter

The `requestOf` of `prime.md` §2: the request built from the state, every field through `fieldOf`, no
type assertion. The block's success: the tests above green, `npm run check` green.

## 5. Reference RED — a page block, end to end

```ts
// e2e/orders.spec.ts
import { type Locator, type Page, expect, test } from "@playwright/test";

const ORDERS = 25;
const AMOUNT_STEP = 10;
const PAGE = 10;

const dataRows = (page: Page): Locator => page.getByRole("row").filter({ has: page.getByRole("gridcell") });

test("a page of rows from the server, the largest amounts first when sorted down", { tag: "@orders" }, async ({ page }) => {
  await page.goto("/");
  await expect(dataRows(page)).toHaveCount(PAGE);

  const amount = page.getByRole("button", { name: "Sort by Amount" });
  await amount.click();
  await amount.click();

  const largest = [...Array.from({ length: PAGE }).keys()].map(
    index => new RegExp(`-[0-9]{2}${String((ORDERS - index) * AMOUNT_STEP)}(?:Open|Closed)`, "u"),
  );
  await expect(dataRows(page)).toHaveText(largest);
});
```

## 6. The skeleton's blocks

The form in TypeScript of each frontend block of the skeleton `j-new-project` plans, one set per
application:

| Block | TypeScript |
|---|---|
| F1 | the framework's CLI or Vite, a single-page application, the scaffold brought to the gate as the framework's file says (§1); the pack's files, from `${CLAUDE_PLUGIN_ROOT}/lint-rules/typescript/native/`, copied into the application's folder only now, because a scaffold refuses a folder that already holds them: `tsconfig.json` merged, `eslint.config.js` with the framework's rules and Playwright's after the pack's, Vitest, Playwright. RED: the root component renders the application's name — `language.md`, `angular.md` / `react.md` / `vue.md` §1, `testing.md` |
| F2 | `orval.config.mjs` on `openapi/<Api project>.json` by its relative path (`../openapi/…` from `frontend/`) with the framework's client, `npm run generate` before the gate, the tests and the build, `src/api/` ignored; the development proxy of `/api` to the backend — `client.md` §1 |
| F3 | the base `load` in the framework's form (Angular: the loader and the problem interceptor; React and Vue: the `fetch` form in a query, retries only for transient failures), its types proved with `expectTypeOf` and `@ts-expect-error`; a failure shown from the `ProblemDetails` with its `Code` — `client.md` §2-3, the framework's file §2-5, `branches/frontend.md` 3, 5 |
| F4 | its list on the load with the UI library chosen in LISTEN — the lazy table and its converter (`prime.md`), or the DataGrid with the converter and the store (`devextreme.md`), the fields checked against the columns — and its create, update and delete through the generated client — `branches/frontend.md` |
| F5 | Playwright against the backend and the application, which its `webServer` starts: the list loads from the server, sorted and filtered there, and a refused request shows its problem — `testing.md`, `branches/frontend.md` 10 |
