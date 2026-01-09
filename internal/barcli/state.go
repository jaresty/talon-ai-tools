package barcli

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

const (
	stateSchemaVersion  = 3
	presetSchemaVersion = 3

	configDirEnv    = "BAR_CONFIG_DIR"
	disableStateEnv = "BAR_DISABLE_STATE"

	configDirName  = "bar"
	stateDirName   = "state"
	presetsDirName = "presets"
	lastBuildFile  = "last_build.json"
)

var errStateDisabled = errors.New("state persistence disabled")

type storedBuild struct {
	Version int         `json:"version"`
	SavedAt time.Time   `json:"saved_at"`
	Result  BuildResult `json:"result"`
	Tokens  []string    `json:"tokens"`
}

type presetFile struct {
	Version int         `json:"version"`
	Name    string      `json:"name"`
	SavedAt time.Time   `json:"saved_at"`
	Source  string      `json:"source"`
	Result  BuildResult `json:"result"`
	Tokens  []string    `json:"tokens"`
}

type presetSummary struct {
	Name     string
	SavedAt  time.Time
	Static   string
	Voice    string
	Audience string
	Tone     string
}

func shouldPersistState() bool {
	value := strings.TrimSpace(os.Getenv(disableStateEnv))
	if value == "" {
		return true
	}
	value = strings.ToLower(value)
	return !(value == "1" || value == "true" || value == "yes")
}

func saveLastBuild(result *BuildResult, tokens []string) error {
	if !shouldPersistState() {
		return errStateDisabled
	}

	root, err := resolveConfigRoot()
	if err != nil {
		return err
	}
	stateDir := filepath.Join(root, stateDirName)
	if err := os.MkdirAll(stateDir, 0o700); err != nil {
		return fmt.Errorf("create state directory: %w", err)
	}

	stored := storedBuild{
		Version: stateSchemaVersion,
		SavedAt: time.Now().UTC(),
		Result:  cloneBuildResult(result),
		Tokens:  append([]string(nil), tokens...),
	}
	stored.Result.Subject = ""
	stored.Result.PlainText = ""

	payload, err := json.MarshalIndent(stored, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal state: %w", err)
	}
	payload = append(payload, '\n')

	path := filepath.Join(stateDir, lastBuildFile)
	if err := atomicWriteFile(path, payload, 0o600); err != nil {
		return fmt.Errorf("write state: %w", err)
	}
	return nil
}

func loadLastBuild() (*storedBuild, error) {
	root, err := resolveConfigRoot()
	if err != nil {
		return nil, err
	}
	path := filepath.Join(root, stateDirName, lastBuildFile)
	data, err := os.ReadFile(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return nil, fmt.Errorf("no cached build found; run 'bar build' before saving presets")
		}
		return nil, fmt.Errorf("read cached build: %w", err)
	}

	var stored storedBuild
	if err := json.Unmarshal(data, &stored); err != nil {
		return nil, fmt.Errorf("parse cached build: %w", err)
	}
	if stored.Version != stateSchemaVersion {
		return nil, fmt.Errorf("cached build schema version %d is not supported; rerun 'bar build'", stored.Version)
	}
	stored.Result.PlainText = ""
	stored.Result.Subject = ""
	return &stored, nil
}

func savePreset(name string, build *storedBuild, force bool) (string, error) {
	root, err := resolveConfigRoot()
	if err != nil {
		return "", err
	}
	dir := filepath.Join(root, presetsDirName)
	if err := os.MkdirAll(dir, 0o700); err != nil {
		return "", fmt.Errorf("create presets directory: %w", err)
	}

	slug := slugName(name)
	path := filepath.Join(dir, slug+".json")
	if !force {
		if _, err := os.Stat(path); err == nil {
			return slug, fmt.Errorf("preset %q already exists; pass --force to overwrite", name)
		}
	}

	preset := presetFile{
		Version: presetSchemaVersion,
		Name:    name,
		SavedAt: time.Now().UTC(),
		Source:  "last_build",
		Result:  cloneBuildResult(&build.Result),
		Tokens:  append([]string(nil), build.Tokens...),
	}
	preset.Result.Subject = ""
	preset.Result.PlainText = ""

	payload, err := json.MarshalIndent(preset, "", "  ")
	if err != nil {
		return slug, fmt.Errorf("marshal preset: %w", err)
	}
	payload = append(payload, '\n')

	if err := atomicWriteFile(path, payload, 0o600); err != nil {
		return slug, fmt.Errorf("write preset: %w", err)
	}
	return slug, nil
}

func listPresets() ([]presetSummary, error) {
	root, err := resolveConfigRoot()
	if err != nil {
		return nil, err
	}
	dir := filepath.Join(root, presetsDirName)
	entries, err := os.ReadDir(dir)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return nil, nil
		}
		return nil, fmt.Errorf("read presets directory: %w", err)
	}

	summaries := make([]presetSummary, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".json" {
			continue
		}
		path := filepath.Join(dir, entry.Name())
		preset, err := loadPresetFile(path)
		if err != nil {
			return nil, err
		}
		summaries = append(summaries, summarisePreset(preset))
	}

	sort.Slice(summaries, func(i, j int) bool {
		if summaries[i].SavedAt.Equal(summaries[j].SavedAt) {
			return summaries[i].Name < summaries[j].Name
		}
		return summaries[i].SavedAt.After(summaries[j].SavedAt)
	})

	return summaries, nil
}

func loadPreset(name string) (*presetFile, string, error) {
	root, err := resolveConfigRoot()
	if err != nil {
		return nil, "", err
	}
	dir := filepath.Join(root, presetsDirName)
	slug := slugName(name)
	path := filepath.Join(dir, slug+".json")
	preset, err := loadPresetFile(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return nil, slug, fmt.Errorf("preset %q not found", name)
		}
		return nil, slug, err
	}
	if preset.Version != presetSchemaVersion {
		return nil, slug, fmt.Errorf("preset %q schema version %d unsupported; rebuild preset", name, preset.Version)
	}
	return preset, slug, nil
}

func deletePreset(name string, force bool) (string, error) {
	root, err := resolveConfigRoot()
	if err != nil {
		return "", err
	}
	slug := slugName(name)
	path := filepath.Join(root, presetsDirName, slug+".json")
	if _, err := os.Stat(path); err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return slug, fmt.Errorf("preset %q not found", name)
		}
		return slug, fmt.Errorf("stat preset: %w", err)
	}
	if !force {
		return slug, fmt.Errorf("preset %q exists; re-run with --force to delete", name)
	}
	if err := os.Remove(path); err != nil {
		return slug, fmt.Errorf("delete preset: %w", err)
	}
	return slug, nil
}

func resolveConfigRoot() (string, error) {
	if override := strings.TrimSpace(os.Getenv(configDirEnv)); override != "" {
		return override, nil
	}
	dir, err := os.UserConfigDir()
	if err != nil || dir == "" {
		home, herr := os.UserHomeDir()
		if herr != nil || home == "" {
			return "", fmt.Errorf("determine config directory: %w", err)
		}
		dir = filepath.Join(home, ".config")
	}
	return filepath.Join(dir, configDirName), nil
}

func atomicWriteFile(path string, data []byte, perm fs.FileMode) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0o700); err != nil {
		return err
	}
	tmp, err := os.CreateTemp(dir, "tmp-")
	if err != nil {
		return err
	}
	tmpName := tmp.Name()
	defer os.Remove(tmpName)

	if _, err := tmp.Write(data); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Chmod(perm); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Sync(); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}

	return os.Rename(tmpName, path)
}

func slugName(name string) string {
	trimmed := strings.TrimSpace(name)
	if trimmed == "" {
		return "preset"
	}
	trimmed = strings.ToLower(trimmed)
	var b strings.Builder
	for _, r := range trimmed {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
			b.WriteRune(r)
			continue
		}
		b.WriteRune('-')
	}
	slug := strings.Trim(b.String(), "-")
	if slug == "" {
		slug = "preset"
	}
	slug = strings.Trim(slug, "-")
	if slug == "" {
		return "preset"
	}
	return slug
}

func loadPresetFile(path string) (*presetFile, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var preset presetFile
	if err := json.Unmarshal(data, &preset); err != nil {
		return nil, fmt.Errorf("parse preset %s: %w", filepath.Base(path), err)
	}
	preset.Result.Subject = ""
	preset.Result.PlainText = ""
	return &preset, nil
}

func summarisePreset(preset *presetFile) presetSummary {
	static := preset.Result.Axes.Static
	voice := preset.Result.Persona.Voice
	audience := preset.Result.Persona.Audience
	tone := preset.Result.Persona.Tone
	return presetSummary{
		Name:     preset.Name,
		SavedAt:  preset.SavedAt,
		Static:   static,
		Voice:    voice,
		Audience: audience,
		Tone:     tone,
	}
}

func cloneBuildResult(result *BuildResult) BuildResult {
	if result == nil {
		return BuildResult{}
	}
	cloned := *result
	cloned.Subject = ""
	cloned.PlainText = ""
	cloned.Constraints = append([]string(nil), result.Constraints...)
	cloned.HydratedConstraints = append([]HydratedPromptlet(nil), result.HydratedConstraints...)
	cloned.HydratedPersona = append([]HydratedPromptlet(nil), result.HydratedPersona...)
	cloned.Axes.Scope = append([]string(nil), result.Axes.Scope...)
	cloned.Axes.Method = append([]string(nil), result.Axes.Method...)
	cloned.Axes.Form = append([]string(nil), result.Axes.Form...)
	cloned.Axes.Channel = append([]string(nil), result.Axes.Channel...)
	cloned.Tokens = append([]string(nil), result.Tokens...)
	return cloned
}
