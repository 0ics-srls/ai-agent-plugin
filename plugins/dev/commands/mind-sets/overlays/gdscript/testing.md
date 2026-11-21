# GDScript (Godot 4.7) — Tests

How `testing-principles.md` is written with gdUnit4 on Godot 4.7.

---

- **gdUnit4** (MIT), committed in `addons/gdUnit4/` at a fixed release (6.2.3 measured). A suite
  `extends GdUnitTestSuite`, one per production module, at the mirrored path under `test/unit/` or
  `test/integration/`, ending in `_test.gd`; its functions start with `test_`.
- **Names**: `test_should_<outcome>_when_<condition>`.
- **Assertions are gdUnit4's** (`assert_int`, `assert_bool`, `assert_object`, `assert_str`…), never
  `assert`: a failed `assert` stops a headless debug run, and the run never ends. The assertions are
  fluent — each returns itself — so a suite opens with `@warning_ignore_start("return_value_discarded")`
  and the reason on the line above; an `Error` inside a test is still asserted
  (`assert_int(DirAccess.remove_absolute(PATH)).is_equal(OK)`), not dropped.
- **Arrange, act, assert**, separated by one blank line; the setup every test of a suite shares in
  `before_test()`, the cleanup in `after_test()`.
- **The doubles** (testing principles 4.2): in GDScript a double is a subclass of the contract, in
  `test/doubles/` — the compiler checks it against the contract. gdUnit4's `mock()` and `spy()` return a
  `Variant`, and stubbing or verifying through them fails the check with the `unsafe_*` warnings at
  error (measured): they are not used. A double that records the calls it receives is the form of a
  call across the boundary (a sound played, a save written).
- **Test objects come from `test/test_data.gd`** (`TestData`), shared by every suite; the logger in a
  test is `AppLog.new(AppLog.Level.OFF)`.
- **A signal is tested with its arguments**: the emitting call is started deferred and the suite awaits
  the signal — `health.take_damage.call_deferred(MAXIMUM)` then
  `await await_signal_on(health, "depleted", [])`; it fails on timeout when the signal does not come, or
  comes with other arguments. The engine does not check `emit`'s arguments: this test does.
- **A scene** is loaded in an integration suite with `scene_runner("res://src/world/player.tscn")`;
  its node gets its doubles through `setup`, and the suite calls the node's methods and awaits its
  signals. Headless, the engine does not deliver `InputEvent`s: the reaction to an action is a method
  the test calls, and the binding of the action is checked on the Input Map
  (`assert_bool(InputMap.has_action("jump")).is_true()`).
- **The smoke test** starts the main scene headless and checks its startup line and exit code
  (`tddab.md` §6, block G1).
- **Fast and slow**: `test/unit/` runs in memory, in milliseconds; `test/integration/` loads scenes and
  touches files. `-a` takes a folder or a suite file — the split is the folder.
- **The run**: `bash tools/gate/run_tests.sh -a <folder or suite>` — the pack's wrapper of gdUnit4's
  `runtest.sh`, which it calls with `--godot_binary "$(command -v godot)" --headless
  --ignoreHeadlessMode`. Exit 0 green, 100 a failed test, 105 a suite that does not compile, and 1 in
  the two cases gdUnit4 itself calls green: no test ran — a path that does not exist, or holds no test
  («No test cases found») — and objects still alive as the engine closes (`instances were leaked at
  exit`, `resources still in use at exit`), which Godot reports after gdUnit4 has set its exit code. A
  single test cannot be run alone (`-i` excludes, it does not select): the smallest run is its suite.
- **Tests obey the production rules**: the same warnings, the same gdlint; the one
  exception is the `return_value_discarded` line above.
