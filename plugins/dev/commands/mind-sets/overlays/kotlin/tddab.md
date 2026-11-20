# Kotlin (KMP) — TDDAB

How the blocks of a TDDAB plan (`mind-sets/tddab-planner.md`) are written in a Kotlin Multiplatform
app: the tests by level and the reference code of a block. How a test is written is `testing.md`.

---

## 1. Tests by level

The values of the `## Tests — by level` keys of `j-settings.md` in a Kotlin project (the component is
the app, its Gradle build); a plan copies them into its blocks (`tddab-planner.md`, "The commands, by
level"). They run on a Mac when the app has an iOS target, with an Android emulator or device that
`adb` sees when it has an Android target (`testing.md` §1).

| Key | Kotlin |
|---|---|
| `@test-focused-<component>` | `./gradlew :{module}:jvmTest --tests '{class}.{test}'` — one test, on the JVM |
| `@test-block-<component>` | `./gradlew :{module}:allTests :{module}:connectedAndroidDeviceTest`, once for each module the block touches — every target, the Android device included |
| `@test-fast` | `./gradlew jvmTest` |
| `@test-slow` | `./gradlew check connectedAndroidDeviceTest` — every target, the Android device |
| `@test-e2e` | `./gradlew :desktopApp:e2eTest`, which starts the backend (`testing.md` §7) |
| `@bench` | `none` |
| `@gate-final` | the lint gate, `./gradlew check connectedAndroidDeviceTest`, the iOS app's `xcodebuild` (`app.md` §5), the audit (`language.md` §5) |

The pack's `kmp.quality.gradle.kts` sets `failFast` on the JVM's test tasks: a run stops at its first
failing test (`testing-principles.md` 6.3). The test tasks of the native and JS targets have no such
option and run their tests to the end; Gradle stops at the first task that fails, without
`--continue`, which is never passed.

Before the tests, the component's gate (`language.md` §5): `./gradlew assemble`.

## 2. Each block at its level

The RED of a block runs at the level of what it builds: a service of the domain in `commonTest` on the
doubles of `:test-support` (`testing.md` §3); a ViewModel with orbit-test (§4); the mapping of the
backend's answers on `MockEngine`, the local database on SQLite (§5); a screen with Compose's UI test
(§6); a binding of the composition in the Koin graph test (§4).

## 3. Reference RED — a domain service block

`domain/src/commonTest/kotlin/shop/domain/CustomerServiceTest.kt` (`testing.md` §3): without
`CustomerService` the test does not compile; with a wrong behaviour, the failing test names it.

## 4. Reference GREEN

```kotlin
// api-contract/src/commonMain/kotlin/shop/contract/Customers.kt
package shop.contract

import shop.core.AppResult
import shop.core.model.Customer
import shop.core.model.PageCustomer

/** The customers as the features use them: a page of them, and the block of one. */
public interface CustomerDirectory {
    public suspend fun page(
        skip: Int,
        take: Int,
    ): AppResult<PageCustomer>

    public suspend fun block(id: Int): AppResult<Customer>
}

/** The customers as the backend serves them. */
public interface CustomerRemote {
    public suspend fun page(
        skip: Int,
        take: Int,
    ): AppResult<PageCustomer>

    public suspend fun get(id: Int): AppResult<Customer>

    public suspend fun block(id: Int): AppResult<Customer>
}

/** The record of what the user did, kept for the diagnostics. */
public interface AuditLog {
    public suspend fun record(event: String)
}
```

```kotlin
// domain/src/commonMain/kotlin/shop/domain/CustomerService.kt
package shop.domain

import shop.contract.AuditLog
import shop.contract.CustomerDirectory
import shop.contract.CustomerRemote
import shop.core.AppError
import shop.core.AppResult
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import shop.core.model.PageCustomer

/** The rules of the customers: a page passes through; a customer already blocked is not blocked again. */
internal class CustomerService(
    private val remote: CustomerRemote,
    private val audit: AuditLog,
) : CustomerDirectory {
    override suspend fun page(
        skip: Int,
        take: Int,
    ): AppResult<PageCustomer> = remote.page(skip, take)

    override suspend fun block(id: Int): AppResult<Customer> {
        val current = remote.get(id)
        if (current !is AppResult.Success) {
            return current
        }
        if (current.value.status == CustomerStatus.BLOCKED) {
            return AppResult.Failure(AppError(ErrorCode.CONFLICT, "customer $id is already blocked"))
        }
        val blocked = remote.block(id)
        if (blocked is AppResult.Success) {
            audit.record("customer $id blocked")
        }
        return blocked
    }
}
```

## 5. Rules of a Kotlin block

- Every declaration with its visibility; data in `data class`es of `val`s; a result that can fail is an
  `AppResult` (`language.md` §1, §3).
- A contract is an interface in `:api-contract`; the domain implements it, `internal`, and binds it in
  its Koin module by its constructor (`app.md` §4).
- A feature speaks only to the contracts; its screen is `(State) → UI` (`app.md` §2-3).
- The state of a contract on the fakes of `:test-support`; a call across the boundary on a Mokkery mock
  (`testing.md` §3).
- A new module applies the convention that fits it and declares only its dependencies; a new dependency
  goes to `gradle/libs.versions.toml`, and the locks are written again (`language.md` §5).
- No console write: Kermit (`language.md` §4).

## 6. The skeleton's blocks

A Kotlin Multiplatform app is the frontend of a backend: `/dev:j-new-project` plans its blocks F1-F5, after
the backend's. Their form in Kotlin:

| Block | Kotlin (KMP) |
|---|---|
| F1 | the Gradle build: `settings.gradle.kts`, `gradle/libs.versions.toml`, `gradle.properties` (`language.md` §5), `build-logic/` with the conventions and the pack's `kmp.quality` and `.editorconfig` as /dev:j-setup copied them; `core` (`AppResult`, `AppError`, `ErrorCode`), `api-contract`, `test-support`. RED: the tests of `core` — `AppResult`, the error codes |
| F2 | the generated client: `openapi/<project>.json`, `kmp.openapi`, the models in `core`, `api-client`, `sharedLogic`'s `ShopApi` and the engine of each target (`client.md` §1-2). RED: `ShopApiTest` on `MockEngine` |
| F3 | the domain: the first entity's contracts, its service, the adapter over sharedLogic, the Koin module (`app.md` §4); the fakes in `test-support`. RED: the service's suite (`testing.md` §3) |
| F4 | the first entity's screens: the feature (ViewModel, screen, module), `ui-kit`, `sharedUI` with the `NavDisplay` and the composition root, the four entry points and their settings (`app.md` §2-5). RED: the ViewModel's suite, the screen's UI test, the Koin graph test |
| F5 | end to end: `e2eTest` of `:desktopApp`, the first entity's screen against the real backend (`testing.md` §7) |

With local storage, a block between F3 and F4 adds the database (`client.md` §3), its RED on SQLite.
