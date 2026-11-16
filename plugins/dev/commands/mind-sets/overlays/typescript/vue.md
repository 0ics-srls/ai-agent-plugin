# TypeScript — Vue

How `branches/frontend.md`, `language.md` and `client.md` are written in a Vue 3.5 application on
Vite.

---

## 1. The application and its gate

- `npx create-vite@latest frontend --template vue-ts`, from the repository root (`frontend/<app>` when the
  project has several applications): a single-page application on Vite,
  TypeScript 6.0, `vue-tsc` for the components.
- The scaffold is brought to the gate:
  - the pack's compiler options merged into `tsconfig.app.json` (its `include` stays
    `["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]`) and `tsconfig.node.json`, whose `include` is
    `vite.config.ts`, `playwright.config.ts` and `e2e`;
  - `package.json` scripts: `generate`, `check` (`vue-tsc -b && eslint --max-warnings 0 .`), `test` (`vitest run`), `e2e` (`playwright test`), `start` (`vite`), `build` (`vue-tsc -b
    && vite build`), and `precheck`, `pretest`, `prebuild` running `generate` (with DevExtreme,
    `prebuild` and `prestart` also run its license tool, `devextreme.md` §1);
  - `vite.config.ts` with `@vitejs/plugin-vue`, the proxy of `/api` and `test: { environment: "jsdom" }`
    (as `react.md` §1);
  - `src/vue-modules.d.ts` — a single-file component as a module, for the TypeScript program the linter
    reads (vue-tsc reads the components itself):

    ```ts
    declare module "*.vue" {
      import type { DefineComponent } from "vue";
      const component: DefineComponent;
      export default component;
    }
    ```

- `eslint.config.js` — the pack's configuration covers the scripts of the components (its `files`
  include `*.vue`); Vue's adds the parser and the rules of `eslint-plugin-vue` that find a defect: its
  own "essential" category for Vue 3 — the one the plugin calls error prevention — without its three
  rules of naming and cleaning, plus four it leaves out; then Playwright's:

  ```js
  import { defineConfig } from "eslint/config";
  import e2e from "./eslint.e2e.js";
  import pack from "./eslint.pack.js";
  import tseslint from "typescript-eslint";
  import vue from "eslint-plugin-vue";
  import vueParser from "vue-eslint-parser";

  export default defineConfig(
    pack,
    {
      files: ["**/*.vue"],
      languageOptions: {
        parser: vueParser,
        parserOptions: { extraFileExtensions: [".vue"], parser: tseslint.parser, projectService: true },
      },
    },
    {
      // The plugin's error-prevention rules: a v-for without its key, a prop mutated, a directive that
      // is not valid, a computed property with a side effect.
      extends: [vue.configs["flat/essential"]],
      files: ["**/*.vue"],
      rules: {
        // Not defects: a component's name, a variable or a component never used.
        "vue/multi-word-component-names": "off",
        "vue/no-unused-vars": "off",
        "vue/no-unused-components": "off",
        // A ref read in a way that loses its reactivity.
        "vue/no-ref-object-reactivity-loss": "error",
        // A condition of the template that is always true or always false.
        "vue/no-constant-condition": "error",
        // target="_blank" without rel="noopener noreferrer"; HTML written into the page with v-html.
        "vue/no-template-target-blank": "error",
        "vue/no-v-html": "error",
        // The scripts are TypeScript: the pack's rules need the types.
        "vue/block-lang": ["error", { script: { lang: "ts" } }],
      },
    },
    e2e,
  );
  ```

## 2. The generated client and the server state

- Orval with `client: "vue-query"` and `httpClient: "fetch"`: fetch functions typed by status and
  TanStack Vue Query composables.
- The load is the `fetch` form of `client.md` §2 on the generated function, in a query whose key holds
  the request as a `computed`, so a change of the request is a new query:

  ```ts
  const request = computed(() => requestOf<Order, typeof FIELDS>(state.value, FIELDS));
  const orders = useQuery({
    placeholderData: keepPreviousData,
    queryFn: async () => load(ordersLoad, request.value),
    queryKey: ["Orders_Load", request],
  });
  const problem = computed(() => (orders.error.value instanceof LoadError ? orders.error.value.problem : undefined));
  ```

- One `QueryClient`, installed with `VueQueryPlugin`, with the same rule of retries as `react.md` §2:
  only a transient failure is tried again.

## 3. Components and routes

- Single-file components with `<script setup lang="ts">`, the server state from the query, the state of
  the interface in `ref`s; a component a template uses is imported in its script (`RouterLink`,
  `RouterView` included).
- `vue-router`: one route per feature page, its component loaded lazily —
  `const OrdersTable: Component = defineAsyncComponent(async () => import("./orders/OrdersTable.vue"));`.
- `main.ts`: `createApp(App).use(router).use(VueQueryPlugin, { queryClient }).use(<UI library>)` (PrimeVue
  with its license, `prime.md` §1).

## 4. DevExtreme

`devextreme-vue/data-grid` (`DxDataGrid`, `DxColumn`, `DxLookup`, `DxPaging`, `DxFilterRow`,
`DxSummary`, `DxTotalItem`), the store built once in the script on the generated function
(`devextreme.md` §3), every true option bound (`<DxFilterRow :visible="true" />`), the theme imported in
`main.ts`.

## 5. Tests

- `vitest run`: tests beside their code (`*.test.ts`) in jsdom, types proved with `expectTypeOf`
  (`testing.md`).
- `playwright test` in `e2e/`, with `playwright.config.ts` starting the backend and
  `vite --port <port> --strictPort` (`testing.md`).
