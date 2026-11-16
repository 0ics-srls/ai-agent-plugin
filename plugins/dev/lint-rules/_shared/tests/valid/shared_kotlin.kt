class Config {
    val apiKey = System.getenv("API_KEY")

    fun query(userId: String) {
        val sql = "SELECT * FROM users WHERE id = ?"
        // TODO(#123): revisit connection pooling
    }
}
