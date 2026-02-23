package bartui

// TokenCategoryKind identifies the class of prompt tokens represented by a category.
type TokenCategoryKind string

const (
	TokenCategoryKindAxis    TokenCategoryKind = "axis"
	TokenCategoryKindPersona TokenCategoryKind = "persona"
	TokenCategoryKindTask    TokenCategoryKind = "task"
)

// TokenOption represents a selectable prompt token within a category.
type TokenOption struct {
	Value       string
	Slug        string
	Label       string
	Description string
	Guidance    string
	UseWhen     string // ADR-0142: routing trigger phrases for nav surfaces
	Kanji       string // ADR-0143: kanji icons for visual display
	// Fills specifies other categories that get auto-filled when this option is selected.
	// Key is the category key, value is the token value to fill.
	// Used by persona presets to auto-fill voice, audience, and tone.
	Fills map[string]string
}

// TokenCategory groups related token options and provides selection constraints.
type TokenCategory struct {
	Key           string
	Label         string
	Kind          TokenCategoryKind
	MaxSelections int
	Options       []TokenOption
}

func cloneTokenCategories(categories []TokenCategory) []TokenCategory {
	if len(categories) == 0 {
		return nil
	}
	cloned := make([]TokenCategory, len(categories))
	for i, category := range categories {
		options := make([]TokenOption, len(category.Options))
		copy(options, category.Options)
		cloned[i] = TokenCategory{
			Key:           category.Key,
			Label:         category.Label,
			Kind:          category.Kind,
			MaxSelections: category.MaxSelections,
			Options:       options,
		}
	}
	return cloned
}
