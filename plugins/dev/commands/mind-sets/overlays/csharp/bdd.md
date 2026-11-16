# C# / .NET 10 — BDD

How `bdd-overlay.md` is written in C#, loaded with it and only on request.

---

Reqnroll with xUnit v3 (`Reqnroll.xunit.v3`, BSD-3), on Microsoft.Testing.Platform like
every other test project. Feature files sit in `Features/` of the API test project. Reqnroll builds
the binding classes again for every scenario, so the application host lives in a static `[Binding]`
class, started once for the run by a `[BeforeTestRun]` hook and disposed by `[AfterTestRun]`; the
steps read it from there:

```csharp
using Reqnroll;

namespace App.Api.Tests.Features;

[Binding]
public static class SharedHost
{
    private static ApiFactory? factory;

    public static ApiFactory Factory =>
        factory ?? throw new InvalidOperationException("The host starts in the BeforeTestRun hook.");

    [BeforeTestRun]
    public static async Task StartAsync()
    {
        factory = new ApiFactory();
        await factory.InitializeAsync();
    }

    [AfterTestRun]
    public static async Task StopAsync() => await Factory.DisposeAsync();
}
```

```csharp
using AwesomeAssertions;
using Reqnroll;

namespace App.Api.Tests.Features;

[Binding]
public sealed class OrderSteps
{
    private HttpResponseMessage? response;

    [When("I send a GET request to {string}")]
    public async Task WhenISendAGetRequest(string endpoint)
    {
        response = await SharedHost.Factory.CreateClient()
            .GetAsync(new Uri(endpoint, UriKind.Relative), TestContext.Current.CancellationToken);
    }

    [Then("the response status should be {int}")]
    public void ThenTheResponseStatusShouldBe(int status)
    {
        ((int)response!.StatusCode).Should().Be(status);
    }
}
```
