package c

import "fmt"

func formatDate(year, month, day int) string {
	return fmt.Sprintf("%d/%02d/%02d", year, month, day)
}

func formatTime(hour, min int) string {
	return fmt.Sprintf("%d:%02d", hour, min)
}
