package main

import (
	"bytes"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli"
	"github.com/talonvoice/talon-ai-tools/internal/updater"
)

func TestUpdateCheckIntegration(t *testing.T) {
	tests := []struct {
		name           string
		currentVersion string
		mockRelease    *updater.Release
		mockError      error
		wantExitCode   int
		wantStdout     []string
		wantStderr     []string
	}{
		{
			name:           "newer version available",
			currentVersion: "1.0.0",
			mockRelease:    &updater.Release{TagName: "v1.1.0", Assets: []string{"bar-darwin-amd64"}},
			wantExitCode:   0,
			wantStdout:     []string{"new version is available", "v1.1.0", "1.0.0"},
		},
		{
			name:           "already on latest",
			currentVersion: "1.1.0",
			mockRelease:    &updater.Release{TagName: "v1.1.0", Assets: []string{"bar-darwin-amd64"}},
			wantExitCode:   0,
			wantStdout:     []string{"you are already on the latest version", "1.1.0"},
		},
		{
			name:           "current version newer",
			currentVersion: "2.0.0",
			mockRelease:    &updater.Release{TagName: "v1.9.9", Assets: []string{"bar-darwin-amd64"}},
			wantExitCode:   0,
			wantStdout:     []string{"you are already on the latest version", "2.0.0"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Create mock client
			mockClient := &updater.MockGitHubClient{
				Releases: []updater.MockRelease{
					{TagName: tt.mockRelease.TagName, Assets: tt.mockRelease.Assets},
				},
				Error: tt.mockError,
			}

			// Set up test environment by injecting mock client into barcli package
			barcli.SetVersion(tt.currentVersion)
			barcli.SetUpdateClient(mockClient)
			defer func() {
				// Reset to defaults after test
				barcli.SetVersion("dev")
				barcli.SetUpdateClient(nil)
			}()

			stdout := &bytes.Buffer{}
			stderr := &bytes.Buffer{}

			exitCode := barcli.Run([]string{"update", "check"}, strings.NewReader(""), stdout, stderr)

			if exitCode != tt.wantExitCode {
				t.Errorf("exit code = %d, want %d\nstdout: %s\nstderr: %s",
					exitCode, tt.wantExitCode, stdout.String(), stderr.String())
			}

			// Check stdout contains expected strings
			stdoutStr := strings.ToLower(stdout.String())
			for _, want := range tt.wantStdout {
				if !strings.Contains(stdoutStr, strings.ToLower(want)) {
					t.Errorf("stdout missing %q\ngot: %s", want, stdout.String())
				}
			}

			// Check stderr contains expected strings
			stderrStr := strings.ToLower(stderr.String())
			for _, want := range tt.wantStderr {
				if !strings.Contains(stderrStr, strings.ToLower(want)) {
					t.Errorf("stderr missing %q\ngot: %s", want, stderr.String())
				}
			}
		})
	}
}
