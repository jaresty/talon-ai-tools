package updater

import (
	"fmt"
	"runtime"
)

// GetAssetName returns the asset name for the given OS, architecture, and version
// Format matches the release workflow: bar_VERSION_OS_ARCH.tar.gz
func GetAssetName(goos, goarch, version string) string {
	return fmt.Sprintf("bar_%s_%s_%s.tar.gz", version, goos, goarch)
}

// DetectPlatform returns the asset name pattern for the current runtime platform
// For compatibility with older code that doesn't pass version
func DetectPlatform() string {
	// Return platform suffix that can be used for matching
	return fmt.Sprintf("%s_%s", runtime.GOOS, runtime.GOARCH)
}
