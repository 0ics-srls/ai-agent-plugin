package main

import "fmt"

func f() error {
	if err := doThing(); err != nil {
		return fmt.Errorf("do thing: %w", err)
	}
	return nil
}
