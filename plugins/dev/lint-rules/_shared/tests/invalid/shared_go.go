package config

var apiKey = "sk-live-abc123def456ghi789"

func query(userId string) string {
	sql := "SELECT * FROM users WHERE id = " + userId
	// TODO fix this later
	return sql
}
