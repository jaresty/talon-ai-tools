package barcli

import (
	"io"
	"strings"
	"testing"
	"time"
)

// A1: timeout fires when pipe stalls
func TestStdinTimeoutExpiresOnStall(t *testing.T) {
	r, _ := io.Pipe() // write end never written — simulates stall
	_, err := readStdinWithTimeout(r, 50*time.Millisecond)
	if err == nil {
		t.Fatal("expected timeout error, got nil")
	}
	if !strings.Contains(err.Error(), "timed out") {
		t.Fatalf("expected 'timed out' in error, got: %v", err)
	}
}

// A1: exit message contains usage suggestion
func TestStdinTimeoutErrorMessageSuggestion(t *testing.T) {
	r, _ := io.Pipe()
	_, err := readStdinWithTimeout(r, 50*time.Millisecond)
	if err == nil {
		t.Fatal("expected timeout error, got nil")
	}
	if !strings.Contains(err.Error(), "--subject") {
		t.Fatalf("expected '--subject' suggestion in error, got: %v", err)
	}
}

// A2: no false positive — data arrives before timeout
func TestStdinTimeoutNoFalsePositiveWhenDataArrives(t *testing.T) {
	r, w := io.Pipe()
	go func() {
		w.Write([]byte("hello world")) //nolint:errcheck
		w.Close()
	}()
	data, err := readStdinWithTimeout(r, 2*time.Second)
	if err != nil {
		t.Fatalf("expected no error when data arrives in time, got: %v", err)
	}
	if string(data) != "hello world" {
		t.Fatalf("expected 'hello world', got: %q", string(data))
	}
}

// A3: timeout is configurable via env var
func TestStdinTimeoutDurationFromEnv(t *testing.T) {
	t.Setenv("BAR_STDIN_TIMEOUT", "100ms")
	dur := stdinTimeoutDuration()
	if dur != 100*time.Millisecond {
		t.Fatalf("expected 100ms from env, got: %v", dur)
	}
}

// A3: default timeout is 5s when env var absent
func TestStdinTimeoutDurationDefault(t *testing.T) {
	t.Setenv("BAR_STDIN_TIMEOUT", "")
	dur := stdinTimeoutDuration()
	if dur != 5*time.Second {
		t.Fatalf("expected default 5s, got: %v", dur)
	}
}
