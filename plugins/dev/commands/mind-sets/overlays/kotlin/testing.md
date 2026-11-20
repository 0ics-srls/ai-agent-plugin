# Kotlin (KMP) — Tests

How `testing-principles.md` is written in a Kotlin Multiplatform app: kotlin-test in `commonTest`,
run on every target; the doubles of the contracts in `:test-support`, Mokkery (Apache 2.0) for a call
across the boundary; orbit-test for the ViewModels; Compose's UI test. JUnit 5, MockK and Espresso do not run in
`commonTest`. Measured with kotlin-test 2.4.21, Mokkery 3.6.0, orbit-test 12.0.1, androidx.test 1.7.0,
on a Mac with the Android emulator.

---

## 1. The runner

- A module's tests in `commonTest` run on every target: `./gradlew :<module>:allTests` runs the JVM,
  the Android host, the iOS simulator and Wasm in ChromeHeadless; `./gradlew
  :<module>:connectedAndroidDeviceTest` runs them on the Android device or emulator that `adb` sees —
  `kmp.library` puts the device's tests in `commonTest`'s tree (`withDeviceTestBuilder`). Neither
  `allTests` nor `check` runs the device's tests, and the root's `connectedCheck` runs only the app's
  (measured). `./gradlew :<module>:jvmTest --tests '<class>.<test>'` runs one test; a filter that
  matches nothing fails («No tests found for given includes», measured).
- **The fast run** is the JVM's: `./gradlew jvmTest`. **The whole run** is `./gradlew check
  connectedAndroidDeviceTest`: every target's tests and the device's.
- A test that touches one target's platform — the Koin graph test — lives in that target's source set
  (`jvmTest`). A test that needs a real engine on several targets — the local database on SQLite —
  lives in a group of its own (`sqliteTest`), each target giving the engine (§5).
- **Where they run**: iOS needs Xcode; Android needs `aapt2` and an emulator or a device; Wasm's tests
  need Chromium.

## 2. The levels

- **Unit** — `commonTest` of each module: the services on the doubles of the contracts (§3), the
  ViewModels with orbit-test (§4), every target.
- **The code that talks to the outside** — the client's mapping on Ktor's `MockEngine`, which answers
  as the backend does (§5), every target; the local database on the real SQLite engine of the JVM, iOS
  and the Android device (§5).
- **The screens** — Compose's UI test on `(State) → UI` (§6): on the desktop, iOS, the web and the
  Android device.
- **The composition** — the Koin graph test (§4).
- The test files are named after the class they test (`CustomerServiceTest`); a test's name says the
  behaviour (`blockUnknownCustomerIsNotFound`).

## 3. The doubles (testing principles 4.2)

- **The state a contract keeps** is a fake written once, in `:test-support`, with the behaviour of the
  real one (ids in order, a failure on demand); only test source sets depend on that module.
- **A call across the boundary that is itself the behaviour** — the audit's record — is a Mokkery mock
  of the contract (`mock<AuditLog>`), checked with `verifySuspend`; another argument fails the test
  («Expected any call, but no matching calls for AuditLog(3).record(event = "customer 1 removed")»,
  measured).

```kotlin
// test-support/src/commonMain/kotlin/shop/testsupport/FakeCustomerRemote.kt
package shop.testsupport

import shop.contract.CustomerRemote
import shop.core.AppError
import shop.core.AppResult
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import shop.core.model.PageCustomer

/** The backend in memory, with its behaviour: ids in order, an unknown id is not found, a failure on demand. */
public class FakeCustomerRemote : CustomerRemote {
    private val rows = mutableMapOf<Int, Customer>()

    /** When set, every call answers this error, as an unreachable backend does. */
    public var failure: AppError? = null

    public fun add(customer: Customer): Customer {
        val stored = customer.copy(id = rows.size + 1, status = customer.status ?: CustomerStatus.ACTIVE)
        rows[stored.id!!] = stored
        return stored
    }

    override suspend fun page(
        skip: Int,
        take: Int,
    ): AppResult<PageCustomer> =
        answer {
            val items = rows.values.sortedBy { it.id }
            PageCustomer(items = items.drop(skip).take(take), total = items.size)
        }

    override suspend fun get(id: Int): AppResult<Customer> = rows[id]?.let { found -> answer { found } } ?: notFound(id)

    override suspend fun block(id: Int): AppResult<Customer> {
        val found = rows[id] ?: return notFound(id)
        return answer {
            found.copy(status = CustomerStatus.BLOCKED).also { rows[id] = it }
        }
    }

    private fun notFound(id: Int): AppResult<Nothing> = AppResult.Failure(AppError(ErrorCode.NOT_FOUND, "customer $id"))

    private inline fun <T> answer(value: () -> T): AppResult<T> =
        failure?.let { AppResult.Failure(it) } ?: AppResult.Success(value())
}
```

```kotlin
// domain/src/commonTest/kotlin/shop/domain/CustomerServiceTest.kt
package shop.domain

import dev.mokkery.answering.returns
import dev.mokkery.everySuspend
import dev.mokkery.matcher.any
import dev.mokkery.mock
import dev.mokkery.verify.VerifyMode.Companion.not
import dev.mokkery.verifySuspend
import kotlinx.coroutines.test.runTest
import shop.contract.AuditLog
import shop.core.AppError
import shop.core.AppResult
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import shop.testsupport.FakeCustomerRemote
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

class CustomerServiceTest {
    private val remote = FakeCustomerRemote()
    private val audit =
        mock<AuditLog> {
            everySuspend { record(any()) } returns Unit
        }
    private val service = CustomerService(remote, audit)

    private fun grace(): Customer = Customer(name = "Grace Hopper", email = "grace@example.com")

    @Test
    fun blockActiveCustomerBlocksItAndRecordsTheEvent() =
        runTest {
            val stored = remote.add(grace())

            val blocked = service.block(stored.id!!)

            assertIs<AppResult.Success<Customer>>(blocked)
            assertEquals(CustomerStatus.BLOCKED, blocked.value.status)
            verifySuspend { audit.record("customer ${stored.id} blocked") }
        }

    @Test
    fun blockCustomerAlreadyBlockedIsConflictAndRecordsNothing() =
        runTest {
            val stored = remote.add(grace().copy(status = CustomerStatus.BLOCKED))

            val blocked = service.block(stored.id!!)

            assertIs<AppResult.Failure>(blocked)
            assertEquals(ErrorCode.CONFLICT, blocked.error.code)
            verifySuspend(not) { audit.record(any()) }
        }

    @Test
    fun blockUnknownCustomerIsNotFound() =
        runTest {
            val blocked = service.block(UNKNOWN_ID)

            assertIs<AppResult.Failure>(blocked)
            assertEquals(ErrorCode.NOT_FOUND, blocked.error.code)
        }

    @Test
    fun pageWhenTheBackendIsUnreachableReportsIt() =
        runTest {
            remote.failure = AppError(ErrorCode.UNAVAILABLE, "no network")

            val page = service.page(skip = 0, take = PAGE_SIZE)

            assertIs<AppResult.Failure>(page)
            assertEquals(ErrorCode.UNAVAILABLE, page.error.code)
        }

    private companion object {
        const val UNKNOWN_ID = 404
        const val PAGE_SIZE = 20
    }
}
```

## 4. The ViewModels and the composition

orbit-test runs the container in the test's scope: `runOnCreate()` starts what the container does when
it is created, `expectInternalState` takes each state in order, `expectSideEffect` the side effects.
The Koin graph test builds the app's modules into one and verifies that every constructor's parameter
has a definition (`app.md` §4).

```kotlin
// feature/customers/src/commonTest/kotlin/shop/feature/customers/application/CustomersViewModelTest.kt
package shop.feature.customers.application

import kotlinx.coroutines.test.runTest
import org.orbitmvi.orbit.test.testWithInternalState
import shop.core.AppError
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import shop.testsupport.FakeCustomerDirectory
import kotlin.test.Test

class CustomersViewModelTest {
    private val grace = Customer(id = 1, name = "Grace", email = "grace@example.com", status = CustomerStatus.ACTIVE)

    @Test
    fun createdLoadsTheFirstPage() =
        runTest {
            val viewModel = CustomersViewModel(FakeCustomerDirectory(listOf(grace)))

            viewModel.testWithInternalState(this) {
                runOnCreate()
                expectInternalState { copy(loading = true) }
                expectInternalState { copy(customers = listOf(grace), total = 1, loading = false) }
            }
        }

    @Test
    fun blockReplacesTheCustomerWithItsBlockedState() =
        runTest {
            val viewModel = CustomersViewModel(FakeCustomerDirectory(listOf(grace)))

            viewModel.testWithInternalState(this, initialState = CustomersState(customers = listOf(grace), total = 1)) {
                containerHost.onIntent(CustomersIntent.Block(1))
                expectInternalState { copy(customers = listOf(grace.copy(status = CustomerStatus.BLOCKED))) }
            }
        }

    @Test
    fun loadWhenTheBackendIsUnreachableShowsTheError() =
        runTest {
            val unreachable = AppError(ErrorCode.UNAVAILABLE, "no network")
            val viewModel = CustomersViewModel(FakeCustomerDirectory().apply { failure = unreachable })

            viewModel.testWithInternalState(this) {
                runOnCreate()
                expectInternalState { copy(loading = true) }
                expectInternalState { copy(loading = false, error = unreachable) }
            }
        }

    @Test
    fun openSendsTheShellToTheCustomer() =
        runTest {
            val viewModel = CustomersViewModel(FakeCustomerDirectory(listOf(grace)))

            viewModel.testWithInternalState(this, initialState = CustomersState()) {
                containerHost.onIntent(CustomersIntent.Open(1))
                expectSideEffect(CustomersEffect.OpenCustomer(1))
            }
        }
}
```

```kotlin
// sharedUI/src/jvmTest/kotlin/shop/sharedui/KoinGraphTest.kt
package shop.sharedui

import org.koin.core.annotation.KoinExperimentalAPI
import org.koin.dsl.module
import org.koin.test.verify.verify
import shop.sharedui.di.appModules
import kotlin.test.Test

class KoinGraphTest {
    @OptIn(KoinExperimentalAPI::class)
    @Test
    fun everyDefinitionOfTheAppResolves() {
        module { includes(appModules(AppSettings("http://shop.test"))) }.verify()
    }
}
```

## 5. The client and the local database

```kotlin
// sharedLogic/src/commonTest/kotlin/shop/sharedlogic/data/ShopApiTest.kt
package shop.sharedlogic.data

import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.client.engine.mock.respondError
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import kotlinx.coroutines.test.runTest
import kotlinx.io.IOException
import shop.core.AppResult
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs

class ShopApiTest {
    private fun api(engine: MockEngine) = ShopApi(BASE_URL, engine)

    @Test
    fun blockAnswerIsTheCustomerWithItsStatusAsDeclared() =
        runTest {
            val engine =
                MockEngine { request ->
                    assertEquals("$BASE_URL/customers/1/block", request.url.toString())
                    respond(BLOCKED_CUSTOMER, HttpStatusCode.OK, headersOf(HttpHeaders.ContentType, "application/json"))
                }

            val blocked = api(engine).block(1)

            assertIs<AppResult.Success<Customer>>(blocked)
            assertEquals(CustomerStatus.BLOCKED, blocked.value.status)
        }

    @Test
    fun conflictProblemBecomesTheDomainCodeWithItsDetail() =
        runTest {
            val engine =
                MockEngine {
                    respond(
                        CONFLICT_PROBLEM,
                        HttpStatusCode.Conflict,
                        headersOf(HttpHeaders.ContentType, "application/problem+json"),
                    )
                }

            val blocked = api(engine).block(1)

            assertIs<AppResult.Failure>(blocked)
            assertEquals(ErrorCode.CONFLICT, blocked.error.code)
            assertEquals("customer 1 is blocked", blocked.error.detail)
        }

    @Test
    fun unreachableBackendIsUnavailable() =
        runTest {
            val engine = MockEngine { throw IOException("connection refused") }

            val page = api(engine).page(skip = 0, take = PAGE_SIZE)

            assertIs<AppResult.Failure>(page)
            assertEquals(ErrorCode.UNAVAILABLE, page.error.code)
        }

    @Test
    fun answerThatIsNotAProblemIsUnavailable() =
        runTest {
            val engine = MockEngine { respondError(HttpStatusCode.BadGateway, "<html>bad gateway</html>") }

            val customer = api(engine).get(1)

            assertIs<AppResult.Failure>(customer)
            assertEquals(ErrorCode.UNAVAILABLE, customer.error.code)
        }

    private companion object {
        const val BASE_URL = "http://shop.test"
        const val PAGE_SIZE = 20
        const val BLOCKED_CUSTOMER = """{"id":1,"name":"Grace","email":"grace@example.com","status":"BLOCKED"}"""
        const val CONFLICT_PROBLEM =
            """{"type":"about:blank","title":"Conflict","status":409,"detail":"customer 1 is blocked","code":"CONFLICT","field":null}"""
    }
}
```

The cache's test runs where SQLite is real: `sharedLogic` groups the JVM and iOS in `sqliteTest` and the
device's tests depend on it (`client.md` §3); each target gives its database in memory.

```kotlin
// sharedLogic/src/sqliteTest/kotlin/shop/sharedlogic/db/CustomerCacheTest.kt
package shop.sharedlogic.db

import app.cash.sqldelight.db.QueryResult
import kotlinx.coroutines.test.runTest
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import kotlin.test.Test
import kotlin.test.assertEquals

class CustomerCacheTest {
    private val driver = inMemoryDriver()
    private val cache = CustomerCache(driver)

    private val grace = Customer(id = 1, name = "Grace", email = "grace@example.com", status = CustomerStatus.BLOCKED)

    @Test
    fun savedCustomersComeBackAsTheyWere() =
        runTest {
            cache.save(listOf(grace))

            assertEquals(listOf(grace), cache.all())
        }

    @Test
    fun savingAgainReplacesTheCustomer() =
        runTest {
            cache.save(listOf(grace))

            cache.save(listOf(grace.copy(status = CustomerStatus.ACTIVE)))

            assertEquals(listOf(grace.copy(status = CustomerStatus.ACTIVE)), cache.all())
        }

    @Test
    fun theStatusIsStoredAsItsDeclaredName() =
        runTest {
            cache.save(listOf(grace))

            val stored =
                driver
                    .executeQuery(null, "SELECT status FROM customer", { cursor ->
                        cursor.next()
                        QueryResult.Value(cursor.getString(0))
                    }, 0)
                    .value

            assertEquals("BLOCKED", stored)
        }
}
```

```kotlin
// sharedLogic/src/sqliteTest/kotlin/shop/sharedlogic/db/InMemoryDriver.kt
package shop.sharedlogic.db

import app.cash.sqldelight.db.SqlDriver

// A database in memory with the schema created, on the target's own SQLite driver.
internal expect fun inMemoryDriver(): SqlDriver
```

```kotlin
// sharedLogic/src/jvmTest/kotlin/shop/sharedlogic/db/InMemoryDriver.jvm.kt
package shop.sharedlogic.db

import app.cash.sqldelight.async.coroutines.synchronous
import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver

internal actual fun inMemoryDriver(): SqlDriver =
    JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also { ShopDatabase.Schema.synchronous().create(it) }
```

```kotlin
// sharedLogic/src/iosTest/kotlin/shop/sharedlogic/db/InMemoryDriver.ios.kt
package shop.sharedlogic.db

import app.cash.sqldelight.async.coroutines.synchronous
import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.native.inMemoryDriver as nativeInMemoryDriver

internal actual fun inMemoryDriver(): SqlDriver = nativeInMemoryDriver(ShopDatabase.Schema.synchronous())
```

```kotlin
// sharedLogic/src/androidDeviceTest/kotlin/shop/sharedlogic/db/InMemoryDriver.android.kt
package shop.sharedlogic.db

import androidx.test.core.app.ApplicationProvider
import app.cash.sqldelight.async.coroutines.synchronous
import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.android.AndroidSqliteDriver

// No name: the database lives in memory.
internal actual fun inMemoryDriver(): SqlDriver =
    AndroidSqliteDriver(ShopDatabase.Schema.synchronous(), ApplicationProvider.getApplicationContext(), null)
```

## 6. The screens

Compose's UI test (`androidx.compose.ui.test.v2.runComposeUiTest`; the first version is deprecated and
the gate refuses it) draws the screen from a state and acts on it. It lives in `skikoTest`, the source
set `kmp.compose` declares for the JVM, iOS and Wasm, and the Android device's tests depend on it. The
JVM's test needs Skia's runtime (`compose.desktop.currentOs`). On the device, measured: the library's
Android resources are on, or Compose's copy of its resources into the device test's assets has no
directory and the build stops; `ui-test-manifest` gives the test its activity; Compose's ui-test brings
Espresso 3.5.0, which looks for `InputManager.getInstance` and fails on Android 37
(`NoSuchMethodException`) — `kmp.compose` takes Espresso 3.7.0.

```kotlin
// build-logic/convention/src/main/kotlin/kmp.compose.gradle.kts
// A multiplatform library with a Compose user interface.
import org.jetbrains.kotlin.gradle.ExperimentalWasmDsl

plugins {
    id("kmp.library")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
}

val catalog = versionCatalogs.named("libs")

kotlin {
    // Compose's tests on Wasm load the Skiko runtime from a webpack bundle: the target is executable
    // (the Compose plugin refuses otherwise, CMP-4906).
    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        binaries.executable()
    }
    // Compose copies its resources into the Android assets, which a library has only with its
    // Android resources on — without them the device tests' copy has nowhere to go.
    android {
        androidResources {
            enable = true
        }
    }
    // The Compose UI tests live in skikoTest, where Compose draws with Skia — desktop, iOS, web — and
    // run on Android too, on the device: androidDeviceTest takes them in.
    @OptIn(org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi::class)
    applyDefaultHierarchyTemplate {
        common {
            group("skiko") {
                withJvm()
                withIos()
                withWasmJs()
            }
        }
    }
    sourceSets {
        jvmTest.dependencies {
            implementation(compose.desktop.currentOs)
        }
        getByName("androidDeviceTest") {
            dependsOn(getByName("skikoTest"))
            dependencies {
                implementation(catalog.findLibrary("compose-ui-test-manifest").get())
                // Compose's ui-test brings Espresso 3.5.0, which looks for InputManager.getInstance — gone
                // on the current Android: the test fails on the device.
                implementation(catalog.findLibrary("androidx-espresso-core").get())
            }
        }
        commonMain.dependencies {
            implementation(catalog.findLibrary("compose-runtime").get())
            implementation(catalog.findLibrary("compose-foundation").get())
            implementation(catalog.findLibrary("compose-ui").get())
            implementation(catalog.findLibrary("compose-material3").get())
        }
    }
}
```

```kotlin
// feature/customers/src/skikoTest/kotlin/shop/feature/customers/ui/CustomersScreenTest.kt
package shop.feature.customers.ui

import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.v2.runComposeUiTest
import shop.core.AppError
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.CustomerStatus
import shop.feature.customers.application.CustomersIntent
import shop.feature.customers.application.CustomersState
import kotlin.test.Test
import kotlin.test.assertEquals

@OptIn(ExperimentalTestApi::class)
class CustomersScreenTest {
    private val grace = Customer(id = 1, name = "Grace", email = "grace@example.com", status = CustomerStatus.ACTIVE)

    @Test
    fun blockOfAnActiveCustomerSendsTheIntent() =
        runComposeUiTest {
            val sent = mutableListOf<CustomersIntent>()
            setContent { CustomersScreen(CustomersState(customers = listOf(grace), total = 1)) { sent += it } }

            onNodeWithTag("block-1").performClick()

            assertEquals(listOf<CustomersIntent>(CustomersIntent.Block(1)), sent)
        }

    @Test
    fun errorOfTheStateIsShown() =
        runComposeUiTest {
            setContent { CustomersScreen(CustomersState(error = AppError(ErrorCode.UNAVAILABLE, "no network"))) {} }

            onNodeWithText("no network").assertIsDisplayed()
        }
}
```

## 7. End to end

The whole app against the real backend, on the desktop target: Compose's UI test (§6) on `App()` with the real composition, in a source set `e2eTest` of `:desktopApp`, run by `./gradlew :desktopApp:e2eTest` with `SHOP_API_URL` set; the task starts the backend with its start command, waits on its readiness URL and stops it at the end; it is left out of `check`. It finds the elements by their test tag, acts as the user does and waits for what the user sees. The mobile targets stay at the level of §6: a device needs its own runner, and the project adds one when it wants it. This form has not been measured, unlike the rest of this file.

A coroutine test is `runTest`: `kotlin-no-runblocking-in-tests` refuses `runBlocking`.
