---
allowed-tools: Bash, Read, Edit, Write, Glob, Grep, TodoWrite
description: Build the app and automatically fix any errors that occur
---

## Context
Detect and run the project's build command, then fix any errors that occur.

## Task
1. First, detect the build system being used by checking for:
   - package.json (npm/yarn/pnpm build scripts)
   - Makefile (make commands)
   - build.sh or similar scripts
   - Other build configuration files (cargo, gradle, etc.)

2. Run the appropriate build command

3. If the build succeeds:
   - Report success to the user

4. If the build fails with errors:
   - Create a todo list with all the errors that need to be fixed
   - Analyze each error carefully
   - Fix each error one by one:
     - Read relevant files
     - Make necessary code changes
     - Mark the error as fixed in the todo list
   - After fixing all errors, re-run the build to verify
   - If new errors appear, repeat the process
   - Continue until the build succeeds or you cannot fix the remaining errors

## Requirements
- Use TodoWrite to track all errors and fixes
- Be thorough in analyzing error messages
- Test the build after making fixes
- If you cannot fix an error, explain why and ask the user for guidance
- Only mark errors as completed after they are actually fixed and verified
