package barcli

import "fmt"

// CLIError describes a structured error emitted by the portable CLI.
type CLIError struct {
	Type         string              `json:"type"`
	Message      string              `json:"message"`
	Unrecognized []string            `json:"unrecognized,omitempty"`
	Recognized   map[string][]string `json:"recognized"`
}

func (e *CLIError) Error() string {
	if e == nil {
		return ""
	}
	return e.Message
}

func newError(errType, message string) *CLIError {
	return &CLIError{Type: errType, Message: message}
}

func errorf(errType, format string, args ...any) *CLIError {
	return &CLIError{Type: errType, Message: fmt.Sprintf(format, args...)}
}
