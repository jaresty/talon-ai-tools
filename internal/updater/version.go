package updater

import (
	"fmt"
	"strconv"
	"strings"
)

// ParseVersion parses a semantic version string and returns major, minor, patch components.
// It handles versions with or without the "v" prefix.
func ParseVersion(version string) (major, minor, patch int, err error) {
	// Remove "v" prefix if present
	version = strings.TrimPrefix(version, "v")

	parts := strings.Split(version, ".")
	if len(parts) != 3 {
		return 0, 0, 0, fmt.Errorf("invalid version format: expected major.minor.patch, got %q", version)
	}

	major, err = strconv.Atoi(parts[0])
	if err != nil {
		return 0, 0, 0, fmt.Errorf("invalid major version: %v", err)
	}

	minor, err = strconv.Atoi(parts[1])
	if err != nil {
		return 0, 0, 0, fmt.Errorf("invalid minor version: %v", err)
	}

	patch, err = strconv.Atoi(parts[2])
	if err != nil {
		return 0, 0, 0, fmt.Errorf("invalid patch version: %v", err)
	}

	return major, minor, patch, nil
}

// CompareVersions compares two semantic version strings.
// Returns -1 if current < latest, 0 if equal, 1 if current > latest.
func CompareVersions(current, latest string) int {
	currentMajor, currentMinor, currentPatch, err := ParseVersion(current)
	if err != nil {
		return 0
	}

	latestMajor, latestMinor, latestPatch, err := ParseVersion(latest)
	if err != nil {
		return 0
	}

	// Compare major version
	if currentMajor < latestMajor {
		return -1
	}
	if currentMajor > latestMajor {
		return 1
	}

	// Major versions equal, compare minor
	if currentMinor < latestMinor {
		return -1
	}
	if currentMinor > latestMinor {
		return 1
	}

	// Major and minor equal, compare patch
	if currentPatch < latestPatch {
		return -1
	}
	if currentPatch > latestPatch {
		return 1
	}

	// All components equal
	return 0
}
