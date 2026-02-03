package updater

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
)

func TestArtifactDownload(t *testing.T) {
	// Create a test server that serves a fake binary
	testContent := []byte("fake-bar-binary-content-v1.2.3")
	expectedChecksum := sha256.Sum256(testContent)
	expectedChecksumHex := hex.EncodeToString(expectedChecksum[:])

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/download/bar-darwin-amd64" {
			w.WriteHeader(http.StatusOK)
			w.Write(testContent)
			return
		}
		http.NotFound(w, r)
	}))
	defer server.Close()

	tests := []struct {
		name          string
		url           string
		wantErr       bool
		verifyContent bool
	}{
		{
			name:          "successful download",
			url:           server.URL + "/download/bar-darwin-amd64",
			wantErr:       false,
			verifyContent: true,
		},
		{
			name:    "not found",
			url:     server.URL + "/download/nonexistent",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tmpDir := t.TempDir()
			destPath := filepath.Join(tmpDir, "bar")

			downloader := &ArtifactDownloader{
				Client: server.Client(),
			}

			ctx := context.Background()
			err := downloader.Download(ctx, tt.url, destPath)

			if tt.wantErr {
				if err == nil {
					t.Errorf("Download() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("Download() unexpected error: %v", err)
				return
			}

			// Verify file exists
			if _, err := os.Stat(destPath); os.IsNotExist(err) {
				t.Errorf("Download() did not create file at %s", destPath)
				return
			}

			// Verify content
			if tt.verifyContent {
				downloaded, err := os.ReadFile(destPath)
				if err != nil {
					t.Errorf("failed to read downloaded file: %v", err)
					return
				}

				downloadedChecksum := sha256.Sum256(downloaded)
				if hex.EncodeToString(downloadedChecksum[:]) != expectedChecksumHex {
					t.Errorf("downloaded content checksum mismatch: got %x, want %s",
						downloadedChecksum, expectedChecksumHex)
				}
			}
		})
	}
}

func TestChecksumVerification(t *testing.T) {
	tests := []struct {
		name         string
		content      []byte
		expectedHash string
		wantErr      bool
	}{
		{
			name:         "valid checksum",
			content:      []byte("test-content"),
			expectedHash: "0a3666a0710c08aa6d0de92ce72beeb5b93124cce1bf3701c9d6cdeb543cb73e",
			wantErr:      false,
		},
		{
			name:         "invalid checksum",
			content:      []byte("test-content"),
			expectedHash: "wronghash123",
			wantErr:      true,
		},
		{
			name:         "empty file",
			content:      []byte(""),
			expectedHash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
			wantErr:      false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tmpDir := t.TempDir()
			filePath := filepath.Join(tmpDir, "test-file")

			// Write test content
			if err := os.WriteFile(filePath, tt.content, 0644); err != nil {
				t.Fatalf("failed to write test file: %v", err)
			}

			verifier := &ChecksumVerifier{}
			err := verifier.VerifySHA256(filePath, tt.expectedHash)

			if tt.wantErr {
				if err == nil {
					t.Errorf("VerifySHA256() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("VerifySHA256() unexpected error: %v", err)
			}
		})
	}
}

func TestComputeSHA256(t *testing.T) {
	tests := []struct {
		name         string
		content      []byte
		expectedHash string
	}{
		{
			name:         "known content",
			content:      []byte("hello world"),
			expectedHash: "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
		},
		{
			name:         "empty content",
			content:      []byte(""),
			expectedHash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tmpDir := t.TempDir()
			filePath := filepath.Join(tmpDir, "test-file")

			if err := os.WriteFile(filePath, tt.content, 0644); err != nil {
				t.Fatalf("failed to write test file: %v", err)
			}

			verifier := &ChecksumVerifier{}
			hash, err := verifier.ComputeSHA256(filePath)
			if err != nil {
				t.Errorf("ComputeSHA256() unexpected error: %v", err)
				return
			}

			if hash != tt.expectedHash {
				t.Errorf("ComputeSHA256() = %s, want %s", hash, tt.expectedHash)
			}
		})
	}
}

func TestParseChecksums(t *testing.T) {
	tests := []struct {
		name      string
		content   string
		wantMap   map[string]string
		wantErr   bool
	}{
		{
			name: "valid checksums file",
			content: `abc123def456  bar-darwin-amd64
789ghi012jkl  bar-linux-amd64
mno345pqr678  bar-darwin-arm64`,
			wantMap: map[string]string{
				"bar-darwin-amd64": "abc123def456",
				"bar-linux-amd64":  "789ghi012jkl",
				"bar-darwin-arm64": "mno345pqr678",
			},
			wantErr: false,
		},
		{
			name: "single entry",
			content: "a1b2c3d4e5f6  bar-darwin-amd64",
			wantMap: map[string]string{
				"bar-darwin-amd64": "a1b2c3d4e5f6",
			},
			wantErr: false,
		},
		{
			name:    "empty content",
			content: "",
			wantMap: map[string]string{},
			wantErr: false,
		},
		{
			name: "with empty lines",
			content: `abc123def456  bar-darwin-amd64

789ghi012jkl  bar-linux-amd64`,
			wantMap: map[string]string{
				"bar-darwin-amd64": "abc123def456",
				"bar-linux-amd64":  "789ghi012jkl",
			},
			wantErr: false,
		},
		{
			name:    "invalid format - single space",
			content: "abc123def456 bar-darwin-amd64",
			wantErr: true,
		},
		{
			name:    "invalid format - no separator",
			content: "abc123def456bar-darwin-amd64",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseChecksums(tt.content)

			if tt.wantErr {
				if err == nil {
					t.Errorf("ParseChecksums() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("ParseChecksums() unexpected error: %v", err)
				return
			}

			if len(got) != len(tt.wantMap) {
				t.Errorf("ParseChecksums() returned %d entries, want %d", len(got), len(tt.wantMap))
				return
			}

			for filename, expectedHash := range tt.wantMap {
				actualHash, ok := got[filename]
				if !ok {
					t.Errorf("ParseChecksums() missing entry for %q", filename)
					continue
				}
				if actualHash != expectedHash {
					t.Errorf("ParseChecksums() for %q = %q, want %q", filename, actualHash, expectedHash)
				}
			}
		})
	}
}
