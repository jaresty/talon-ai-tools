package bartui

// TokenCategoryKind identifies the class of prompt tokens represented by a category.
type TokenCategoryKind string

const (
	TokenCategoryKindAxis    TokenCategoryKind = "axis"
	TokenCategoryKindPersona TokenCategoryKind = "persona"
	TokenCategoryKindStatic  TokenCategoryKind = "static"
)

// TokenOption represents a selectable prompt token within a category.
type TokenOption struct {
	Value       string
	Slug        string
	Label       string
	Description string
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
