package updater

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// UpdateInfo stores the result of an update check
type UpdateInfo struct {
	Available     bool      `json:"available"`
	LatestVersion string    `json:"latest_version"`
	CheckedAt     time.Time `json:"checked_at"`
}

// UpdateCache manages cached update check results
type UpdateCache struct {
	CacheFile string
}

// NewUpdateCache creates a new update cache with default location
func NewUpdateCache() *UpdateCache {
	cacheDir := os.Getenv("BAR_CONFIG_DIR")
	if cacheDir == "" {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			// Fallback to temp directory if home dir not available
			cacheDir = os.TempDir()
		} else {
			cacheDir = filepath.Join(homeDir, ".config", "bar")
		}
	}

	return &UpdateCache{
		CacheFile: filepath.Join(cacheDir, "update-cache.json"),
	}
}

// Read reads the cached update info
func (c *UpdateCache) Read() (UpdateInfo, error) {
	data, err := os.ReadFile(c.CacheFile)
	if err != nil {
		return UpdateInfo{}, err
	}

	var info UpdateInfo
	if err := json.Unmarshal(data, &info); err != nil {
		return UpdateInfo{}, err
	}

	return info, nil
}

// Write writes update info to the cache
func (c *UpdateCache) Write(info UpdateInfo) error {
	// Ensure cache directory exists
	cacheDir := filepath.Dir(c.CacheFile)
	if err := os.MkdirAll(cacheDir, 0755); err != nil {
		return fmt.Errorf("failed to create cache directory: %w", err)
	}

	data, err := json.Marshal(info)
	if err != nil {
		return err
	}

	return os.WriteFile(c.CacheFile, data, 0644)
}

// ShouldCheck returns true if an update check should be performed
func (c *UpdateCache) ShouldCheck(interval time.Duration) bool {
	info, err := c.Read()
	if err != nil {
		// No cache or read error - should check
		return true
	}

	// Check if enough time has passed since last check
	return time.Since(info.CheckedAt) >= interval
}
