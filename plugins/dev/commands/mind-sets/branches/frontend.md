# Frontend

For an application whose user interface talks to an API of the project (`api.md`).

---

1. **The contract is generated.** Every request, every answer and their types come from the client
   generated from the API's OpenAPI document — the file the API's test keeps (`api.md` 2). It is
   regenerated from that file at every build, and nobody edits it: a type the frontend needs from the
   API is the generated one.

2. **The data travels as it is** (code principles 3.5), in both directions; a value is converted only
   where it is shown — a day arrives as its text and the view formats it.

3. **Every list runs on the server** (`api.md` 3). A list is a request to its entity's load: paging,
   filter, sort, grouping and summaries are options of the request, and a component never holds a
   whole table to work on it. The type of what comes back is computed from the request — the rows,
   the fields it selects, or the groups — so a field the entity does not have does not compile.

4. **What comes from the API lives where it was fetched.** The data layer that called the API holds
   it, with its loading state, its error and its refresh; components read it and do not copy it. The
   state of the interface — an open panel, the current selection — lives in the component that owns
   it.

5. **Every failure reaches the user** (principles 4.2). The API answers a failure with its code and
   message; the interface shows it where it belongs — a field's error at the field, the others as a
   message — and an unexpected failure leaves the user a way forward.

6. **The server validates; the form helps** (principles 4.3). The form checks, for the user's
   convenience, the rules the contract already declares — required, lengths, formats — taken from the
   contract, never written a second time.

7. **Organized by feature** (principles 3.5). A feature has its routes, its pages, its components and
   its use of the generated client; a shared component has one responsibility and its own folder; the
   generated client is one folder of its own.

8. **Configuration from outside the code** (principles 5.1): the API's address and the settings of
   each environment come from the configuration the platform reads, and one build serves every
   environment where the platform allows it.

9. **The interface reacts to events** (code principles 4.7, 4.8): an answer, a signal, a stream. A
   timer that polls is for a server that offers no push channel.

10. **Each level of test proves its part** (testing principles §3): the logic of a component or a
    service with doubles of the generated client (testing principles 4.2); the application end to end, in a browser, against the
    real backend, waiting for what the user sees (testing principles 4.5).
