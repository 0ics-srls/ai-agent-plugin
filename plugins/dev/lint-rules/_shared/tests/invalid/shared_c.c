#include <stdio.h>

const char* api_key = "sk-live-abc123def456ghi789";

void query(char* sql, size_t size, const char* user_id) {
  (void)snprintf(sql, size, "SELECT * FROM users WHERE id = '%s'", user_id);
  // TODO fix this later
}
