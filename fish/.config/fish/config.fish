if status is-interactive
    set -gx CHROME_BIN /usr/bin/chromium-browser
    set -gx EDITOR nvim
    set -gx VISUAL nvim
    
    # Use Node LTS version on startup
    nvm use lts
    
    # Start tmux if not already in a tmux session
    if not set -q TMUX
        tmux
    end
end
