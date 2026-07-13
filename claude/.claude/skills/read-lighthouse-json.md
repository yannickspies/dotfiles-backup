---
name: read-lighthouse-json
description: Analyze Lighthouse JSON reports — extract key metrics (CLS, LCP, FCP, TBT, Performance), layout shift culprits, LCP element, and document size. Supports single file or multi-file comparison.
user_invocable: true
---

Analyze Lighthouse JSON report(s) using the Python script at `~/.claude/scripts/read-lighthouse-json.py`.

## Usage

The user provides one or more file paths as arguments (or describes which files to analyze). The script outputs a markdown table with key Web Vitals metrics.

## Steps

1. Identify the Lighthouse JSON file(s) to analyze from the user's arguments or by searching the current directory for Lighthouse JSON files.
2. Run the script:
   ```bash
   python3 ~/.claude/scripts/read-lighthouse-json.py <file1> [file2] [file3...]
   ```
   - Single file: outputs a detailed metrics table
   - Multiple files: outputs a side-by-side comparison table
3. Present the output to the user as-is (it's already markdown formatted).
4. If the user didn't specify files, look for JSON files in the current working directory that look like Lighthouse reports (contain `lighthouseVersion` in the first few bytes).

## Notes

- The script only works with Lighthouse **JSON** format (not HTML reports).
- For HTML Lighthouse reports, the JSON is embedded in a `<script>` tag — extract it first if needed.
- Key metrics extracted: Performance score, FCP, LCP, CLS, TBT, Speed Index, LCP element, layout shift elements, document size.
