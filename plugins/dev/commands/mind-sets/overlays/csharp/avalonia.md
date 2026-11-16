# C# / .NET 10 — A desktop client (Avalonia)

How `branches/frontend.md` is written in a desktop application on Avalonia (MIT). The language is `language.md`, the tests `testing.md`. These rules have not been measured on a project.

---

## 1. The client, generated

- The client and its types come from the API's OpenAPI document, `openapi/<Api project>.json`, through Kiota (MIT), as a dotnet tool in the
  project's manifest: `dotnet kiota generate`, in a target that runs before the build, into a folder nobody edits (frontend 1). The generated
  types are what the application uses, as they are (frontend 2); the generated folder is outside the gate (`language.md` §5).
- Every answer that is not a success becomes the domain's error once, in one adapter over the client, with the `Code` of the `ProblemDetails`
  (frontend 5).
- Every list runs on the server, through the load (`aspnetcore.md` §3, frontend 3).

## 2. A screen's logic

- One view model per screen, on CommunityToolkit.Mvvm (MIT): `[ObservableProperty]` and `[RelayCommand]`. It holds what the screen shows — the
  data with its loading state and its error (frontend 4) — and speaks only to the contracts; where the user goes next is the shell's.
- The `async` commands take the `CancellationToken` of the toolkit, and the UI thread is left only by `await` (`language.md` §2).

## 3. The screen

- A view is AXAML with compiled bindings on (`x:DataType`), so a wrong binding stops the build; it holds no logic and no data from the API.
- Every failure reaches the user (frontend 5); the form helps, the server validates (frontend 6).

## 4. Composition and settings

- `Program` builds the host with the same `Microsoft.Extensions.DependencyInjection` and Options as a service (`aspnetcore.md` §2, §6); a view model
  arrives by constructor.
- The API's address and the settings come from outside the code, and are validated at startup (frontend 8); a secret is in the platform's
  secure store, never in the program.
- Logging as in `language.md` §6.

## 5. Tests

- A view model is a unit test on doubles of its contracts (`testing.md` §1).
- A view runs headless with `Avalonia.Headless.XUnit`, finding its controls by name and acting on them.
- End to end: the headless application against the real backend, started as `testing.md` starts it.
