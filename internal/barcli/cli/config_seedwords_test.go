package cli

import "testing"

// TestParseSeedWordsFlag specifies that `bar build --seed-words N` parses into
// Config.SeedWords, supporting both the space and = forms. Default is 0 (off).
func TestParseSeedWordsFlag(t *testing.T) {
	t.Run("space form", func(t *testing.T) {
		cfg, err := Parse([]string{"build", "make", "--seed-words", "3"})
		if err != nil {
			t.Fatalf("parse: %v", err)
		}
		if cfg.SeedWords != 3 {
			t.Fatalf("expected SeedWords=3, got %d", cfg.SeedWords)
		}
	})

	t.Run("equals form", func(t *testing.T) {
		cfg, err := Parse([]string{"build", "make", "--seed-words=2"})
		if err != nil {
			t.Fatalf("parse: %v", err)
		}
		if cfg.SeedWords != 2 {
			t.Fatalf("expected SeedWords=2, got %d", cfg.SeedWords)
		}
	})

	t.Run("default off", func(t *testing.T) {
		cfg, err := Parse([]string{"build", "make"})
		if err != nil {
			t.Fatalf("parse: %v", err)
		}
		if cfg.SeedWords != 0 {
			t.Fatalf("expected default SeedWords=0, got %d", cfg.SeedWords)
		}
	})

	t.Run("non-integer errors", func(t *testing.T) {
		if _, err := Parse([]string{"build", "--seed-words", "many"}); err == nil {
			t.Fatal("expected error for non-integer --seed-words value")
		}
	})
}
