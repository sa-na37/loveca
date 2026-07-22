#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON:-python3}"
LOVECA_LAUNCH_TTY="$(tty || true)"

close_loveca_terminal_window() {
  if [[ "${LOVECA_KEEP_TERMINAL_OPEN:-0}" == "1" ]]; then
    return 0
  fi
  if [[ -z "${LOVECA_LAUNCH_TTY}" || "${LOVECA_LAUNCH_TTY}" == "not a tty" ]]; then
    return 0
  fi

  case "${TERM_PROGRAM:-}" in
    Apple_Terminal)
      osascript >/dev/null 2>&1 <<OSA || true
tell application "Terminal"
  repeat with w in windows
    repeat with t in tabs of w
      try
        if (tty of t) is "${LOVECA_LAUNCH_TTY}" then
          if (count of tabs of w) is 1 then
            close w
          else
            close t
          end if
          return
        end if
      end try
    end repeat
  end repeat
end tell
OSA
      ;;
    iTerm.app)
      osascript >/dev/null 2>&1 <<OSA || true
tell application "iTerm2"
  repeat with w in windows
    repeat with t in tabs of w
      repeat with s in sessions of t
        try
          if (tty of s) is "${LOVECA_LAUNCH_TTY}" then
            close w
            return
          end if
        end try
      end repeat
    end repeat
  end repeat
end tell
OSA
      ;;
  esac
}

set +e
"$PYTHON_BIN" ./run_loveca_app.py --window-mode app
status=$?
set -e
if [[ "$status" -eq 0 ]]; then
  close_loveca_terminal_window
fi
exit "$status"
