# TypeScript — the Prime family (PrimeNG, PrimeReact, PrimeVue)

How a lazy table of the Prime family sits on the load of an entity (`api.md` 3,
`branches/frontend.md` 3). The Prime family is a licensed dependency (principles 6.4).

---

## 1. Versions and license

- PrimeNG 22 (Angular 22), PrimeReact 11 with `@primereact/ui` (React 19), PrimeVue 5, and the themes
  of `@primeuix/themes` 3 — under the PrimeUI license, which wants a license key: without it the
  components show a notice.
- The key is a secret of the project (principles 5.2): `.00-secrets/primeui.json`,
  `{ "license": "<key>" }`, read by the build — `import primeui from "../../.00-secrets/primeui.json"
  with { type: "json" };` (the relative path from the file that imports it, `resolveJsonModule` in the
  application's `tsconfig`) — and given once, with the theme:
  - PrimeNG: `providePrimeNG({ license: primeui.license, theme: { preset: Aura } })`;
  - PrimeReact: `<PrimeReactProvider license={primeui.license} theme={{ preset: Aura }}>`
    (`@primereact/core/config`);
  - PrimeVue: `app.use(PrimeVue, { license: primeui.license, theme: { preset: Aura } })`;

  with `import Aura from "@primeuix/themes/aura";`. Like every key a browser needs, it ends up in the
  bundle; in the repository it stays encrypted.

## 2. The request of a lazy table

The table sends its page, sort and filters; the request selects the columns' fields, so the rows are
typed exactly, and every field it names is checked against the columns (`fieldOf`, `client.md`
§2). The state is the table's lazy-load event — PrimeReact's `UseDataTableLazyLoadEvent`, PrimeVue's
`DataTableSortEvent`, PrimeNG's `TableLazyLoadEvent` — with its filters always present:

```ts
import type { Condition, Filter, LoadRequest, Path } from "./load";
import type { UseDataTableLazyLoadEvent } from "@primereact/types/headless/datatable";
import { fieldOf } from "./fields";

const DESCENDING = -1;

/** The state of a lazy table the request is made from. */
export type TableState = Pick<UseDataTableLazyLoadEvent, "first" | "rows" | "sortField" | "sortOrder"> & {
  readonly filters: NonNullable<UseDataTableLazyLoadEvent["filters"]>;
};

/** The request of one page of a lazy table: its columns selected, never grouped. */
export type PageRequest<T, F extends readonly Path<T>[]> = Omit<LoadRequest<T>, "Group" | "GroupSummary" | "Select"> & {
  readonly Select: F;
};

const joined = <T>(conditions: readonly Condition<T>[]): Filter<T> | undefined => {
  const [first, ...rest] = conditions;
  return first && rest.reduce<Filter<T>>((filter, condition) => [filter, "and", condition], first);
};

const textOf = (metadata: unknown): string | undefined => {
  const value: unknown = typeof metadata === "object" && metadata !== null ? Reflect.get(metadata, "value") : undefined;
  return typeof value === "string" && value !== "" ? value : undefined;
};

/** The page, the sort and the text filters of a lazy table, on the fields its columns declare. */
export const requestOf = <T, const F extends readonly Path<T>[]>(state: TableState, fields: F): PageRequest<T, F> => {
  const sortField = fieldOf(fields, state.sortField);
  const conditions = Object.entries(state.filters).flatMap(([name, metadata]): Condition<T>[] => {
    const field = fieldOf(fields, name);
    const text = textOf(metadata);
    return field !== undefined && text !== undefined ? [[field, "contains", text]] : [];
  });
  const filter = joined(conditions);
  return {
    RequireTotalCount: true,
    Select: fields,
    Skip: state.first,
    Take: state.rows,
    ...(sortField !== undefined && { Sort: [{ Desc: state.sortOrder === DESCENDING, Selector: sortField }] }),
    ...(filter && { Filter: filter }),
  };
};
```

The columns are a constant — `const FIELDS = ["Id", "Date", "Amount", "Status", "Customer.Name"] as const;`
— and `requestOf<Order, typeof FIELDS>(state, FIELDS)` types the rows
`{ Id?: number; …; Customer?: { Name?: string } | null }[]`. A text filter is `contains`, on text only:
the server refuses `contains` on an enum.

## 3. The table, by framework

- **PrimeNG** — `TableModule` with `[lazy]="true"`, `(onLazyLoad)` setting the request signal of an
  `rxResource` (`angular.md` §6); `<p-sort-icon field="Amount" />`, `<p-column-filter type="text"
  field="Customer.Name" />`; the row template typed with `[appRowOf]="rows()"`; the problem in a
  `<p-message severity="error">`.
- **PrimeReact 11** — a composition of parts from `@primereact/ui/datatable`. The table is
  controlled: its filters, its page and its sort live in the state, `onFilter` and `onLazyLoad` update
  it, and the paginator is `@primereact/ui/paginator`, bound to the same state. A callback of a part
  gets its parameter's type written, because the styled parts are generic components:

  ```tsx
  <DataTable.Root
    data={rows}
    dataKey="Id"
    filters={state.filters}
    lazy
    loading={orders.isFetching}
    onFilter={(event: UseDataTableFilterEvent) => {
      setState({ ...state, filters: event.filters, first: FIRST_ROW });
    }}
    onLazyLoad={(event: UseDataTableLazyLoadEvent) => {
      setState({
        filters: event.filters ?? state.filters,
        first: event.first,
        rows: event.rows,
        ...(event.sortField !== undefined && { sortField: event.sortField }),
        ...(event.sortOrder !== undefined && { sortOrder: event.sortOrder }),
      });
    }}
    rows={state.rows}
    totalRecords={orders.data?.totalCount ?? NO_ROWS}
  >
    <DataTable.TableContainer>
      <DataTable.Table>
        <DataTable.THead>
          <DataTable.THeadRow>
            <DataTable.THeadCell><DataTable.Sort field="Amount">Amount</DataTable.Sort></DataTable.THeadCell>
            <DataTable.THeadCell>Customer</DataTable.THeadCell>
          </DataTable.THeadRow>
          <DataTable.THeadRow>
            <DataTable.THeadCell />
            <DataTable.THeadCell>
              <DataTable.Filter display="row" field="Customer.Name">
                {(filter: DataTableFilterInstance) => (
                  <InputText
                    aria-label="Customer"
                    onChange={(event: ChangeEvent<HTMLInputElement>) => {
                      filter.onChange(event, event.target.value, FilterMatchMode.Contains);
                    }}
                    onKeyDown={(event: KeyboardEvent<HTMLInputElement>) => {
                      if (event.key === "Enter") {
                        filter.onApply(event);
                      }
                    }}
                    value={typeof filter.value === "string" ? filter.value : ""}
                  />
                )}
              </DataTable.Filter>
            </DataTable.THeadCell>
          </DataTable.THeadRow>
        </DataTable.THead>
        <DataTable.TBody<Row>>
          {({ item }) => (
            <DataTable.Row>
              <DataTable.Cell>{item.Amount}</DataTable.Cell>
              <DataTable.Cell>{item.Customer?.Name}</DataTable.Cell>
            </DataTable.Row>
          )}
        </DataTable.TBody>
      </DataTable.Table>
    </DataTable.TableContainer>
  </DataTable.Root>
  <Paginator.Root
    itemsPerPage={state.rows}
    onPageChange={(event: PaginatorRootChangeEvent) => {
      setState({ ...state, first: (event.value - FIRST_PAGE) * state.rows });
    }}
    page={state.first / state.rows + FIRST_PAGE}
    total={orders.data?.totalCount ?? NO_ROWS}
  >
    <Paginator.Content>
      <Paginator.First /><Paginator.Prev /><Paginator.Pages /><Paginator.Next /><Paginator.Last />
    </Paginator.Content>
  </Paginator.Root>
  ```

  (`type Row = (typeof rows)[number]` — the rows of the query; the paginator counts pages from 1, the
  load from row 0.) The problem is a `<Message.Root severity="error">` with its `Message.Content` and
  `Message.Text`.
- **PrimeVue 5** — `<DataTable lazy v-model:filters filter-display="row">` with `@page`, `@sort`,
  `@filter` updating the state; the filter of a column in its `#filter` slot (`<InputText
  v-model="filterModel.value" aria-label="Customer" @keydown.enter="filterCallback" />`); the problem in
  a `<Message severity="error">`.

## 4. Proving it

- The converter, unit: page, sort, a text filter on a declared field; an undeclared field and an empty
  filter dropped; two filters joined with `and`; the type of `Select`.
- End to end: a page of rows from the server, the largest first when sorted down; the next page from
  the server; a filter through a navigation; a refused request showing the server's problem. The
  roles are the component's own — PrimeReact 11 gives its cells `gridcell` and its sort a button
  ("Sort by Amount").
