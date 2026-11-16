const API_KEY: &str = "sk-live-abc123def456ghi789";

fn query(user_id: &str) -> String {
    let sql = "SELECT * FROM users WHERE id = ".to_string() + user_id;
    // TODO fix this later
    sql
}
