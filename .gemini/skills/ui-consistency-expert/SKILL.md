---
name: ui-consistency-expert
description: Use this skill when the user wants to add new pages, modify existing templates, or create UI components. It ensures that all changes adhere to the "Sarathi Wallet" design language, uses existing CSS variables, extends base.html, and avoids inline styles.
---

# UI Consistency Expert — Sarathi Wallet

You are an expert in the Sarathi Wallet design system. Your goal is to ensure that every new page, component, or UI modification feels like a native part of the application.

## Core Design Principles
1. **Lightweight & Modern**: Clean layouts, generous whitespace, and purposeful typography.
2. **"Paper" Aesthetic**: Use the defined paper-themed background colors and card styles.
3. **Typography First**: Use `DM Serif Display` for headings and `DM Sans` for body text.

## Technical Rules

### 1. Template Structure
- **ALWAYS** extend `templates/base.html`.
- Use blocks correctly: `{% block title %}`, `{% block head %}`, `{% block content %}`, and `{% block scripts %}`.
- Never hardcode navbars or footers; they are handled by `base.html`.

### 2. Styling (CSS)
- **Prefer Vanilla CSS**: Avoid adding external libraries unless requested.
- **CSS Variables**: **NEVER** use hardcoded hex values. Always use the variables defined in `static/css/style.css`.
  - Background: `var(--paper)`, `var(--paper-warm)`, `var(--paper-card)`
  - Text: `var(--ink)`, `var(--ink-soft)`, `var(--ink-muted)`, `var(--ink-faint)`
  - Accents: `var(--accent)`, `var(--accent-light)`, `var(--accent-2)`
  - Borders: `var(--border)`, `var(--border-soft)`
- **Specific Files**: For page-specific styles, create a new CSS file (e.g., `static/css/profile.css`) and include it in the `{% block head %}`.

### 3. Common Components
- **Buttons**: Use `.btn-primary` and `.btn-ghost`.
- **Cards**: Use `.mock-card` or similar structures with `var(--paper-card)`, `var(--radius-md)`, and subtle shadows.
- **Forms**: Use `.form-group`, `.form-input`, and `.btn-submit` classes for consistent input styling.

### 4. Layout
- Use `max-width: var(--max-width)` for page containers to ensure alignment with the navbar.
- Use `grid` or `flex` for layouts; avoid legacy float-based layouts.

## Workflow
1. **Analyze**: Look at existing pages (`landing.html`, `register.html`) to understand the structure.
2. **Draft**: Create the Jinja2 template ensuring all blocks are present.
3. **Style**: Check `style.css` for existing classes before writing new ones.
4. **Refine**: Ensure responsive design using the project's breakpoints (900px, 600px).

## Example: Creating a New Page
```html
{% extends "base.html" %}

{% block title %}New Feature - Sarathi Wallet{% endblock %}

{% block head %}
<link rel="stylesheet" href="{{ url_for('static', path='/css/new-feature.css') }}">
{% endblock %}

{% block content %}
<section class="feature-container">
    <h1 class="feature-title">Feature Title</h1>
    <div class="mock-card">
        <!-- Content here -->
    </div>
</section>
{% endblock %}
```
