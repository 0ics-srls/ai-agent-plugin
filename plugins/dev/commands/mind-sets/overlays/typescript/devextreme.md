# TypeScript — DevExtreme UI

How DevExtreme's data components (DataGrid, TreeList, the editors with a list) sit on the load of an
entity (`api.md` 3, `branches/frontend.md` 3). DevExtreme is a licensed dependency (principles 6.4).

---

## 1. The license

- The key of the developer's DevExpress account is read by the package's tool from
  `DevExpress_License` (an environment variable), `DevExpress_LicensePath` (a file), or the
  developer's own file (`~/.config/DevExpress/DevExpress_License.txt`, `%APPDATA%` on Windows) — a file of
  one developer, outside the repository (principles 5.2); a build machine gets it from its secrets, or
  `DevExpress_LicensePath=.00-secrets/DevExpress_License.txt`.
- The tool runs before the build and the development server — `"prebuild": "devextreme-license --out
  src/.devextreme/license-key.ts"` (it adds the file to `.gitignore`) — and the application passes the
  key once, at its start: `config({ licenseKey })` (`devextreme/core/config`). Without it the components
  show the trial notice.

## 2. The request from the component's options

A component sends its `LoadOptions` (`devextreme/common/data`): `sort` and `group` as a field name or
`{ selector, desc }`, `filter` typed `any`. Each selector is checked against the fields the view
declares — only a declared field becomes a `Path` of the entity — and the filter expression part by
part; what does not match is dropped, and a filter with one unknown part is refused whole. The
checks of the filter, beside `fieldOf` (`client.md` §2) in `src/app/shared/load/fields.ts`,
framework-free:

```ts
import type { Condition, Filter, Operator, Path } from "./load.types";

const OPERATORS: readonly Operator[] = ["=", "<>", "<", "<=", ">", ">=", "contains", "notcontains", "startswith", "endswith"];
const operatorOf = (value: unknown): Operator | undefined => OPERATORS.find(operator => operator === value);
const valueOf = (value: unknown): string | number | boolean | null | undefined =>
  typeof value === "string" || typeof value === "number" || typeof value === "boolean" || value === null ? value : undefined;

const conditionOf = <T>(fields: readonly Path<T>[], parts: readonly unknown[]): Condition<T> | undefined => {
  const [name, operator, value] = parts;
  const field = fieldOf(fields, name);
  const op = operatorOf(operator);
  const operand = valueOf(value);
  return field !== undefined && op !== undefined && operand !== undefined ? [field, op, operand] : undefined;
};

/** A filter expression from a component, checked part by part; anything else is refused. */
export const filterOf = <T>(fields: readonly Path<T>[], expression: unknown): Filter<T> | undefined => {
  if (!Array.isArray(expression)) {
    return undefined;
  }
  const parts: readonly unknown[] = expression;
  const [head, ...rest] = parts;
  if (head === undefined) {
    return undefined;
  }
  if (head === "!") {
    const [negated] = rest;
    const inner = filterOf(fields, negated);
    return inner && ["!", inner];
  }
  if (typeof head === "string") {
    return conditionOf(fields, parts);
  }
  const items = parts.map(part => (part === "and" || part === "or" ? part : filterOf(fields, part)));
  return items.every(item => item !== undefined) ? items : undefined;
};
```

The converter (`src/app/shared/load/devextreme.ts`) reads a member of an untyped descriptor with
`Reflect.get` into `unknown`, and narrows it:

```ts
const memberOf = (value: unknown, name: string): unknown => {
  if (typeof value !== "object" || value === null) {
    return undefined;
  }
  const member: unknown = Reflect.get(value, name);
  return member;
};
const selectorOf = <T>(fields: readonly Path<T>[], descriptor: unknown): Path<T> | undefined =>
  fieldOf(fields, typeof descriptor === "string" ? descriptor : memberOf(descriptor, "selector"));
const sortOf = <T>(fields: readonly Path<T>[], descriptor: unknown): SortBy<T> | undefined => {
  const selector = selectorOf(fields, descriptor);
  return selector === undefined ? undefined : { Desc: memberOf(descriptor, "desc") === true, Selector: selector };
};
const groupOf = <T>(fields: readonly Path<T>[], descriptor: unknown): GroupBy<T> | undefined => {
  const sort = sortOf(fields, descriptor);
  const interval = memberOf(descriptor, "groupInterval");
  const groupInterval = typeof interval === "number" ? interval : INTERVALS.find(known => known === interval);
  return sort && { ...sort, ...(groupInterval !== undefined && { GroupInterval: groupInterval }) };
};
const summaryOf = <T>(fields: readonly Path<T>[], descriptor: unknown): SummaryOf<T> | undefined => {
  const selector = selectorOf(fields, descriptor);
  const summaryType = SUMMARY_TYPES.find(known => known === memberOf(descriptor, "summaryType"));
  return selector === undefined || summaryType === undefined ? undefined : { Selector: selector, SummaryType: summaryType };
};

/** The options a DevExtreme component sends, as the load request; a field it does not declare is dropped. */
export const requestOf = <T>(options: LoadOptions<T>, fields: readonly Path<T>[]): LoadRequest<T> => {
  const filter = filterOf(fields, options.filter);
  const group = each(options.group, descriptor => groupOf(fields, descriptor));
  const groupSummary = each(options.groupSummary, descriptor => summaryOf(fields, descriptor));
  const sort = each(options.sort, descriptor => sortOf(fields, descriptor));
  const totalSummary = each(options.totalSummary, descriptor => summaryOf(fields, descriptor));
  return {
    ...(options.skip !== undefined && { Skip: options.skip }),
    ...(options.take !== undefined && { Take: options.take }),
    ...(options.requireTotalCount !== undefined && { RequireTotalCount: options.requireTotalCount }),
    ...(options.requireGroupCount !== undefined && { RequireGroupCount: options.requireGroupCount }),
    ...(filter && { Filter: filter }),
    ...(group.length > NONE && { Group: group }),
    ...(groupSummary.length > NONE && { GroupSummary: groupSummary }),
    ...(sort.length > NONE && { Sort: sort }),
    ...(totalSummary.length > NONE && { TotalSummary: totalSummary }),
  };
};
```

(`each` maps a descriptor or a list of them, dropping what does not read; `SUMMARY_TYPES`,
`INTERVALS` and `NONE = 0` are the constants of the file.)

## 3. The store

A `CustomStore` whose load is the entity's loader (the framework's overlay gives the loader); the
request a component builds may group or not, so the result is typed rows or groups (`client.md` §2):

```ts
export const loadStore = <Result extends { data: readonly unknown[] }>(
  load: Loader<Result>,
  fields: readonly NoInfer<Path<EntityOf<Result>>>[],
  key: NoInfer<Path<EntityOf<Result>>>,
): CustomStore<EntityOf<Result>> =>
  new CustomStore<EntityOf<Result>>({ key, load: async options => lastValueFrom(load(requestOf(options, fields))) });
```

`NoInfer` keeps the entity coming from the loader alone. In Angular `lastValueFrom` turns the loader's
`Observable` into the `Promise` the store expects. With a `fetch` client (React, Vue) the store takes
the generated function itself, and the entity comes from it:

```ts
export const loadStore = <C extends LoadCall>(
  call: C,
  fields: readonly NoInfer<Path<EntityOf<C>>>[],
  key: NoInfer<Path<EntityOf<C>>>,
): CustomStore<EntityOf<C>> => new CustomStore<EntityOf<C>>({ key, load: async options => load(call, requestOf(options, fields)) });
```

## 4. The component

- `remoteOperations: { filtering: true, grouping: true, groupPaging: true, paging: true, sorting: true,
  summary: true }`: every operation runs on the server. `groupPaging` matches the load's groups, which
  carry keys, counts and sums and never rows: the grid asks the rows of an expanded group with a filter
  on its key.
- A column of a closed set is a lookup on the values the contract generated, so its filter offers them
  with `=` (the server refuses `contains` on an enum): `statuses = Object.values(OrderStatus)` →
  `<dxi-data-grid-column dataField="Status"><dxo-data-grid-lookup [dataSource]="statuses" /></dxi-data-grid-column>`.
- Angular: the standalone components of `devextreme-angular/ui/data-grid` and its `nested` entry point
  (`DxDataGridComponent`, `DxiDataGridColumnComponent`, `DxoDataGridLookupComponent`…); the theme
  `node_modules/devextreme/dist/css/dx.light.css` in the application's styles.

  ```ts
  private readonly orders = inject(OrdersService);
  private readonly load = loader(options => this.orders.ordersLoad(options));
  protected readonly store = loadStore(this.load, ["Id", "CustomerId", "Date", "Amount", "Status"] as const, "Id");
  ```

## 5. Proving it

- The converter, unit: paging, sort (by name and by descriptor), groups with an interval, filters with
  `and` and `!`, summaries; an undeclared field dropped; a filter with one unknown part refused.
- End to end: the summary computed by the server is shown; a filter of the filter row changes the rows
  the server sends.
