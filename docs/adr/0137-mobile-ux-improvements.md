# ADR-0137: Mobile UX Improvements for Bar Prompt Builder

## Status

Accepted

## Context

The Bar Prompt Builder PWA is currently optimized for desktop use but provides a poor experience on mobile devices (iPhones, Android phones). The application was designed with a two-column desktop layout that stacks vertically on mobile, resulting in significant usability issues.

### Current Mobile Problems

1. **Excessive Vertical Scrolling** - The app uses `grid-template-columns: 1fr 340px` which stacks vertically on mobile. Users must scroll past ALL 7 token axis sections (task, completeness, scope, method, form, channel, directional) plus persona selections to reach the preview panel.

2. **Sticky Preview Panel** - The `.preview-panel` uses `position: sticky` which on mobile takes up valuable viewport space without providing the intended utility.

3. **Undersized Touch Targets** - Token chips have `padding: 0.25rem 0.5rem` (~11px height), buttons have `padding: 0.3rem 0.75rem` - both below the recommended 44px minimum for touch interfaces.

4. **Information Overload** - All 7 axis sections are visible simultaneously on mobile, creating a overwhelming interface that requires extensive scrolling.

5. **Cramped Text Inputs** - Textareas for `--subject` (rows=3) and `--addendum` (rows=2) are too small on mobile where the virtual keyboard consumes ~50% of the viewport.

6. **Inline Select Dropdowns** - Persona selects (voice, audience, tone) are laid out in an inline flex wrap that becomes difficult to use on narrow screens.

7. **Token Guidance Hard to Access** - The `.meta-panel` showing `use_when`, description, and guidance is critical for user understanding but displays inline below the token grid. On mobile, users must tap a token to reveal guidance, which may be obscured or require additional scrolling.

## Decision

We will implement the following mobile UX improvements:

### High Priority

1. **Tabbed Axis Interface** - Replace the vertical list of 7 axis sections with a horizontal tab bar (Task | Completeness | Scope | Method | Form | Channel | Directional). Only one axis is visible at a time, dramatically reducing scroll distance.

2. **Token Guidance Accessibility** - Ensure `.meta-panel` showing `use_when`, description, and guidance is fully visible and usable on mobile. Increase font size to minimum 16px for readability, ensure panel isn't cut off by viewport, and verify touch targets for opening/closing are 44px+.

3. **Bottom Sheet for Preview** - On mobile viewports (< 768px), move the preview panel to a slide-up bottom sheet triggered by a "Preview" button. The desktop layout retains the inline sidebar.

4. **Enforce 44px Touch Targets** - Add CSS media queries for viewport < 768px that set `min-height: 44px` on all buttons, token chips, and interactive elements.

### Medium Priority

4. **Collapsible Axis Sections** - Each axis is an accordion that defaults to collapsed on mobile, showing only the axis name and selected token count.

5. **Expanded Textareas** - Increase `rows` attribute to 6+ on mobile; use `flex-grow` to fill available space above the virtual keyboard.

6. **Floating Action Button** - Replace the action row (Copy cmd, Copy prompt, Share, Clear) with a floating "..." menu that expands into an action sheet on mobile.

7. **Stacked Persona Selects** - On mobile, stack persona select dropdowns vertically instead of inline.

## Alternatives Considered

1. **Fully Separate Mobile App** - Rejected: Would require maintaining two codebases and defeats the purpose of PWA.

2. **Responsive Grid Only** - Rejected: Simply stacking the current layout vertically doesn't solve the core problem of having too much content visible at once.

3. **Native App Wrapper (Capacitor)** - Rejected: Adds complexity and removes the simplicity of a web-based PWA.

4. **Progressive Web App Library (PWA Builder)** - Deferred: Could explore in future, but custom CSS is more controllable for this specific use case.

## Consequences

### Positive

- Dramatically reduced scroll distance on mobile
- Improved touch target sizes for accessibility
- Cleaner visual hierarchy with tabbed interface
- Bottom sheet provides quick access to preview without losing context
- Consistent experience across iOS and Android

### Negative

- Additional complexity in CSS for responsive behavior
- Tabbed interface requires state management for active tab
- Bottom sheet implementation requires overlay handling
- Desktop UX must be preserved while adding mobile styles

### Technical Debt

- Need to maintain both desktop and mobile layouts in CSS
- Potential for edge cases in breakpoint detection
- May need to test across multiple mobile browsers

## Implementation Notes

- Use CSS `@media (max-width: 767px)` for mobile breakpoints
- Consider using Svelte's built-in transitions for tab/bottom sheet animations
- Test touch interactions thoroughly on actual iOS and Android devices
- Ensure keyboard accessibility is maintained alongside touch optimizations
