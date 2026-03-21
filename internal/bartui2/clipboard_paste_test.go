package bartui2

import (
	"strings"
	"testing"
)

func TestClipboardPasteNilRead(t *testing.T) {
	h := NewHarness(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
		ClipboardRead:   nil,
	})

	h.m.showSubjectModal = true
	h.m.subjectInput.Focus()
	h.m.subjectInput.SetValue("existing text")

	if err := h.Act(HarnessAction{Type: "paste", Text: "hello world"}); err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	s := h.Observe()
	if s.ToastMessage != "Clipboard read not configured" {
		t.Errorf("expected toast %q, got %q", "Clipboard read not configured", s.ToastMessage)
	}
	if s.ModalInputs.Subject != "existing text" {
		t.Errorf("expected subject unchanged %q, got %q", "existing text", s.ModalInputs.Subject)
	}
}

func TestClipboardPasteReadError(t *testing.T) {
	h := NewHarness(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
		ClipboardRead: func() (string, error) {
			return "", strings.NewReader("clipboard unavailable").Read(nil)
		},
	})

	h.m.showSubjectModal = true
	h.m.subjectInput.Focus()
	h.m.subjectInput.SetValue("existing")

	if err := h.Act(HarnessAction{Type: "paste", Text: "hello"}); err == nil {
		t.Error("expected error when ClipboardRead returns error")
	}
}

func TestClipboardPasteSubjectInput(t *testing.T) {
	h := NewHarness(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
		ClipboardRead: func() (string, error) {
			return "pasted content", nil
		},
	})

	h.m.showSubjectModal = true
	h.m.subjectInput.Focus()
	h.m.subjectInput.SetValue("prefix")

	if err := h.Act(HarnessAction{Type: "paste", Text: "from clipboard"}); err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	s := h.Observe()
	if !strings.Contains(s.ModalInputs.Subject, "pasted content") {
		t.Errorf("expected subject to contain pasted content, got %q", s.ModalInputs.Subject)
	}
	if !strings.Contains(s.ModalInputs.Subject, "prefix") {
		t.Errorf("expected subject to preserve prefix, got %q", s.ModalInputs.Subject)
	}
}

func TestClipboardPasteAddendumInput(t *testing.T) {
	h := NewHarness(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
		ClipboardRead: func() (string, error) {
			return "addendum paste", nil
		},
	})

	h.m.showAddendumModal = true
	h.m.addendumInput.Focus()
	h.m.addendumInput.SetValue("base addendum")

	if err := h.Act(HarnessAction{Type: "paste", Text: "clip"}); err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	s := h.Observe()
	if !strings.Contains(s.ModalInputs.Addendum, "addendum paste") {
		t.Errorf("expected addendum to contain pasted content, got %q", s.ModalInputs.Addendum)
	}
}

func TestClipboardPasteShellCommandInput(t *testing.T) {
	h := NewHarness(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
		ClipboardRead: func() (string, error) {
			return "echo test", nil
		},
	})

	h.m.showCommandModal = true
	h.m.shellCommandInput.Focus()
	h.m.shellCommandInput.SetValue("")

	if err := h.Act(HarnessAction{Type: "paste", Text: "cmd"}); err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	s := h.Observe()
	if !strings.Contains(s.ModalInputs.ShellCommand, "echo test") {
		t.Errorf("expected shell command to contain pasted content, got %q", s.ModalInputs.ShellCommand)
	}
}

func TestClipboardPasteNoModal(t *testing.T) {
	h := NewHarness(Options{
		TokenCategories: testCategories(),
		InitialWidth:    80,
		InitialHeight:   24,
		ClipboardRead: func() (string, error) {
			return "should not be called", nil
		},
	})

	h.m.showSubjectModal = false
	h.m.showAddendumModal = false
	h.m.showCommandModal = false

	if err := h.Act(HarnessAction{Type: "paste", Text: "x"}); err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	s := h.Observe()
	if s.ToastMessage != "No active text input" {
		t.Errorf("expected toast %q, got %q", "No active text input", s.ToastMessage)
	}
}
