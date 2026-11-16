# Kotlin (KMP) — Language

How the principles and the code principles are written in a Kotlin Multiplatform app with Compose
Multiplatform, for Android, iOS, desktop and the web. Every form below was built and tested with
Kotlin 2.4.21, Gradle 9.8.2 and the pack (`lint-rules/kotlin/native/`), in the project of the examples: `shop` stands for the project's name and
root package. How the app is put together — modules, screens, navigation — is `app.md`; the backend's
client and the local storage are `client.md`.

---

## 1. Language and conventions

- **Kotlin 2.4 (K2)**, Kotlin's official code style.
- **An implementation is `internal`**; what another module uses is `public` (code principles 4.4).
- **Data is a `data class` of `val`s**, changed with `copy()` (code principles 3.1); an entity travels
  as it is (3.2) — the models generated from the backend's document are the app's data (`client.md`
  §1). A closed set is an `enum class` or a `sealed interface` (3.3); whether a value can be absent is
  its type (`?`), and it is not silenced: no `!!` and no `lateinit` in production code — the value
  comes through the constructor, stays nullable and handled (`?.`, `?:`), `by lazy`, or an explicit
  state (`Loading` / `Ready(value)`); a value known to be there fails where that is known
  (`?: error("…why…")`). The pack's rules `kotlin-no-not-null-assertion` and `kotlin-no-lateinit`
  refuse them; the tests are out of both.
- **A dependency comes through the constructor**, typed by its contract (code principles 1.8); Koin
  builds the graph (`app.md` §4).
- **The console is never written directly** — `println`, `print`, `System.out`: the pack's ast-grep
  rule `kotlin-no-console-output` refuses them; the app logs with Kermit (§4).
- **`commonMain` imports no platform** — `android.*`, `platform.*`: the rule `kotlin-no-platform-import-in-commonmain` refuses it;
  what differs per target is `expect`/`actual`.

## 2. Coroutines and waiting

Asynchronous work is a `suspend` function all the way up (code principles 4.6), run in the scope of
its owner — the ViewModel's, through Orbit (`app.md` §2) — never in `GlobalScope`. Something that
changes over time is a `Flow` or a `StateFlow` the reader collects (4.7); a test advances virtual time
(`runTest`) instead of waiting for it.

## 3. Errors

An outcome the caller handles is a value: `AppResult<T>`, a success or the domain's `AppError` with a
code from a closed set (code principles 3.4); the code that calls the outside turns its failures into
it once (`client.md` §2). An exception is a programming error — `require`, a null where none can be —
and is not caught to steer the flow.

```kotlin
// core/src/commonMain/kotlin/shop/core/AppResult.kt
package shop.core

/** The outcome of an operation the caller handles: a value, or the domain's error. */
public sealed interface AppResult<out T> {
    public data class Success<out T>(
        val value: T,
    ) : AppResult<T>

    public data class Failure(
        val error: AppError,
    ) : AppResult<Nothing>
}

/** What went wrong, as the domain names it; the boundary maps each code once. */
public enum class ErrorCode {
    NOT_FOUND,
    INVALID,
    CONFLICT,
    UNAVAILABLE,
}

/** A failure the domain reports, with its code and the field or resource involved. */
public data class AppError(
    val code: ErrorCode,
    val detail: String,
    val field: String? = null,
)
```

## 4. Logging

Kermit (Apache 2.0): a logger with a tag per class or concern, a constant message with its values
(code principles 4.9); the platform's writer is the console of each target (Logcat, OSLog, the
JVM's), and a project adds its own writers where it keeps logs.

```kotlin
// domain/src/commonMain/kotlin/shop/domain/adapters/LogAuditLog.kt
package shop.domain.adapters

import co.touchlab.kermit.Logger
import shop.contract.AuditLog

/** The audit as log lines of the "audit" tag. */
internal class LogAuditLog : AuditLog {
    private val logger = Logger.withTag("audit")

    override suspend fun record(event: String) {
        logger.i { event }
    }
}
```

## 5. Project and build

- **Gradle with the Kotlin DSL; every version in `gradle/libs.versions.toml`** (principles 6.2); every
  dependency Apache 2.0, MIT or BSD (principles 6.4). Material 3 of Compose Multiplatform has no
  stable release for Compose 1.12: the app uses `1.12.0-alpha03`.
- **The modules and their arrows** are `app.md` §1: Gradle enforces them — a module that does not depend
  on another cannot import it.
- **The shared configuration is in `build-logic/`**, convention plugins each module applies by id:
  `kmp.library` (the four targets), `kmp.compose`, `kmp.serialization`, `kmp.openapi` (`client.md`
  §1), `kmp.android.application`, `kmp.desktop.application`, `kmp.web.application`, `kmp.jvm.test`,
  and `kmp.quality`, the gate, which the library and application conventions apply. A module declares
  only its own dependencies.

```kotlin
// build-logic/convention/src/main/kotlin/kmp.library.gradle.kts
// A multiplatform library of the app: the four targets, the gate, Mokkery for the tests.
import org.jetbrains.kotlin.gradle.ExperimentalWasmDsl

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
    id("dev.mokkery")
    id("kmp.quality")
}

val catalog = versionCatalogs.named("libs")

kotlin {
    jvmToolchain(21)

    android {
        namespace = rootProject.name.lowercase() + "." + project.path.removePrefix(":").replace(':', '.').replace('-', '_')
        compileSdk = catalog.findVersion("android-compileSdk").get().requiredVersion.toInt()
        minSdk = catalog.findVersion("android-minSdk").get().requiredVersion.toInt()
        withHostTest {}
        // The device tests share commonTest's tree: the same tests run on the emulator.
        withDeviceTestBuilder {
            sourceSetTreeName = "test"
        }.configure {
            instrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        }
    }
    jvm()
    iosArm64()
    iosSimulatorArm64()

    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser()
    }

    sourceSets {
        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation(catalog.findLibrary("kotlinx-coroutines-test").get())
        }
        getByName("androidDeviceTest").dependencies {
            implementation(catalog.findLibrary("androidx-test-runner").get())
            implementation(catalog.findLibrary("androidx-test-core").get())
        }
    }
}
```

- **The gate is the build** (the pack's `kmp.quality`): every compiler warning is an error, and what
  the app ships is locked. No format check and no style rule: they find no defect, and on code that
  exists they only make it be rewritten. The manifest's `native_lint` is `./gradlew assemble`, run on
  a Mac when the app has an iOS target; the Android target builds where Android's
  `aapt2` runs — macOS, Windows, Linux on x86-64, not Linux on ARM (`aapt2` 9.5.0 is published for
  Linux only on x86-64, measured). The metadata compilations of shared source
  sets keep their warnings as warnings, by the owner's decision: there Kotlin/Native warns that two
  libraries share a `unique_name` (Compose's and SQLDelight's runtime) and no option silences it; the
  same sources compile for every target, where a warning stays an error (measured).

```kotlin
// build-logic/convention/src/main/kotlin/kmp.quality.gradle.kts
// The gate every module shares: every warning of the compiler is an error.

// Every compilation of the code turns a warning into an error. The metadata compilations of shared
// source sets are left out, by the owner's decision: there Kotlin/Native warns that two libraries share
// a unique_name (Compose's and SQLDelight's runtime), a warning of the dependencies that no option
// silences; the same sources are compiled for every target, where the warnings stay errors.
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompilationTask<*>>().configureEach {
    compilerOptions.allWarningsAsErrors.set(!name.endsWith("KotlinMetadata"))
}

// What the app ships — each target's runtime classpath, the iOS klibs — is locked in the module's
// gradle.lockfile, written by `./gradlew resolveAndLockAll --write-locks`: the audit reads it, and a
// version that changes without a new lock fails the build. The classpaths of tests and tools stay out.
val shipped =
    configurations.matching { config ->
        val shipping = config.name.endsWith("untimeClasspath") || config.name.endsWith("CompileKlibraries")
        shipping && !config.name.contains("test", ignoreCase = true)
    }
shipped.configureEach { resolutionStrategy.activateDependencyLocking() }

tasks.register("resolveAndLockAll") {
    notCompatibleWithConfigurationCache("resolves the configurations while it runs")
    doFirst { require(gradle.startParameter.isWriteDependencyLocks) { "run it with --write-locks" } }
    doLast { shipped.filter { it.isCanBeResolved }.forEach { it.incoming.resolutionResult.allComponents } }
}
```

- **Memory**: `org.gradle.jvmargs=-Xmx8g` and `kotlin.daemon.jvmargs=-Xmx6g` — with less, the native
  compilation of Compose for `iosArm64` and the Wasm test compilation stop for lack of heap (measured).
- **The audit of the dependencies** (principles 6.5), in `@gate-final`: `./gradlew resolveAndLockAll
  --write-locks` writes each module's `gradle.lockfile` — the runtime classpath of every target and the
  iOS klibs, committed — and `osv-scanner scan source -r --x-no-default-plugins --x-plugins
  java/gradlelockfile .` reads them: exit 1 with the advisories when one is found. The lockfiles hold
  what the app ships, not the classpaths of the tools: Gradle's `verification-metadata.xml` lists the
  tools too (Android lint's libraries) and the versions the resolution discarded
  (measured).
- **The version** is the app's: `versionName` in `androidApp`, `packageVersion` in `desktopApp`,
  `CFBundleShortVersionString` in the iOS app; each entry point logs it at startup (operations 2).

## 6. Serialization

kotlinx.serialization (Apache 2.0), as is (code principles 3.5): the models are generated from the
backend's OpenAPI document with `@SerialName` equal to the declared names, and an enumeration's values
are its names (`"ACTIVE"`); nothing is renamed between the wire, the code and the local storage
(`client.md` §3).

Every serialized form is read into the program's types and written from them (code principles 3.7) —
the mapper of each form, and the hand practice it replaces:
- JSON: the `@Serializable` classes, a non-null field with no default failing the decoding when it is
  missing (`MissingFieldException`) — not `parseToJsonElement` walked
  (`element.jsonObject["x"]?.jsonPrimitive?.content` ends in `null`, in silence), nor `buildJsonObject`
  by hand;
- other forms (XML, YAML, the local settings): a kotlinx.serialization format on the same classes —
  not a document or a map read by key;
- HTTP with Ktor: `body<T>()` and `call.receive<T>()` on serializable classes, typed routes for the
  parameters — not `bodyAsText()` parsed by hand, nor `call.parameters["x"]` in the code;
- the local database: SQLDelight's generated queries and their types — not a cursor read by column.

## 7. What j-setup and j-new-project read in a Kotlin project

- **Recognized by**: `settings.gradle.kts` and `gradle/libs.versions.toml` with the Kotlin Gradle plugin
  (`org.jetbrains.kotlin:kotlin-gradle-plugin`, which `build-logic/` applies as
  `org.jetbrains.kotlin.multiplatform`); the Compose Gradle plugin (`org.jetbrains.compose`) says it is a
  Compose Multiplatform app, the app modules (`androidApp`, `desktopApp`, `webApp`, `iosApp/`) its
  targets.
- **The files of this overlay, with the branches**:

  | File | With |
  |---|---|
  | `language.md` | every Kotlin project |
  | `testing.md` | every Kotlin project |
  | `tddab.md` | the TDDAB plans, with `tddab-planner.md` |
  | `app.md` | `branches/frontend.md` |
  | `client.md` | `branches/frontend.md`, `branches/data.md`, `branches/resilience.md`, `branches/security.md` (§4) |

- **What LISTEN asks** (`j-new-project`): the targets — iOS, desktop, Android, web (Wasm); the backend
  whose OpenAPI document the client is generated from; whether the app keeps data on the device.
- **The lint gate**: the manifest's `native_lint`, run from the root of the Gradle build, on a Mac when
  the app has an iOS target; the pack's `.editorconfig` goes to the root, `kmp.quality.gradle.kts` to
  `build-logic/convention/src/main/kotlin/`.
- **Vendored** (`@vendored-globs`): `build/`, `.gradle/`, `.kotlin/`, `iosApp/build/`.
- **The test levels**: the keys of `tddab.md` §1.
- **The start command**: desktop `SHOP_API_URL=<backend> ./gradlew :desktopApp:run`; web `./gradlew
  :webApp:wasmJsBrowserDevelopmentRun`; Android `./gradlew :androidApp:installDebug` on a device or an
  emulator; iOS `iosApp/iosApp.xcodeproj` in Xcode.
- **Where its errors show** (`j-debug`): the compiler's output of the build; the failed
  tests' reports (`build/reports/tests/`); Kermit's lines in the console of each target (the terminal,
  Logcat, the Xcode console, the browser's console); the `problem+json` the backend answers, with its
  `code`.
