package main

import "log/slog"

func f() {
	slog.Info("event", "key", "value")
}
