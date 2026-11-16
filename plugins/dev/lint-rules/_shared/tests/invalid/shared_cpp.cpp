const char* api_key = "sk-live-abc123def456ghi789";

std::string query(std::string userId) {
    std::string sql = "SELECT * FROM users WHERE id = " + userId;
    // TODO fix this later
    return sql;
}
