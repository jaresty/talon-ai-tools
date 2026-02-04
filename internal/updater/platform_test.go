package updater

import (
	"testing"
)

func TestPlatformDetection(t *testing.T) {
	tests := []struct {
		name     string
		goos     string
		goarch   string
		version  string
		expected string
	}{
		{
			name:     "darwin amd64",
			goos:     "darwin",
			goarch:   "amd64",
			version:  "0.3.0",
			expected: "bar_0.3.0_darwin_amd64.tar.gz",
		},
		{
			name:     "darwin arm64",
			goos:     "darwin",
			goarch:   "arm64",
			version:  "0.3.0",
			expected: "bar_0.3.0_darwin_arm64.tar.gz",
		},
		{
			name:     "linux amd64",
			goos:     "linux",
			goarch:   "amd64",
			version:  "1.2.3",
			expected: "bar_1.2.3_linux_amd64.tar.gz",
		},
		{
			name:     "linux arm64",
			goos:     "linux",
			goarch:   "arm64",
			version:  "1.2.3",
			expected: "bar_1.2.3_linux_arm64.tar.gz",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assetName := GetAssetName(tt.goos, tt.goarch, tt.version)
			if assetName != tt.expected {
				t.Errorf("GetAssetName(%q, %q, %q) = %q, want %q", tt.goos, tt.goarch, tt.version, assetName, tt.expected)
			}
		})
	}
}

func TestDetectPlatform(t *testing.T) {
	// This test validates that DetectPlatform returns a valid platform suffix
	// It should match the current runtime platform
	platformSuffix := DetectPlatform()

	// Platform suffix should be non-empty
	if platformSuffix == "" {
		t.Error("DetectPlatform() returned empty string")
	}

	// Platform suffix should match expected format: {os}_{arch}
	// Valid combinations: darwin/linux × amd64/arm64
	validPlatforms := map[string]bool{
		"darwin_amd64": true,
		"darwin_arm64": true,
		"linux_amd64":  true,
		"linux_arm64":  true,
	}

	if !validPlatforms[platformSuffix] {
		t.Errorf("DetectPlatform() = %q, want one of [darwin_amd64, darwin_arm64, linux_amd64, linux_arm64]", platformSuffix)
	}
}
