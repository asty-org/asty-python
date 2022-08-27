package main

func decorate(s string) string {
	return "<" + s + ">"
}

func main() {
	print(
		decorate("hello") + " " +
		decorate("world"))
}
