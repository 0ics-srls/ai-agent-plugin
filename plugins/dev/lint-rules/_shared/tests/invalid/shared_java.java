public class Config {
    String apiKey = "sk-live-abc123def456ghi789";

    void query(String userId) {
        String sql = "SELECT * FROM users WHERE id = " + userId;
        // TODO fix this later
    }
}
