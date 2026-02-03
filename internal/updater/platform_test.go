package updater

import (
	"testing"
)

func TestPlatformDetection(t *testing.T) {
	tests := []struct {
		name     string
		goos     string
		goarch   string
		expected string
	}{
		{
			name:     "darwin amd64",
			goos:     "darwin",
			goarch:   "amd64",
			expected: "bar-darwin-amd64",
		},
		{
			name:     "darwin arm64",
			goos:     "darwin",
			goarch:   "arm64",
			expected: "bar-darwin-arm64",
		},
		{
			name:     "linux amd64",
			goos:     "linux",
			goarch:   "amd64",
			expected: "bar-linux-amd64",
		},
		{
			name:     "linux arm64",
			goos:     "linux",
			goarch:   "arm64",
			expected: "bar-linux-arm64",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assetName := GetAssetName(tt.goos, tt.goarch)
			if assetName != tt.expected {
				t.Errorf("GetAssetName(%q, %q) = %q, want %q", tt.goos, tt.goarch, assetName, tt.expected)
			}
		})
	}
}

func TestDetectPlatform(t *testing.T) {
	// This test validates that DetectPlatform returns a valid asset name
	// It should match the current runtime platform
	assetName := DetectPlatform()

	// Asset name should be non-empty
	if assetName == "" {
		t.Error("DetectPlatform() returned empty string")
	}

	// Asset name should match expected format: bar-{os}-{arch}
	// Valid combinations: darwin/linux × amd64/arm64
	validAssets := map[string]bool{
		"bar-darwin-amd64": true,
		"bar-darwin-arm64": true,
		"bar-linux-amd64":  true,
		"bar-linux-arm64":  true,
	}

	if !validAssets[assetName] {
		t.Errorf("DetectPlatform() = %q, want one of [bar-darwin-amd64, bar-darwin-arm64, bar-linux-amd64, bar-linux-arm64]", assetName)
	}
}
