package updater

import (
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// BinaryInstaller handles atomic binary replacement with backup
type BinaryInstaller struct {
	BackupDir string
}

// Install atomically replaces the current binary with a new one
func (bi *BinaryInstaller) Install(ctx context.Context, newBinaryPath, currentBinaryPath string) error {
	// Get current binary permissions
	currentInfo, err := os.Stat(currentBinaryPath)
	if err != nil {
		return fmt.Errorf("failed to stat current binary: %w", err)
	}
	currentPerm := currentInfo.Mode().Perm()

	// Create backup of current binary
	backupPath, err := bi.CreateBackup(currentBinaryPath)
	if err != nil {
		return fmt.Errorf("failed to create backup: %w", err)
	}

	// Copy new binary to temp location in same directory as target
	// (ensures same filesystem for atomic rename)
	targetDir := filepath.Dir(currentBinaryPath)
	tempPath := filepath.Join(targetDir, ".bar-update-tmp")

	if err := copyFile(newBinaryPath, tempPath); err != nil {
		return fmt.Errorf("failed to copy new binary: %w", err)
	}
	defer os.Remove(tempPath) // Clean up temp file if we fail

	// Set permissions on new binary to match current
	if err := os.Chmod(tempPath, currentPerm); err != nil {
		return fmt.Errorf("failed to set permissions on new binary: %w", err)
	}

	// Atomic rename (replaces old binary with new one)
	if err := os.Rename(tempPath, currentBinaryPath); err != nil {
		return fmt.Errorf("failed to replace binary: %w", err)
	}

	// Success - backup created at backupPath
	_ = backupPath
	return nil
}

// CreateBackup creates a timestamped backup of the current binary
func (bi *BinaryInstaller) CreateBackup(binaryPath string) (string, error) {
	// Ensure backup directory exists
	if err := os.MkdirAll(bi.BackupDir, 0755); err != nil {
		return "", fmt.Errorf("failed to create backup directory: %w", err)
	}

	// Generate backup filename with timestamp
	timestamp := time.Now().Format("20060102-150405")
	binaryName := filepath.Base(binaryPath)
	backupName := fmt.Sprintf("%s.%s.bak", binaryName, timestamp)
	backupPath := filepath.Join(bi.BackupDir, backupName)

	// Copy current binary to backup location
	if err := copyFile(binaryPath, backupPath); err != nil {
		return "", fmt.Errorf("failed to copy binary to backup: %w", err)
	}

	return backupPath, nil
}

// Rollback restores the most recent backup of the binary
func (bi *BinaryInstaller) Rollback(ctx context.Context, currentBinaryPath string) error {
	// List available backups
	backups, err := bi.ListBackups()
	if err != nil {
		return fmt.Errorf("failed to list backups: %w", err)
	}

	if len(backups) == 0 {
		return fmt.Errorf("no backups available for rollback")
	}

	// Use most recent backup (first in sorted list)
	mostRecentBackup := backups[0]
	backupPath := filepath.Join(bi.BackupDir, mostRecentBackup)

	// Get backup permissions
	backupInfo, err := os.Stat(backupPath)
	if err != nil {
		return fmt.Errorf("failed to stat backup: %w", err)
	}
	backupPerm := backupInfo.Mode().Perm()

	// Copy backup to temp location in same directory as target
	// (ensures same filesystem for atomic rename)
	targetDir := filepath.Dir(currentBinaryPath)
	tempPath := filepath.Join(targetDir, ".bar-rollback-tmp")

	if err := copyFile(backupPath, tempPath); err != nil {
		return fmt.Errorf("failed to copy backup: %w", err)
	}
	defer os.Remove(tempPath) // Clean up temp file if we fail

	// Set permissions on temp file to match backup
	if err := os.Chmod(tempPath, backupPerm); err != nil {
		return fmt.Errorf("failed to set permissions on rollback binary: %w", err)
	}

	// Atomic rename (replaces current binary with backup)
	if err := os.Rename(tempPath, currentBinaryPath); err != nil {
		return fmt.Errorf("failed to replace binary with backup: %w", err)
	}

	return nil
}

// ListBackups returns a list of available backups, sorted by timestamp (most recent first)
func (bi *BinaryInstaller) ListBackups() ([]string, error) {
	// Check if backup directory exists
	if _, err := os.Stat(bi.BackupDir); os.IsNotExist(err) {
		return []string{}, nil
	}

	// Read backup directory
	entries, err := os.ReadDir(bi.BackupDir)
	if err != nil {
		return nil, fmt.Errorf("failed to read backup directory: %w", err)
	}

	// Filter for .bak files
	var backups []string
	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}
		if strings.HasSuffix(entry.Name(), ".bak") {
			backups = append(backups, entry.Name())
		}
	}

	// Sort by name (which includes timestamp) in reverse order (most recent first)
	sort.Sort(sort.Reverse(sort.StringSlice(backups)))

	return backups, nil
}

// copyFile copies a file from src to dst, preserving permissions
func copyFile(src, dst string) error {
	srcFile, err := os.Open(src)
	if err != nil {
		return err
	}
	defer srcFile.Close()

	srcInfo, err := srcFile.Stat()
	if err != nil {
		return err
	}

	dstFile, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer dstFile.Close()

	if _, err := io.Copy(dstFile, srcFile); err != nil {
		return err
	}

	// Preserve permissions
	if err := os.Chmod(dst, srcInfo.Mode().Perm()); err != nil {
		return err
	}

	return nil
}
