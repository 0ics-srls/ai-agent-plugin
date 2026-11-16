api_key = "sk-live-abc123def456ghi789"


def query(user_id):
    sql = "SELECT * FROM users WHERE id = " + user_id
    # TODO fix this later
    return sql
