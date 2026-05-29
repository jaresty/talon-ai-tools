package g

import "testing"

func TestNewConfig_host(t *testing.T) {
	cfg := NewConfig("", 8080)
	if cfg.Host != "localhost" {
		t.Fatalf("got %q, want %q", cfg.Host, "localhost")
	}
}

func TestNewConfig_port(t *testing.T) {
	cfg := NewConfig("localhost", 0)
	if cfg.Port != 8080 {
		t.Fatalf("got %d, want 8080", cfg.Port)
	}
}

func TestNewConfig_valid(t *testing.T) {
	cfg := NewConfig("myhost", 9090)
	if cfg.Host != "myhost" || cfg.Port != 9090 {
		t.Fatal("explicit values not preserved")
	}
}
