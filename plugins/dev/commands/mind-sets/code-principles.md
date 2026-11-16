# Code Principles

How the code is written and designed, in any language. The language overlay says how each one is
written in that language.

---

## 1. Design: KISS, DRY, SOLID

1.1 **KISS.** The simplest solution that works; clarity over cleverness. If it cannot be explained in
one sentence, it is too complex. Simple is not the same as specific: a generic base with one clear
contract is simpler than the same code copied per entity.

1.2 **DRY.** The same rule in several places, which must change together, is written once. Two things
that look alike but change for different reasons are not the same rule.

1.3 **The base is written generically**, as `principles.md` 3.2 states it: over the contracts of the
base, with the entity as a type parameter.

1.4 **Single responsibility.** A type — and the file that holds it — has one reason to change, judged
by WHO asks for the changes, whatever its length. It does not mean splitting everything into
micro-classes that change together anyway.

1.5 **Open/closed.** A new case is new code behind the contract; the code using the contract is not
edited.

1.6 **Liskov substitution.** A subtype keeps what the base promises: no stronger preconditions, no
weaker postconditions, no undeclared exceptions. No override refuses the base (an empty or throw-only
body), and no caller type-tests what it receives.

1.7 **Interface segregation.** Interfaces are small and shaped by their clients; nobody implements
no-op methods.

1.8 **Dependency inversion.** The code that decides depends on contracts shaped by what it needs, and
the details — storage, network, external services, the clock — sit behind them. Injection is the
usual mechanism, not the principle.

## 2. The mechanism that governs behaviour

For each behaviour with more than one case, a mechanism is chosen at design time. The question: when
the next case arrives, is it one new thing to write, or five existing places to find and edit? What
every feature repeats is the base's job, not a mechanism of its own.

2.1 **State machine**, when what is legal depends on the state (an order, a subscription, a document
under review). The states, the events and the transitions are named; the state is one value of a
closed type and changes only through the transition. Scattered boolean flags are a state machine
nobody wrote down. The machine lives where its state lives: the state of an entity, in the entity,
which keeps it private and exposes the state read-only. A library that provides the machine is used
as its own instructions say (principles 1.1).

2.2 **Strategy behind one contract**, when the same operation behaves differently by kind (payment
providers, export formats). One contract, one implementation per kind, the selection in one place.

2.3 **Named pipeline**, when the work is a sequence of transformations. Each step has a name, one
input and one output; the run stops at the first error and says which step failed.

2.4 **Invariants enforced at construction**, when a value has a rule of its own that must hold for its
whole life and that several places rely on (a date range whose end follows its start, an amount with
its currency). A field that is merely required or length-limited is not such a value: that is input
validation, done at the boundary.

2.5 **Rules as data**, when what changes often is the rules themselves (thresholds, mappings,
permissions). The rules live in a table and the code reads it, instead of branching.

## 3. Data and types

3.1 **Values are immutable; entities are data.** Requests, responses, messages and values keep the
content they were built with. An entity is data with an identity: the base reads and writes its
fields, and the rules that govern its changes live in the domain services — except its state
machine, which lives with the state (2.1). Shared state is immutable.

3.2 **Data travels as it is.** An entity crosses the layers as itself; a shape of its own exists for
composite data — several entities together, a computed summary.

3.3 **What the compiler can check is typed.** A closed set (status, kind, role, error code) is an
enumeration or a closed type. Data crossing a boundary becomes a typed object. Whether a value can be
absent is part of its type, and the type is not silenced: no assertion that a value is there (C#'s
`!` and `null!`, Kotlin's `!!` and `lateinit`, TypeScript's and Swift's and Dart's `!`, Rust's
`unwrap`, Python's `cast`) and no switch that turns the checks off (`#nullable disable`, a warning
disabled). The value is given at construction, its absence is handled, or the program fails where the
absence is known, with its reason (`?? throw`, `?: error(…)`) — not far away, at a use. The tests may
assert what their own setup guarantees; the language's overlay names its rules and its exceptions.

3.4 **Errors have typed codes, not opaque strings**, and carry the context a caller needs to react:
the code, the field or resource involved, what was expected.

3.5 **Serialization is as is, everywhere.** Wherever data is serialized — JSON, messages, files, the
storage — property names leave and arrive exactly as declared in the code, and enumerations as their
declared names. No naming policy and no conversion transform them.

3.6 **Every value has one home.** Configurable values live in configuration; fixed values are
enumerations or single named constants, and every place that needs the value reads that constant.

3.7 **Data in a serialized form is read into types and written from them.** Whatever crosses a
boundary serialized — a file or a message (JSON, XML, YAML, TOML, CSV, INI…), the configuration, a
request's body, query, form and headers, a database row — is read into the program's types by a
mapper (the language's serializer, the framework's binder, the ORM) at the boundary, and written
from them; in between, the code works on the types. Walking the generic tree of a format by key, path
or index, building one by hand, casting what was read to a type: forbidden. A key mistyped, a field
renamed or missing, a value of another type passes the compiler there and fails at run time — or
worse, yields a default in silence. A required field that is missing fails the reading, not a use far
away. Where the language has no such mapper, the parsed tree stays inside the one reader that maps it
to types, and nothing else sees it. Data the program only stores or forwards untouched, without
reading into it, stays an opaque value (a string, bytes). The one exception is a measured need of
performance, only when the user asks for it: then the hand reading stays in one reader, said in its
comment. The language's overlay names its mappers and the forms of this practice.

## 4. Writing

4.1 **Names say what they hold.** Descriptive names (`getUserById`, `invoiceTotal`); booleans start
with `is`, `has`, `should` or `can`; public APIs use full words.

4.2 **A function does one thing**: if its name needs an "and", that "and" is where it splits.

4.3 **The main path reads top to bottom.** Exceptional cases leave early, so the normal case is not
buried inside branches.

4.4 **Private by default.** Only what must be public is public: every public element is a commitment
to its consumers. Nobody reads another object's internals.

4.5 **The public members of a contract stop at the door a programming error the types cannot
exclude** — an empty name, a count below zero. What the type already guarantees is not checked again:
a parameter that cannot be absent (3.3) is not tested for absence. Validation of incoming data is the
boundary's job, done once.

4.6 **Async stays async all the way up.** A function that calls an asynchronous operation is itself
asynchronous and awaits it; cancellation is passed through every call; every asynchronous operation
is awaited exactly once; work in the background gets its own copies of the data and its own
resources.

4.7 **Every wait is a wait for an event.** Code learns that something happened from the signal of
whoever made it happen — a completed task, a message, a channel, a notification — and waits on that
signal with a deadline. The code is awaitable from end to end: a sleep in the middle of the code, or a
loop that checks and sleeps, has no place in it. Time itself is waited for only where time is the
requirement: a backoff, a schedule.

4.8 **Polling is for a third party that offers no signal.** When an external system has no event, no
callback and no notification for what is needed, one component polls it, with its interval and its
deadline in configuration, and turns the result into a signal the rest of the code awaits.

4.9 **Logging is structured, and the console is one of its sinks.** Every log entry is a constant
message template with named values (`"Customer {CustomerId} created"`), written by the author of the
code through the logger abstraction; it carries identifiers, and secrets and personal data stay out of
it. Output meant for a person watching the console reaches it through the logger's console sink: a
direct write to the console (`print`, `console.log`, `Console.WriteLine`) is a defect — it skips
levels, structure and every other sink.

4.10 **Code that nothing uses is deleted**: the version history keeps it.
