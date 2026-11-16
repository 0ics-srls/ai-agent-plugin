# TypeScript — React

How `branches/frontend.md`, `language.md` and `client.md` are written in a React 19 application on
Vite.

---

## 1. The application and its gate

- `npx create-vite@latest frontend --template react-ts`, from the repository root (`frontend/<app>` when the
  project has several applications): a single-page application on Vite.
- The scaffold is brought to the gate:
  - TypeScript `6.0.3` in place of the template's 7 (typescript-eslint accepts `<6.1`), and ESLint
    with the pack in place of the template's oxlint (its package and its `lint` script removed);
  - the pack's compiler options merged into `tsconfig.app.json` (with `"lib": ["ES2023", "DOM",
    "DOM.Iterable"]`) and `tsconfig.node.json`, whose `include` is `vite.config.ts`,
    `playwright.config.ts` and `e2e`;
  - `package.json` scripts: `generate` (`orval --config orval.config.mjs`), `check` (`tsc -b && eslint
    --max-warnings 0 .`), `test` (`vitest run`), `e2e` (`playwright test`),
    `start` (`vite`), `build` (`tsc -b && vite build`), and `precheck`, `pretest`, `prebuild` running
    `generate` (with DevExtreme, `prebuild` and `prestart` also run its license tool, `devextreme.md` §1);
  - `vite.config.ts` — the proxy of the API and the test environment:

    ```ts
    import { defineConfig } from "vitest/config";
    import react from "@vitejs/plugin-react";

    export default defineConfig({
      plugins: [react()],
      server: { proxy: { "/api": { target: "http://127.0.0.1:<backend port>" } } },
      test: { environment: "jsdom", include: ["src/**/*.test.{ts,tsx}"] },
    });
    ```

- `eslint.config.js` — the pack's configuration, then React's rules and Playwright's: the ones listed,
  each because it finds a defect — a list without keys, a hook called in a condition, a listener nobody
  removes, state changed while rendering — and only them. ESLint 10 is outside the range of
  `eslint-plugin-react`; its maintained successor is `@eslint-react/eslint-plugin` (MIT):

  ```js
  import { defineConfig } from "eslint/config";
  import e2e from "./eslint.e2e.js";
  import hooks from "eslint-plugin-react-hooks";
  import pack from "./eslint.pack.js";
  import react from "@eslint-react/eslint-plugin";

  export default defineConfig(
    pack,
    {
      files: ["src/**/*.{ts,tsx}"],
      // The plugins, with no rule of theirs turned on.
      plugins: { ...react.configs.all.plugins, "react-hooks": hooks },
      rules: {
        // Disallows missing 'key' on items in list rendering.
        "@eslint-react/no-missing-key": "error",
        // Prevents duplicate 'key' props on sibling elements when rendering lists.
        "@eslint-react/no-duplicate-key": "error",
        // Disallows direct mutation of 'this.state'.
        "@eslint-react/no-direct-mutation-state": "error",
        // Disallows accessing 'this.state' inside 'setState' calls.
        "@eslint-react/no-access-state-in-setstate": "error",
        // Disallows declaring lazy components that wrap dynamic imports inside other components or hooks.
        "@eslint-react/no-nested-lazy-component-declarations": "error",
        // Prevents comment strings from being accidentally inserted into a JSX element's text nodes.
        "@eslint-react/jsx-no-comment-textnodes": "error",
        // Catches `$` before `{expr}` in JSX — typically from template literal `${expr}` being copy-pasted into JSX without removing the `$`. The `$` "leaks" into the rendered output.
        "@eslint-react/jsx-no-leaked-dollar": "error",
        // Catches `;` at the start of JSX text nodes — typically from accidentally placing a statement-ending `;` inside JSX. The `;` "leaks" into the rendered output.
        "@eslint-react/jsx-no-leaked-semicolon": "error",
        // Disallows passing 'children' as a prop when children are also passed as nested content.
        "@eslint-react/jsx-no-children-prop-with-children": "error",
        // Disallows DOM elements from using 'dangerouslySetInnerHTML'.
        "@eslint-react/dom-no-dangerously-set-innerhtml": "error",
        // Disallows DOM elements from using 'dangerouslySetInnerHTML' and 'children' at the same time.
        "@eslint-react/dom-no-dangerously-set-innerhtml-with-children": "error",
        // Disallows 'javascript:' URLs as attribute values.
        "@eslint-react/dom-no-script-url": "error",
        // Disallows 'target="_blank"' without 'rel="noreferrer"'.
        "@eslint-react/dom-no-unsafe-target-blank": "error",
        // Enforces that the 'sandbox' attribute for 'iframe' elements is not set to unsafe combinations.
        "@eslint-react/dom-no-unsafe-iframe-sandbox": "error",
        // Disallows 'children' in void DOM elements.
        "@eslint-react/dom-no-void-elements-with-children": "error",
        // Disallows unknown 'DOM' properties.
        "@eslint-react/dom-no-unknown-property": "error",
        // Disallows the use of string style prop in JSX. Use an object instead.
        "@eslint-react/dom-no-string-style-prop": "error",
        // Enforces that every 'addEventListener' in a component or custom hook has a corresponding 'removeEventListener'.
        "@eslint-react/web-api-no-leaked-event-listener": "error",
        // Enforces that every 'setInterval' in a component or custom hook has a corresponding 'clearInterval'.
        "@eslint-react/web-api-no-leaked-interval": "error",
        // Enforces that every 'setTimeout' in a component or custom hook has a corresponding 'clearTimeout'.
        "@eslint-react/web-api-no-leaked-timeout": "error",
        // Enforces that every 'ResizeObserver' created in a component or custom hook has a corresponding 'ResizeObserver.disconnect()'.
        "@eslint-react/web-api-no-leaked-resize-observer": "error",
        // Enforces that every 'IntersectionObserver' created in a component or custom hook has a corresponding 'IntersectionObserver.disconnect()'.
        "@eslint-react/web-api-no-leaked-intersection-observer": "error",
        // Enforces that every 'fetch' in a component or custom hook has a corresponding 'AbortController' abort in the cleanup function.
        "@eslint-react/web-api-no-leaked-fetch": "error",
        // Enforces the Rules of Hooks.
        "react-hooks/rules-of-hooks": "error",
        // Verifies the list of dependencies for Hooks like useEffect and similar.
        "react-hooks/exhaustive-deps": "error",
        // Validates that [components/hooks are pure](https://react.dev/reference/rules/components-and-hooks-must-be-pure) by checking that they do not call known-impure functions.
        "react-hooks/purity": "error",
        // Validates against mutating props, state, and other values that [are immutable](https://react.dev/reference/rules/components-and-hooks-must-be-pure#props-and-state-are-immutable).
        "react-hooks/immutability": "error",
        // Validates correct usage of refs, not reading/writing during render.
        "react-hooks/refs": "error",
        // Validates against assignment/mutation of globals during render, part of ensuring that [side effects must render outside of render](https://react.dev/reference/rules/components-and-hooks-must-be-pure#side-effects-must-run-outside-of-render).
        "react-hooks/globals": "error",
        // Validates against setting state during render, which can trigger additional renders and potential infinite render loops.
        "react-hooks/set-state-in-render": "error",
        // Validates that components are static, not recreated every render. Components that are recreated dynamically can reset state and trigger excessive re-rendering.
        "react-hooks/static-components": "error",
        // Validates usage of the useMemo() hook against common mistakes.
        "react-hooks/use-memo": "error",
        // Validates that useMemos always return a value and that the result of the useMemo is used by the component/hook.
        "react-hooks/void-use-memo": "error",
        // Validates usage of error boundaries instead of try/catch for errors in child components.
        "react-hooks/error-boundaries": "error",
      },
    },
    e2e,
  );
  ```

## 2. The generated client and the server state

- Orval with `client: "react-query"` and `httpClient: "fetch"`: every operation is a fetch function
  typed by status (`ordersGetById(id): Promise<{ status: 200; data: Order } | { status: 404; data:
  ProblemDetails } …>`) and a TanStack Query hook (`useOrdersGetById`).
- The load is the `fetch` form of `client.md` §2, called on the generated function —
  `load(ordersLoad, request)` — inside a query keyed by the operation and the request:

  ```ts
  const orders = useQuery({
    placeholderData: keepPreviousData,
    queryFn: async () => load(ordersLoad, request),
    queryKey: ["Orders_Load", request],
  });
  const problem = orders.error instanceof LoadError ? orders.error.problem : undefined;
  ```

- One `QueryClient` for the application. A request the server refused is refused again, so only a
  transient failure is tried again (`branches/resilience.md`):

  ```ts
  const ATTEMPTS = 3;
  const SERVER_FAILURE = 500;
  const queries = new QueryClient({
    defaultOptions: {
      queries: {
        retry: (failures, error): boolean => !(error instanceof LoadError && error.status < SERVER_FAILURE) && failures < ATTEMPTS,
      },
    },
  });
  ```

## 3. Components and routes

- Function components with their return type (`(): JSX.Element`), the server state from the query, the
  state of the interface from `useState`.
- `react-router`: one route per feature page, loaded lazily —
  `const OrdersTable = lazy(async () => import("./orders/OrdersTable").then(module => ({ default: module.OrdersTable })));`
  inside `<Suspense>`.
- `main.tsx`: the root element checked (`document.getElementById("root")`, a missing one is an error),
  then `StrictMode`, `QueryClientProvider`, the UI library's provider (`prime.md` §1) and
  `BrowserRouter`.

## 4. DevExtreme

`devextreme-react/data-grid` (`DataGrid`, `Column`, `Lookup`, `Paging`, `FilterRow`, `Summary`,
`TotalItem`), the store built once at module level on the generated function:
`const STORE = loadStore(ordersLoad, FIELDS, "Id");` (`devextreme.md` §3), and the theme imported in
`main.tsx` (`import "devextreme/dist/css/dx.light.css";`).

## 5. Tests

- `vitest run`: tests beside their code (`*.test.ts`, `*.test.tsx`) in jsdom, types proved with
  `expectTypeOf` (`testing.md`).
- `playwright test` in `e2e/`, with `playwright.config.ts` starting the backend and
  `vite --port <port> --strictPort` (`testing.md`).
