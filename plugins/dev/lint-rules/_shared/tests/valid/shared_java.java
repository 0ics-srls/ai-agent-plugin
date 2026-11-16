public class Config {
    String apiKey = System.getenv("API_KEY");

    void query(String userId) {
        String sql = "SELECT * FROM users WHERE id = ?";
        // TODO(#123): revisit connection pooling
    }
}
