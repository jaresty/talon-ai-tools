package updater

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
)

// HTTPGitHubClient is a real GitHub API client using HTTP
type HTTPGitHubClient struct {
	BaseURL    string
	HTTPClient *http.Client
}

// NewGitHubClient creates a new GitHub API client
func NewGitHubClient() *HTTPGitHubClient {
	return &HTTPGitHubClient{
		BaseURL:    "https://api.github.com",
		HTTPClient: &http.Client{},
	}
}

// githubRelease represents the JSON structure returned by GitHub API
type githubRelease struct {
	TagName string         `json:"tag_name"`
	Assets  []githubAsset  `json:"assets"`
}

// githubAsset represents an asset in a GitHub release
type githubAsset struct {
	Name               string `json:"name"`
	BrowserDownloadURL string `json:"browser_download_url"`
}

// GetLatestRelease fetches the latest release from GitHub
func (c *HTTPGitHubClient) GetLatestRelease(ctx context.Context, owner, repo string) (*Release, error) {
	url := fmt.Sprintf("%s/repos/%s/%s/releases/latest", c.BaseURL, owner, repo)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/vnd.github+json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch release: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil, fmt.Errorf("no releases found")
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("GitHub API returned status %d", resp.StatusCode)
	}

	var ghRelease githubRelease
	if err := json.NewDecoder(resp.Body).Decode(&ghRelease); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	// Convert to our Release struct
	release := &Release{
		TagName: ghRelease.TagName,
		Assets:  make([]string, len(ghRelease.Assets)),
	}

	for i, asset := range ghRelease.Assets {
		release.Assets[i] = asset.Name
	}

	return release, nil
}

// GetAssetDownloadURL finds the download URL for a specific asset name
func (c *HTTPGitHubClient) GetAssetDownloadURL(ctx context.Context, owner, repo, assetName string) (string, error) {
	url := fmt.Sprintf("%s/repos/%s/%s/releases/latest", c.BaseURL, owner, repo)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Accept", "application/vnd.github+json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to fetch release: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("GitHub API returned status %d", resp.StatusCode)
	}

	var ghRelease githubRelease
	if err := json.NewDecoder(resp.Body).Decode(&ghRelease); err != nil {
		return "", fmt.Errorf("failed to decode response: %w", err)
	}

	// Find the asset by name
	for _, asset := range ghRelease.Assets {
		if asset.Name == assetName {
			return asset.BrowserDownloadURL, nil
		}
	}

	return "", fmt.Errorf("asset %q not found in release", assetName)
}
