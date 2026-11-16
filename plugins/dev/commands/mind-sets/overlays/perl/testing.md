# Perl — Tests

How `testing-principles.md` is written with `Test2::V0` and `prove`.

---

## 1. The runner

- `prove -l`, always with the library path. **The default run is the fast one** (testing principles 6.2): `prove -lr t/unit`; the full run is `prove -lr t`.
- A run with no test files is an error for `prove`.
- A `subtest` proves one behaviour, its name saying it: `should <behaviour> when <condition>`; several inputs are a loop over a list of cases (testing principles 1.4).
- An exception with `dies { }`, its absence with `lives { }`.
- `alarm` on a test that can hang, so it fails with its name (testing principles 7.3).

## 2. The levels

- `t/unit/`: the logic, on doubles of the contracts, in memory.
- `t/integration/`: the code that talks to the outside on the real thing (testing principles 7.2): a real database; each test owns its data.
- `t/` mirrors `lib/`, one test file for one module; shared code in `t/lib/`. A test file opens with its `#!/usr/bin/env perl`: Perl::Critic reads
  it as a script, not as a module.

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, consuming the role, in `t/lib/`.
- **A call across the boundary that is itself the behaviour** is a `Test2::Mock` of the class, and the test checks the call it records.
- Plain data and pure functions are used as they are.
