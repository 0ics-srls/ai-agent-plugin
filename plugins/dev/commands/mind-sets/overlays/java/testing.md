# Java — Tests

How `testing-principles.md` is written with JUnit, AssertJ and Mockito.

---

## 1. The runner

- JUnit Jupiter through Surefire, with the pack's configuration. **The default run is the fast one** (testing
  principles 6.2): a test that needs something real carries `@Tag("slow")`, and `./mvnw -q test` leaves it out; the full
  run is `./mvnw -q test -DexcludedGroups=`.
- The assertions are AssertJ's `assertThat` and `assertThatThrownBy`: the gate refuses JUnit's.
- Several inputs of one behaviour are one `@ParameterizedTest` (testing principles 1.4).
- A test's name says the behaviour: `should_<behaviour>_When_<condition>`.
- `@Timeout` on a test that can hang, so it fails with its name (testing principles 7.3).
- New tests extend the class of the type under test; a new file is for a type that has none.

## 2. The levels

- Unit: plain JUnit, the logic on doubles of the contracts.
- Integration: `@Tag("slow")`, the code that talks to the outside on the real thing (testing principles 7.2): a real
  database through Testcontainers, the container started once for the run; each test owns its data.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, with the real behaviour, in a `test-support` module.
- **A call across the boundary that is itself the behaviour** is a Mockito mock of the interface, and the test verifies
  the call.
- Plain data and pure functions are used as they are. Test objects come from shared builders (testing principles 5.1).
