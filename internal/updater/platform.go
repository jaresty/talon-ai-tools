package updater

import (
	"fmt"
	"runtime"
)

// GetAssetName returns the asset name for the given OS and architecture
func GetAssetName(goos, goarch string) string {
	return fmt.Sprintf("bar-%s-%s", goos, goarch)
}

// DetectPlatform returns the asset name for the current runtime platform
func DetectPlatform() string {
	return GetAssetName(runtime.GOOS, runtime.GOARCH)
}
