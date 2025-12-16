---
allowed-tools: Read, Edit, Write, Glob, Grep, Bash(git ls-files:*), Bash(find:*), Bash(wc:*)
argument-hint: [optional: file/directory path]
description: Analyze and clean up messy code: remove comments, extract methods, create reusable components
---

# Clean Code Refactoring

Analyze the codebase and clean up messy, hard-to-maintain code by removing unnecessary comments, extracting long methods, consolidating CSS, and creating reusable components.

## Target Scope

$ARGUMENTS

## Analysis Phase

First, analyze the codebase (or specified path) for code quality issues:

### 1. Comment Analysis
- Find files with excessive comments (especially LLM-added comments)
- Identify comments that should be replaced with self-documenting code
- Look for commented-out code that should be removed
- Find TODO/FIXME comments that need addressing

### 2. Code Complexity
- Identify functions/methods longer than 30 lines
- Find deeply nested code blocks (>3 levels)
- Locate complex conditional logic that needs extraction
- Spot repetitive code patterns

### 3. CSS/Styling Issues
- Find files with inline styles or scattered CSS
- Identify repeated style patterns that should be global
- Look for CSS-in-JS that could use shared theme variables
- Find duplicate style definitions across components

### 4. Component Reusability
- Identify similar components with slight variations
- Find duplicated JSX/template patterns
- Locate copy-pasted code blocks
- Spot opportunities for higher-order components or composition

## Execution Phase

After analysis, systematically refactor the code:

### Priority 1: Remove Unnecessary Comments
- Delete obvious comments (e.g., "// initialize variable")
- Replace explanatory comments with descriptive variable/function names
- Remove commented-out code blocks
- Keep only essential comments (complex algorithms, business logic, warnings)

### Priority 2: Extract Long Functions
- Break down functions >30 lines into smaller, focused functions
- Give extracted functions clear, descriptive names
- Each function should do one thing well
- Improve testability through smaller units

### Priority 3: Consolidate Styles
- Extract repeated CSS to global styles or CSS variables
- Create shared theme constants for colors, spacing, typography
- Move inline styles to CSS classes or styled components
- Establish consistent styling patterns

### Priority 4: Build Reusable Components
- Extract common patterns into reusable components
- Use composition over duplication
- Create prop-driven components for variations
- Document component APIs clearly

## Execution Guidelines

1. **Read Before Edit**: Always read the full file before making changes
2. **One File at a Time**: Complete refactoring one file before moving to the next
3. **Preserve Functionality**: Ensure behavior remains unchanged
4. **Test-Friendly**: Make changes that improve testability
5. **Progressive**: Start with low-risk changes, then tackle complex refactorings
6. **Document**: Brief summary of changes made to each file

## Report Format

After each file refactoring, report:
- File path
- Issues found
- Changes made
- Lines of code removed/simplified
- Any risks or follow-up needed

## Notes

- Focus on maintainability and readability improvements
- Avoid premature optimization
- Preserve existing code style and conventions
- If unsure about a refactoring, explain the trade-offs
- Skip files that are auto-generated or vendored
