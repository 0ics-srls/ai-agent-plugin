namespace App.Tests;
public class GuardTests {
    private Fixture _fixture = null!;
    [Fact]
    public void Create_NullName_Throws() => Assert.Throws<ArgumentNullException>(() => new Customer(null!));
}
