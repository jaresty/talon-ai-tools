package updater

import "context"

// MockRelease represents a test release
type MockRelease struct {
	TagName string
	Assets  []string
}

// MockGitHubClient simulates GitHub API responses for testing
type MockGitHubClient struct {
	Releases []MockRelease
	Error    error
}

// GetLatestRelease implements GitHubClient interface for testing
func (m *MockGitHubClient) GetLatestRelease(ctx context.Context, owner, repo string) (*Release, error) {
	if m.Error != nil {
		return nil, m.Error
	}
	if len(m.Releases) == 0 {
		return nil, nil
	}
	latest := m.Releases[0]
	return &Release{
		TagName: latest.TagName,
		Assets:  latest.Assets,
	}, nil
}
