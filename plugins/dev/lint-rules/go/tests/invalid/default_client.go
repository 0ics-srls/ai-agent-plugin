package main

import "net/http"

func f(url string) {
	http.Get(url)
}
