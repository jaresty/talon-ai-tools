package updater

import (
	"context"
	"os"
	"path/filepath"
	"testing"
)

func TestRollback(t *testing.T) {
	tests := []struct {
		name            string
		currentContent  string
		backupContent   string
		currentPerm     os.FileMode
		wantErr         bool
		verifyRestored  bool
	}{
		{
			name:           "successful rollback",
			currentContent: "new-binary-v1.1.0",
			backupContent:  "old-binary-v1.0.0",
			currentPerm:    0755,
			wantErr:        false,
			verifyRestored: true,
		},
		{
			name:           "rollback preserves permissions",
			currentContent: "new-binary",
			backupContent:  "old-binary",
			currentPerm:    0700,
			wantErr:        false,
			verifyRestored: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tmpDir := t.TempDir()
			currentBinaryPath := filepath.Join(tmpDir, "bar")
			backupDir := filepath.Join(tmpDir, "backups")

			// Create current binary (the "new" version we want to roll back from)
			if err := os.WriteFile(currentBinaryPath, []byte(tt.currentContent), tt.currentPerm); err != nil {
				t.Fatalf("failed to create current binary: %v", err)
			}

			// Create backup directory and backup file
			if err := os.MkdirAll(backupDir, 0755); err != nil {
				t.Fatalf("failed to create backup directory: %v", err)
			}

			backupName := "bar.20240101-120000.bak"
			backupPath := filepath.Join(backupDir, backupName)
			if err := os.WriteFile(backupPath, []byte(tt.backupContent), tt.currentPerm); err != nil {
				t.Fatalf("failed to create backup file: %v", err)
			}

			installer := &BinaryInstaller{
				BackupDir: backupDir,
			}

			ctx := context.Background()
			err := installer.Rollback(ctx, currentBinaryPath)

			if tt.wantErr {
				if err == nil {
					t.Errorf("Rollback() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("Rollback() unexpected error: %v", err)
				return
			}

			// Verify rollback restored the backup content
			if tt.verifyRestored {
				content, err := os.ReadFile(currentBinaryPath)
				if err != nil {
					t.Errorf("failed to read restored binary: %v", err)
					return
				}
				if string(content) != tt.backupContent {
					t.Errorf("restored binary content = %q, want %q", string(content), tt.backupContent)
				}

				// Verify permissions preserved
				info, err := os.Stat(currentBinaryPath)
				if err != nil {
					t.Errorf("failed to stat restored binary: %v", err)
					return
				}
				if info.Mode().Perm() != tt.currentPerm {
					t.Errorf("restored binary permissions = %o, want %o", info.Mode().Perm(), tt.currentPerm)
				}
			}
		})
	}
}

func TestRollbackNoBackupsAvailable(t *testing.T) {
	tmpDir := t.TempDir()
	currentBinaryPath := filepath.Join(tmpDir, "bar")
	backupDir := filepath.Join(tmpDir, "backups")

	// Create current binary
	if err := os.WriteFile(currentBinaryPath, []byte("current-binary"), 0755); err != nil {
		t.Fatalf("failed to create current binary: %v", err)
	}

	installer := &BinaryInstaller{
		BackupDir: backupDir,
	}

	ctx := context.Background()
	err := installer.Rollback(ctx, currentBinaryPath)

	// Should error when no backups available
	if err == nil {
		t.Errorf("Rollback() expected error when no backups available, got nil")
	}
}

func TestListBackups(t *testing.T) {
	tmpDir := t.TempDir()
	backupDir := filepath.Join(tmpDir, "backups")

	// Create backup directory with multiple backups
	if err := os.MkdirAll(backupDir, 0755); err != nil {
		t.Fatalf("failed to create backup directory: %v", err)
	}

	// Create backups in time order
	backupFiles := []string{
		"bar.20240101-120000.bak",
		"bar.20240102-120000.bak",
		"bar.20240103-120000.bak", // Most recent
	}

	for _, name := range backupFiles {
		path := filepath.Join(backupDir, name)
		if err := os.WriteFile(path, []byte("backup-content"), 0644); err != nil {
			t.Fatalf("failed to create backup file: %v", err)
		}
	}

	installer := &BinaryInstaller{
		BackupDir: backupDir,
	}

	backups, err := installer.ListBackups()
	if err != nil {
		t.Fatalf("ListBackups() unexpected error: %v", err)
	}

	if len(backups) != 3 {
		t.Errorf("ListBackups() returned %d backups, want 3", len(backups))
	}

	// Should be sorted with most recent first
	if len(backups) > 0 && backups[0] != backupFiles[2] {
		t.Errorf("ListBackups() most recent backup = %s, want %s", backups[0], backupFiles[2])
	}
}
