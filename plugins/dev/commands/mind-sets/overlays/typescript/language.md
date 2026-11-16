# TypeScript — Language

How the principles and the code principles are written in TypeScript 6 for a frontend.

---

## 1. Toolchain

- TypeScript 6.0.x: the range Angular 22 and typescript-eslint 8 accept (`>=6.0 <6.1`). Node 24 LTS
  (the client generator needs 22.18 or later); npm, with `package-lock.json` in the repository and
  `npm ci` wherever the build runs.
- ES modules: `"type": "module"` in `package.json`.
- The frontend lives in `frontend/` at the repository root, one folder per application when there are
  several; the generated client in `src/api/` of each.

## 2. The compiler

- The checks of the compiler that find a defect are on — the pack's `tsconfig.json`, merged into the
  one the framework creates: `strict`, `noUncheckedIndexedAccess`, `noImplicitOverride`,
  `noImplicitReturns`, `noFallthroughCasesInSwitch`, `allowUnreachableCode: false`,
  `noUncheckedSideEffectImports`, `forceConsistentCasingInFileNames`; `isolatedModules` is what the
  bundlers need, and `skipLibCheck` leaves the libraries' declaration files to their authors. The
  options that only ask for another form — unused parameters, `import type`, no enum — are not there.

## 3. Types

- A type the API defines is the generated one (frontend branch 1); the hand-written code adds the
  types of its own logic.
- `unknown` is the type of what is not known yet, narrowed by a check — `typeof`, `in`, a
  discriminant — before it is used.
- Serialized data is read into types and written from them (code principles 3.7). `JSON.parse` gives
  `any`, and `JSON.parse(s) as T` is a cast that lies: the compiler believes the type, the data need not
  hold it. What the API describes arrives as the generated client's types; what it does not — a file,
  a message, the browser's storage, a URL's query — goes through one reader that checks it into a
  declared type. Not `obj["x"]`, `any`, or a `Record<string, unknown>` passed on: a field missing is
  `undefined` there, in silence.
- Types flow from the generated client to the view without assertions: the hand-written code holds
  no `as` (the lint gate refuses it). A result whose type depends on the arguments is declared with an
  overload signature — the implementation returns the wider type, the signature states the narrower
  one. `as const` fixes a literal.
- A closed set is a union of literals; the generated client writes each enum of the API as a `const`
  object with its union type, names as declared.
- `@ts-expect-error` stands on the line of the error it expects, with its reason, in the tests that
  prove a type refuses a wrong value.

## 4. Async and waiting

- `async`/`await` all the way; every promise is awaited, returned or handed to a framework that owns
  it (`no-floating-promises`).
- Cancellation travels as an `AbortSignal` down to the request.
- Code waits for the event it needs — an answer, a signal, an observable; `setTimeout` and
  `setInterval` are for a timer the user sees, not for waiting.

## 5. Errors and logging

- A failure is an `Error` subclass carrying its data typed (the load's `LoadError` carries the status
  and the `ProblemDetails` of the answer); `catch` receives `unknown` and narrows it.
- The console is not written: an error reaches the user through the interface and the framework's
  error handler.

## 6. The gate

- `npm run check`, the gate of the pack: `tsc --noEmit && eslint --max-warnings 0 .` in a project
  without a framework, the framework's compiler in its place otherwise (`vue-tsc -b`, each `tsconfig`
  of Angular — the framework's file §1). The compiler's checks above, and the rules of ESLint and
  typescript-eslint that `eslint.pack.js` lists one by one — each because it finds a defect: a promise
  nobody awaits, a check of the compiler silenced (`!`, `any`, a ts-ignore comment), an error of logic. Style,
  order, naming and counts are not in the gate, and the gate checks no formatting: they find no
  defect, and on code that exists they only make it be rewritten. The generated client is ignored by
  ESLint and checked by the compiler.
- The pack's rules are `eslint.pack.js`, and those of the end-to-end code `eslint.e2e.js`;
  `eslint.config.js` uses the pack's as they are, and a framework replaces it with its own, which starts
  from the pack's, adds its plugins and ends with `eslint.e2e.js` (the framework's file §1).

## 7. What /dev:j-setup and /dev:j-new-project read in a TypeScript project

- **Recognized by**: `package.json`; the framework and the UI library from its `dependencies`, which
  say the frontend branch and the overlay files.
- **The files of this overlay, with the branches** — a frontend on the project's API:

  | File | With |
  |---|---|
  | `language.md` | every TypeScript project |
  | `testing.md` | every TypeScript project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |
  | `client.md` | `branches/frontend.md`: the generated client and the typed load |
  | `angular.md`, `react.md`, `vue.md` | the application's framework |
  | `prime.md` | PrimeNG, PrimeReact or PrimeVue on the load |
  | `devextreme.md` | the DevExtreme UI on the load |
- **What LISTEN asks** (`/dev:j-new-project`), one answer per application: the framework (Angular, React,
  Vue) and the UI library (PrimeNG / PrimeReact / PrimeVue, DevExtreme).
- **The lint gate**: `npm run check`. A component without a `check` script gets
  `"check": "tsc --noEmit && eslint --max-warnings 0 ."`, asking first; a
  framework's own check is the one its file defines (§1). The pack's configuration files go to the
  component's root: on an existing component /dev:j-setup copies them; on a project to create the block F1 does, after the
  scaffold, which refuses a folder that already holds them (`tddab.md` §6).
- **Vendored** (`@vendored-globs`): `node_modules/`, `dist/`; the generated client (`src/api/`) is
  ignored by the linters and checked by the compiler (§6).
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: `npm start` in the component's folder — the framework's `start` script (Vite's
  `vite`, Angular's `ng serve`).
- **Where its errors show** (`/dev:j-debug`): the browser's console and network requests, through
  ChromeDevTools (`/dev:j-browse`); the `ProblemDetails` of a failed call; the development server's output.
