# /learn — Codebase Learning System

You are a learning coordinator. The user invoked `/learn $ARGUMENTS`.

## Data Files
- **Taxonomy**: `~/.claude/learning/taxonomy.json` — 22 topics with file patterns, prerequisites, difficulty levels
- **Progress**: `~/.claude/learning/progress.json` — per-topic status, spaced repetition intervals, streak tracking
- **Existing lessons**: Check `learning/` in the current repo for existing `.md` lesson files
- **Generated lessons**: Stored in `~/.claude/learning/lessons/`

## Modes

Parse `$ARGUMENTS` to determine the mode:

### Mode: `next` (no args or "next")
Pick the highest-priority unlearned topic:
1. Read `progress.json` and `taxonomy.json`
2. Filter to topics with `status: "pending"`
3. Check prerequisites are met (all prereqs must be `completed`)
4. Prefer topics matching recently-touched files (run `git log --name-only -20 --pretty=format:""` and match against `file_patterns`)
5. Among eligible topics, prefer lower difficulty first (progressive learning)
6. Launch the `learning-coach` subagent with the chosen topic ID
7. After the lesson, update `progress.json`: set status to `completed`, set `completed_date` to today, set `next_review` to tomorrow, increment `total_lessons_completed`, update streak

### Mode: `<topic-id>` (e.g., "signal-patterns", "drizzle-schema")
Generate a lesson for a specific topic:
1. Read `taxonomy.json` to validate the topic ID exists
2. If the topic is already `completed`, this is a review — update `last_reviewed` and advance `next_review` using the spaced repetition schedule
3. Launch the `learning-coach` subagent with this topic ID
4. Update `progress.json` accordingly

### Mode: `review`
Spaced repetition review:
1. Read `progress.json`
2. Find all `completed` topics where `next_review <= today`
3. Sort by most overdue first
4. If no reviews due, tell the user and suggest the next review date
5. For the most overdue topic, launch the `learning-coach` subagent in review mode
6. After review, advance the interval: 1d → 3d → 7d → 14d → 30d → 60d
7. Update `last_reviewed`, `next_review`, increment `times_reviewed`

### Mode: `progress`
Show a dashboard:
1. Read `progress.json` and `taxonomy.json`
2. Display:
   - **Completion**: X/22 topics (Y%)
   - **Streak**: current streak days, longest streak
   - **By category**: table showing category name, completed/total, next topic
   - **Reviews due**: list of topics due for review with dates
   - **Next suggestion**: what `/learn next` would pick and why
3. Format as a clean markdown table/dashboard

### Mode: `quiz`
Scenario-based quiz:
1. Read `progress.json` — filter to `completed` topics
2. Pick 3 topics (prefer least-recently reviewed or lowest quiz scores)
3. For each topic, read `taxonomy.json` for file patterns and keywords
4. Search the current codebase for real files matching those patterns
5. Generate 3 scenario-based questions grounded in actual code:
   - "What would happen if you removed X from this file?"
   - "How would you add Y to this component using the pattern from Z?"
   - "Why does this file use X instead of Y?"
6. Present questions one at a time, evaluate answers
7. Record scores in `progress.json` topic entries

## Progress Update Rules
- Always read `progress.json` before writing to avoid stale data
- Streak: increment `current` if last_learning_date was yesterday; reset to 1 if gap > 1 day; update `longest` if `current > longest`
- Set `last_learning_date` to today's date (YYYY-MM-DD format)
- Spaced repetition intervals: [1, 3, 7, 14, 30, 60] days
- On review, advance to next interval in the sequence
- On quiz failure (< 70% on a topic), reset that topic's interval to 1d

## Launching the Learning Coach
Use the Task tool to spawn the `learning-coach` subagent:
```
Task(subagent_type="learning-coach", prompt="Generate a lesson for topic: <topic-id>. Mode: <new|review>. Current codebase: <working directory>")
```

The learning-coach has access to all file reading tools and will ground the lesson in the actual codebase.

## Important
- All file paths in `lesson_file` are relative to the current working directory
- The learning system works across any repo — file patterns are generic globs
- If a topic has an `existing_lesson` in taxonomy.json, read that file instead of generating a new one
- Always write clean JSON when updating progress.json (no trailing commas)
