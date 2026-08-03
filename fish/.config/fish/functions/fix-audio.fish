function fix-audio --description 'Diagnose/repair WSLg audio (PulseAudio) for /voice'
    # sox/rec default to ALSA, which has no sound card under WSL. Force the
    # PulseAudio backend so recording reaches WSLg's audio bridge. NB: the
    # driver is named `pulseaudio` here — `pulse` is rejected and falls back
    # to ALSA, which is the "no recorder" failure this helper exists to fix.
    set -gx AUDIODRIVER pulseaudio

    if pactl info >/dev/null 2>&1
        echo "✅ WSLg audio is healthy — PulseAudio is reachable."
        pactl list short sources 2>/dev/null
        echo
        echo "If /voice still can't find a recorder, run: rec -d /tmp/mic-test.wav trim 0 1"
        return 0
    end

    echo "❌ WSLg PulseAudio is not responding."
    echo "   Socket exists ($PULSE_SERVER) but the server refuses connections —"
    echo "   the classic stale-socket state after the Windows host sleeps/resumes."
    echo
    echo "   Only a full WSLg restart revives it. This can't be fixed from inside"
    echo "   the distro (WSLg's audio server lives in the system distro)."
    echo
    read -l -P "Run 'wsl.exe --shutdown' now? This CLOSES ALL WSL sessions (incl. tmux). [y/N] " ans
    switch $ans
        case y Y yes
            echo "Shutting down WSL… reopen your terminal, then run 'fix-audio' to confirm."
            wsl.exe --shutdown
        case '*'
            echo "Skipped. When ready: run 'wsl.exe --shutdown', reopen a terminal, then 'fix-audio'."
    end
    return 1
end
