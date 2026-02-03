package updater

import (
	"context"
)

// Release represents a GitHub release
type Release struct {
	TagName string
	Assets  []string
}

// GitHubClient defines the interface for querying GitHub releases
type GitHubClient interface {
	GetLatestRelease(ctx context.Context, owner, repo string) (*Release, error)
}

// UpdateChecker checks for available updates
type UpdateChecker struct {
	Client         GitHubClient
	CurrentVersion string
	Owner          string
	Repo           string
}

// CheckForUpdate queries GitHub for the latest release and compares versions.
// Returns (true, version) if an update is available, (false, "") otherwise.
func (uc *UpdateChecker) CheckForUpdate(ctx context.Context) (bool, string, error) {
	release, err := uc.Client.GetLatestRelease(ctx, uc.Owner, uc.Repo)
	if err != nil {
		return false, "", err
	}

	if release == nil {
		// No releases available
		return false, "", nil
	}

	// Compare versions
	comparison := CompareVersions(uc.CurrentVersion, release.TagName)
	if comparison < 0 {
		// Current version is older than latest
		return true, release.TagName, nil
	}

	// Current version is same or newer
	return false, "", nil
}
