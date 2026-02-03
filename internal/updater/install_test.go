package updater

import (
	"context"
	"os"
	"path/filepath"
	"testing"
)

func TestBinaryInstallation(t *testing.T) {
	tests := []struct {
		name            string
		currentContent  string
		newContent      string
		currentPerm     os.FileMode
		wantErr         bool
		verifyBackup    bool
		verifyNewBinary bool
	}{
		{
			name:            "successful installation",
			currentContent:  "old-binary-v1.0.0",
			newContent:      "new-binary-v1.1.0",
			currentPerm:     0755,
			wantErr:         false,
			verifyBackup:    true,
			verifyNewBinary: true,
		},
		{
			name:            "preserve execute permissions",
			currentContent:  "old-binary",
			newContent:      "new-binary",
			currentPerm:     0700,
			wantErr:         false,
			verifyBackup:    true,
			verifyNewBinary: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tmpDir := t.TempDir()
			currentBinaryPath := filepath.Join(tmpDir, "bar")
			newBinaryPath := filepath.Join(tmpDir, "bar-new")
			backupDir := filepath.Join(tmpDir, "backups")

			// Create current binary
			if err := os.WriteFile(currentBinaryPath, []byte(tt.currentContent), tt.currentPerm); err != nil {
				t.Fatalf("failed to create current binary: %v", err)
			}

			// Create new binary
			if err := os.WriteFile(newBinaryPath, []byte(tt.newContent), 0644); err != nil {
				t.Fatalf("failed to create new binary: %v", err)
			}

			installer := &BinaryInstaller{
				BackupDir: backupDir,
			}

			ctx := context.Background()
			err := installer.Install(ctx, newBinaryPath, currentBinaryPath)

			if tt.wantErr {
				if err == nil {
					t.Errorf("Install() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("Install() unexpected error: %v", err)
				return
			}

			// Verify new binary is in place
			if tt.verifyNewBinary {
				content, err := os.ReadFile(currentBinaryPath)
				if err != nil {
					t.Errorf("failed to read installed binary: %v", err)
					return
				}
				if string(content) != tt.newContent {
					t.Errorf("installed binary content = %q, want %q", string(content), tt.newContent)
				}

				// Verify permissions preserved
				info, err := os.Stat(currentBinaryPath)
				if err != nil {
					t.Errorf("failed to stat installed binary: %v", err)
					return
				}
				if info.Mode().Perm() != tt.currentPerm {
					t.Errorf("installed binary permissions = %o, want %o", info.Mode().Perm(), tt.currentPerm)
				}
			}

			// Verify backup was created
			if tt.verifyBackup {
				backups, err := os.ReadDir(backupDir)
				if err != nil {
					t.Errorf("failed to read backup dir: %v", err)
					return
				}
				if len(backups) == 0 {
					t.Errorf("no backup created")
					return
				}

				// Verify backup content matches old binary
				backupPath := filepath.Join(backupDir, backups[0].Name())
				backupContent, err := os.ReadFile(backupPath)
				if err != nil {
					t.Errorf("failed to read backup: %v", err)
					return
				}
				if string(backupContent) != tt.currentContent {
					t.Errorf("backup content = %q, want %q", string(backupContent), tt.currentContent)
				}
			}
		})
	}
}

func TestBinaryInstallationBackupCreation(t *testing.T) {
	tmpDir := t.TempDir()
	currentBinaryPath := filepath.Join(tmpDir, "bar")
	backupDir := filepath.Join(tmpDir, "backups")

	// Create current binary
	originalContent := "original-binary-v1.0.0"
	if err := os.WriteFile(currentBinaryPath, []byte(originalContent), 0755); err != nil {
		t.Fatalf("failed to create current binary: %v", err)
	}

	installer := &BinaryInstaller{
		BackupDir: backupDir,
	}

	backupPath, err := installer.CreateBackup(currentBinaryPath)
	if err != nil {
		t.Fatalf("CreateBackup() unexpected error: %v", err)
	}

	// Verify backup exists
	if _, err := os.Stat(backupPath); os.IsNotExist(err) {
		t.Errorf("backup file not created at %s", backupPath)
	}

	// Verify backup content
	backupContent, err := os.ReadFile(backupPath)
	if err != nil {
		t.Fatalf("failed to read backup: %v", err)
	}
	if string(backupContent) != originalContent {
		t.Errorf("backup content = %q, want %q", string(backupContent), originalContent)
	}
}
