let apiKey = "sk-live-abc123def456ghi789"

func query(userId: String) -> String {
    let sql = "SELECT * FROM users WHERE id = " + userId
    // TODO fix this later
    return sql
}
