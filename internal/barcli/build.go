package barcli

import (
	"errors"
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/tokens"
)

const (
	errorUnknownToken   = "unknown_token"
	errorConflict       = "conflict"
	errorPresetConflict = "preset_conflict"
	errorFormat         = "format"
	errorMissingStatic  = "missing_static"
)

// BuildResult captures the structured output of `bar build`.
type BuildResult struct {
	SchemaVersion       string              `json:"schema_version"`
	Subject             string              `json:"subject"`
	Task                string              `json:"task"`
	Constraints         []string            `json:"constraints"`
	HydratedConstraints []HydratedPromptlet `json:"hydrated_constraints"`
	Axes                AxesResult          `json:"axes"`
	Persona             PersonaResult       `json:"persona,omitempty"`
	HydratedPersona     []HydratedPromptlet `json:"hydrated_persona,omitempty"`
	Tokens              []string            `json:"tokens,omitempty"`
	PlainText           string              `json:"-"`
}

type AxesResult struct {
	Static       string   `json:"static"`
	Completeness string   `json:"completeness,omitempty"`
	Scope        []string `json:"scope,omitempty"`
	Method       []string `json:"method,omitempty"`
	Form         []string `json:"form,omitempty"`
	Channel      []string `json:"channel,omitempty"`
	Directional  string   `json:"directional,omitempty"`
}

type PersonaResult struct {
	Preset      string `json:"preset,omitempty"`
	PresetLabel string `json:"preset_label,omitempty"`
	Voice       string `json:"voice,omitempty"`
	Audience    string `json:"audience,omitempty"`
	Tone        string `json:"tone,omitempty"`
	Intent      string `json:"intent,omitempty"`
}

type HydratedPromptlet struct {
	Axis        string `json:"axis"`
	Token       string `json:"token"`
	Description string `json:"description"`
}

type buildState struct {
	grammar *Grammar

	static         string
	staticExplicit bool

	completeness         string
	completenessExplicit bool

	scope       []string
	method      []string
	form        []string
	channel     []string
	directional string

	personaPreset      string
	personaPresetLabel string
	personaVoice       string
	personaAudience    string
	personaTone        string
	personaIntent      string

	overrideMode bool

	recognized          map[string][]string
	unrecognized        []string
	hydratedConstraints []HydratedPromptlet
	hydratedPersona     []HydratedPromptlet
}

func newBuildState(g *Grammar) *buildState {
	static := g.Hierarchy.Defaults.StaticPrompt
	if static == "" {
		static = "infer"
	}
	completeness := g.Hierarchy.Defaults.Completeness
	return &buildState{
		grammar:      g,
		static:       static,
		completeness: completeness,
		scope:        []string{},
		method:       []string{},
		form:         []string{},
		channel:      []string{},
		recognized:   make(map[string][]string),
	}
}

func (s *buildState) requireSlugInput(canonical, source string) *CLIError {
	if s == nil || s.grammar == nil {
		return nil
	}
	canonical = strings.TrimSpace(canonical)
	source = strings.TrimSpace(source)
	if canonical == "" || source == "" {
		return nil
	}
	if idx := strings.Index(canonical, "="); idx >= 0 {
		value := strings.TrimSpace(canonical[idx+1:])
		if value == "" {
			return nil
		}
	}
	slug := s.grammar.slugForToken(canonical)
	normalizedSlug := strings.ToLower(strings.TrimSpace(slug))
	normalizedSource := strings.ToLower(source)
	canonicalNormalized := strings.ToLower(canonical)

	if strings.Contains(canonical, "=") {
		if normalizedSource == canonicalNormalized {
			return nil
		}
	}

	if normalizedSource == normalizedSlug && normalizedSlug != "" {
		return nil
	}
	if canonicalNormalized == normalizedSlug && normalizedSlug != "" {
		return nil
	}
	if normalizedSource == canonicalNormalized {
		s.unrecognized = append(s.unrecognized, source)
		reason := slug
		if reason == "" {
			reason = canonical
		}
		return s.fail(&CLIError{
			Type:         errorUnknownToken,
			Message:      fmt.Sprintf("token %q must use slug %q", source, reason),
			Unrecognized: append([]string{}, s.unrecognized...),
			Recognized:   s.cloneRecognized(),
		})
	}
	return nil
}

// Build assembles the canonical prompt recipe from the supplied tokens.
func Build(g *Grammar, tokens []string) (*BuildResult, *CLIError) {
	var normalizedTokens []NormalizedToken
	if os.Getenv("BAR_DISABLE_MULTIWORD") != "1" {
		normalizedTokens = g.NormalizeTokensWithSource(tokens)
	} else {
		normalizedTokens = make([]NormalizedToken, 0, len(tokens))
		for _, raw := range tokens {
			trimmed := strings.TrimSpace(raw)
			if trimmed == "" {
				continue
			}
			normalizedTokens = append(normalizedTokens, NormalizedToken{
				Canonical: trimmed,
				Source:    trimmed,
			})
		}
	}
	state := newBuildState(g)

	filtered := make([]NormalizedToken, 0, len(normalizedTokens))
	for _, entry := range normalizedTokens {
		if _, ok := parseSkipStage(entry.Canonical); ok {
			continue
		}
		filtered = append(filtered, entry)
	}
	normalizedTokens = filtered

	for _, entry := range normalizedTokens {
		token := strings.TrimSpace(entry.Canonical)
		if token == "" {
			continue
		}

		if !state.overrideMode {

			if strings.HasPrefix(token, "persona=") {
				preset := strings.TrimSpace(strings.TrimPrefix(token, "persona="))
				if preset == "" {
					return nil, state.errorf(errorFormat, "persona preset requires a value")
				}

				if err := state.applyPersonaPreset(preset, false); err != nil {
					return nil, err
				}
				continue
			}
			if strings.Contains(token, "=") {
				state.overrideMode = true
			} else {
				if err := state.applyShorthandToken(token); err != nil {
					return nil, err
				}
				continue
			}
		}

		if err := state.applyOverrideToken(token); err != nil {
			return nil, err
		}
	}

	if err := state.finalise(); err != nil {
		return nil, err
	}

	return state.toResult(), nil
}

func (s *buildState) applyShorthandToken(token string) *CLIError {
	if s.isStaticPrompt(token) {
		if s.staticExplicit {
			return s.errorf(errorConflict, "multiple static prompt tokens provided")
		}
		s.static = token
		s.staticExplicit = true
		s.addRecognized("static", token)
		return nil
	}

	if axis, ok := s.resolveAxisToken(token); ok {
		return s.applyShorthandAxis(axis, token)
	}

	if axis, ok := s.resolvePersonaToken(token); ok {
		return s.applyPersonaAxis(axis, token, false)
	}

	// Check if token is a persona preset (no persona= prefix required)
	if _, _, ok := s.grammar.ResolvePersonaPreset(token); ok {
		return s.applyPersonaPreset(token, false)
	}

	s.unrecognized = append(s.unrecognized, token)
	return s.fail(&CLIError{
		Type:         errorUnknownToken,
		Message:      "unrecognized token",
		Unrecognized: append([]string{}, s.unrecognized...),
		Recognized:   s.cloneRecognized(),
	})
}

func (s *buildState) applyOverrideToken(token string) *CLIError {
	ctx := tokens.OverrideContext{
		IsStaticPrompt: s.isStaticPrompt,
		IsAxisToken:    s.isAxisToken,
		AxisCap:        s.axisCap,
		SplitList:      s.splitValueList,
		Contains:       contains,
		AddRecognized:  s.addRecognized,
		Errorf: func(kind, format string, args ...any) error {
			return s.errorf(kind, format, args...)
		},
		UnknownValue: func(axis, value string) error {
			return s.unknownValue(axis, value)
		},
		ApplyPersona: func(axis, value string, override bool) error {
			return s.applyPersonaAxis(axis, value, override)
		},
		SetStatic: func(value string) error {
			s.static = value
			s.staticExplicit = true
			return nil
		},
		SetCompleteness: func(value string) error {
			s.completeness = value
			s.completenessExplicit = true
			return nil
		},
		SetScope: func(values []string) error {
			s.scope = append([]string(nil), values...)
			return nil
		},
		SetMethod: func(values []string) error {
			s.method = append([]string(nil), values...)
			return nil
		},
		SetForm: func(value string) error {
			s.form = []string{value}
			return nil
		},
		SetChannel: func(value string) error {
			s.channel = []string{value}
			return nil
		},
		SetDirectional: func(value string) error {
			s.directional = value
			return nil
		},
	}

	if err := tokens.ApplyOverride(ctx, token); err != nil {
		var cliErr *CLIError
		if errors.As(err, &cliErr) {
			return cliErr
		}
		return s.errorf(errorFormat, err.Error())
	}
	return nil
}

func (s *buildState) applyShorthandAxis(axis, token string) *CLIError {
	switch axis {
	case "completeness":
		if s.completenessExplicit {
			return s.errorf(errorConflict, "multiple completeness tokens provided")
		}
		s.completeness = token
		s.completenessExplicit = true
	case "scope":
		if contains(s.scope, token) {
			return nil
		}
		cap := s.axisCap(axis)
		if cap > 0 && len(s.scope) >= cap {
			return s.errorf(errorConflict, "scope supports at most %d tokens", cap)
		}
		s.scope = append(s.scope, token)
	case "method":
		if contains(s.method, token) {
			return nil
		}
		cap := s.axisCap(axis)
		if cap > 0 && len(s.method) >= cap {
			return s.errorf(errorConflict, "method supports at most %d tokens", cap)
		}
		s.method = append(s.method, token)
	case "form":
		if len(s.form) > 0 {
			return s.errorf(errorConflict, "form accepts a single token")
		}
		s.form = append(s.form, token)
	case "channel":
		if len(s.channel) > 0 {
			return s.errorf(errorConflict, "channel accepts a single token")
		}
		s.channel = append(s.channel, token)
	case "directional":
		if s.directional != "" {
			return s.errorf(errorConflict, "directional accepts a single token")
		}
		s.directional = token
	default:
		return s.unknownValue(axis, token)
	}

	s.addRecognized(axis, token)
	return nil
}

func (s *buildState) applyPersonaPreset(value string, override bool) *CLIError {
	if override {
		return s.errorf(errorPresetConflict, "persona presets must appear before overrides")
	}
	if s.personaPreset != "" {
		return s.errorf(errorPresetConflict, "multiple persona presets supplied")
	}
	key, preset, ok := s.grammar.ResolvePersonaPreset(value)
	if !ok {
		return s.unknownValue("persona", value)
	}
	s.personaPreset = key
	s.personaPresetLabel = strings.TrimSpace(preset.Label)
	if preset.Voice != nil {
		v := strings.TrimSpace(*preset.Voice)
		if v != "" {
			s.personaVoice = v
			s.addRecognized("voice", v)
		}
	}
	if preset.Audience != nil {
		a := strings.TrimSpace(*preset.Audience)
		if a != "" {
			s.personaAudience = a
			s.addRecognized("audience", a)
		}
	}
	if preset.Tone != nil {
		t := strings.TrimSpace(*preset.Tone)
		if t != "" {
			s.personaTone = t
			s.addRecognized("tone", t)
		}
	}
	s.addRecognized("persona_preset", key)
	return nil
}

func (s *buildState) applyPersonaAxis(axis, token string, override bool) *CLIError {
	if axis == "intent" && !s.isPersonaToken(axis, token) {
		return s.unknownValue(axis, token)
	}
	if axis != "intent" && !s.isPersonaToken(axis, token) {
		return s.unknownValue(axis, token)
	}

	switch axis {
	case "voice":
		if s.personaVoice != "" && !override {
			return s.errorf(errorConflict, "voice provided multiple times in shorthand")
		}
		s.personaVoice = token
	case "audience":
		if s.personaAudience != "" && !override {
			return s.errorf(errorConflict, "audience provided multiple times in shorthand")
		}
		s.personaAudience = token
	case "tone":
		if s.personaTone != "" && !override {
			return s.errorf(errorConflict, "tone provided multiple times in shorthand")
		}
		s.personaTone = token
	case "intent":
		if s.personaIntent != "" && !override {
			return s.errorf(errorConflict, "intent provided multiple times in shorthand")
		}
		s.personaIntent = token
	default:
		return s.unknownValue(axis, token)
	}
	s.addRecognized(axis, token)
	return nil
}

func (s *buildState) resolveAxisToken(token string) (string, bool) {
	for _, axis := range s.grammar.Hierarchy.AxisPriority {
		if s.isAxisToken(axis, token) {
			return axis, true
		}
	}
	for axis := range s.grammar.axisTokens {
		if s.isAxisToken(axis, token) {
			return axis, true
		}
	}
	return "", false
}

func (s *buildState) resolvePersonaToken(token string) (string, bool) {
	for axis := range s.grammar.personaTokens {
		if s.isPersonaToken(axis, token) {
			return axis, true
		}
	}
	return "", false
}

func (s *buildState) isAxisToken(axis, token string) bool {
	if axis == "" {
		return false
	}
	set := s.grammar.axisTokens[axis]
	if set == nil {
		return false
	}
	_, ok := set[token]
	return ok
}

func (s *buildState) isPersonaToken(axis, token string) bool {
	set := s.grammar.personaTokens[axis]
	if set == nil {
		return false
	}
	if _, ok := set[token]; ok {
		return true
	}
	if _, ok := set[strings.ToLower(token)]; ok {
		return true
	}
	return false
}

func (s *buildState) axisCap(axis string) int {
	if cap, ok := s.grammar.Hierarchy.AxisSoftCaps[axis]; ok {
		return cap
	}
	return 0
}

func (s *buildState) isStaticPrompt(token string) bool {
	if token == "" {
		return false
	}
	if _, ok := s.grammar.Static.Profiles[token]; ok {
		return true
	}
	if _, ok := s.grammar.Static.Descriptions[token]; ok {
		return true
	}
	return false
}

func (s *buildState) splitValueList(value string) []string {
	collect := func(segment string) []string {
		words := strings.Fields(segment)
		return s.grammar.NormalizeTokens(words)
	}

	if strings.Contains(value, ",") {
		parts := strings.Split(value, ",")
		out := make([]string, 0, len(parts))
		for _, part := range parts {
			p := strings.TrimSpace(part)
			if p == "" {
				continue
			}
			out = append(out, collect(p)...)
		}
		return out
	}

	return collect(value)
}

func (s *buildState) unknownValue(key, value string) *CLIError {
	msg := "unrecognized token"
	if key != "" {
		msg = "unrecognized token for " + key
	}
	s.unrecognized = append(s.unrecognized, value)
	return s.fail(&CLIError{
		Type:         errorUnknownToken,
		Message:      msg,
		Unrecognized: append([]string{}, s.unrecognized...),
		Recognized:   s.cloneRecognized(),
	})
}

func (s *buildState) fail(err *CLIError) *CLIError {
	if err == nil {
		return nil
	}
	if err.Recognized == nil {
		err.Recognized = s.cloneRecognized()
	}
	if len(err.Unrecognized) == 0 && len(s.unrecognized) > 0 {
		err.Unrecognized = append([]string{}, s.unrecognized...)
	}
	return err
}

func (s *buildState) errorf(errType, format string, args ...any) *CLIError {
	return s.fail(errorf(errType, format, args...))
}

func (s *buildState) addRecognized(bucket string, tokens ...string) {
	if bucket == "" || len(tokens) == 0 {
		return
	}
	existing := s.recognized[bucket]
	for _, token := range tokens {
		if token == "" {
			continue
		}
		if !contains(existing, token) {
			existing = append(existing, token)
		}
	}
	s.recognized[bucket] = existing
}

func (s *buildState) cloneRecognized() map[string][]string {
	out := make(map[string][]string, len(s.recognized))
	for key, tokens := range s.recognized {
		dup := append([]string(nil), tokens...)
		sort.Strings(dup)
		out[key] = dup
	}
	return out
}

func (s *buildState) finalise() *CLIError {
	if s.static == "" {
		return s.errorf(errorMissingStatic, "static prompt missing")
	}
	// Sort scope and method for deterministic output while preserving initial order for text.
	s.scope = dedupeInOrder(s.scope)
	s.method = dedupeInOrder(s.method)

	s.hydratedConstraints = s.buildHydratedConstraints()
	s.hydratedPersona = s.buildHydratedPersona()
	return nil
}

func (s *buildState) buildHydratedConstraints() []HydratedPromptlet {
	entries := make([]HydratedPromptlet, 0, 8)
	add := func(axis string, tokens []string) {
		for _, token := range tokens {
			canonical := strings.TrimSpace(token)
			if canonical == "" {
				continue
			}
			description := s.grammar.AxisDescription(axis, canonical)
			entries = append(entries, HydratedPromptlet{
				Axis:        axis,
				Token:       canonical,
				Description: description,
			})
		}
	}

	if s.completeness != "" {
		add("completeness", []string{s.completeness})
	}
	if len(s.scope) > 0 {
		add("scope", s.scope)
	}
	if len(s.method) > 0 {
		add("method", s.method)
	}
	if len(s.form) > 0 {
		add("form", s.form)
	}
	if len(s.channel) > 0 {
		add("channel", s.channel)
	}
	if s.directional != "" {
		add("directional", []string{s.directional})
	}

	return entries
}

func (s *buildState) buildHydratedPersona() []HydratedPromptlet {
	entries := make([]HydratedPromptlet, 0, 5)
	if s.personaPreset != "" {
		description := s.personaPresetLabel
		if description == "" {
			if preset, ok := s.grammar.Persona.Presets[s.personaPreset]; ok {
				description = strings.TrimSpace(preset.Label)
			}
		}
		entries = append(entries, HydratedPromptlet{
			Axis:        "persona_preset",
			Token:       s.personaPreset,
			Description: description,
		})
	}
	add := func(axis, token string) {
		canonical := strings.TrimSpace(token)
		if canonical == "" {
			return
		}
		description := s.grammar.PersonaDescription(axis, canonical)
		entries = append(entries, HydratedPromptlet{
			Axis:        axis,
			Token:       canonical,
			Description: description,
		})
	}

	if s.personaVoice != "" {
		add("voice", s.personaVoice)
	}
	if s.personaAudience != "" {
		add("audience", s.personaAudience)
	}
	if s.personaTone != "" {
		add("tone", s.personaTone)
	}
	if s.personaIntent != "" {
		add("intent", s.personaIntent)
	}

	return entries
}

func (s *buildState) toResult() *BuildResult {
	description := s.grammar.StaticPromptDescription(s.static)
	if description == "" {
		description = s.static
	}
	task := "Task:\n  " + description

	constraints := make([]string, 0, len(s.hydratedConstraints))
	for _, entry := range s.hydratedConstraints {
		constraints = append(constraints, formatPromptlet(entry))
	}

	persona := PersonaResult{}
	if s.personaPreset != "" {
		persona.Preset = s.personaPreset
		label := s.personaPresetLabel
		if label == "" {
			if preset, ok := s.grammar.Persona.Presets[s.personaPreset]; ok {
				label = strings.TrimSpace(preset.Label)
			}
		}
		if label != "" {
			persona.PresetLabel = label
		}
	}
	if s.personaVoice != "" {
		persona.Voice = s.personaVoice
	}
	if s.personaAudience != "" {
		persona.Audience = s.personaAudience
	}
	if s.personaTone != "" {
		persona.Tone = s.personaTone
	}
	if s.personaIntent != "" {
		persona.Intent = s.personaIntent
	}

	result := &BuildResult{
		SchemaVersion: s.grammar.SchemaVersion,
		Task:          task,
		Constraints:   constraints,
		Axes: AxesResult{
			Static:       s.static,
			Completeness: s.completeness,
			Scope:        cloneSlice(s.scope),
			Method:       cloneSlice(s.method),
			Form:         cloneSlice(s.form),
			Channel:      cloneSlice(s.channel),
			Directional:  s.directional,
		},
	}

	if persona != (PersonaResult{}) {
		result.Persona = persona
	}
	if len(s.hydratedConstraints) > 0 {
		result.HydratedConstraints = append([]HydratedPromptlet(nil), s.hydratedConstraints...)
	}
	if len(s.hydratedPersona) > 0 {
		result.HydratedPersona = append([]HydratedPromptlet(nil), s.hydratedPersona...)
	}

	return result
}

func formatPromptlet(p HydratedPromptlet) string {
	axis := axisHeading(p.Axis)
	token := strings.TrimSpace(p.Token)
	description := strings.TrimSpace(p.Description)

	switch {
	case token != "" && description != "":
		return fmt.Sprintf("%s (%s): %s", axis, token, description)
	case token != "":
		return fmt.Sprintf("%s: %s", axis, token)
	case description != "":
		return fmt.Sprintf("%s: %s", axis, description)
	default:
		return axis
	}
}

func axisHeading(axis string) string {
	axis = strings.TrimSpace(axis)
	if axis == "" {
		return ""
	}
	switch axis {
	case "persona_preset":
		return "Persona preset"
	default:
		return strings.ToUpper(axis[:1]) + axis[1:]
	}
}

func dedupeInOrder(in []string) []string {
	if len(in) == 0 {
		return in
	}
	out := make([]string, 0, len(in))
	seen := make(map[string]struct{})
	for _, token := range in {
		if _, ok := seen[token]; ok {
			continue
		}
		seen[token] = struct{}{}
		out = append(out, token)
	}
	return out
}

func cloneSlice(in []string) []string {
	if len(in) == 0 {
		return nil
	}
	out := make([]string, len(in))
	copy(out, in)
	return out
}

func contains(list []string, token string) bool {
	for _, item := range list {
		if item == token {
			return true
		}
	}
	return false
}
