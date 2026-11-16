let apiKey = ProcessInfo.processInfo.environment["API_KEY"]

func query(userId: String) -> String {
    let sql = "SELECT * FROM users WHERE id = ?"
    // TODO(#123): revisit connection pooling
    return sql
}
