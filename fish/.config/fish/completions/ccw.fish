# Completions for ccw (Claude Code Worktree)

function __ccw_needs_command
    set -l cmd (commandline -opc)
    test (count $cmd) -eq 1
end

function __ccw_using
    set -l cmd (commandline -opc)
    test (count $cmd) -ge 2; and contains -- $cmd[2] $argv
end

# Existing worktree branch names, derived from git worktree list.
function __ccw_worktree_branches
    git worktree list --porcelain 2>/dev/null \
        | string match -rg '^branch refs/heads/(.+)'
end

# Subcommands
complete -c ccw -f
complete -c ccw -n __ccw_needs_command -a new   -d 'Create worktree + launch claude'
complete -c ccw -n __ccw_needs_command -a ls    -d 'List worktrees'
complete -c ccw -n __ccw_needs_command -a cd    -d 'cd into a worktree'
complete -c ccw -n __ccw_needs_command -a merge -d 'Merge a worktree branch back'
complete -c ccw -n __ccw_needs_command -a rm    -d 'Remove a worktree'
complete -c ccw -n __ccw_needs_command -a help  -d 'Show help'

# cd / rm / merge take an existing worktree branch name
complete -c ccw -n '__ccw_using cd rm remove merge' -a '(__ccw_worktree_branches)'
# new takes any existing local branch (or a fresh name)
complete -c ccw -n '__ccw_using new n' -a '(git branch --format="%(refname:short)" 2>/dev/null)'
