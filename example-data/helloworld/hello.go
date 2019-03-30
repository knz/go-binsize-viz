package main

import "fmt"

var x = struct { x [10000]int }{}

func main() {
	fmt.Println("hello world", x)
}
