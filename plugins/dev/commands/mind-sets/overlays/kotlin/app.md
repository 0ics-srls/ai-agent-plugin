# Kotlin (KMP) — The app

How `branches/frontend.md` is written in a Compose Multiplatform app: the modules and their arrows, the
screens in MVI with Orbit, the one navigation of the shell, the composition with Koin, the settings of
each platform. Measured with Compose Multiplatform 1.12.2, Orbit 12.0.1, Navigation 3 1.2.0
(`org.jetbrains.androidx.navigation3`), Koin 4.2.2.

---

## 1. The modules and their arrows

The layers are the backend's (Core / Db / Domain / Api); a module sees only what it depends on, and
Gradle enforces it (A → B: A depends on B).

| Module | Holds | Depends on |
|---|---|---|
| `:core` | the base types (`AppResult`, `AppError`, `ErrorCode`) and the data that crosses the contracts — the models generated from the backend's document | nothing of the project |
| `:api-contract` | the contracts: interfaces only — what the features use, what the domain needs from the outside | `core` |
| `:api-client` | the backend's client, generated (`client.md` §1) | `core` |
| `:sharedLogic` | the app's logic over the outside: the backend through the client, the local database, the engine of each target; it implements no contract, its public classes are wrapped by the domain | `core`, `api-client` (implementation: no other module sees the client) |
| `:domain` | the services that implement the contracts, the adapters over sharedLogic, the one Koin module that binds each contract to its implementation | `api-contract`, `sharedLogic` |
| `:feature:<x>` | `application/` — the ViewModel; `ui/` — the screen, `(State) → UI` | `api-contract`, `ui-kit` |
| `:ui-kit` | the design system: the theme, the shared components | Compose |
| `:sharedUI` | `App()`, the one `NavDisplay`, the composition root in `di/` | the features, `domain`, `sharedLogic`, `ui-kit` |
| `:test-support` | the doubles of the contracts, written once (`testing.md` §3) | `api-contract`; only tests see it |
| `:androidApp`, `:desktopApp`, `:webApp`, `iosApp/` | each platform's entry point and settings (§5) | `sharedUI` |

A feature never sees another feature, the domain or sharedLogic: it speaks to the contracts.

## 2. A screen's logic: MVI with Orbit

The ViewModel holds one immutable state, receives the user's intents as a `sealed interface`, and
sends what happens once — the navigation — as a side effect; it speaks only to the contracts. Orbit's
`OrbitContainerHost` and `orbitContainer` (the earlier `ContainerHost` and `container` are deprecated,
and the gate refuses them).

```kotlin
// feature/customers/src/commonMain/kotlin/shop/feature/customers/application/CustomersViewModel.kt
package shop.feature.customers.application

import androidx.lifecycle.ViewModel
import org.orbitmvi.orbit.OrbitContainer
import org.orbitmvi.orbit.OrbitContainerHost
import org.orbitmvi.orbit.viewmodel.orbitContainer
import shop.contract.CustomerDirectory
import shop.core.AppError
import shop.core.AppResult
import shop.core.model.Customer

/** What the customers screen shows. */
public data class CustomersState(
    val customers: List<Customer> = emptyList(),
    val total: Int = 0,
    val loading: Boolean = false,
    val error: AppError? = null,
)

/** What the user does on the customers screen. */
public sealed interface CustomersIntent {
    public data object Load : CustomersIntent

    public data class Block(
        val id: Int,
    ) : CustomersIntent

    public data class Open(
        val id: Int,
    ) : CustomersIntent
}

/** What happens once and is not state: the shell navigates. */
public sealed interface CustomersEffect {
    public data class OpenCustomer(
        val id: Int,
    ) : CustomersEffect
}

/** The customers screen's logic: it speaks only to the contracts. */
public class CustomersViewModel(
    private val directory: CustomerDirectory,
) : ViewModel(),
    OrbitContainerHost<CustomersState, CustomersState, CustomersEffect> {
    override val container: OrbitContainer<CustomersState, CustomersState, CustomersEffect> =
        orbitContainer(CustomersState()) { load() }

    public fun onIntent(intent: CustomersIntent) {
        when (intent) {
            CustomersIntent.Load -> load()
            is CustomersIntent.Block -> block(intent.id)
            is CustomersIntent.Open -> intent { postSideEffect(CustomersEffect.OpenCustomer(intent.id)) }
        }
    }

    private fun load() =
        intent {
            reduce { state.copy(loading = true, error = null) }
            when (val page = directory.page(skip = 0, take = PAGE_SIZE)) {
                is AppResult.Success -> {
                    reduce { state.copy(customers = page.value.items, total = page.value.total, loading = false) }
                }

                is AppResult.Failure -> {
                    reduce { state.copy(loading = false, error = page.error) }
                }
            }
        }

    private fun block(id: Int) =
        intent {
            when (val blocked = directory.block(id)) {
                is AppResult.Success -> {
                    reduce { state.copy(customers = state.customers.map { if (it.id == id) blocked.value else it }) }
                }

                is AppResult.Failure -> {
                    reduce { state.copy(error = blocked.error) }
                }
            }
        }

    private companion object {
        const val PAGE_SIZE = 50
    }
}
```

## 3. The screen: (State) → UI

The screen draws the state and sends intents; it decides nothing. The route around it gets the
ViewModel from Koin, collects the state, and turns the side effects into the shell's callbacks.

```kotlin
// feature/customers/src/commonMain/kotlin/shop/feature/customers/ui/CustomersScreen.kt
package shop.feature.customers.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ListItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import org.koin.compose.viewmodel.koinViewModel
import org.orbitmvi.orbit.compose.collectAsState
import org.orbitmvi.orbit.compose.collectSideEffect
import shop.core.model.CustomerStatus
import shop.feature.customers.application.CustomersEffect
import shop.feature.customers.application.CustomersIntent
import shop.feature.customers.application.CustomersState
import shop.feature.customers.application.CustomersViewModel

/** The customers screen as the shell places it: its ViewModel, and where it goes when a customer opens. */
@Composable
public fun CustomersRoute(onOpenCustomer: (Int) -> Unit) {
    val viewModel = koinViewModel<CustomersViewModel>()
    val state by viewModel.collectAsState()
    viewModel.collectSideEffect { effect ->
        when (effect) {
            is CustomersEffect.OpenCustomer -> onOpenCustomer(effect.id)
        }
    }
    CustomersScreen(state, viewModel::onIntent)
}

/** The screen: what the state says, and the intents the user sends. */
@Composable
public fun CustomersScreen(
    state: CustomersState,
    onIntent: (CustomersIntent) -> Unit,
) {
    Column {
        if (state.loading) {
            CircularProgressIndicator()
        }
        state.error?.let { error -> Text(error.detail, Modifier.testTag("error")) }
        LazyColumn {
            items(state.customers, key = { it.id ?: 0 }) { customer ->
                val id = customer.id ?: return@items
                ListItem(
                    headlineContent = { Text(customer.name) },
                    supportingContent = { Text(customer.status?.value ?: "") },
                    trailingContent = {
                        if (customer.status == CustomerStatus.ACTIVE) {
                            Button(
                                { onIntent(CustomersIntent.Block(id)) },
                                Modifier.testTag("block-$id"),
                            ) { Text("Block") }
                        }
                    },
                    modifier = Modifier.clickable { onIntent(CustomersIntent.Open(id)) },
                )
            }
        }
    }
}
```

## 4. The composition and the one navigation

- **Every module registers its own parts with Koin, by their constructors** (`singleOf`,
  `viewModelOf`): the graph test reads the constructors' parameters, and a contract with no binding
  fails it (`testing.md` §4). With a lambda (`single<X> { Impl(get()) }`) the test sees only the
  interface and passes on a missing binding (measured).
- **The domain's module is the one place where a contract meets its implementation.**
- **The shell owns the navigation**: one `NavDisplay` with the app's keys, `@Serializable` `NavKey`s
  registered for saving; the features call back (`onOpenCustomer`) and never see Navigation 3. The
  entry decorators keep each entry's saved state and its ViewModels.

```kotlin
// domain/src/commonMain/kotlin/shop/domain/DomainModule.kt
package shop.domain

import org.koin.core.module.Module
import org.koin.core.module.dsl.bind
import org.koin.core.module.dsl.singleOf
import org.koin.dsl.module
import shop.contract.AuditLog
import shop.contract.CustomerDirectory
import shop.contract.CustomerRemote
import shop.domain.adapters.LogAuditLog
import shop.domain.adapters.ShopCustomerRemote

/**
 * The one place where the contracts meet their implementations. Each one is declared by its
 * constructor, so the graph test reads the parameters it needs.
 */
public val domainModule: Module =
    module {
        singleOf(::ShopCustomerRemote) { bind<CustomerRemote>() }
        singleOf(::LogAuditLog) { bind<AuditLog>() }
        singleOf(::CustomerService) { bind<CustomerDirectory>() }
    }
```

```kotlin
// feature/customers/src/commonMain/kotlin/shop/feature/customers/di/CustomersModule.kt
package shop.feature.customers.di

import org.koin.core.module.Module
import org.koin.core.module.dsl.viewModelOf
import org.koin.dsl.module
import shop.feature.customers.application.CustomersViewModel

/** The feature registers its own ViewModel. */
public val customersModule: Module =
    module {
        viewModelOf(::CustomersViewModel)
    }
```

```kotlin
// sharedUI/src/commonMain/kotlin/shop/sharedui/di/AppModules.kt
package shop.sharedui.di

import org.koin.core.module.Module
import shop.domain.domainModule
import shop.feature.customers.di.customersModule
import shop.sharedlogic.di.sharedLogicModule
import shop.sharedui.AppSettings

/** The composition root: what exists, and who provides it. */
internal fun appModules(settings: AppSettings): List<Module> =
    listOf(
        sharedLogicModule(settings.apiBaseUrl),
        domainModule,
        customersModule,
    )
```

```kotlin
// sharedUI/src/commonMain/kotlin/shop/sharedui/App.kt
package shop.sharedui

import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.navigation3.rememberViewModelStoreNavEntryDecorator
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.runtime.rememberSaveableStateHolderNavEntryDecorator
import androidx.navigation3.ui.NavDisplay
import androidx.savedstate.serialization.SavedStateConfiguration
import kotlinx.serialization.Serializable
import kotlinx.serialization.modules.SerializersModule
import kotlinx.serialization.modules.polymorphic
import kotlinx.serialization.modules.subclass
import org.koin.compose.KoinApplication
import org.koin.dsl.koinConfiguration
import shop.feature.customers.ui.CustomersRoute
import shop.sharedui.di.appModules
import shop.uikit.ShopTheme

/** The destinations of the app: the shell owns them; the features only call back. */
@Serializable
internal data object CustomerList : NavKey

@Serializable
internal data class CustomerDetail(
    val id: Int,
) : NavKey

private val navigation =
    SavedStateConfiguration {
        serializersModule =
            SerializersModule {
                polymorphic(NavKey::class) {
                    subclass(CustomerList::class)
                    subclass(CustomerDetail::class)
                }
            }
    }

/** The app: the composition root, the theme, and the one NavDisplay. */
@Composable
public fun App(settings: AppSettings) {
    KoinApplication(configuration = koinConfiguration { modules(appModules(settings)) }) {
        ShopTheme {
            val backStack = rememberNavBackStack(navigation, CustomerList)
            NavDisplay(
                backStack = backStack,
                entryDecorators =
                    listOf(
                        rememberSaveableStateHolderNavEntryDecorator(),
                        rememberViewModelStoreNavEntryDecorator(),
                    ),
                entryProvider =
                    entryProvider {
                        entry<CustomerList> {
                            CustomersRoute(onOpenCustomer = { id ->
                                backStack.add(CustomerDetail(id))
                            })
                        }
                        entry<CustomerDetail> { key -> Text("Customer ${key.id}") }
                    },
            )
        }
    }
}
```

## 5. The settings, each platform's entry point

The settings are checked once, at startup (principles 5.1); each platform reads them where it keeps
them and hands them to `App`. Without a valid backend address the desktop app stops before its window
opens and says why (measured: «startup aborted: SHOP_API_URL — apiBaseUrl must be an http(s) address,
not ''»).

```kotlin
// sharedUI/src/commonMain/kotlin/shop/sharedui/AppSettings.kt
package shop.sharedui

/** The settings of the app, given by each platform's entry point and checked once, at startup. */
public data class AppSettings(
    val apiBaseUrl: String,
) {
    init {
        require(apiBaseUrl.startsWith("https://") || apiBaseUrl.startsWith("http://")) {
            "apiBaseUrl must be an http(s) address, not '$apiBaseUrl'"
        }
    }
}
```

```kotlin
// desktopApp/src/main/kotlin/shop/desktop/Main.kt
package shop.desktop

import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import co.touchlab.kermit.Logger
import shop.sharedui.App
import shop.sharedui.AppSettings
import kotlin.system.exitProcess

/** The desktop entry point: the backend's address from SHOP_API_URL, checked before the window opens. */
public fun main() {
    val settings =
        runCatching { AppSettings(System.getenv("SHOP_API_URL").orEmpty()) }.getOrElse { invalid ->
            Logger.withTag("startup").e { "startup aborted: SHOP_API_URL — ${invalid.message}" }
            exitProcess(1)
        }
    application {
        Window(onCloseRequest = ::exitApplication, title = "Shop") { App(settings) }
    }
}
```

```kotlin
// androidApp/src/main/kotlin/shop/android/MainActivity.kt
package shop.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import shop.sharedui.App
import shop.sharedui.AppSettings

/** The Android entry point: the shared UI with the settings of this build. */
public class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val settings = AppSettings(BuildConfig.API_BASE_URL)
        setContent { App(settings) }
    }
}
```

```kotlin
// webApp/src/wasmJsMain/kotlin/shop/web/Main.kt
package shop.web

import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.window.ComposeViewport
import kotlinx.browser.window
import shop.sharedui.App
import shop.sharedui.AppSettings

/** The web entry point: the backend is the origin that served the page. */
@OptIn(ExperimentalComposeUiApi::class)
public fun main() {
    val settings = AppSettings(window.location.origin)
    ComposeViewport(viewportContainerId = "composeTarget") { App(settings) }
}
```

```kotlin
// sharedUI/src/iosMain/kotlin/shop/sharedui/MainViewController.kt
package shop.sharedui

import androidx.compose.ui.window.ComposeUIViewController
import platform.UIKit.UIViewController

/** The iOS entry point: the Swift app shows this controller, with the settings it read from its Info.plist. */
public fun mainViewController(apiBaseUrl: String): UIViewController =
    ComposeUIViewController { App(AppSettings(apiBaseUrl)) }
```

```swift
// iosApp/iosApp/ContentView.swift
import UIKit
import SwiftUI
import SharedUI

/// The shared UI, with the backend's address from the app's Info.plist (ShopApiBaseUrl).
struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        let apiBaseUrl = Bundle.main.object(forInfoDictionaryKey: "ShopApiBaseUrl") as? String ?? ""
        return MainViewControllerKt.mainViewController(apiBaseUrl: apiBaseUrl)
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

struct ContentView: View {
    var body: some View {
        ComposeView()
            .ignoresSafeArea()
    }
}
```

- Android: the address is the Gradle property `shop.apiBaseUrl`, written into `BuildConfig` by
  `androidApp/build.gradle.kts`; the web app's is the origin that served the page; the iOS app's is
  `ShopApiBaseUrl` in `iosApp/iosApp/Info.plist`.
- The iOS app is the Xcode project `iosApp/`: its build phase runs `./gradlew
  :sharedUI:embedAndSignAppleFrameworkForXcode`, and it is built with `xcodebuild -scheme iosApp
  -configuration Debug -sdk iphonesimulator -arch arm64 CODE_SIGNING_ALLOWED=NO` (measured).
