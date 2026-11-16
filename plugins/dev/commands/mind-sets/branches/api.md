# Api

For a program that exposes a contract over the network.

---

1. **Requests and responses are as is** (code principles 3.5), in both directions.

2. **The contract is an OpenAPI document**, produced by the server from its own endpoints and types;
   every consumer's contracts and client are generated from it. A client holds no request or response
   type written by hand. The document is a file versioned with the code and kept equal, by a test, to
   what the server produces. Every operation has a name, and every type is exact — a number is a
   number, a list says what its items are — so the generated client holds no untyped value.

3. **Every list operation runs on the server.** Filter, sort, page, group and summary come from the
   load options the client sends and run against the storage; the client never loads a list to work
   on it. Each entity has one list operation: the request decides what comes back — the rows, only the
   fields it selects, or its groups — and the contract documents the result as that entity's own, so
   the client knows which entity the list holds. The protocol of the load options, and the names its
   own types leave with, are the language overlay's.

4. **The data travels as it is** (code principles 3.2): the same shape is mapped on both ends of the
   transport.

5. **The API has one error format**, the platform's standard where there is one, and every failure
   the API produces uses it — including the ones the framework produces (unknown route, unreadable
   body, unhandled exception). An error names the field, not its content; internal details (stack
   traces, SQL) stay on the server.

6. **The domain's absence and codes get their transport terms in one place**: "not found", "invalid",
   "conflict" each have their status.

7. **A published contract changes by addition.** New fields and new endpoints extend it; a change
   that breaks a consumer is a new version, and the old one stays until its announced end date.
