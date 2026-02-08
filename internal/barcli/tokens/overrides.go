package tokens

import "strings"

// OverrideContext provides the host state required to apply CLI overrides
// without depending on the concrete buildState implementation.
type OverrideContext struct {
	IsTask  func(string) bool
	IsAxisToken     func(axis, value string) bool
	AxisCap         func(axis string) int
	SplitList       func(value string) []string
	Contains        func(list []string, value string) bool
	AddRecognized   func(axis string, values ...string)
	Errorf          func(kind, format string, args ...any) error
	UnknownValue    func(axis, value string) error
	ApplyPersona    func(axis, value string, override bool) error
	SetTask       func(value string) error
	SetCompleteness func(value string) error
	SetScope        func(values []string) error
	SetMethod       func(values []string) error
	SetForm         func(value string) error
	SetChannel      func(value string) error
	SetDirectional  func(value string) error
}

// ApplyOverride applies a single key=value override using the provided context.
func ApplyOverride(ctx OverrideContext, token string) error {
	idx := strings.Index(token, "=")
	if idx <= 0 || idx == len(token)-1 {
		return ctx.Errorf("format", "key=value override expected")
	}
	key := strings.TrimSpace(token[:idx])
	value := strings.TrimSpace(token[idx+1:])
	if value == "" {
		return ctx.Errorf("format", "override for %s missing value", key)
	}

	switch key {
	case "persona":
		return ctx.Errorf("preset_conflict", "persona presets must appear before overrides")

	case "task":
		if !ctx.IsTask(value) {
			return ctx.UnknownValue(key, value)
		}
		if err := ctx.SetTask(value); err != nil {
			return err
		}
		ctx.AddRecognized("task", value)
		return nil
	case "completeness":
		if !ctx.IsAxisToken("completeness", value) {
			return ctx.UnknownValue(key, value)
		}
		if err := ctx.SetCompleteness(value); err != nil {
			return err
		}
		ctx.AddRecognized("completeness", value)
		return nil
	case "scope":
		tokens := ctx.SplitList(value)
		if len(tokens) == 0 {
			return ctx.Errorf("format", "scope override requires at least one token")
		}
		processed := make([]string, 0, len(tokens))
		for _, item := range tokens {
			if !ctx.IsAxisToken("scope", item) {
				return ctx.UnknownValue(key, item)
			}
			if !ctx.Contains(processed, item) {
				processed = append(processed, item)
			}
		}
		if cap := ctx.AxisCap("scope"); cap > 0 && len(processed) > cap {
			return ctx.Errorf("conflict", "scope supports at most %d tokens", cap)
		}
		if err := ctx.SetScope(processed); err != nil {
			return err
		}
		ctx.AddRecognized("scope", processed...)
		return nil
	case "method":
		tokens := ctx.SplitList(value)
		if len(tokens) == 0 {
			return ctx.Errorf("format", "method override requires at least one token")
		}
		processed := make([]string, 0, len(tokens))
		for _, item := range tokens {
			if !ctx.IsAxisToken("method", item) {
				return ctx.UnknownValue(key, item)
			}
			if !ctx.Contains(processed, item) {
				processed = append(processed, item)
			}
		}
		if cap := ctx.AxisCap("method"); cap > 0 && len(processed) > cap {
			return ctx.Errorf("conflict", "method supports at most %d tokens", cap)
		}
		if err := ctx.SetMethod(processed); err != nil {
			return err
		}
		ctx.AddRecognized("method", processed...)
		return nil
	case "form":
		tokens := ctx.SplitList(value)
		if len(tokens) == 0 {
			return ctx.Errorf("format", "form override requires a value")
		}
		if len(tokens) > 1 {
			return ctx.Errorf("conflict", "form accepts a single token")
		}
		if !ctx.IsAxisToken("form", tokens[0]) {
			return ctx.UnknownValue(key, tokens[0])
		}
		if err := ctx.SetForm(tokens[0]); err != nil {
			return err
		}
		ctx.AddRecognized("form", tokens[0])
		return nil
	case "channel":
		tokens := ctx.SplitList(value)
		if len(tokens) == 0 {
			return ctx.Errorf("format", "channel override requires a value")
		}
		if len(tokens) > 1 {
			return ctx.Errorf("conflict", "channel accepts a single token")
		}
		if !ctx.IsAxisToken("channel", tokens[0]) {
			return ctx.UnknownValue(key, tokens[0])
		}
		if err := ctx.SetChannel(tokens[0]); err != nil {
			return err
		}
		ctx.AddRecognized("channel", tokens[0])
		return nil
	case "directional":
		if !ctx.IsAxisToken("directional", value) {
			return ctx.UnknownValue(key, value)
		}
		if err := ctx.SetDirectional(value); err != nil {
			return err
		}
		ctx.AddRecognized("directional", value)
		return nil
	case "voice", "audience", "tone", "intent":
		return ctx.ApplyPersona(key, value, true)
	default:
		return ctx.Errorf("unknown_token", "unknown override key %s", key)
	}
}
