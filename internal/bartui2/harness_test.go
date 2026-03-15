package bartui2

import (
	"testing"
)

func harnessOpts() Options {
	return Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
}

// TestHarnessInitialState verifies that a new Harness starts at the first
// incomplete stage with all tokens visible and nothing selected.
func TestHarnessInitialState(t *testing.T) {
	h := NewHarness(harnessOpts())
	s := h.Observe()

	if s.Stage != "task" {
		t.Errorf("expected initial stage %q, got %q", "task", s.Stage)
	}
	if s.Done {
		t.Error("expected done=false on init")
	}
	if s.Error != "" {
		t.Errorf("expected no error on init, got %q", s.Error)
	}
	if len(s.VisibleTokens) != 2 {
		t.Errorf("expected 2 visible tokens for task stage, got %d", len(s.VisibleTokens))
	}
	if s.FocusedToken != "todo" {
		t.Errorf("expected focused token %q, got %q", "todo", s.FocusedToken)
	}
	if len(s.Selected) != 0 {
		t.Errorf("expected empty selection on init, got %v", s.Selected)
	}
	if s.CommandPreview != "bar build" {
		t.Errorf("expected empty command preview, got %q", s.CommandPreview)
	}
}

// TestHarnessSelectAdvancesStage verifies that selecting a token in a single-select
// stage causes the stage to advance.
func TestHarnessSelectAdvancesStage(t *testing.T) {
	h := NewHarness(harnessOpts())

	if err := h.Act(HarnessAction{Type: "select", Target: "todo"}); err != nil {
		t.Fatalf("Act(select todo) failed: %v", err)
	}

	s := h.Observe()
	// task is MaxSelections=1, so after selecting it advances past task.
	// stageOrder: ..., task, completeness, scope, ...
	// testCategories has completeness next.
	if s.Stage != "completeness" {
		t.Errorf("expected stage %q after task select, got %q", "completeness", s.Stage)
	}
	if s.Selected["task"] == nil || s.Selected["task"][0] != "todo" {
		t.Errorf("expected task=todo in selection, got %v", s.Selected)
	}
}

// TestHarnessSelectUpdatesCommandPreview verifies that CommandPreview reflects selected tokens.
func TestHarnessSelectUpdatesCommandPreview(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "select", Target: "todo"})
	h.Act(HarnessAction{Type: "select", Target: "full"})

	s := h.Observe()
	if s.CommandPreview != "bar build todo full" {
		t.Errorf("expected command preview %q, got %q", "bar build todo full", s.CommandPreview)
	}
}

// TestHarnessSelectNotFound verifies that selecting a non-existent token returns an error.
func TestHarnessSelectNotFound(t *testing.T) {
	h := NewHarness(harnessOpts())

	err := h.Act(HarnessAction{Type: "select", Target: "nonexistent"})
	if err == nil {
		t.Error("expected error for unknown token, got nil")
	}
	s := h.Observe()
	if s.Error == "" {
		t.Error("expected Error in Observe() after failed select")
	}
	if s.Stage != "task" {
		t.Error("stage should not advance after failed select")
	}
}

// TestHarnessFilter verifies that the filter action restricts visible tokens.
func TestHarnessFilter(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "filter", Text: "todo"})
	s := h.Observe()

	if len(s.VisibleTokens) != 1 {
		t.Errorf("expected 1 visible token after filter, got %d", len(s.VisibleTokens))
	}
	if s.VisibleTokens[0].Key != "todo" {
		t.Errorf("expected visible token %q, got %q", "todo", s.VisibleTokens[0].Key)
	}
}

// TestHarnessFilterClear verifies that setting filter to "" restores all tokens.
func TestHarnessFilterClear(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "filter", Text: "todo"})
	h.Act(HarnessAction{Type: "filter", Text: ""})
	s := h.Observe()

	if len(s.VisibleTokens) != 2 {
		t.Errorf("expected 2 visible tokens after filter cleared, got %d", len(s.VisibleTokens))
	}
}

// TestHarnessSelectClearsFilter verifies that a successful select clears the filter.
func TestHarnessSelectClearsFilter(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "filter", Text: "todo"})
	h.Act(HarnessAction{Type: "select", Target: "todo"})

	// Now on completeness stage; filter should be cleared.
	s := h.Observe()
	if len(s.VisibleTokens) != 2 { // full and gist both visible
		t.Errorf("expected filter cleared after select, got %d visible tokens", len(s.VisibleTokens))
	}
}

// TestHarnessDeselect verifies that a selected token can be removed.
func TestHarnessDeselect(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "select", Target: "todo"})
	if err := h.Act(HarnessAction{Type: "deselect", Target: "todo"}); err != nil {
		t.Fatalf("Act(deselect todo) failed: %v", err)
	}

	s := h.Observe()
	if len(s.Selected) != 0 {
		t.Errorf("expected empty selection after deselect, got %v", s.Selected)
	}
	if s.CommandPreview != "bar build" {
		t.Errorf("expected empty command preview after deselect, got %q", s.CommandPreview)
	}
}

// TestHarnessDeselectNotFound verifies that deselecting a non-selected token returns an error.
func TestHarnessDeselectNotFound(t *testing.T) {
	h := NewHarness(harnessOpts())

	err := h.Act(HarnessAction{Type: "deselect", Target: "nonexistent"})
	if err == nil {
		t.Error("expected error for unknown token in deselect")
	}
	s := h.Observe()
	if s.Error == "" {
		t.Error("expected Error in Observe() after failed deselect")
	}
}

// TestHarnessNav verifies that nav jumps to a named stage.
func TestHarnessNav(t *testing.T) {
	h := NewHarness(harnessOpts())

	// Start at task; jump directly to scope.
	if err := h.Act(HarnessAction{Type: "nav", Target: "scope"}); err != nil {
		t.Fatalf("Act(nav scope) failed: %v", err)
	}

	s := h.Observe()
	if s.Stage != "scope" {
		t.Errorf("expected stage %q after nav, got %q", "scope", s.Stage)
	}
}

// TestHarnessNavUnknown verifies that navigating to an unknown stage returns an error.
func TestHarnessNavUnknown(t *testing.T) {
	h := NewHarness(harnessOpts())

	err := h.Act(HarnessAction{Type: "nav", Target: "notastage"})
	if err == nil {
		t.Error("expected error for unknown stage in nav")
	}
	s := h.Observe()
	if s.Stage != "task" {
		t.Error("stage should not change after failed nav")
	}
}

// TestHarnessSkip verifies that skip advances to the next stage without selecting.
func TestHarnessSkip(t *testing.T) {
	h := NewHarness(harnessOpts())

	if err := h.Act(HarnessAction{Type: "skip"}); err != nil {
		t.Fatalf("Act(skip) failed: %v", err)
	}

	s := h.Observe()
	if s.Stage == "task" {
		t.Error("expected stage to advance after skip")
	}
	if len(s.Selected) != 0 {
		t.Error("expected nothing selected after skip")
	}
}

// TestHarnessBack verifies that back returns to the previous stage.
func TestHarnessBack(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "select", Target: "todo"})
	// Now on completeness; go back.
	if err := h.Act(HarnessAction{Type: "back"}); err != nil {
		t.Fatalf("Act(back) failed: %v", err)
	}

	s := h.Observe()
	if s.Stage != "task" {
		t.Errorf("expected stage %q after back, got %q", "task", s.Stage)
	}
}

// TestHarnessQuit verifies that quit sets done=true.
func TestHarnessQuit(t *testing.T) {
	h := NewHarness(harnessOpts())

	if err := h.Act(HarnessAction{Type: "quit"}); err != nil {
		t.Fatalf("Act(quit) failed: %v", err)
	}

	s := h.Observe()
	if !s.Done {
		t.Error("expected done=true after quit")
	}
}

// TestHarnessUnknownAction verifies that an unknown action type returns an error.
func TestHarnessUnknownAction(t *testing.T) {
	h := NewHarness(harnessOpts())

	err := h.Act(HarnessAction{Type: "teleport"})
	if err == nil {
		t.Error("expected error for unknown action type")
	}
	s := h.Observe()
	if s.Error == "" {
		t.Error("expected Error in Observe() after unknown action")
	}
}

// testCategoriesWithPersona returns categories that include a persona_preset stage before task,
// used to test that stageTraversalOrder places task first regardless of persona presence.
func testCategoriesWithPersona() []TokenCategory {
	return []TokenCategory{
		{
			Key:           "persona_preset",
			Label:         "Persona Preset",
			MaxSelections: 1,
			Options: []TokenOption{
				{Value: "peer", Slug: "peer", Label: "Peer Engineer"},
			},
		},
		{
			Key:           "task",
			Label:         "Task",
			MaxSelections: 1,
			Options: []TokenOption{
				{Value: "todo", Slug: "todo", Label: "Todo", Description: "Return a todo list"},
				{Value: "infer", Slug: "infer", Label: "Infer", Description: "Infer the task"},
			},
		},
		{
			Key:           "completeness",
			Label:         "Completeness",
			MaxSelections: 1,
			Options: []TokenOption{
				{Value: "full", Slug: "full", Label: "Full", Description: "Thorough answer"},
			},
		},
	}
}

// ADR-0168 Fix 1: TestFilterSearchesHeuristics verifies that the filter matches tokens
// by heuristics[] trigger words, not only slug/label.
func TestFilterSearchesHeuristics(t *testing.T) {
	opts := Options{
		TokenCategories: testCategoriesWithHeuristics(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
	h := NewHarness(opts)

	// "explaining" appears in show's Heuristics but not in its slug ("show") or label ("Show").
	h.Act(HarnessAction{Type: "filter", Text: "explaining"})
	s := h.Observe()

	found := false
	for _, t := range s.VisibleTokens {
		if t.Key == "show" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected 'show' to be visible when filtering by heuristic 'explaining', got: %v", s.VisibleTokens)
	}
}

// ADR-0168 Fix 1: TestFilterHeuristicsDistinctFromLabel verifies that a token is found
// by a heuristic trigger word that does not appear in its label or slug.
func TestFilterHeuristicsDistinctFromLabel(t *testing.T) {
	opts := Options{
		TokenCategories: testCategoriesWithHeuristics(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
	h := NewHarness(opts)

	// "creating" appears in make's Heuristics; "make" is the slug/label.
	// Filtering by "creating" should surface make even though "creating" != "make".
	h.Act(HarnessAction{Type: "filter", Text: "creating"})
	s := h.Observe()

	found := false
	for _, tok := range s.VisibleTokens {
		if tok.Key == "make" {
			found = true
		}
	}
	if !found {
		t.Errorf("expected 'make' to be visible when filtering by heuristic 'creating', got: %v", s.VisibleTokens)
	}
}

// ADR-0168 Fix 2: TestInitialStageIsTaskWhenPersonaCategoriesPresent verifies that the
// harness starts at "task" even when persona_preset is present in the token categories.
// Before Fix 2, the initial stage was "persona_preset".
func TestInitialStageIsTaskWhenPersonaCategoriesPresent(t *testing.T) {
	opts := Options{
		TokenCategories: testCategoriesWithPersona(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
	h := NewHarness(opts)
	s := h.Observe()

	if s.Stage != "task" {
		t.Errorf("expected initial stage %q, got %q (persona stages should be deferred)", "task", s.Stage)
	}
}

// ADR-0168 Fix 2: TestPersonaStageReachableAfterTask verifies that persona_preset is
// reachable via skip after completing the core stages.
func TestPersonaStageReachableAfterTask(t *testing.T) {
	opts := Options{
		TokenCategories: testCategoriesWithPersona(),
		InitialWidth:    80,
		InitialHeight:   24,
	}
	h := NewHarness(opts)

	// Skip through task and completeness, then persona_preset should be reachable.
	h.Act(HarnessAction{Type: "skip"}) // skip task
	h.Act(HarnessAction{Type: "skip"}) // skip completeness

	// At this point all core stages are done; persona_preset should be next.
	if err := h.Act(HarnessAction{Type: "nav", Target: "persona_preset"}); err != nil {
		t.Fatalf("expected persona_preset to be navigable, got: %v", err)
	}
	s := h.Observe()
	if s.Stage != "persona_preset" {
		t.Errorf("expected stage %q after nav, got %q", "persona_preset", s.Stage)
	}
}

// ADR-0168 Fix 3: TestBackReSelectReplaces verifies that going back to a completed
// single-capacity stage and selecting a new token replaces the old one.
// Before Fix 3, the new selection was silently dropped.
func TestBackReSelectReplaces(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "select", Target: "todo"})   // select task; auto-advances to completeness
	h.Act(HarnessAction{Type: "back"})                     // return to task
	if err := h.Act(HarnessAction{Type: "select", Target: "infer"}); err != nil {
		t.Fatalf("select infer after back failed: %v", err)
	}

	s := h.Observe()
	if len(s.Selected["task"]) != 1 || s.Selected["task"][0] != "infer" {
		t.Errorf("expected task=[infer] after back+re-select, got %v", s.Selected["task"])
	}
	if s.Stage == "task" {
		t.Error("expected stage to advance past task after re-select")
	}
}

// ADR-0168 Fix 3: TestBackReSelectOnMultiCapacityStageAppends verifies that replace
// semantics only apply to MaxSelections==1 stages; a MaxSelections==2 stage that is
// full (both slots taken) still blocks a third selection.
func TestBackReSelectOnMultiCapacityStageAppends(t *testing.T) {
	h := NewHarness(harnessOpts())

	h.Act(HarnessAction{Type: "nav", Target: "scope"})
	h.Act(HarnessAction{Type: "select", Target: "focus"})  // scope=[focus], not full
	h.Act(HarnessAction{Type: "select", Target: "system"}) // scope=[focus,system], now full

	s := h.Observe()
	if len(s.Selected["scope"]) != 2 {
		t.Errorf("expected scope=[focus system] after two selects, got %v", s.Selected["scope"])
	}
}

// TestHarnessObserveIdempotent verifies that multiple Observe calls return the same state.
func TestHarnessObserveIdempotent(t *testing.T) {
	h := NewHarness(harnessOpts())
	s1 := h.Observe()
	s2 := h.Observe()

	if s1.Stage != s2.Stage {
		t.Errorf("Observe not idempotent: stage %q vs %q", s1.Stage, s2.Stage)
	}
	if len(s1.VisibleTokens) != len(s2.VisibleTokens) {
		t.Errorf("Observe not idempotent: visible token count %d vs %d", len(s1.VisibleTokens), len(s2.VisibleTokens))
	}
}

// TestHarnessInitialTokens verifies that pre-selected tokens from Options are reflected in state.
func TestHarnessInitialTokens(t *testing.T) {
	opts := Options{
		TokenCategories: testCategories(),
		InitialTokens:   []string{"todo"},
		InitialWidth:    80,
		InitialHeight:   24,
	}
	h := NewHarness(opts)
	s := h.Observe()

	// task is pre-selected and complete; should advance past it.
	if s.Stage == "task" {
		t.Error("expected stage to advance past pre-selected task")
	}
	if s.Selected["task"] == nil {
		t.Error("expected pre-selected task=todo in selection")
	}
}
