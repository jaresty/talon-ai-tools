package updater

import (
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
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
