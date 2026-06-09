function claude-scan --description 'Inspect a repo .claude/ config for auto-executing hooks before launching Claude Code'
    set -l target (test -n "$argv[1]"; and echo $argv[1]; or pwd)
    set -l here (dirname (status current-filename))
    python3 "$here/claude-scan.py" "$target"
end
