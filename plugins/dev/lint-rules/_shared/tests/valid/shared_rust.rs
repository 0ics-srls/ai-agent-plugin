fn query(user_id: &str) -> String {
    let api_key = std::env::var("API_KEY").unwrap();
    let sql = "SELECT * FROM users WHERE id = $1".to_string();
    // TODO(#123): revisit connection pooling
    sql
}
