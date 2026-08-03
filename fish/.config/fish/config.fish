if status is-interactive
    set -gx CHROME_BIN /usr/bin/chromium-browser
    set -gx EDITOR nvim
    set -gx VISUAL nvim

    # Advertise 24-bit color for apps that gate on COLORTERM rather than terminfo.
    # Windows Terminal supports truecolor but doesn't export this itself.
    set -gx COLORTERM truecolor

    # sox/rec default to ALSA (no sound card under WSL) — force PulseAudio so
    # /voice's recorder detection reaches WSLg's audio bridge. See `fix-audio`.
    # NB: this SoX build names the driver `pulseaudio`, not `pulse` (which it
    # rejects, silently falling back to ALSA → "no recorder").
    set -gx AUDIODRIVER pulseaudio

    # Use Node LTS version on startup
    nvm use lts

    # Start tmux if not already in a tmux session
    if not set -q TMUX
        tmux
    end
end
