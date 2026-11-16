# TypeScript — Testing

How `testing-principles.md` is written in a TypeScript frontend.

---

- **Vitest** for every framework: Angular's `unit-test` builder runs it (`ng test`), Vite's projects run it
  directly (`vitest run`, `test.environment: "jsdom"` in `vite.config.ts`). Tests sit beside their code
  (`*.spec.ts` in Angular, `*.test.ts` / `*.test.tsx` in React and Vue).
- **Types are behaviour.** What a type promises is proved with `expectTypeOf(value).toEqualTypeOf<…>()`,
  checked by the compiler in the gate, and a value a type must refuse with `@ts-expect-error` on the
  line of the error, with its reason. A type expectation that does not fail when the type is wrong
  proves nothing: changing the expected type turns the compiler red.
- **Unit — the logic of the frontend**: the converters of the components' state to the load request,
  the reading of a `ProblemDetails`, the loader with a fake of the generated call — a function of the
  generated call's shape that records what it is sent and answers what the test gives it. A fake, not a
  mock of a library.
- **End to end — Playwright**, in a browser, against the real backend and the application's development
  server (`playwright.config.ts`: `forbidOnly`, one Chromium project, the proxy of `/api` to the backend, and a
  `webServer` with two entries, so that `npm run e2e` starts what it needs, in the gate and in the pipeline: the
  backend with its start command, its local database started first where it has one (`docker compose up -d --wait`),
  waited for on its readiness or health URL; the framework's server on a port of its own; both with
  `reuseExistingServer` outside CI):
  - elements are found as the user finds them — by role and accessible name (`getByRole("row")`,
    `getByRole("columnheader", { name: "Amount" })`) — the roles the component gives, which its
    accessibility tree shows (`locator.ariaSnapshot()`) — never by CSS or position; a list is checked
    whole and in order (`toHaveText([...])`);
  - every assertion waits for what the user sees (web-first assertions); no timers;
  - each test has a tag (`{ tag: "@orders" }`), so a part of the suite runs alone (`--grep @orders`);
  - the expected values come from the backend's seed, as named constants;
  - the network is replaced only to produce what the interface cannot provoke — a refused request —
    and then with the API's real shape: `route.fulfill({ status: 400, contentType:
    "application/problem+json", body: JSON.stringify({ Code: "InvalidRequest", detail: "…", status: 400 }) })`.
- The gate lints the end-to-end code with the rules of `eslint-plugin-playwright` that find a test
  that does not test — a call nobody awaits, an assertion that cannot fail, a `.only` left behind:
  the pack's `eslint.e2e.js`, which each framework's `eslint.config.js` adds after its own rules.
