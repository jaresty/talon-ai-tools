package updater

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitHubAPIClient(t *testing.T) {
	tests := []struct {
		name          string
		owner         string
		repo          string
		mockResponse  interface{}
		mockStatus    int
		wantErr       bool
		wantTagName   string
		wantAssetName string
	}{
		{
			name:  "successful release fetch",
			owner: "talonvoice",
			repo:  "talon-ai-tools",
			mockResponse: map[string]interface{}{
				"tag_name": "v1.2.3",
				"assets": []map[string]interface{}{
					{
						"name":                 "bar-darwin-amd64",
						"browser_download_url": "https://github.com/talonvoice/talon-ai-tools/releases/download/v1.2.3/bar-darwin-amd64",
					},
					{
						"name":                 "bar-linux-amd64",
						"browser_download_url": "https://github.com/talonvoice/talon-ai-tools/releases/download/v1.2.3/bar-linux-amd64",
					},
				},
			},
			mockStatus:    http.StatusOK,
			wantErr:       false,
			wantTagName:   "v1.2.3",
			wantAssetName: "bar-darwin-amd64",
		},
		{
			name:         "no releases",
			owner:        "talonvoice",
			repo:         "talon-ai-tools",
			mockResponse: map[string]interface{}{"message": "Not Found"},
			mockStatus:   http.StatusNotFound,
			wantErr:      true,
		},
		{
			name:  "release with no assets",
			owner: "talonvoice",
			repo:  "talon-ai-tools",
			mockResponse: map[string]interface{}{
				"tag_name": "v1.0.0",
				"assets":   []map[string]interface{}{},
			},
			mockStatus:  http.StatusOK,
			wantErr:     false,
			wantTagName: "v1.0.0",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				// Verify the request is going to the right endpoint
				expectedPath := "/repos/" + tt.owner + "/" + tt.repo + "/releases/latest"
				if r.URL.Path != expectedPath {
					t.Errorf("unexpected request path: got %s, want %s", r.URL.Path, expectedPath)
				}

				w.WriteHeader(tt.mockStatus)
				json.NewEncoder(w).Encode(tt.mockResponse)
			}))
			defer server.Close()

			client := &HTTPGitHubClient{
				BaseURL:    server.URL,
				HTTPClient: server.Client(),
			}

			ctx := context.Background()
			release, err := client.GetLatestRelease(ctx, tt.owner, tt.repo)

			if tt.wantErr {
				if err == nil {
					t.Errorf("GetLatestRelease() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("GetLatestRelease() unexpected error: %v", err)
				return
			}

			if release == nil {
				t.Errorf("GetLatestRelease() returned nil release")
				return
			}

			if release.TagName != tt.wantTagName {
				t.Errorf("GetLatestRelease() TagName = %s, want %s", release.TagName, tt.wantTagName)
			}

			if tt.wantAssetName != "" {
				found := false
				for _, asset := range release.Assets {
					if asset == tt.wantAssetName {
						found = true
						break
					}
				}
				if !found {
					t.Errorf("GetLatestRelease() missing expected asset %s in %v", tt.wantAssetName, release.Assets)
				}
			}
		})
	}
}

func TestGitHubAPIClientAssetURLResolution(t *testing.T) {
	mockResponse := map[string]interface{}{
		"tag_name": "v2.0.0",
		"assets": []map[string]interface{}{
			{
				"name":                 "bar-darwin-amd64",
				"browser_download_url": "https://example.com/download/bar-darwin-amd64",
			},
			{
				"name":                 "bar-darwin-arm64",
				"browser_download_url": "https://example.com/download/bar-darwin-arm64",
			},
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(mockResponse)
	}))
	defer server.Close()

	client := &HTTPGitHubClient{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	}

	ctx := context.Background()
	url, err := client.GetAssetDownloadURL(ctx, "owner", "repo", "bar-darwin-arm64")
	if err != nil {
		t.Fatalf("GetAssetDownloadURL() unexpected error: %v", err)
	}

	expectedURL := "https://example.com/download/bar-darwin-arm64"
	if url != expectedURL {
		t.Errorf("GetAssetDownloadURL() = %s, want %s", url, expectedURL)
	}
}

func TestGitHubAPIClientAssetNotFound(t *testing.T) {
	mockResponse := map[string]interface{}{
		"tag_name": "v2.0.0",
		"assets": []map[string]interface{}{
			{
				"name":                 "bar-linux-amd64",
				"browser_download_url": "https://example.com/download/bar-linux-amd64",
			},
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(mockResponse)
	}))
	defer server.Close()

	client := &HTTPGitHubClient{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	}

	ctx := context.Background()
	_, err := client.GetAssetDownloadURL(ctx, "owner", "repo", "bar-windows-amd64")
	if err == nil {
		t.Errorf("GetAssetDownloadURL() expected error for missing asset, got nil")
	}
}

func TestGetAssetDownloadURLSendsTokenWhenEnvSet(t *testing.T) {
	var gotAuth string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth = r.Header.Get("Authorization")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"tag_name": "v1.0.0",
			"assets": []map[string]interface{}{
				{"name": "bar-darwin-arm64", "browser_download_url": "https://example.com/bar-darwin-arm64"},
			},
		})
	}))
	defer server.Close()

	t.Setenv("GITHUB_TOKEN", "test-token-xyz")
	client := NewGitHubClient()
	client.BaseURL = server.URL
	client.HTTPClient = server.Client()

	ctx := context.Background()
	_, _ = client.GetAssetDownloadURL(ctx, "owner", "repo", "bar-darwin-arm64")

	want := "Bearer test-token-xyz"
	if gotAuth != want {
		t.Errorf("Authorization header = %q, want %q", gotAuth, want)
	}
}

func TestNewGitHubClientSendsTokenWhenEnvSet(t *testing.T) {
	var gotAuth string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth = r.Header.Get("Authorization")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"tag_name": "v1.0.0",
			"assets":   []interface{}{},
		})
	}))
	defer server.Close()

	t.Setenv("GITHUB_TOKEN", "test-token-abc")
	client := NewGitHubClient()
	client.BaseURL = server.URL
	client.HTTPClient = server.Client()

	ctx := context.Background()
	_, _ = client.GetLatestRelease(ctx, "owner", "repo")

	want := "Bearer test-token-abc"
	if gotAuth != want {
		t.Errorf("Authorization header = %q, want %q", gotAuth, want)
	}
}

func TestNewGitHubClientNoAuthWhenEnvAbsent(t *testing.T) {
	var gotAuth string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth = r.Header.Get("Authorization")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"tag_name": "v1.0.0",
			"assets":   []interface{}{},
		})
	}))
	defer server.Close()

	t.Setenv("GITHUB_TOKEN", "")
	client := NewGitHubClient()
	client.BaseURL = server.URL
	client.HTTPClient = server.Client()

	ctx := context.Background()
	_, _ = client.GetLatestRelease(ctx, "owner", "repo")

	if gotAuth != "" {
		t.Errorf("Authorization header = %q, want empty", gotAuth)
	}
}
