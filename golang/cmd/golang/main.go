// Package main wires the Go starter scaffold into an executable.
package main

import (
	"fmt"

	"example.com/golang-scaffold/internal/mathx"
)

func main() {
	fmt.Println(mathx.Add(2, 3))
}
