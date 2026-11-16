public class Config
{
    public string ApiKey = Environment.GetEnvironmentVariable("API_KEY");

    public void Query(string userId)
    {
        var sql = "SELECT * FROM users WHERE id = @id";
        // TODO(#123): revisit connection pooling
    }
}
