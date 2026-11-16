const char* api_key = std::getenv("API_KEY");

std::string query(std::string userId) {
    std::string sql = "SELECT * FROM users WHERE id = ?";
    // TODO(#123): revisit connection pooling
    return sql;
}
