package barcli

import (
	"fmt"
	"io"
	"os"
	"time"
)

// readStdinWithTimeout reads all data from r, returning a timeout error if no
// data arrives within dur.
func readStdinWithTimeout(r io.Reader, dur time.Duration) ([]byte, error) {
	type result struct {
		data []byte
		err  error
	}
	ch := make(chan result, 1)
	go func() {
		data, err := io.ReadAll(r)
		ch <- result{data, err}
	}()
	select {
	case res := <-ch:
		return res.data, res.err
	case <-time.After(dur):
		return nil, fmt.Errorf("stdin timed out waiting for input: use --subject \"text\" to pass content directly, or pipe data before invoking bar")
	}
}

// stdinTimeoutDuration returns the configured stdin timeout duration.
// Reads BAR_STDIN_TIMEOUT env var (e.g. "5s", "500ms"); defaults to 5s.
func stdinTimeoutDuration() time.Duration {
	if v := os.Getenv("BAR_STDIN_TIMEOUT"); v != "" {
		if d, err := time.ParseDuration(v); err == nil {
			return d
		}
	}
	return 5 * time.Second
}
