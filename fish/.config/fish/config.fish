if status is-interactive
    set -gx CHROME_BIN /usr/bin/chromium-browser
    set -gx EDITOR nvim
    set -gx VISUAL nvim

    # Advertise 24-bit color for apps that gate on COLORTERM rather than terminfo.
    # Windows Terminal supports truecolor but doesn't export this itself.
    set -gx COLORTERM truecolor

    # Use Node LTS version on startup
    nvm use lts

    # Start tmux if not already in a tmux session
    if not set -q TMUX
        tmux
    end
end
