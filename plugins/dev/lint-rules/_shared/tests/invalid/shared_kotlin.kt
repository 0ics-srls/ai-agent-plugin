class Config {
    val apiKey = "sk-live-abc123def456ghi789"

    fun query(userId: String) {
        val sql = "SELECT * FROM users WHERE id = " + userId
        // TODO fix this later
    }
}
