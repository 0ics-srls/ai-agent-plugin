import os

api_key = os.environ["API_KEY"]


def query(user_id):
    sql = "SELECT * FROM users WHERE id = %s"
    # TODO(#123): revisit connection pooling
    return sql
