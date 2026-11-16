namespace App.Tests;
public class FooTests {
    [Fact]
    public async void Should_Fail_WhenAsyncVoid() {
        await Task.Yield();
    }
}
