package bartui2

import (
	"fmt"
	"strings"
)

// HarnessState is the structured snapshot emitted by Harness.Observe after each action.
// It describes the full observable state of the TUI without any terminal rendering.
type HarnessState struct {
	// Stage is the current axis stage key (e.g. "task", "method"). Empty when all stages complete.
	Stage string `json:"stage"`
	// FocusedToken is the key of the first visible token in the current stage.
	FocusedToken string `json:"focused_token"`
	// VisibleTokens are the tokens available for selection in the current stage,
	// filtered by the current filter string.
	VisibleTokens []HarnessToken `json:"visible_tokens"`
	// Selected maps stage keys to their selected token values (auto-filled tokens excluded).
	Selected map[string][]string `json:"selected"`
	// CommandPreview is the bar build command that would be generated from current selections.
	CommandPreview string `json:"command_preview"`
	// Done is true after a "quit" action has been received.
	Done bool `json:"done"`
	// Error is set when the previous action failed; empty on success.
	Error string `json:"error,omitempty"`
}

// HarnessToken represents a selectable token visible in the current stage.
type HarnessToken struct {
	Key      string `json:"key"`
	Label    string `json:"label"`
	Selected bool   `json:"selected"`
}

// HarnessAction is a JSON-decodable instruction for Harness.Act.
// Type must be one of: "nav", "select", "deselect", "filter", "skip", "back", "quit".
type HarnessAction struct {
	// Type identifies the action.
	Type string `json:"type"`
	// Target is the stage key (nav) or token key (select/deselect).
	Target string `json:"target,omitempty"`
	// Text is the filter string (filter action only).
	Text string `json:"text,omitempty"`
}

// Harness wraps a model for headless, PTY-free interaction.
// An LLM drives the TUI by calling Act with a HarnessAction and reading
// the resulting state with Observe. No terminal is allocated.
type Harness struct {
	m       model
	filter  string
	done    bool
	lastErr string
}

// NewHarness creates a Harness from Options. No Bubble Tea program or PTY is started.
func NewHarness(opts Options) *Harness {
	m := newModel(opts)
	m.ready = true
	if m.width == 0 {
		m.width = 80
	}
	if m.height == 0 {
		m.height = 24
	}
	m.advanceToNextIncompleteStage()
	return &Harness{m: m}
}

// Observe returns a snapshot of the current model state.
// It is safe to call multiple times without side effects.
func (h *Harness) Observe() HarnessState {
	stage := h.m.getCurrentStage()

	// Compute visible tokens for the current stage, applying the harness filter.
	var visible []HarnessToken
	if stage != "" {
		cat := h.m.getCategoryByKey(stage)
		if cat != nil {
			selectedSet := make(map[string]bool)
			for _, t := range h.m.tokensByCategory[stage] {
				selectedSet[strings.ToLower(t)] = true
			}
			filterLower := strings.ToLower(h.filter)
			for _, opt := range cat.Options {
				if filterLower != "" {
					if !fuzzyMatch(strings.ToLower(opt.Value), filterLower) &&
						!fuzzyMatch(strings.ToLower(opt.Slug), filterLower) &&
						!(opt.Label != "" && fuzzyMatch(strings.ToLower(opt.Label), filterLower)) &&
						!(opt.Heuristics != "" && fuzzyMatch(strings.ToLower(opt.Heuristics), filterLower)) {
						continue
					}
				}
				key := opt.Slug
				if key == "" {
					key = opt.Value
				}
				visible = append(visible, HarnessToken{
					Key:      key,
					Label:    opt.Label,
					Selected: selectedSet[strings.ToLower(opt.Value)],
				})
			}
		}
	}

	focused := ""
	if len(visible) > 0 {
		focused = visible[0].Key
	}

	// Build selected map: non-auto-filled tokens only, keyed by stage.
	selected := make(map[string][]string)
	for _, s := range stageOrder {
		tokens := h.m.tokensByCategory[s]
		var nonAuto []string
		for _, t := range tokens {
			if !h.m.isAutoFilled(s, t) {
				nonAuto = append(nonAuto, t)
			}
		}
		if len(nonAuto) > 0 {
			selected[s] = nonAuto
		}
	}

	preview := "bar build"
	if tokens := h.m.getCommandTokens(); len(tokens) > 0 {
		preview = "bar build " + strings.Join(tokens, " ")
	}

	return HarnessState{
		Stage:          stage,
		FocusedToken:   focused,
		VisibleTokens:  visible,
		Selected:       selected,
		CommandPreview: preview,
		Done:           h.done,
		Error:          h.lastErr,
	}
}

// ObserveView returns the rendered TUI view content for the current state.
// Useful for asserting detail-panel content (e.g. caution/natural lines) that is
// not captured in the structured HarnessState.
func (h *Harness) ObserveView() string {
	return h.m.View().Content
}

// Act applies an action and updates the model state.
// Returns an error if the action is invalid; the error is also reflected in
// the next Observe().Error so callers reading JSON output need not inspect
// the return value separately.
func (h *Harness) Act(action HarnessAction) error {
	h.lastErr = ""
	switch action.Type {
	case "nav":
		idx := -1
		for i, s := range stageTraversalOrder {
			if s == action.Target {
				idx = i
				break
			}
		}
		if idx < 0 {
			h.lastErr = fmt.Sprintf("unknown stage: %q", action.Target)
			return fmt.Errorf("%s", h.lastErr)
		}
		h.m.currentStageIndex = idx
		h.filter = ""

	case "select":
		stage := h.m.getCurrentStage()
		if stage == "" {
			h.lastErr = "no active stage: all stages complete"
			return fmt.Errorf("%s", h.lastErr)
		}
		cat := h.m.getCategoryByKey(stage)
		if cat == nil {
			h.lastErr = fmt.Sprintf("no category for stage %q", stage)
			return fmt.Errorf("%s", h.lastErr)
		}
		var found *TokenOption
		for i := range cat.Options {
			opt := &cat.Options[i]
			if strings.EqualFold(opt.Value, action.Target) || strings.EqualFold(opt.Slug, action.Target) {
				found = opt
				break
			}
		}
		if found == nil {
			h.lastErr = fmt.Sprintf("token %q not found in stage %q", action.Target, stage)
			return fmt.Errorf("%s", h.lastErr)
		}
		slugDisplay := h.m.formatCompletionDisplay(stage, found.Value, found.Slug)
		display := slugDisplay
		if found.Label != "" {
			display = slugDisplay + " \u2014 " + found.Label
		}
		h.m.selectCompletion(completion{
			Value:          found.Value,
			Display:        display,
			Category:       cat.Label,
			Description:    found.Description,
			Distinctions:   found.Distinctions,
			Heuristics:     found.Heuristics,
			Kanji:          found.Kanji,
			SemanticGroup:  found.SemanticGroup,
			RoutingConcept: found.RoutingConcept,
			Fills:          found.Fills,
		})
		h.filter = ""

	case "deselect":
		removed := false
		for _, s := range stageOrder {
			tokens := h.m.tokensByCategory[s]
			for i, t := range tokens {
				if strings.EqualFold(t, action.Target) {
					sourceKey := s + ":" + t
					h.m.removeAutoFilledBy(sourceKey)
					delete(h.m.autoFilledTokens, sourceKey)
					delete(h.m.autoFillSource, sourceKey)
					h.m.tokensByCategory[s] = append(tokens[:i:i], tokens[i+1:]...)
					h.m.rebuildCommandLine()
					removed = true
					break
				}
			}
			if removed {
				break
			}
		}
		if !removed {
			h.lastErr = fmt.Sprintf("token %q not found in selection", action.Target)
			return fmt.Errorf("%s", h.lastErr)
		}

	case "focus":
		// Move the completion cursor to the named token without selecting it.
		h.m.updateCompletions()
		found := false
		for i, c := range h.m.completions {
			if strings.EqualFold(c.Value, action.Target) {
				h.m.completionIndex = i
				h.m.ensureCompletionVisible()
				found = true
				break
			}
		}
		if !found {
			h.lastErr = fmt.Sprintf("token %q not found for focus in stage %q", action.Target, h.m.getCurrentStage())
			return fmt.Errorf("%s", h.lastErr)
		}

	case "filter":
		h.filter = action.Text

	case "skip":
		h.m.skipCurrentStage()
		h.filter = ""

	case "back":
		h.m.goToPreviousStage()
		h.filter = ""

	case "quit":
		h.done = true

	default:
		h.lastErr = fmt.Sprintf("unknown action type: %q", action.Type)
		return fmt.Errorf("%s", h.lastErr)
	}
	return nil
}
