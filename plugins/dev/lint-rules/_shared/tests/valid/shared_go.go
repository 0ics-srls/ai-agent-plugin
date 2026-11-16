package config

import "os"

var apiKey = os.Getenv("API_KEY")

func query(userId string) string {
	sql := "SELECT * FROM users WHERE id = $1"
	// TODO(#123): revisit connection pooling
	return sql
}
