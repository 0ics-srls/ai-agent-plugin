# Rust — A service

How `branches/service-layers.md`, `branches/api.md`, `branches/data.md`, `branches/resilience.md`, `branches/operations.md` and
`branches/security.md` are written in a Rust service, on Axum and sqlx. The language is `language.md`.

---

## 1. The layers are crates

- A workspace with one crate per layer, `core`, `db`, `domain`, `api`, and every reference one way
  (service-layers 1): the compiler refuses the wrong one.
- `core` holds the contracts and the errors; `db` implements the contracts; `domain` the rules; `api` the
  transport and `main`.
- `main` is the composition root, with no container: each crate exposes what builds it, each constructor names
  what it needs, `Arc` shares it (principles 3.6).

## 2. The transport

- A handler is an Axum function that extracts, calls the service and answers; the rules stay in `domain`
  (service-layers 3). `State` carries the services.
- The contract is the OpenAPI document produced by `utoipa` from the handlers and types (api 2), the file in the
  repository kept equal to what the server serves by a test.
- One error format, `application/problem+json`, for every failure (api 5): the domain's error implements
  `IntoResponse` once, and only there its codes get their transport terms (api 6). Internal details never leave
  the server.
- Every list runs on the server, with a page size (api 3, data 7), on the protocol of `overlays/csharp/aspnetcore.md` §3: the same load options
  (`Skip`, `Take`, `Filter`, `Sort`, `Select`, `Group`) and the same answer, written once in `api`, the one library being .NET's. So the
  typed load of a TypeScript frontend holds as it is.

## 3. The storage

- `sqlx`, with the checked macros (`query_as!`); a value reaches a query only as a parameter (data 8).
- An operation that changes several things runs in one transaction (data 1).
- A unique or foreign key violation becomes the domain's error once, in `db` (data 2).
- The schema changes through `sqlx migrate`, the files in `migrations/`, applied by an explicit command (data 12).

## 4. Configuration and running

- The configuration is a struct parsed and validated at startup, no default hidden in the code (principles
  5.1); the secrets come from `.00-secrets/` (principles 5.2).
- Logs go to files through `tracing-appender`, the console one more layer of the same subscriber (operations 1).
- A liveness and a readiness route, traces and metrics through `tracing` with OpenTelemetry (operations 3); `with_graceful_shutdown`
  on the server (operations 4).
- Time comes through a contract, so a test controls it (testing principles 4.4).

## 5. Outgoing calls

`reqwest` with its timeout from the configuration (resilience 1); a retry with backoff and jitter only for what is safe to repeat (resilience 2);
tower's layers bound the concurrent calls and cut off a dependency that keeps failing (resilience 3, 4).

## 6. Security

Every route is behind the authentication layer, a public one declared one by one (security 1); a handler receives the caller's identity from an
extractor, already verified (security 2); TLS, and the rate limit as a tower layer (security 3, 4); what the caller may do is checked in the logic, on the record it touches, and a refusal is its error (security 5).
