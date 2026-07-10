function claude --wraps claude --description "Guard: nudge feature work into a git worktree (ccw) when launched in a repo's primary tree"
    # Why this exists: opening a new tmux tab lands you in the SAME working tree,
    # and a second bare `claude` there shares one checkout with the first session —
    # commits and Drizzle migrations entangle, and a sibling's `git checkout` can
    # make your next commit land on the wrong branch (both bit us for real).
    # `ccw` already gives isolated worktrees; this wrapper just makes sure the
    # choice is in front of you at launch instead of silently sharing the tree.

    # Only guard the bare interactive launch — the exact habit that causes it.
    # `claude --resume`, `claude -p …`, `claude mcp …`, etc. pass straight through.
    if test (count $argv) -gt 0
        command claude $argv
        return
    end

    set -l main (git worktree list --porcelain 2>/dev/null | string match -rg '^worktree (.+)' | head -1)
    set -l top (git rev-parse --show-toplevel 2>/dev/null)

    # Not in a repo, or already inside an isolated .worktrees/<branch> → no friction.
    if test -z "$main"; or test "$top" != "$main"
        command claude
        return
    end

    # In the primary tree. Your rule: a question or quick bugfix can stay on the
    # current branch; every new feature gets its own worktree. So make it a choice.
    set -l branch (git rev-parse --abbrev-ref HEAD 2>/dev/null)
    echo "⚠️  Primary working tree ($main, on '$branch')."
    echo "    A second live session here shares this checkout — commits & migrations entangle."
    read -l -P "Branch for an isolated worktree (Enter to stay on '$branch'): " wt
    if test -n "$wt"
        ccw new $wt
    else
        command claude
    end
end
