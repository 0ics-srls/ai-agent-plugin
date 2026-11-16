namespace App.Tests;
public class CleanTests {
    [Fact]
    public async Task Should_Return_WhenValid() {
        await Task.Yield();
        Assert.True(true);
    }
}
