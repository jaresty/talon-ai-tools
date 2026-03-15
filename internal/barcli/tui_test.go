package barcli

import (
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/bartui2"
)

// TestTUITokenCategoriesUseShortLabels specifies that BuildTokenCategories returns
// TokenOptions whose Label field is a short label (not the full long description)
// for axis, task, and persona tokens that have labels defined (ADR-0111 D4).
func TestTUITokenCategoriesUseShortLabels(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)

	findOption := func(categoryKey, slug string) (string, bool) {
		for _, cat := range categories {
			if cat.Key != categoryKey {
				continue
			}
			for _, opt := range cat.Options {
				if opt.Slug == slug {
					return opt.Label, true
				}
			}
		}
		return "", false
	}

	// Axis token: scope:act should have short label, not the full description.
	if label, ok := findOption("scope", "act"); !ok {
		t.Error("scope category must have an 'act' option (ADR-0111 D4)")
	} else if strings.Contains(label, "The response focuses on") {
		t.Errorf("scope:act tui label must be short label, not full description; got: %q", label)
	} else if label == "" {
		t.Error("scope:act tui label must be non-empty (ADR-0111 D4)")
	}

	// Task token: 'make' should have short label.
	if label, ok := findOption("task", "make"); !ok {
		t.Error("task category must have a 'make' option (ADR-0111 D4)")
	} else if strings.Contains(label, "The response creates new content") {
		t.Errorf("task:make tui label must be short label, not full description; got: %q", label)
	} else if label == "" {
		t.Error("task:make tui label must be non-empty (ADR-0111 D4)")
	}

	// Persona axis token: voice 'as-kent-beck' should have short label.
	if label, ok := findOption("voice", "as-kent-beck"); !ok {
		t.Error("voice category must have an 'as-kent-beck' option (ADR-0111 D4)")
	} else if strings.Contains(label, "The response channels") {
		t.Errorf("voice:as-kent-beck tui label must be short label, not full description; got: %q", label)
	} else if label == "" {
		t.Error("voice:as-kent-beck tui label must be non-empty (ADR-0111 D4)")
	}
}

// TestHarnessCautionRealGrammar is an integration test that verifies the Direction A caution
// fix (only show caution for active tokens) against the real grammar data (ADR-0148).
//
// Uses channel.shellscript → task.{sim,probe} which are genuine caution pairs in the grammar.
func TestHarnessCautionRealGrammar(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)

	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural := make(map[string][]string)
		cautionary := make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}

	opts := func(initialTokens []string) bartui2.Options {
		return bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			InitialHeight:           50,
		}
	}

	// Case 1: sim is active — caution must appear when shellscript is focused.
	h := bartui2.NewHarness(opts([]string{"sim"}))
	state := h.Observe()
	if state.Stage == "task" {
		t.Fatalf("expected to advance past task after sim pre-selected, still at task")
	}
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "channel"}); err != nil {
		t.Fatalf("nav to channel: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "shellscript"}); err != nil {
		t.Fatalf("focus shellscript: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "⚠") {
		t.Errorf("real grammar: caution must appear when sim is active and shellscript focused; got:\n%s", view)
	}
	if !strings.Contains(view, "sim") {
		t.Errorf("real grammar: 'sim' must appear in caution line; got:\n%s", view)
	}

	// Case 2: make is active (not a cautionary task) — no caution when shellscript focused.
	h2 := bartui2.NewHarness(opts([]string{"make"}))
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "channel"}); err != nil {
		t.Fatalf("nav to channel: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "shellscript"}); err != nil {
		t.Fatalf("focus shellscript (make active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "⚠") {
		t.Errorf("real grammar: caution must NOT appear when make (non-cautionary) is active; got:\n%s", view2)
	}
}

// TestHarnessCautionRealGrammarFormAxis verifies the Direction A fix for the form axis:
// form.commit has a completeness caution (max, deep) — caution must appear only when
// those completeness tokens are active, not when a non-cautionary completeness is active.
func TestHarnessCautionRealGrammarFormAxis(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)

	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural := make(map[string][]string)
		cautionary := make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}

	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			// Height 70: form axis has ~40 tokens; the list requires more pane space
			// before the detail section becomes visible (paneHeight ≈ 20 needed).
			InitialHeight:           70,
		})
	}

	// Case 1: max completeness is active (cautionary for commit) — caution must appear.
	h := newH([]string{"make", "max"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "form"}); err != nil {
		t.Fatalf("nav to form: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "commit"}); err != nil {
		t.Fatalf("focus commit: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "⚠") {
		t.Errorf("form axis: caution must appear when max completeness active + commit focused; got:\n%s", view)
	}
	if !strings.Contains(view, "max") {
		t.Errorf("form axis: 'max' must appear in caution line; got:\n%s", view)
	}

	// Case 2: full completeness is active (NOT cautionary for commit) — no caution.
	h2 := newH([]string{"make", "full"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "form"}); err != nil {
		t.Fatalf("nav to form: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "commit"}); err != nil {
		t.Fatalf("focus commit (full active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "⚠") {
		t.Errorf("form axis: caution must NOT appear when full completeness (non-cautionary) is active; got:\n%s", view2)
	}
}

// TestHarnessCautionFormToChannel specifies that Direction A shows caution text when
// browsing the form axis and the focused form token has a caution against an active
// channel token (form→channel caution pair, ADR-0148 Direction A extension).
//
// form.faq → channel: caution=[shellscript, code, codetour], natural=[plain, slack, jira]
func TestHarnessCautionFormToChannel(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)

	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural := make(map[string][]string)
		cautionary := make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}

	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			// Height 90: form list has ~40 tokens; faq is at position ~13,
			// requiring more pane space than shallower tokens like commit.
			InitialHeight:           90,
		})
	}

	// Case 1: shellscript channel active + faq focused → caution must appear.
	h := newH([]string{"make", "shellscript"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "form"}); err != nil {
		t.Fatalf("nav to form: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "faq"}); err != nil {
		t.Fatalf("focus faq: %v", err)
	}
	view := h.ObserveView()
	// Check for detail-panel caution text, not just chip-column ⚠.
	if !strings.Contains(view, "⚠ Caution: shellscript") {
		t.Errorf("form→channel: detail-panel caution must appear when shellscript active + faq focused; got:\n%s", view)
	}

	// Case 2: plain channel active (natural for faq, not cautionary) → no caution.
	h2 := newH([]string{"make", "plain"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "form"}); err != nil {
		t.Fatalf("nav to form: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "faq"}); err != nil {
		t.Fatalf("focus faq (plain active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "⚠ Caution: plain") {
		t.Errorf("form→channel: detail-panel caution must NOT appear when plain (natural) channel active; got:\n%s", view2)
	}
}

// TestHarnessCautionChannelToForm specifies that Direction A shows caution text when
// browsing the channel axis and the focused channel token has a caution against an active
// form token (channel→form caution pair, ADR-0148 Direction A extension).
//
// channel.gherkin → form: caution=[case, log, questions, recipe], natural=[story]
func TestHarnessCautionChannelToForm(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)

	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural := make(map[string][]string)
		cautionary := make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}

	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			InitialHeight:           50,
		})
	}

	// Case 1: case form active + gherkin channel focused → caution must appear.
	h := newH([]string{"make", "case"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "channel"}); err != nil {
		t.Fatalf("nav to channel: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "gherkin"}); err != nil {
		t.Fatalf("focus gherkin: %v", err)
	}
	view := h.ObserveView()
	// Check for detail-panel caution text, not just chip-column ⚠.
	if !strings.Contains(view, "⚠ Caution: case") {
		t.Errorf("channel→form: detail-panel caution must appear when case form active + gherkin focused; got:\n%s", view)
	}

	// Case 2: story form active (natural for gherkin, not cautionary) → no caution.
	h2 := newH([]string{"make", "story"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "channel"}); err != nil {
		t.Fatalf("nav to channel: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "gherkin"}); err != nil {
		t.Fatalf("focus gherkin (story active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "⚠ Caution: story") {
		t.Errorf("channel→form: detail-panel caution must NOT appear when story (natural) form active; got:\n%s", view2)
	}
}

// TestHarnessCautionDirectionalCompleteness specifies that browsing the directional axis
// with an active completeness token shows a detail-panel caution when the focused
// directional token conflicts with that completeness token.
//
// completeness.gist → directional: caution=[fig, bog, fly-ong, ...]
func TestHarnessCautionDirectionalCompleteness(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)
	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural, cautionary := make(map[string][]string), make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 { natural[axisB] = pair.Natural }
			if len(pair.Cautionary) > 0 { cautionary[axisB] = pair.Cautionary }
		}
		return natural, cautionary
	}
	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			InitialHeight:           50,
		})
	}

	// Case 1: gist active + fig focused → caution must appear.
	h := newH([]string{"make", "gist"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "directional"}); err != nil {
		t.Fatalf("nav to directional: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "fig"}); err != nil {
		t.Fatalf("focus fig: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "With gist") {
		t.Errorf("directional: detail-panel caution must appear when gist active + fig focused; got:\n%s", view)
	}

	// Case 2: full active + fig focused → no detail-panel caution (full has no directional cautions).
	h2 := newH([]string{"make", "full"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "directional"}); err != nil {
		t.Fatalf("nav to directional: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "fig"}); err != nil {
		t.Fatalf("focus fig (full active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "⚠ With full") {
		t.Errorf("directional: caution must NOT appear when full active; got:\n%s", view2)
	}
}

// TestHarnessCautionDirectionalForm specifies that browsing the directional axis
// with an active form token shows a detail-panel caution when the focused directional
// token conflicts with that form token.
//
// form.commit → directional: caution=[fig, bog, fly-ong, fly-rog, ...]
func TestHarnessCautionDirectionalForm(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)
	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural, cautionary := make(map[string][]string), make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 { natural[axisB] = pair.Natural }
			if len(pair.Cautionary) > 0 { cautionary[axisB] = pair.Cautionary }
		}
		return natural, cautionary
	}

	// commit form active + fig directional focused → caution must appear.
	h := bartui2.NewHarness(bartui2.Options{
		TokenCategories:         categories,
		InitialTokens:           []string{"make", "commit"},
		CrossAxisCompositionFor: crossAxisFor,
		InitialWidth:            80,
		InitialHeight:           50,
	})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "directional"}); err != nil {
		t.Fatalf("nav to directional: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "fig"}); err != nil {
		t.Fatalf("focus fig: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "With commit") {
		t.Errorf("directional+form: detail-panel caution must appear when commit active + fig focused; got:\n%s", view)
	}
}

// TestHarnessCautionMethodCompleteness specifies that browsing the method axis
// with an active completeness token shows a detail-panel caution when the focused
// method token conflicts with that completeness token.
//
// completeness.skim → method: caution=[rigor]
func TestHarnessCautionMethodCompleteness(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)
	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural, cautionary := make(map[string][]string), make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 { natural[axisB] = pair.Natural }
			if len(pair.Cautionary) > 0 { cautionary[axisB] = pair.Cautionary }
		}
		return natural, cautionary
	}
	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			InitialHeight:           50,
		})
	}

	// Case 1: skim active + rigor focused → caution must appear.
	h := newH([]string{"make", "skim"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "method"}); err != nil {
		t.Fatalf("nav to method: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "rigor"}); err != nil {
		t.Fatalf("focus rigor: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "With skim") {
		t.Errorf("method: detail-panel caution must appear when skim active + rigor focused; got:\n%s", view)
	}

	// Case 2: full active + rigor focused → no detail-panel caution.
	h2 := newH([]string{"make", "full"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "method"}); err != nil {
		t.Fatalf("nav to method: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "rigor"}); err != nil {
		t.Fatalf("focus rigor (full active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "⚠ With full") {
		t.Errorf("method: caution must NOT appear when full active; got:\n%s", view2)
	}
}

// TestHarnessCautionToneChannel specifies that browsing the channel axis with an active
// tone token shows a detail-panel caution when the focused channel token conflicts with
// that tone token.
//
// tone.formally → channel: caution=[slack, sync, remote]
func TestHarnessCautionToneChannel(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)
	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural, cautionary := make(map[string][]string), make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}
	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			InitialHeight:           50,
		})
	}

	// Case 1: formally active + slack focused → caution must appear.
	h := newH([]string{"make", "formally"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "channel"}); err != nil {
		t.Fatalf("nav to channel: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "slack"}); err != nil {
		t.Fatalf("focus slack: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "With formally") {
		t.Errorf("tone→channel: detail-panel caution must appear when formally active + slack focused; got:\n%s", view)
	}

	// Case 2: casually active + slack focused → no caution (casually has no channel cautions).
	h2 := newH([]string{"make", "casually"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "channel"}); err != nil {
		t.Fatalf("nav to channel: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "slack"}); err != nil {
		t.Fatalf("focus slack (casually active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "With casually") {
		t.Errorf("tone→channel: caution must NOT appear when casually active; got:\n%s", view2)
	}
}

// TestHarnessCautionChannelAudience specifies that browsing the audience axis with an
// active channel token shows a detail-panel caution when the focused audience token
// conflicts with that channel token.
//
// channel.code → audience: caution=[to-managers, to-stakeholders, to-team, to-ceo]
func TestHarnessCautionChannelAudience(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	categories := BuildTokenCategories(grammar)
	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural, cautionary := make(map[string][]string), make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}
	newH := func(initialTokens []string) *bartui2.Harness {
		return bartui2.NewHarness(bartui2.Options{
			TokenCategories:         categories,
			InitialTokens:           initialTokens,
			CrossAxisCompositionFor: crossAxisFor,
			InitialWidth:            80,
			InitialHeight:           50,
		})
	}

	// Case 1: code active + to-managers focused → caution must appear.
	h := newH([]string{"make", "code"})
	if err := h.Act(bartui2.HarnessAction{Type: "nav", Target: "audience"}); err != nil {
		t.Fatalf("nav to audience: %v", err)
	}
	if err := h.Act(bartui2.HarnessAction{Type: "focus", Target: "to-managers"}); err != nil {
		t.Fatalf("focus to-managers: %v", err)
	}
	view := h.ObserveView()
	if !strings.Contains(view, "With code") {
		t.Errorf("channel→audience: detail-panel caution must appear when code active + to-managers focused; got:\n%s", view)
	}

	// Case 2: plain active + to-managers focused → no caution (plain has no audience cautions).
	h2 := newH([]string{"make", "plain"})
	if err := h2.Act(bartui2.HarnessAction{Type: "nav", Target: "audience"}); err != nil {
		t.Fatalf("nav to audience: %v", err)
	}
	if err := h2.Act(bartui2.HarnessAction{Type: "focus", Target: "to-managers"}); err != nil {
		t.Fatalf("focus to-managers (plain active): %v", err)
	}
	view2 := h2.ObserveView()
	if strings.Contains(view2, "With plain") {
		t.Errorf("channel→audience: caution must NOT appear when plain active; got:\n%s", view2)
	}
}
