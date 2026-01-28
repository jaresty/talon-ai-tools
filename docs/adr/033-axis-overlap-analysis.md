# Axis Overlap Analysis (ADR 033)

Manual, qualitative assessment of ambiguous adjectives using ADR 033 methods (substitution, conflict-stress, meaning decomposition). Outcomes assign each token to a fixed category or note replacement guidance.

## Tokens reviewed and decisions

- **skim** — Hits completeness (light pass) and scope (narrow). Decision: Treat as *completeness*; add prefix if mixed.  
- **gist** — Completeness vs. style (short). Decision: *Completeness*; use “short” for style.  
- **max** — Completeness vs. method (effort). Decision: *Completeness*.  
- **deep** — Completeness vs. method (depth of reasoning). Decision: *Completeness*.  
- **focus/focused** — Scope vs. style/conciseness. Decision: *Scope*; use “concise” for style.  
- **system** — Scope vs. method. Decision: *Scope* (target = system-level).  
- **actions** — Scope vs. form. Decision: *Form* (action list format); use "act" for scope.  
- **steps** — Method vs. form (bulleted). Decision: *Form* (step-by-step format); use "flow" for method.  
- **structure** — Method vs. scope vs. style. Decision: *Method* (organising reasoning).  
- **flow** — Method vs. scope vs. style. Decision: *Method* (sequence/temporal reasoning).  
- **samples** — Method vs. style. Decision: *Method* (generation strategy).  
- **headline** — Method vs. style vs. completeness. Decision: *Style* (presentation order).  
- **socratic** — Method vs. form. Decision: *Form* (question-led dialogue format).  
- **direct/indirect** — Method vs. form. Decision: *Form* (communication style).  
- **plain** — Method vs. style. Decision: *Style* (register).  
- **tight/compact** — Completeness vs. style. Decision: *Style* (concise form); for dense content use “dense” under completeness.  
- **bullets** — Style vs. scope. Decision: *Style* (format).  
- **table** — Style vs. completeness. Decision: *Style* (container); for coverage, specify completeness separately.  
- **faq** — Style vs. completeness. Decision: *Style* (container).  
- **announce** — Style vs. method. Decision: *Style* (container).  
- **debugging** — Method vs. scope vs. style. Decision: *Method* (process).  
- **mapping** — Method vs. style. Decision: *Method* (representational approach).  
- **analysis** — Method vs. scope. Decision: *Method* (analytic stance).  
- **liberating** — Method vs. scope vs. style. Decision: *Method* (facilitation pattern).  
- **taxonomy** — Method vs. completeness vs. style. Decision: *Method* (structuring approach).  
- **bug** — Style vs. method vs. scope. Decision: *Style* (container/report).  
- **codetour** — Style vs. scope. Decision: *Style* (output schema).  
- **gherkin** — Style vs. scope. Decision: *Style* (output schema).  
- **shellscript** — Style vs. scope. Decision: *Style* (output schema).  
- **presenterm** — Style vs. scope. Decision: *Style* (output schema).

## Notes and guidance

- Use prefixes (`Completeness:`, `Method:`, `Scope:`, `Style:`) when applying tokens outside their default axis.  
- Replace ambiguous style/completeness blends with atomic pairs (e.g., `Style:concise` + `Completeness:full`).  
- When a static profile needs a cross-axis flavor (e.g., “deep” for thoroughness), express it with the chosen category and an explicit prefix.  
- Consider adding lint/tests to keep profiles and help text aligned with these fixed-category decisions.***
