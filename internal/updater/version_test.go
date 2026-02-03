package updater

import (
	"testing"
)

func TestVersionCompare(t *testing.T) {
	tests := []struct {
		name     string
		current  string
		latest   string
		expected int // -1 if current < latest, 0 if equal, 1 if current > latest
	}{
		{
			name:     "current less than latest",
			current:  "1.0.0",
			latest:   "1.1.0",
			expected: -1,
		},
		{
			name:     "current equal to latest",
			current:  "1.2.3",
			latest:   "1.2.3",
			expected: 0,
		},
		{
			name:     "current greater than latest",
			current:  "2.0.0",
			latest:   "1.9.9",
			expected: 1,
		},
		{
			name:     "patch version difference",
			current:  "1.0.0",
			latest:   "1.0.1",
			expected: -1,
		},
		{
			name:     "major version difference",
			current:  "1.0.0",
			latest:   "2.0.0",
			expected: -1,
		},
		{
			name:     "with v prefix",
			current:  "v1.0.0",
			latest:   "v1.1.0",
			expected: -1,
		},
		{
			name:     "with bar-v prefix",
			current:  "0.1.80",
			latest:   "bar-v0.1.82",
			expected: -1,
		},
		{
			name:     "both with bar-v prefix",
			current:  "bar-v0.1.80",
			latest:   "bar-v0.1.82",
			expected: -1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := CompareVersions(tt.current, tt.latest)
			if result != tt.expected {
				t.Errorf("CompareVersions(%q, %q) = %d, want %d", tt.current, tt.latest, result, tt.expected)
			}
		})
	}
}

func TestParseVersion(t *testing.T) {
	tests := []struct {
		name      string
		version   string
		wantMajor int
		wantMinor int
		wantPatch int
		wantErr   bool
	}{
		{
			name:      "standard semver",
			version:   "1.2.3",
			wantMajor: 1,
			wantMinor: 2,
			wantPatch: 3,
			wantErr:   false,
		},
		{
			name:      "with v prefix",
			version:   "v2.0.1",
			wantMajor: 2,
			wantMinor: 0,
			wantPatch: 1,
			wantErr:   false,
		},
		{
			name:      "invalid format",
			version:   "not-a-version",
			wantErr:   true,
		},
		{
			name:      "missing patch",
			version:   "1.2",
			wantErr:   true,
		},
		{
			name:      "with bar-v prefix",
			version:   "bar-v0.1.82",
			wantMajor: 0,
			wantMinor: 1,
			wantPatch: 82,
			wantErr:   false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			major, minor, patch, err := ParseVersion(tt.version)
			if tt.wantErr {
				if err == nil {
					t.Errorf("ParseVersion(%q) expected error, got nil", tt.version)
				}
				return
			}
			if err != nil {
				t.Errorf("ParseVersion(%q) unexpected error: %v", tt.version, err)
				return
			}
			if major != tt.wantMajor || minor != tt.wantMinor || patch != tt.wantPatch {
				t.Errorf("ParseVersion(%q) = (%d, %d, %d), want (%d, %d, %d)",
					tt.version, major, minor, patch, tt.wantMajor, tt.wantMinor, tt.wantPatch)
			}
		})
	}
}
