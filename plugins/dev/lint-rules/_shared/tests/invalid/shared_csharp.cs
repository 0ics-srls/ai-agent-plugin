public class Config
{
    public string ApiKey = "sk-live-abc123def456ghi789";

    public void Query(string userId)
    {
        var sql = "SELECT * FROM users WHERE id = " + userId;
        // TODO fix this later
    }
}
