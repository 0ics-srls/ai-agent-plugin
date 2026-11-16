# Kotlin (KMP) — The backend's client and the local storage

How `branches/frontend.md` 1 and 5 (the generated contract, every failure to the user),
`branches/data.md` and `branches/resilience.md` are written in the app: the client generated from the
backend's OpenAPI document, the one class that turns its answers into results, the local database.
Measured with openapi-generator 7.27.0 (Apache 2.0), Ktor 3.6.1, SQLDelight 2.4.1 (Apache 2.0).

---

## 1. The client, generated at every build

The backend's document is a file of the app's repository, `openapi/shop.json`, kept equal to what the
backend serves (`branches/api.md` 2). The convention `kmp.openapi` generates from it at every build,
with the `kotlin` generator for multiplatform: the models into `core` (public, the app's data), the APIs
and their infrastructure into `api-client`; only the generated Kotlin is copied into the module's
sources — the generator also writes a Gradle project, which must not be compiled — and nobody edits it.

- The generator's OpenAPI 3.1 support is in beta: a tuple (`prefixItems`) becomes `List<List<Any>>`,
  which kotlinx.serialization cannot serialize, and the module does not compile. The contract uses
  objects with named fields (the list's filters are `Filter {field, value}`, measured).
- The client is public in a module of its own, which only sharedLogic depends on.
- The generated code compiles with every warning as an error (measured).

```kotlin
// build-logic/convention/src/main/kotlin/kmp.openapi.gradle.kts
// Code generated from the backend's OpenAPI document (openapi/ at the root) at every build: the
// kotlin generator for multiplatform (Ktor, kotlinx.serialization), the models in shop.core.model,
// every declaration with its visibility. Only the generated Kotlin is copied into the module's
// sources; nobody edits it. Each module says what it generates (globalProperties).
plugins {
    id("org.openapi.generator")
}

val generated = layout.buildDirectory.dir("generated/openapi")

openApiGenerate {
    generatorName.set("kotlin")
    library.set("multiplatform")
    inputSpec.set(rootProject.file("openapi/${rootProject.name}.json").path)
    outputDir.set(generated)
    packageName.set("${rootProject.name}.client")
    modelPackage.set("${rootProject.name}.core.model")
    configOptions.set(
        mapOf(
            "explicitApi" to "true",
            "enumPropertyNaming" to "original",
            "dateLibrary" to "kotlinx-datetime",
            "sourceFolder" to "src/commonMain/kotlin",
        ),
    )
}

val generatedSources =
    tasks.register<Sync>("generatedSources") {
        dependsOn(tasks.openApiGenerate)
        from(generated.map { it.dir("src/commonMain/kotlin") })
        into(layout.buildDirectory.dir("generated/sources/kotlin"))
    }

extensions.configure<org.jetbrains.kotlin.gradle.dsl.KotlinMultiplatformExtension> {
    sourceSets.named("commonMain") { kotlin.srcDir(generatedSources) }
}
```

```kotlin
// core/build.gradle.kts
// Core: the base types of the app and the data that crosses the contracts. The models of the API are
// generated here, public.
plugins {
    id("kmp.library")
    id("kmp.serialization")
    id("kmp.openapi")
}

openApiGenerate {
    globalProperties.set(mapOf("models" to "", "modelDocs" to "false", "modelTests" to "false"))
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(libs.kotlinx.serialization.json)
        }
    }
}
```

```kotlin
// api-client/build.gradle.kts
// The client of the backend, generated here: the APIs and their infrastructure; the models come from
// core. Only sharedLogic depends on it (implementation): no other module sees it.
plugins {
    id("kmp.library")
    id("kmp.serialization")
    id("kmp.openapi")
}

openApiGenerate {
    globalProperties.set(mapOf("apis" to "", "supportingFiles" to "", "apiDocs" to "false", "apiTests" to "false"))
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(projects.core)
            api(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
        }
    }
}
```

## 2. The answers as results

One class of sharedLogic, `ShopApi`, calls the generated client and turns every answer into an
`AppResult` (`language.md` §3): a success with its body; a `problem+json` answer into the domain's
error with its `code`, detail and field (`branches/frontend.md` 5); an unreachable backend or an
answer that is not a problem into `UNAVAILABLE`. The domain wraps it behind a contract (`app.md` §1),
so a feature never sees an HTTP status. Each target brings its HTTP engine: OkHttp on Android and the
JVM, Darwin on iOS, the browser's fetch on the web.

```kotlin
// sharedLogic/src/commonMain/kotlin/shop/sharedlogic/data/ShopApi.kt
package shop.sharedlogic.data

import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.statement.bodyAsText
import kotlinx.coroutines.CancellationException
import kotlinx.serialization.SerializationException
import kotlinx.serialization.json.Json
import shop.client.apis.CustomersApi
import shop.client.infrastructure.HttpResponse
import shop.core.AppError
import shop.core.AppResult
import shop.core.ErrorCode
import shop.core.model.Customer
import shop.core.model.PageCustomer
import shop.core.model.PageQuery
import shop.core.model.Problem

/**
 * The backend, through its generated client: each answer becomes an [AppResult]; a `problem+json`
 * answer becomes the domain's error with its code, an unreachable backend [ErrorCode.UNAVAILABLE].
 */
public class ShopApi internal constructor(
    private val customers: CustomersApi,
) {
    public constructor(baseUrl: String, engine: HttpClientEngine = platformEngine()) :
        this(CustomersApi(baseUrl = baseUrl, httpClientEngine = engine))

    public suspend fun page(
        skip: Int,
        take: Int,
    ): AppResult<PageCustomer> = call { customers.customersLoad(PageQuery(skip = skip, take = take)) }

    public suspend fun get(id: Int): AppResult<Customer> = call { customers.customersGetById(id) }

    public suspend fun block(id: Int): AppResult<Customer> = call { customers.customersBlock(id) }

    private suspend fun <T : Any> call(request: suspend () -> HttpResponse<T>): AppResult<T> {
        val response =
            try {
                request()
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (
                @Suppress("TooGenericExceptionCaught") unreachable: Exception,
            ) {
                return AppResult.Failure(
                    AppError(
                        ErrorCode.UNAVAILABLE,
                        unreachable.message ?: "the backend did not answer",
                    ),
                )
            }
        return if (response.success) AppResult.Success(response.body()) else AppResult.Failure(problemOf(response))
    }

    private suspend fun problemOf(response: HttpResponse<*>): AppError =
        try {
            val problem = problemJson.decodeFromString<Problem>(response.response.bodyAsText())
            AppError(
                ErrorCode.entries.firstOrNull {
                    it.name == problem.code
                } ?: ErrorCode.UNAVAILABLE,
                problem.detail,
                problem.field,
            )
        } catch (unreadable: SerializationException) {
            AppError(ErrorCode.UNAVAILABLE, "status ${response.status}: ${unreadable.message}")
        }

    private companion object {
        val problemJson = Json { ignoreUnknownKeys = true }
    }
}

/** The HTTP engine of the target the app runs on. */
internal expect fun platformEngine(): HttpClientEngine
```

```kotlin
// sharedLogic/src/iosMain/kotlin/shop/sharedlogic/data/PlatformEngine.kt
package shop.sharedlogic.data

import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.engine.darwin.Darwin

internal actual fun platformEngine(): HttpClientEngine = Darwin.create()
```

## 3. The local database

SQLDelight, SQL first: the schema and the named queries in `.sq` files, the columns with the API's
names, an enumeration stored as its declared name. The schema is generated asynchronous, because the
web's driver runs in a worker; the other drivers — Android's, the native one, the JVM's SQLite — take
it through `synchronous()`. The cache is proved on the real SQLite engine of the JVM, iOS and Android
(`testing.md` §6); on the web it compiles with its driver.

```sql
-- sharedLogic/src/commonMain/sqldelight/shop/sharedlogic/db/Customer.sq
-- The customers the app has seen, kept for offline reading; the columns are the API's names.
CREATE TABLE customer (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    status TEXT NOT NULL
);

save:
INSERT OR REPLACE INTO customer(id, name, email, status) VALUES (?, ?, ?, ?);

all:
SELECT id, name, email, status FROM customer ORDER BY id;
```

```kotlin
// sharedLogic/src/commonMain/kotlin/shop/sharedlogic/db/CustomerCache.kt
package shop.sharedlogic.db

import app.cash.sqldelight.async.coroutines.awaitAsList
import app.cash.sqldelight.db.SqlDriver
import shop.core.model.Customer
import shop.core.model.CustomerStatus

/** The customers kept on the device, with their status as its declared name. */
public class CustomerCache(
    driver: SqlDriver,
) {
    private val queries = ShopDatabase(driver).customerQueries

    public suspend fun save(customers: List<Customer>) {
        customers.forEach { customer ->
            val id = requireNotNull(customer.id) { "a stored customer has an id" }
            queries.save(id.toLong(), customer.name, customer.email, (customer.status ?: CustomerStatus.ACTIVE).value)
        }
    }

    public suspend fun all(): List<Customer> =
        queries.all().awaitAsList().map { row ->
            Customer(
                id = row.id.toInt(),
                name = row.name,
                email = row.email,
                status = CustomerStatus.entries.first { it.value == row.status },
            )
        }
}
```

```kotlin
// sharedLogic/build.gradle.kts
// The app's own logic over the outside world: the backend through its generated client, the HTTP
// engine of each target. It implements no contract: the domain wraps its public classes.
plugins {
    id("kmp.library")
    id("kmp.serialization")
    id("app.cash.sqldelight")
}

// The local database: SQL first, the queries named in .sq files. The schema is asynchronous because
// the web's driver runs in a worker; the other drivers take it through synchronous().
sqldelight {
    databases {
        create("ShopDatabase") {
            packageName.set("shop.sharedlogic.db")
            generateAsync.set(true)
        }
    }
}

kotlin {
    // The cache's tests run on a real SQLite engine — JVM, iOS, Android on the device — in sqliteTest,
    // each target giving its in-memory driver. The web's driver runs in a worker: it is only compiled.
    @OptIn(org.jetbrains.kotlin.gradle.ExperimentalKotlinGradlePluginApi::class)
    applyDefaultHierarchyTemplate {
        common {
            group("sqlite") {
                withJvm()
                group("ios")
            }
        }
    }
    sourceSets {
        getByName("androidDeviceTest").dependsOn(getByName("sqliteTest"))
        commonMain.dependencies {
            api(projects.core)
            api(libs.ktor.client.core)
            implementation(projects.apiClient)
            implementation(libs.koin.core)
            implementation(libs.sqldelight.async)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
            implementation(libs.sqldelight.android.driver)
        }
        jvmMain.dependencies {
            implementation(libs.ktor.client.okhttp)
            implementation(libs.sqldelight.sqlite.driver)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }
        wasmJsMain.dependencies {
            implementation(libs.ktor.client.js)
            implementation(libs.sqldelight.web.worker.driver)
        }
        commonTest.dependencies { implementation(libs.ktor.client.mock) }
    }
}
```

## 4. Security

The app's rules, as contracts in `api-contract` with their implementation for each target chosen by
the project (`branches/security.md`):

- The user signs in with OpenID Connect, Authorization Code with PKCE, in the system's browser — never
  a web view inside the app.
- Tokens live in the platform's secure store — the Keychain on iOS and macOS, the Keystore on Android;
  the web keeps them only for the session.
- The binary carries no secret: the app talks to its own backend, which holds the keys of third
  parties.
- What the app logs carries no token, no personal data, no request body.
