package updater

import (
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestUpdateCache(t *testing.T) {
	tmpDir := t.TempDir()
	cacheFile := filepath.Join(tmpDir, "update-cache.json")

	cache := &UpdateCache{
		CacheFile: cacheFile,
	}

	// Test writing and reading cache
	info := UpdateInfo{
		Available:     true,
		LatestVersion: "1.2.3",
		CheckedAt:     time.Now(),
	}

	if err := cache.Write(info); err != nil {
		t.Fatalf("Write() failed: %v", err)
	}

	// Verify cache file exists
	if _, err := os.Stat(cacheFile); err != nil {
		t.Errorf("cache file not created: %v", err)
	}

	// Read back the cache
	readInfo, err := cache.Read()
	if err != nil {
		t.Fatalf("Read() failed: %v", err)
	}

	if readInfo.Available != info.Available {
		t.Errorf("Available = %v, want %v", readInfo.Available, info.Available)
	}

	if readInfo.LatestVersion != info.LatestVersion {
		t.Errorf("LatestVersion = %q, want %q", readInfo.LatestVersion, info.LatestVersion)
	}

	// Check times are close (within 1 second)
	if readInfo.CheckedAt.Sub(info.CheckedAt).Abs() > time.Second {
		t.Errorf("CheckedAt = %v, want %v", readInfo.CheckedAt, info.CheckedAt)
	}
}

func TestUpdateCacheShouldCheck(t *testing.T) {
	tmpDir := t.TempDir()
	cacheFile := filepath.Join(tmpDir, "update-cache.json")

	cache := &UpdateCache{
		CacheFile: cacheFile,
	}

	// No cache file exists - should check
	if !cache.ShouldCheck(24 * time.Hour) {
		t.Error("ShouldCheck() = false for missing cache, want true")
	}

	// Write a recent cache entry
	info := UpdateInfo{
		Available:     true,
		LatestVersion: "1.2.3",
		CheckedAt:     time.Now(),
	}
	if err := cache.Write(info); err != nil {
		t.Fatalf("Write() failed: %v", err)
	}

	// Recent check - should not check again
	if cache.ShouldCheck(24 * time.Hour) {
		t.Error("ShouldCheck() = true for recent cache, want false")
	}

	// Write an old cache entry
	oldInfo := UpdateInfo{
		Available:     true,
		LatestVersion: "1.2.3",
		CheckedAt:     time.Now().Add(-25 * time.Hour),
	}
	if err := cache.Write(oldInfo); err != nil {
		t.Fatalf("Write() failed: %v", err)
	}

	// Old check - should check again
	if !cache.ShouldCheck(24 * time.Hour) {
		t.Error("ShouldCheck() = false for old cache, want true")
	}
}

func TestUpdateCacheReadMissing(t *testing.T) {
	tmpDir := t.TempDir()
	cacheFile := filepath.Join(tmpDir, "nonexistent.json")

	cache := &UpdateCache{
		CacheFile: cacheFile,
	}

	_, err := cache.Read()
	if err == nil {
		t.Error("Read() for missing file returned nil error, want error")
	}
}
