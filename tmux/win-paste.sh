#!/bin/sh
# Paste the Windows clipboard into a tmux pane via win32yank, bypassing WezTerm's own
# PasteFrom, which delivers empty bracketed pastes into WSL (wezterm#5368 family).
# Bound to C-v in .tmux.conf. When the clipboard holds no text (an image, say), the
# raw C-v goes through so Claude Code can still read the image itself.
pane="$1"

if ! command -v win32yank.exe >/dev/null 2>&1; then
	tmux display-message "win-paste: win32yank.exe not on PATH, sending raw C-v"
	tmux send-keys -t "$pane" C-v
	exit 0
fi

# A read can come back empty while another process holds the clipboard open, so
# retry briefly before deciding the clipboard really has no text.
txt=""
for _ in 1 2 3 4 5; do
	txt=$(win32yank.exe -o --lf 2>/dev/null)
	[ -n "$txt" ] && break
	sleep 0.1
done

if [ -n "$txt" ]; then
	printf '%s' "$txt" | tmux load-buffer -b winclip - && tmux paste-buffer -p -d -b winclip -t "$pane"
else
	tmux display-message "win-paste: clipboard has no text, sending raw C-v"
	tmux send-keys -t "$pane" C-v
fi
