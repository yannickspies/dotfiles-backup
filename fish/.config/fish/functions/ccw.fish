function ccw -d "Claude Code Worktree — parallel Claude sessions in isolated git worktrees"
    # Ported from the idea behind craigsc/cmux ("tmux for Claude Code"), adapted to
    # fish/WSL2. Each worktree lives under <primary-root>/.worktrees/<sanitized-branch>/
    # and shares one .git DB — no clones, no stash chaos, no branch collisions.
    # See docs/ccw-worktrees.md for when to use this vs Workflow vs agent-teams.

    set -l cmd $argv[1]
    set -e argv[1]

    # Everything except help needs a git repo. Anchor .worktrees/ on the PRIMARY
    # working tree (first entry of `worktree list`), never the current worktree —
    # otherwise running ccw from inside a worktree would nest .worktrees/ dirs.
    set -l main (git worktree list --porcelain 2>/dev/null | string match -rg '^worktree (.+)' | head -1)
    if test -z "$main"; and test "$cmd" != help; and test -n "$cmd"
        echo "ccw: not inside a git repository" >&2
        return 1
    end

    switch "$cmd"
        case new n
            set -l branch $argv[1]
            if test -z "$branch"
                echo "ccw: usage: ccw new <branch>" >&2
                return 1
            end
            set -l dir "$main/.worktrees/"(string replace -a / - -- $branch)
            if test -d "$dir"
                echo "ccw: worktree already exists at $dir" >&2
                return 1
            end
            # Reuse an existing branch if present, otherwise create it.
            if git show-ref --verify --quiet "refs/heads/$branch"
                git worktree add "$dir" "$branch"; or return 1
            else
                git worktree add "$dir" -b "$branch"; or return 1
            end
            echo "ccw: created $dir on branch '$branch' — launching claude" >&2
            cd "$dir"; and command -q claude; and claude

        case ls list
            git worktree list

        case cd
            set -l branch $argv[1]
            if test -z "$branch"
                echo "ccw: usage: ccw cd <branch>" >&2
                return 1
            end
            set -l dir "$main/.worktrees/"(string replace -a / - -- $branch)
            if test -d "$dir"
                cd "$dir"
            else
                echo "ccw: no worktree for '$branch' (expected $dir)" >&2
                return 1
            end

        case merge
            # Merge a worktree's branch into the primary working tree's branch.
            set -l branch $argv[1]
            if test -z "$branch"
                set branch (git rev-parse --abbrev-ref HEAD)
            end
            echo "ccw: merging '$branch' into "(git -C "$main" rev-parse --abbrev-ref HEAD)" at $main" >&2
            git -C "$main" merge --no-ff "$branch"

        case rm remove
            # Default to the worktree of $PWD when no branch is given.
            set -l branch $argv[1]
            set -l dir
            if test -z "$branch"
                set dir (git rev-parse --show-toplevel)
            else
                set dir "$main/.worktrees/"(string replace -a / - -- $branch)
            end
            if string match -q "*/.worktrees/*" "$dir"
                # cd out before removing the tree we may be standing in.
                test (pwd) = "$dir"; and cd "$main"
                git worktree remove "$dir"; and git worktree prune
                echo "ccw: removed $dir" >&2
            else
                echo "ccw: '$dir' is not a ccw worktree (must be under .worktrees/)" >&2
                return 1
            end

        case '' help -h --help
            printf 'ccw — Claude Code Worktree\n\n'
            printf '  ccw new <branch>    create .worktrees/<branch>, cd in, launch claude\n'
            printf '  ccw ls              list all worktrees\n'
            printf '  ccw cd <branch>     cd into an existing worktree\n'
            printf '  ccw merge [branch]  merge worktree branch into the primary tree (default: current)\n'
            printf '  ccw rm [branch]     remove a worktree (default: current)\n'
            printf '  ccw help            this help\n'

        case '*'
            echo "ccw: unknown subcommand '$cmd' (try: ccw help)" >&2
            return 1
    end
end
