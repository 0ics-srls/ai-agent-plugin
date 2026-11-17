# TypeScript — Angular

How `branches/frontend.md`, `language.md` and `client.md` are written in an Angular 22 application.

---

## 1. The application and its gate

- `npx @angular/cli@22 new <app> --directory frontend --defaults --ssr=false --style=css --skip-git`, from the
  repository root (`--directory frontend/<app>` when the project has several applications): a single-page
  application, standalone components, zoneless, the `unit-test` builder on Vitest, TypeScript 6.0.
- The scaffold is brought to the gate:
  - `package.json`: `"type": "module"`, and the scripts `generate` (`orval --config
    orval.config.mjs`), `check` (`tsc -p tsconfig.app.json --noEmit && tsc -p tsconfig.spec.json
    --noEmit && tsc -p tsconfig.e2e.json && eslint --max-warnings 0 .`),
    `test` (`ng test`), `e2e` (`playwright test -x`), and `precheck`, `pretest`, `prebuild` running
    `generate` (with DevExtreme, `prebuild` and `prestart` also run its license tool, `devextreme.md` §1);
  - `tsconfig.json`: the pack's compiler options merged into its `compilerOptions`, and in
    `angularCompilerOptions` `"strictTemplates": true` and `"extendedDiagnostics": { "defaultCategory":
    "error" }` — the templates are checked like the code;
  - the scaffold's own code obeys the gate: a start failure
    reported with `reportError` (`bootstrapApplication(App, appConfig).catch((failure: unknown) => {
    reportError(failure); })`).
- `eslint.config.js` — the pack's configuration (`eslint.pack.js`), then Angular's rules and
  Playwright's: the ones listed, each because it finds a defect, and only them:

  ```js
  import angular from "angular-eslint";
  import { defineConfig } from "eslint/config";
  import e2e from "./eslint.e2e.js";
  import pack from "./eslint.pack.js";

  export default defineConfig(
    pack,
    {
      files: ["**/*.ts"],
      plugins: { "@angular-eslint": angular.tsPlugin },
      processor: angular.processInlineTemplates,
      rules: {
        // Ensures that computed() returns a value. Omitting the value is likely a mistake.
        "@angular-eslint/computed-must-return": "error",
        // Ensures that lifecycle methods are used in a correct context.
        "@angular-eslint/contextual-lifecycle": "error",
        // Angular Lifecycle methods should not be async. Angular does not wait for async lifecycle but the code incorrectly suggests it does.
        "@angular-eslint/no-async-lifecycle-method": "error",
        // Ensures that `takeUntilDestroyed()` is called with an explicit `DestroyRef` when used outside of an injection context.
        "@angular-eslint/no-implicit-take-until-destroyed": "error",
        // Warns user about unintentionally doing logic on the signal, rather than the signal's value.
        "@angular-eslint/no-uncalled-signals": "error",
        // Ensures that reactive contexts such as computed(), linkedSignal() and effect() read at least one reactive value (a signal). A reactive context with no reactive dependencies never re-runs, which is almost always a mistake.
        "@angular-eslint/reactive-context-must-read-signal": "error",
      },
    },
    {
      files: ["**/*.html"],
      plugins: { "@angular-eslint/template": angular.templatePlugin },
      languageOptions: { parser: angular.templateParser },
      rules: {
        // Ensures that the two-way data binding syntax is correct.
        "@angular-eslint/template/banana-in-box": "error",
        // Requires `===` and `!==` in place of `==` and `!=`.
        "@angular-eslint/template/eqeqeq": "error",
        // The use of "$any" nullifies the compile-time benefits of Angular's type system.
        "@angular-eslint/template/no-any": "error",
        // Ensures that there are no duplicate input properties or output event listeners.
        "@angular-eslint/template/no-duplicate-attributes": "error",
        // Ensures that async pipe results, as well as values used with the async pipe, are not negated.
        "@angular-eslint/template/no-negated-async": "error",
        // Disallows the non-null assertion operator (!) in templates.
        "@angular-eslint/template/no-non-null-assertion": "error",
      },
    },
    e2e,
  );
  ```

- `tsconfig.e2e.json` (`extends: ./tsconfig.json`, `types: ["node"]`, the `e2e/` folder and
  `playwright.config.ts`) is in the references of `tsconfig.json`, so the end-to-end code is typed and
  linted with the rest.
- The development server proxies the API: `proxy.conf.json` —
  `{ "/api": { "target": "http://127.0.0.1:<backend port>", "secure": false } }` — named in
  `angular.json` (`serve.options.proxyConfig`).
- The build budgets stay errors. With the DevExtreme theme, whose CSS is about 700 kB raw (70 kB
  transferred), the initial budget is `maximumWarning: 1.5MB`, `maximumError: 2MB`.

## 2. Providers

```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(withInterceptors([problemInterceptor])), // fetch is the default backend
    provideRouter(routes),
  ],
};
```

The UI library's provider joins them (PrimeNG's with its license, `prime.md` §1).

Each feature is a lazily loaded route:
`{ path: "orders", loadComponent: async () => import("./orders/orders-table").then(module => module.OrdersTable) }`.

## 3. The generated client

- Orval with `client: "angular"`: one `@Injectable({ providedIn: "root" })` service per tag, on
  `HttpClient`; the default `observe` overloads stay (without them the generated file holds unused
  types the compiler refuses).
- A generated method is **called**, never passed: `options => this.orders.ordersLoad(options)`. Its
  type parameter `TData` defaults to the generated result (`LoadResultOfOrder`); a method passed as a
  value loses that default, and the entity becomes `unknown`.

## 4. The errors — one interceptor

Every failure of a call to the API becomes a `ProblemError` carrying the `ProblemDetails` of the
answer, read member by member (`client.md` 1): one place, for the loads and the CRUD alike.

```ts
export class ProblemError extends Error {
  public readonly status: number;
  public readonly problem: ProblemDetails;
  public constructor(status: number, problem: ProblemDetails) {
    super(`${String(status)} ${problem.Code ?? ""}: ${problem.detail ?? problem.title ?? ""}`);
    this.status = status;
    this.problem = problem;
  }
}

const textOf = (value: unknown): string | undefined => (typeof value === "string" ? value : undefined);
const codeOf = (value: unknown): ApiErrorCode | undefined => Object.values(ApiErrorCode).find(code => code === value);
const errorsOf = (value: unknown): Record<string, string[]> | undefined =>
  typeof value === "object" && value !== null
    ? Object.fromEntries(Object.entries(value).map(([field, messages]: [string, unknown]) =>
        [field, Array.isArray(messages) ? messages.filter(message => typeof message === "string") : []]))
    : undefined;

/** The ProblemDetails in a body, each member taken only when it has its type. */
export const problemOf = (body: unknown, status: number): ProblemDetails => {
  const fields: Record<string, unknown> = typeof body === "object" && body !== null ? { ...body } : {};
  const code = codeOf(fields["Code"]);
  const detail = textOf(fields["detail"]);
  const errors = errorsOf(fields["errors"]);
  const title = textOf(fields["title"]);
  return { status, ...(code && { Code: code }), ...(detail !== undefined && { detail }), ...(errors && { errors }), ...(title !== undefined && { title }) };
};

export const problemInterceptor: HttpInterceptorFn = (request, next) =>
  next(request).pipe(
    catchError((failure: unknown) =>
      throwError(() => (failure instanceof HttpErrorResponse ? new ProblemError(failure.status, problemOf(failure.error, failure.status)) : failure)),
    ),
  );
```

## 5. The load — a loader per entity

The types of `client.md` §2 live in `src/app/shared/load/load.types.ts`; the Angular form returns an
`Observable`. The entity comes from the call, the shape of each result from its request — in two
steps, because a callback whose parameter is not annotated is inferred after the other arguments.

```ts
export type LoadCall<Result> = (options: DataSourceLoadOptionsBase) => Observable<Result>;
export type EntityOf<Result> = Result extends { data: infer D } ? (D extends readonly (infer X)[] ? Exclude<X, LoadGroup> : never) : never;

/** The load of one entity, typed from each request; result names, for the compiler, what the call answers. */
export interface Loader<Result> {
  <const R extends LoadRequest<EntityOf<Result>>>(request: R): Observable<Loaded<LoadData<EntityOf<Result>, R>>>;
  readonly result?: Result;
}

export const loader = <Result extends { data: readonly unknown[] }>(call: LoadCall<Result>): Loader<Result> => {
  function run<const R extends LoadRequest<EntityOf<Result>>>(request: R): Observable<Loaded<LoadData<EntityOf<Result>, R>>>;
  function run(request: LoadRequest<unknown>): Observable<unknown> {
    return call(body(request)); // body: client.md §2
  }
  return run;
};
```

A loader is a field of its own, declared before what uses it — passed inline into another generic
call it loses its entity: `private readonly load = loader(options => this.orders.ordersLoad(options));`.

## 6. Components

- Standalone, `ChangeDetectionStrategy.OnPush`, signals for their state, `inject()` fields first.
- A load bound to the view is an `rxResource`: the request is a signal, the resource reloads when it
  changes. A resource in error throws from `value()`, so it is read through `hasValue()`:

  ```ts
  private readonly orders = inject(OrdersService);
  private readonly load = loader(options => this.orders.ordersLoad(options));
  private readonly request = signal<PageRequest<Order, typeof FIELDS> | undefined>(undefined);
  protected readonly page = rxResource({ params: () => this.request(), stream: ({ params }) => this.load(params) });
  protected readonly rows = computed(() => (this.page.hasValue() ? this.page.value().data : []));
  protected readonly problem = computed(() => {
    const failure = this.page.error();
    return failure instanceof ProblemError ? failure.problem : undefined;
  });
  ```

- The template uses the control flow (`@if`, `@for`) and shows a problem where it belongs
  (`branches/frontend.md` 5).
- A library's row template passes its rows untyped; a template context guard gives them their type —
  Angular's mechanism for typing a template's `let-` variables:

  ```ts
  @Directive({ selector: "ng-template[appRowOf]" })
  export class RowOf<T> {
    public readonly appRowOf = input.required<readonly T[]>();
    public static ngTemplateContextGuard<T>(directive: RowOf<T>, context: unknown): context is { $implicit: T } {
      // Read by the template compiler only: Angular never calls a context guard at run time.
      return directive instanceof RowOf && typeof context === "object";
    }
  }
  ```

  `<ng-template #body let-order [appRowOf]="rows()">` — `order.Nope` is a compile error.

## 7. Tests

- `ng test`: Vitest through the `unit-test` builder, specs beside their code (`*.spec.ts`), types
  proved with `expectTypeOf` (`testing.md`). The builder's `runnerConfig` names a Vitest file with
  `test: { bail: 1 }`: the run stops at its first failure (testing principles 6.3).
- `playwright test -x` in `e2e/`, with `playwright.config.ts` starting the backend and `ng serve` on its own
  port (`testing.md`).
