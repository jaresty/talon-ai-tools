package updater

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
)

// ArtifactDownloader handles downloading release artifacts
type ArtifactDownloader struct {
	Client *http.Client
}

// Download retrieves an artifact from the given URL and saves it to destPath
func (ad *ArtifactDownloader) Download(ctx context.Context, url, destPath string) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	resp, err := ad.Client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to download artifact: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("download failed with status %d", resp.StatusCode)
	}

	// Create destination file
	out, err := os.Create(destPath)
	if err != nil {
		return fmt.Errorf("failed to create destination file: %w", err)
	}
	defer out.Close()

	// Copy response body to file
	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return fmt.Errorf("failed to write artifact: %w", err)
	}

	return nil
}

// ChecksumVerifier handles SHA256 checksum verification
type ChecksumVerifier struct{}

// ComputeSHA256 calculates the SHA256 hash of a file
func (cv *ChecksumVerifier) ComputeSHA256(filePath string) (string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", fmt.Errorf("failed to open file: %w", err)
	}
	defer f.Close()

	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", fmt.Errorf("failed to compute hash: %w", err)
	}

	return hex.EncodeToString(h.Sum(nil)), nil
}

// VerifySHA256 checks if a file's SHA256 hash matches the expected value
func (cv *ChecksumVerifier) VerifySHA256(filePath, expectedHash string) error {
	actualHash, err := cv.ComputeSHA256(filePath)
	if err != nil {
		return err
	}

	if actualHash != expectedHash {
		return fmt.Errorf("checksum mismatch: got %s, want %s", actualHash, expectedHash)
	}

	return nil
}
