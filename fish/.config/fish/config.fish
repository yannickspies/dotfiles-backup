if status is-interactive
    set -gx CHROME_BIN /usr/bin/chromium-browser
    set -gx EDITOR nvim
    set -gx VISUAL nvim
    
    # Set TERM_PROGRAM for WSL (WezTerm on Windows doesn't pass env vars through)
    if not set -q TERM_PROGRAM; and test -f /proc/sys/fs/binfmt_misc/WSLInterop
        set -gx TERM_PROGRAM WezTerm
    end

    # Use Node LTS version on startup
    nvm use lts

    # Start tmux if not already in a tmux session
    if not set -q TMUX
        tmux
    end
end
