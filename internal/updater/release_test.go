package updater

import (
	"context"
	"testing"
)

func TestReleaseDiscovery(t *testing.T) {
	tests := []struct {
		name           string
		currentVersion string
		mockReleases   []MockRelease
		mockError      error
		wantAvailable  bool
		wantVersion    string
		wantErr        bool
	}{
		{
			name:           "newer version available",
			currentVersion: "1.0.0",
			mockReleases: []MockRelease{
				{TagName: "v1.1.0", Assets: []string{"bar-darwin-amd64"}},
			},
			wantAvailable: true,
			wantVersion:   "v1.1.0",
			wantErr:       false,
		},
		{
			name:           "already on latest",
			currentVersion: "1.1.0",
			mockReleases: []MockRelease{
				{TagName: "v1.1.0", Assets: []string{"bar-darwin-amd64"}},
			},
			wantAvailable: false,
			wantVersion:   "v1.1.0",
			wantErr:       false,
		},
		{
			name:           "current newer than release",
			currentVersion: "2.0.0",
			mockReleases: []MockRelease{
				{TagName: "v1.9.9", Assets: []string{"bar-darwin-amd64"}},
			},
			wantAvailable: false,
			wantVersion:   "v1.9.9",
			wantErr:       false,
		},
		{
			name:           "no releases available",
			currentVersion: "1.0.0",
			mockReleases:   []MockRelease{},
			wantAvailable:  false,
			wantVersion:    "",
			wantErr:        false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			client := &MockGitHubClient{
				Releases: tt.mockReleases,
				Error:    tt.mockError,
			}

			checker := &UpdateChecker{
				Client:         client,
				CurrentVersion: tt.currentVersion,
				Owner:          "talonvoice",
				Repo:           "talon-ai-tools",
			}

			ctx := context.Background()
			available, version, err := checker.CheckForUpdate(ctx)

			if tt.wantErr {
				if err == nil {
					t.Errorf("CheckForUpdate() expected error, got nil")
				}
				return
			}

			if err != nil {
				t.Errorf("CheckForUpdate() unexpected error: %v", err)
				return
			}

			if available != tt.wantAvailable {
				t.Errorf("CheckForUpdate() available = %v, want %v", available, tt.wantAvailable)
			}

			if version != tt.wantVersion {
				t.Errorf("CheckForUpdate() version = %q, want %q", version, tt.wantVersion)
			}
		})
	}
}
