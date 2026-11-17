# Testing Principles

What a test is for, in any language. The tools that implement these principles belong to the
platform.

---

## 1. What a test is

1.1 **A test proves a behaviour.** It fails when that behaviour breaks, and only then. A test that
cannot fail, or fails for reasons unrelated to the behaviour, proves nothing.

1.2 **Every test verifies something.** A test without an assertion is false safety: rewrite it, don't
keep it. Assertions vary with what is proved — a value, an error, a state, a side effect, a stored
row.

1.3 **A test's name states the expected behaviour**, so a red test names what is broken without
opening the file.

1.4 **A test has one action.** Arrange, act, assert, in that order; several inputs of the same
behaviour are cases of one parametrized test, and the test body is straight-line code.

1.5 **A test goes through the public surface** of what it tests.

1.6 **Tests are production code**, held to the same standards.

## 2. Test first

2.1 **RED, then GREEN.** A failing test that defines the behaviour; then the minimum code that passes
it, cleaned up before the gate runs — the clean-up changes no behaviour.

2.2 **Cover the cases that matter**: the normal path, the edge cases, the errors, the boundaries. A
coverage percentage does not say whether they are tested: it counts lines executed, not lines
verified.

## 3. Each level proves something different

A test proves only what it actually runs. Each part of the system is tested at the level where its
behaviour really happens.

3.1 **Unit — the logic.** The business rules and the operations, in isolation, fast. The logic works
through contracts, and the test gives it doubles of those contracts (4.2): what surrounds the logic is
replaced, and only that.

3.2 **Integration — the code that talks to something outside.** Storage, HTTP clients, files,
queues: tested against the real thing, or the same engine started for the test. This is where the
mapping, the queries, the constraints, the transactions and the migrations are proved. **A double of
the storage proves nothing about the storage code**: the code that maps, queries and commits is exactly
what the double replaced.

3.3 **API / end-to-end — the running application, through its real transport.** Routes, status codes,
the error format, serialization, the framework's own failures (unknown route, unreadable body),
against the real storage. A test at this level with a double of the storage proves the transport, not
the system.

3.4 **Each layer has tests at the level that proves it.** Logic → unit. Data access → integration with
the real storage. Transport → API tests. A layer whose behaviour lives only in a level that is never
run is untested, however many tests are green.

## 4. Doubles

4.1 **Replace only what is not the subject of the test**, and only at a boundary: the storage when
testing the logic, an external service, the clock, randomness.

4.2 **The double fits what the test proves.** A fake — an in-memory implementation of the contract
with real behaviour — where the test needs the state the contract keeps (a repository, a store). A
mock — expectations on the calls — where the behaviour IS the call made across the boundary (the
message sent, the notification, the payment requested), and wherever mocks are the language's or
framework's usual practice (the language overlay says so). Every double stands in for something that
is itself tested against the real thing at its own level.

4.3 **Test behaviour, not implementation.** An expectation on a call checks behaviour when the call
crosses a boundary and is what the test is about; calls inside the unit are not asserted. No doubles
of pure functions or of plain data: those are used directly.

4.4 **Time and randomness are injected**, so a test controls them: time-dependent logic is driven by
advancing a fake clock.

4.5 **A test waits for the event it expects.** It awaits the signal that the work is done — the
task, the message, the notification — with a deadline that fails the test when it passes. The test
holds that signal because the code under test exposes it.

## 5. Test data

5.1 **Test objects come from shared builders, factories or fixtures.** A new field changes one place,
not forty tests. An arrangement repeated in several tests goes in one place: DRY applies to tests too.

5.2 **A test states only what it is about.** The builder supplies valid defaults; the test overrides
the one value its behaviour depends on, with the minimum input the behaviour needs; a value with a
meaning is a named constant.

## 6. Organization and running

6.1 **The tests of a behaviour live together**, next to the module they prove, so the set for a module
is visible at once.

6.2 **Fast tests run by default, in seconds**; the tests that need real external systems sit apart,
and the default run leaves them out through the runner's own configuration — a label alone leaves them
in. They run on demand and always before a merge: green means both runs are green.

6.3 **A run stops at the first failure.** One failing test makes the run red, and nothing is learned
by running the rest: the runner is told to stop there — its own option, on every command that runs
tests, at every level — and a chain of commands stops at the first one that fails. A run is never
read as "x failed of y": the first failure is what gets fixed, and then the run starts again. Where a
runner cannot stop there, the language's overlay says how far it goes.

## 7. A suite that stays fast as it grows

7.1 **The tests run in parallel.** Each test owns its data and its resources and depends on no other
test's leftovers or on the order tests run in, so the runner can run them side by side, and the
suite's time grows with the slowest group rather than with the count.

7.2 **An expensive resource is started once and shared**: the database engine, the application host,
a container — once per run or per test project. Each test isolates its data inside it: its own keys,
or a reset between tests.

7.3 **Each test has a time limit.** A test that hangs fails with its name; the run goes on. A flaky
test is a defect fixed in its cause, and the run keeps no retry to hide it.

7.4 **Each behaviour is proved at the lowest level that can prove it.** The bulk of the suite is unit
tests in milliseconds; integration tests cover the code that talks to the outside; a few end-to-end
tests cover the paths that cross the whole system.

7.5 **The run reports its slowest tests**, and a test over its level's budget is a defect fixed in the
code that made it slow — usually a wait on time instead of a wait on the event (4.5).

7.6 **A test depends only on what it sets up**: its own data, an injected clock, a fixed seed for any
randomness, a culture and time zone set by the test when the behaviour depends on them.

