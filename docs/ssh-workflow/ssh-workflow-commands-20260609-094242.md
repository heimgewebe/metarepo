# SSH / tmux / crashclip command inventory

Generated: 2026-06-09T09:42:42+02:00
Host: heim-pc
User: alex
HOME: /home/alex

## Productive commands

    ssh heim-pc
    ssh pcclip
    ssh pcnew
    ssh pclatest
    ssh -T heim-pc crashclip
    ssh -T heim-pc 'crashclip why'
    ssh -T heim-pc 'crashclip path'
    ssh -T heim-pc 'crashclip print'
    ssh -T heim-pc 'crash why'
    ssh -T heim-pc 'crash path'
    ssh -T heim-pc 'crash tail'
    ssh -tt heim-pc new
    ssh -tt heim-pc latest
    ssh -tt heim-pc 'new pr-name'
    ssh -tt -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc new
    ssh -tt -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc latest
    ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc crashclip

## Blink host targets expected

    heim-pc   = normaler Notzugang, kein RemoteCommand
    pcclip    = RequestTTY no, RemoteCommand crashclip
    pcnew     = RequestTTY force, RemoteCommand new
    pclatest  = RequestTTY force, RemoteCommand latest

## Installed remote commands

    new                      /usr/local/bin/new
    latest                   /usr/local/bin/latest
    crash                    /usr/local/bin/crash
    crashclip                /home/alex/.local/bin/crashclip
    mark-session-tmux-last   /usr/local/bin/mark-session-tmux-last

## Command file metadata

    -rwxr-xr-x 1 root root 805 Jun  9 07:32 /usr/local/bin/new
    -rwxr-xr-x 1 root root 856 Jun  9 07:32 /usr/local/bin/latest
    -rwxr-xr-x 1 root root 5887 Jun  8 15:39 /usr/local/bin/crash
    -rwxr-xr-x 1 root root 668 Jun  9 07:32 /usr/local/bin/mark-session-tmux-last
    -rwxr-xr-x 1 alex alex 3268 Jun  9 07:42 /home/alex/.local/bin/crashclip

## Log symlinks

    ls: Zugriff auf '/home/alex/logs/session-crash-last.log' nicht möglich: Datei oder Verzeichnis nicht gefunden
    lrwxrwxrwx 1 alex alex 52 Jun  9 09:42 /home/alex/logs/session-last.log -> /home/alex/logs/sessions/session-20260609-094231.log
    lrwxrwxrwx 1 alex alex 52 Jun  9 09:42 /home/alex/logs/session-tmux-last.log -> /home/alex/logs/sessions/session-20260609-093243.log
[2026-06-09T09:42:42+02:00] CMD: echo "    resolved_session_last=$(readlink -f "$HOME/logs/session-last.log" 2>/dev/null || true)"
    resolved_session_last=/home/alex/logs/sessions/session-20260609-094231.log
[2026-06-09T09:42:42+02:00] CMD: echo "    resolved_tmux_last=$(readlink -f "$HOME/logs/session-tmux-last.log" 2>/dev/null || true)"
    resolved_tmux_last=/home/alex/logs/sessions/session-20260609-093243.log
[2026-06-09T09:42:42+02:00] CMD: echo "    resolved_crash_last=$(readlink -f "$HOME/logs/session-crash-last.log" 2>/dev/null || true)"
    resolved_crash_last=/home/alex/logs/session-crash-last.log

## Current selectors

### crashclip why

    reason=tmux-last
    path=/home/alex/logs/sessions/session-20260609-093243.log
    size=24
    session_last=/home/alex/logs/sessions/session-20260609-094231.log
    session_tmux_last=/home/alex/logs/sessions/session-20260609-093243.log
    session_crash_last=/home/alex/logs/session-crash-last.log
    crash_path=/home/alex/logs/sessions/session-20260609-071910.log

### crash why

    reason=nonzero-exit
    path=/home/alex/logs/sessions/session-20260609-071910.log
    current=/home/alex/logs/sessions/session-20260609-094231.log
    explicit_crash=
    min_bytes=24576
    size=14422
    last_nonzero_exit=[2026-06-09T07:19:32+02:00] EXIT 1 (dir=/home/alex)
    last_error_signal:
    Traceback (most recent call last):
    KeyError: 'BASE'

## Dotfile hooks and risky lines

    /home/alex/.bashrc:71:# --- tmux/SSH -> lokales Clipboard ---
    /home/alex/.bashrc:75:# Holt aktuellen tmux-Buffer vom Heimserver ins lokale Clipboard
    /home/alex/.bashrc:78:# Holt aktuellen tmux-Buffer vom Heimserver ins lokale Clipboard (Wayland oder X11)
    /home/alex/.bashrc:79:alias tmuxclip='ssh heimserver "tmux save-buffer - 2>/dev/null || true" | clip-local'
    /home/alex/.bashrc:82:# SSH mit Reverse-Tunnel für tmux->lokales Clipboard
    /home/alex/.bashrc:85:alias tmuxclipall=omnicopy
    /home/alex/.bashrc:89:# >>> heim-pc ssh auto-tmux
    /home/alex/.bashrc:90:# Auto-attach tmux only for interactive SSH shells.
    /home/alex/.bashrc:91:# Disable temporarily with: touch ~/.no-auto-tmux
    /home/alex/.bashrc:98:   && [[ ! -f "$HOME/.no-auto-tmux" ]] \
    /home/alex/.bashrc:99:   && command -v tmux >/dev/null 2>&1; then
    /home/alex/.bashrc:100:  tmux new-session -A -s main
    /home/alex/.bashrc:101:  exit $?
    /home/alex/.bashrc:103:# <<< heim-pc ssh auto-tmux
    /home/alex/.profile:2:# >>> heim-pc profile ssh auto-tmux
    /home/alex/.profile:3:# Early SSH auto-tmux.
    /home/alex/.profile:6:#   touch ~/.no-auto-tmux
    /home/alex/.profile:14:   && [ ! -f "$HOME/.no-auto-tmux" ]; then
    /home/alex/.profile:16:  if command -v tmux >/dev/null 2>&1; then
    /home/alex/.profile:17:    exec tmux new-session -A -s main
    /home/alex/.profile:20:# <<< heim-pc profile ssh auto-tmux
    /home/alex/.profile:31:# Source ~/.bashrc for interactive Bash sessions so the SSH auto-tmux block can run.

## ~/.bashrc context 70-150

        70	
        71	# --- tmux/SSH -> lokales Clipboard ---
        72	alias clipssh='ssh heimserver'
        73	
        74	
        75	# Holt aktuellen tmux-Buffer vom Heimserver ins lokale Clipboard
        76	
        77	
        78	# Holt aktuellen tmux-Buffer vom Heimserver ins lokale Clipboard (Wayland oder X11)
        79	alias tmuxclip='ssh heimserver "tmux save-buffer - 2>/dev/null || true" | clip-local'
        80	
        81	
        82	# SSH mit Reverse-Tunnel für tmux->lokales Clipboard
        83	alias sshhs='ssh -R 127.0.0.1:8377:127.0.0.1:8377 heimserver'
        84	
        85	alias tmuxclipall=omnicopy
        86	export PATH="$PATH:$HOME/.local/bin"
        87	export PATH=$HOME/.npm-global/bin:$PATH
        88	
        89	# >>> heim-pc ssh auto-tmux
        90	# Auto-attach tmux only for interactive SSH shells.
        91	# Disable temporarily with: touch ~/.no-auto-tmux
        92	if [[ -n "${SSH_CONNECTION:-}${SSH_CLIENT:-}${SSH_TTY:-}" ]] \
        93	   && [[ -z "${TMUX:-}" ]] \
        94	   && [[ "$-" == *i* ]] \
        95	   && [[ -t 0 ]] \
        96	   && [[ -t 1 ]] \
        97	   && [[ "${TERM:-}" != "dumb" ]] \
        98	   && [[ ! -f "$HOME/.no-auto-tmux" ]] \
        99	   && command -v tmux >/dev/null 2>&1; then
       100	  tmux new-session -A -s main
       101	  exit $?
       102	fi
       103	# <<< heim-pc ssh auto-tmux
       104	
       105	
       106	# >>> CLAUDE CODE TTY ALIAS BEGIN
       107	# Claude Code TUI braucht echte TTY-Streams.
       108	# Das automatische Session-Logging macht stdout/stderr non-tty;
       109	# claudei repariert das über /dev/tty.
       110	if [[ $- == *i* ]] && command -v claudei >/dev/null 2>&1; then
       111	  alias claude='claudei'
       112	fi
       113	# >>> CLAUDE CODE TTY ALIAS END
       114	
       115	# Lokale Coding-Agenten
       116	alias agent-doc='${PAGER:-less} ~/.config/local-ai-agents/README.md'
       117	alias alocal='aider-local'
       118	alias alocal7='aider-local-7b'
       119	alias alocal14='aider-local-14b'

## ~/.profile context 1-100

         1	
         2	# >>> heim-pc profile ssh auto-tmux
         3	# Early SSH auto-tmux.
         4	# Runs before ~/.bashrc so session logging or other shell hooks cannot intercept it.
         5	# Disable temporarily with:
         6	#   touch ~/.no-auto-tmux
         7	if [ -n "${BASH_VERSION:-}" ] \
         8	   && [ -n "${SSH_CONNECTION:-}${SSH_CLIENT:-}${SSH_TTY:-}" ] \
         9	   && [ -z "${TMUX:-}" ] \
        10	   && case "$-" in *i*) true ;; *) false ;; esac \
        11	   && [ -t 0 ] \
        12	   && [ -t 1 ] \
        13	   && [ "${TERM:-}" != "dumb" ] \
        14	   && [ ! -f "$HOME/.no-auto-tmux" ]; then
        15	  PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
        16	  if command -v tmux >/dev/null 2>&1; then
        17	    exec tmux new-session -A -s main
        18	  fi
        19	fi
        20	# <<< heim-pc profile ssh auto-tmux
        21	
        22	
        23	. "$HOME/.local/bin/env"
        24	
        25	
        26	# Added by Toolbox App
        27	export PATH="$PATH:/home/alex/.local/share/JetBrains/Toolbox/scripts"
        28	
        29	# >>> heim-pc source bashrc for bash login shells
        30	# SSH login shells read ~/.profile, not ~/.bashrc directly.
        31	# Source ~/.bashrc for interactive Bash sessions so the SSH auto-tmux block can run.
        32	if [ -n "${BASH_VERSION:-}" ] && [ -f "$HOME/.bashrc" ]; then
        33	  . "$HOME/.bashrc"
        34	fi
        35	# <<< heim-pc source bashrc for bash login shells

## ~/.bash_profile / ~/.bash_login / ~/.ssh/rc

[2026-06-09T09:42:42+02:00] CMD: echo "### $f"
### /home/alex/.bash_profile
[2026-06-09T09:42:42+02:00] CMD: [ -e "$f" ]
[2026-06-09T09:42:42+02:00] CMD: echo "    missing"
    missing
[2026-06-09T09:42:42+02:00] CMD: echo

[2026-06-09T09:42:42+02:00] CMD: echo "### $f"
### /home/alex/.bash_login
[2026-06-09T09:42:42+02:00] CMD: [ -e "$f" ]
[2026-06-09T09:42:42+02:00] CMD: echo "    missing"
    missing
[2026-06-09T09:42:42+02:00] CMD: echo

[2026-06-09T09:42:42+02:00] CMD: echo "### $f"
### /home/alex/.ssh/rc
[2026-06-09T09:42:42+02:00] CMD: [ -e "$f" ]
[2026-06-09T09:42:42+02:00] CMD: echo "    missing"
    missing
[2026-06-09T09:42:42+02:00] CMD: echo

[2026-06-09T09:42:42+02:00] CMD: echo

[2026-06-09T09:42:42+02:00] CMD: echo "## $p"
## /usr/local/bin/new
[2026-06-09T09:42:42+02:00] CMD: [ -e "$p" ]
[2026-06-09T09:42:42+02:00] CMD: nl -ba "$p"
[2026-06-09T09:42:43+02:00] CMD: sed -n '1,320p'
[2026-06-09T09:42:43+02:00] CMD: sed 's/^/    /'
         1	#!/usr/bin/env bash
         2	set -euo pipefail
         3	
         4	command -v tmux >/dev/null || {
         5	  echo "ERROR: tmux not found" >&2
         6	  exit 1
         7	}
         8	
         9	if ! [ -t 0 ] || ! [ -t 1 ]; then
        10	  echo "ERROR: new braucht eine TTY. Nutze: ssh -tt heim-pc new" >&2
        11	  exit 88
        12	fi
        13	
        14	/usr/local/bin/mark-session-tmux-last || true
        15	
        16	raw_name="${1:-}"
        17	stamp="$(date +%Y%m%d-%H%M%S)"
        18	
        19	if [ -z "$raw_name" ]; then
        20	  name="new-$stamp"
        21	else
        22	  name="$raw_name"
        23	fi
        24	
        25	if ! printf '%s' "$name" | grep -Eq '^[A-Za-z0-9._-]+$'; then
        26	  echo "ERROR: unsafe tmux session name: $name" >&2
        27	  echo "Allowed: A-Z a-z 0-9 . _ -" >&2
        28	  exit 2
        29	fi
        30	
        31	if tmux has-session -t "$name" 2>/dev/null; then
        32	  name="${name}-${stamp}"
        33	fi
        34	
        35	echo "== creating tmux session =="
        36	echo "$name"
        37	
        38	tmux new-session -d -s "$name" -c "$HOME"
        39	
        40	echo "== attaching =="
        41	exec tmux attach-session -t "$name"
[2026-06-09T09:42:43+02:00] CMD: echo

[2026-06-09T09:42:43+02:00] CMD: echo "## $p"
## /usr/local/bin/latest
[2026-06-09T09:42:43+02:00] CMD: [ -e "$p" ]
[2026-06-09T09:42:43+02:00] CMD: nl -ba "$p"
[2026-06-09T09:42:43+02:00] CMD: sed -n '1,320p'
[2026-06-09T09:42:43+02:00] CMD: sed 's/^/    /'
         1	#!/usr/bin/env bash
         2	set -euo pipefail
         3	
         4	command -v tmux >/dev/null || {
         5	  echo "ERROR: tmux not found" >&2
         6	  exit 1
         7	}
         8	
         9	if [ -n "${TMUX:-}" ]; then
        10	  echo "INFO: already inside tmux"
        11	  tmux display-message -p 'session=#{session_name} window=#{window_name}' 2>/dev/null || true
        12	  exit 0
        13	fi
        14	
        15	if tmux ls >/dev/null 2>&1; then
        16	  session="$(
        17	    tmux list-sessions -F '#{session_last_attached}|#{session_activity}|#{session_name}' \
        18	      | sort -t'|' -k1,1nr -k2,2nr \
        19	      | head -n1 \
        20	      | cut -d'|' -f3-
        21	  )"
        22	
        23	  if [ -n "${session:-}" ] && tmux has-session -t "$session" 2>/dev/null; then
        24	    if [ -t 0 ] && [ -t 1 ]; then
        25	      /usr/local/bin/mark-session-tmux-last || true
        26	      echo "== attaching tmux session =="
        27	      echo "$session"
        28	      exec tmux attach-session -t "$session"
        29	    else
        30	      echo "$session"
        31	      exit 0
        32	    fi
        33	  fi
        34	fi
        35	
        36	exec crash
[2026-06-09T09:42:43+02:00] CMD: echo

[2026-06-09T09:42:43+02:00] CMD: echo "## $p"
## /usr/local/bin/crash
[2026-06-09T09:42:43+02:00] CMD: [ -e "$p" ]
[2026-06-09T09:42:43+02:00] CMD: nl -ba "$p"
[2026-06-09T09:42:43+02:00] CMD: sed -n '1,320p'
[2026-06-09T09:42:43+02:00] CMD: sed 's/^/    /'
         1	#!/usr/bin/env bash
         2	set -euo pipefail
         3	
         4	LOG_ROOT="${HOME}/logs"
         5	LOG_DIR="${LOG_ROOT}/sessions"
         6	LAST_LINK="${LOG_ROOT}/session-last.log"
         7	CRASH_LINK="${LOG_ROOT}/session-crash-last.log"
         8	
         9	MODE="${1:-tail}"
        10	MIN_BYTES="${CRASH_MIN_BYTES:-24576}"
        11	
        12	die() {
        13	  echo "ERROR: $*" >&2
        14	  exit 1
        15	}
        16	
        17	[ -d "$LOG_DIR" ] || die "missing log dir: $LOG_DIR"
        18	
        19	resolve_path() {
        20	  readlink -f "$1" 2>/dev/null || printf '%s\n' "$1"
        21	}
        22	
        23	current_target=""
        24	if [ -e "$LAST_LINK" ] || [ -L "$LAST_LINK" ]; then
        25	  current_target="$(resolve_path "$LAST_LINK")"
        26	fi
        27	
        28	explicit_crash=""
        29	if [ -e "$CRASH_LINK" ] || [ -L "$CRASH_LINK" ]; then
        30	  explicit_crash="$(resolve_path "$CRASH_LINK")"
        31	fi
        32	
        33	list_logs_newest_first() {
        34	  find "$LOG_DIR" -maxdepth 1 -type f -name 'session-*.log' -printf '%T@ %p\n' \
        35	    | sort -nr \
        36	    | while IFS= read -r line; do
        37	        printf '%s\n' "${line#* }"
        38	      done
        39	}
        40	
        41	is_current_log() {
        42	  local f resolved
        43	  f="$1"
        44	  [ -n "$current_target" ] || return 1
        45	  resolved="$(resolve_path "$f")"
        46	  [ "$resolved" = "$current_target" ]
        47	}
        48	
        49	has_nonzero_exit_near_end() {
        50	  local f="$1"
        51	  tail -n 180 "$f" 2>/dev/null \
        52	    | grep -aEq '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[^]]+\] EXIT [1-9][0-9]* \(dir='
        53	}
        54	
        55	last_nonzero_exit_near_end() {
        56	  local f="$1"
        57	  tail -n 180 "$f" 2>/dev/null \
        58	    | grep -aE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[^]]+\] EXIT [1-9][0-9]* \(dir=' \
        59	    | tail -n 1 || true
        60	}
        61	
        62	has_error_signal_near_end() {
        63	  local f="$1"
        64	  tail -n 260 "$f" 2>/dev/null \
        65	    | grep -aEiq 'ERROR:|Traceback|Exception|FAILED | failed|failure|crash|aborted|segmentation fault|Befehl nicht gefunden|command not found|Ungültige Option|Permission denied|Operation timed out|Socket error|No such file|Datei oder Verzeichnis nicht gefunden|exit status [1-9]|returned non-zero|panic:|AssertionError|TypeError|NameError'
        66	}
        67	
        68	last_error_signal_near_end() {
        69	  local f="$1"
        70	  tail -n 260 "$f" 2>/dev/null \
        71	    | grep -aEi 'ERROR:|Traceback|Exception|FAILED | failed|failure|crash|aborted|segmentation fault|Befehl nicht gefunden|command not found|Ungültige Option|Permission denied|Operation timed out|Socket error|No such file|Datei oder Verzeichnis nicht gefunden|exit status [1-9]|returned non-zero|panic:|AssertionError|TypeError|NameError' \
        72	    | tail -n 5 || true
        73	}
        74	
        75	select_log() {
        76	  local f resolved size
        77	
        78	  # 1. Expliziter Crash-Symlink gewinnt, wenn vorhanden.
        79	  if [ -n "$explicit_crash" ] && [ -f "$explicit_crash" ]; then
        80	    printf 'explicit-crash-link|%s\n' "$explicit_crash"
        81	    return 0
        82	  fi
        83	
        84	  # 2. Neuester nicht-aktueller Log mit nonzero EXIT am Log-Ende.
        85	  while IFS= read -r f; do
        86	    [ -n "$f" ] || continue
        87	    is_current_log "$f" && continue
        88	    if has_nonzero_exit_near_end "$f"; then
        89	      resolved="$(resolve_path "$f")"
        90	      printf 'nonzero-exit|%s\n' "$resolved"
        91	      return 0
        92	    fi
        93	  done < <(list_logs_newest_first)
        94	
        95	  # 3. Neuester nicht-aktueller Log mit klaren Fehlerindikatoren am Log-Ende.
        96	  while IFS= read -r f; do
        97	    [ -n "$f" ] || continue
        98	    is_current_log "$f" && continue
        99	    if has_error_signal_near_end "$f"; then
       100	      resolved="$(resolve_path "$f")"
       101	      printf 'error-signal|%s\n' "$resolved"
       102	      return 0
       103	    fi
       104	  done < <(list_logs_newest_first)
       105	
       106	  # 4. Größenfallback: neuester nicht-aktueller Log ab MIN_BYTES.
       107	  while IFS= read -r f; do
       108	    [ -n "$f" ] || continue
       109	    is_current_log "$f" && continue
       110	    size="$(stat -c '%s' "$f" 2>/dev/null || echo 0)"
       111	    if [ "$size" -ge "$MIN_BYTES" ]; then
       112	      resolved="$(resolve_path "$f")"
       113	      printf 'size-fallback|%s\n' "$resolved"
       114	      return 0
       115	    fi
       116	  done < <(list_logs_newest_first)
       117	
       118	  # 5. Rohfallback: neuester nicht-aktueller Log.
       119	  while IFS= read -r f; do
       120	    [ -n "$f" ] || continue
       121	    is_current_log "$f" && continue
       122	    resolved="$(resolve_path "$f")"
       123	    printf 'raw-fallback|%s\n' "$resolved"
       124	    return 0
       125	  done < <(list_logs_newest_first)
       126	
       127	  # 6. Letzter Ausweg: current.
       128	  if [ -n "$current_target" ] && [ -f "$current_target" ]; then
       129	    printf 'current-last-resort|%s\n' "$current_target"
       130	    return 0
       131	  fi
       132	
       133	  return 1
       134	}
       135	
       136	selection="$(select_log || true)"
       137	[ -n "$selection" ] || die "no session log candidate found"
       138	
       139	reason="${selection%%|*}"
       140	candidate="${selection#*|}"
       141	
       142	case "$MODE" in
       143	  path)
       144	    printf '%s\n' "$candidate"
       145	    ;;
       146	  reason)
       147	    printf '%s\n' "$reason"
       148	    ;;
       149	  why)
       150	    echo "reason=$reason"
       151	    echo "path=$candidate"
       152	    echo "current=${current_target:-}"
       153	    echo "explicit_crash=${explicit_crash:-}"
       154	    echo "min_bytes=$MIN_BYTES"
       155	    if [ -f "$candidate" ]; then
       156	      echo "size=$(stat -c '%s' "$candidate" 2>/dev/null || echo 0)"
       157	      echo "last_nonzero_exit=$(last_nonzero_exit_near_end "$candidate")"
       158	      echo "last_error_signal:"
       159	      last_error_signal_near_end "$candidate"
       160	    fi
       161	    ;;
       162	  current-path)
       163	    printf '%s\n' "$current_target"
       164	    ;;
       165	  crash-link-path)
       166	    printf '%s\n' "$explicit_crash"
       167	    ;;
       168	  any-path|raw-path)
       169	    while IFS= read -r f; do
       170	      [ -n "$f" ] || continue
       171	      is_current_log "$f" && continue
       172	      resolve_path "$f"
       173	      exit 0
       174	    done < <(list_logs_newest_first)
       175	    [ -n "$current_target" ] && printf '%s\n' "$current_target"
       176	    ;;
       177	  recent)
       178	    find "$LOG_DIR" -maxdepth 1 -type f -name 'session-*.log' \
       179	      -printf '%T@ %TY-%Tm-%Td %TH:%TM:%TS %s %p\n' \
       180	      | sort -nr \
       181	      | head -n "${2:-20}"
       182	    ;;
       183	  tail|"")
       184	    echo "== crash log =="
       185	    echo "reason=$reason"
       186	    echo "$candidate"
       187	    echo
       188	    exec tail -n 220 "$candidate"
       189	    ;;
       190	  less|pager)
       191	    echo "== crash log =="
       192	    echo "reason=$reason"
       193	    echo "$candidate"
       194	    echo
       195	    exec less +G "$candidate"
       196	    ;;
       197	  follow)
       198	    echo "== crash log =="
       199	    echo "reason=$reason"
       200	    echo "$candidate"
       201	    echo
       202	    exec tail -n 220 -f "$candidate"
       203	    ;;
       204	  *)
       205	    echo "Usage: crash [tail|less|follow|path|reason|why|current-path|crash-link-path|any-path|recent]" >&2
       206	    echo "Env: CRASH_MIN_BYTES=$MIN_BYTES" >&2
       207	    exit 2
       208	    ;;
       209	esac
[2026-06-09T09:42:43+02:00] CMD: echo

[2026-06-09T09:42:43+02:00] CMD: echo "## $p"
## /home/alex/.local/bin/crashclip
[2026-06-09T09:42:43+02:00] CMD: [ -e "$p" ]
[2026-06-09T09:42:43+02:00] CMD: nl -ba "$p"
[2026-06-09T09:42:43+02:00] CMD: sed -n '1,320p'
[2026-06-09T09:42:43+02:00] CMD: sed 's/^/    /'
         1	#!/usr/bin/env bash
         2	set -euo pipefail
         3	
         4	mode="${1:-300}"
         5	max_bytes="${CRASHCLIP_MAX_BYTES:-8000}"
         6	
         7	die() {
         8	  echo "ERROR: $*" >&2
         9	  exit 1
        10	}
        11	
        12	osc52_file() {
        13	  local file="$1"
        14	  printf '\033]52;c;%s\007' "$(base64 -w0 "$file")"
        15	}
        16	
        17	valid_resolved_file() {
        18	  local p="$1"
        19	  local r=""
        20	  [ -e "$p" ] || [ -L "$p" ] || return 1
        21	  r="$(readlink -f "$p" 2>/dev/null || true)"
        22	  [ -n "$r" ] && [ -f "$r" ] || return 1
        23	  printf '%s\n' "$r"
        24	}
        25	
        26	choose_log() {
        27	  local resolved=""
        28	
        29	  # 1. Expliziter tmux-Arbeitslog, wenn vorhanden.
        30	  resolved="$(valid_resolved_file "$HOME/logs/session-tmux-last.log" 2>/dev/null || true)"
        31	  if [ -n "$resolved" ]; then
        32	    printf 'tmux-last|%s\n' "$resolved"
        33	    return 0
        34	  fi
        35	
        36	  # 2. Letzter allgemein geloggter Arbeitskontext.
        37	  # Das ist aktuell der entscheidende Fallback für ssh heim-pc / pcnew.
        38	  resolved="$(valid_resolved_file "$HOME/logs/session-last.log" 2>/dev/null || true)"
        39	  if [ -n "$resolved" ]; then
        40	    printf 'session-last|%s\n' "$resolved"
        41	    return 0
        42	  fi
        43	
        44	  # 3. Späterer echter Crash-Symlink, falls einmal vorhanden.
        45	  resolved="$(valid_resolved_file "$HOME/logs/session-crash-last.log" 2>/dev/null || true)"
        46	  if [ -n "$resolved" ]; then
        47	    printf 'crash-link|%s\n' "$resolved"
        48	    return 0
        49	  fi
        50	
        51	  # 4. Alter Heuristik-Fallback.
        52	  resolved="$(crash path 2>/dev/null || true)"
        53	  if [ -n "$resolved" ] && [ -f "$resolved" ]; then
        54	    printf 'crash-selector|%s\n' "$resolved"
        55	    return 0
        56	  fi
        57	
        58	  return 1
        59	}
        60	
        61	selection="$(choose_log || true)"
        62	[ -n "$selection" ] || die "no log candidate found"
        63	
        64	reason="${selection%%|*}"
        65	log="${selection#*|}"
        66	
        67	tmp="$(mktemp)"
        68	trap 'rm -f "$tmp" "$tmp.cut"' EXIT
        69	
        70	case "$mode" in
        71	  test)
        72	    printf 'OSC52_TEST_heim-pc_%s\n' "$(date +%H%M%S)" > "$tmp"
        73	    ;;
        74	  path)
        75	    printf '%s\n' "$log" > "$tmp"
        76	    ;;
        77	  why)
        78	    echo "reason=$reason"
        79	    echo "path=$log"
        80	    echo "size=$(stat -c '%s' "$log" 2>/dev/null || echo 0)"
        81	    echo "session_last=$(readlink -f "$HOME/logs/session-last.log" 2>/dev/null || true)"
        82	    echo "session_tmux_last=$(readlink -f "$HOME/logs/session-tmux-last.log" 2>/dev/null || true)"
        83	    echo "session_crash_last=$(readlink -f "$HOME/logs/session-crash-last.log" 2>/dev/null || true)"
        84	    echo "crash_path=$(crash path 2>/dev/null || true)"
        85	    exit 0
        86	    ;;
        87	  print)
        88	    echo "== clipped log =="
        89	    echo "reason=$reason"
        90	    echo "$log"
        91	    echo
        92	    tail -n "${2:-300}" "$log"
        93	    exit 0
        94	    ;;
        95	  full)
        96	    {
        97	      echo "== clipped log =="
        98	      echo "reason=$reason"
        99	      echo "$log"
       100	      echo
       101	      cat "$log"
       102	    } > "$tmp"
       103	    ;;
       104	  ''|*[!0-9]*)
       105	    echo "Usage: crashclip [LINES|path|why|print|full|test]" >&2
       106	    echo "Default: crashclip 300" >&2
       107	    exit 2
       108	    ;;
       109	  *)
       110	    {
       111	      echo "== clipped log =="
       112	      echo "reason=$reason"
       113	      echo "$log"
       114	      echo
       115	      tail -n "$mode" "$log"
       116	    } > "$tmp"
       117	    ;;
       118	esac
       119	
       120	size="$(wc -c < "$tmp" | tr -d ' ')"
       121	
       122	if [ "$size" -gt "$max_bytes" ]; then
       123	  {
       124	    echo "[crashclip truncated to last $max_bytes bytes]"
       125	    echo "reason=$reason"
       126	    echo "source=$log"
       127	    echo
       128	    tail -c "$max_bytes" "$tmp"
       129	  } > "$tmp.cut"
       130	  mv "$tmp.cut" "$tmp"
       131	  size="$(wc -c < "$tmp" | tr -d ' ')"
       132	fi
       133	
       134	echo "crashclip: copying $size bytes from $log ($reason)" >&2
       135	osc52_file "$tmp"
       136	echo >&2
       137	echo "crashclip: copied" >&2
[2026-06-09T09:42:43+02:00] CMD: echo

[2026-06-09T09:42:43+02:00] CMD: echo "## $p"
## /usr/local/bin/mark-session-tmux-last
[2026-06-09T09:42:43+02:00] CMD: [ -e "$p" ]
[2026-06-09T09:42:43+02:00] CMD: nl -ba "$p"
[2026-06-09T09:42:43+02:00] CMD: sed -n '1,320p'
[2026-06-09T09:42:43+02:00] CMD: sed 's/^/    /'
         1	#!/usr/bin/env bash
         2	set -euo pipefail
         3	
         4	quiet=0
         5	case "${1:-}" in
         6	  --quiet|-q)
         7	    quiet=1
         8	    ;;
         9	esac
        10	
        11	LOG_ROOT="${HOME}/logs"
        12	LAST_LINK="${LOG_ROOT}/session-last.log"
        13	TMUX_LAST="${LOG_ROOT}/session-tmux-last.log"
        14	
        15	mkdir -p "$LOG_ROOT"
        16	
        17	current=""
        18	if [ -e "$LAST_LINK" ] || [ -L "$LAST_LINK" ]; then
        19	  current="$(readlink -f "$LAST_LINK" 2>/dev/null || true)"
        20	fi
        21	
        22	if [ -n "$current" ] && [ -f "$current" ]; then
        23	  ln -sfn "$current" "$TMUX_LAST"
        24	  if [ "$quiet" != "1" ]; then
        25	    echo "== marked tmux/session log =="
        26	    echo "$current"
        27	  fi
        28	  exit 0
        29	fi
        30	
        31	if [ "$quiet" != "1" ]; then
        32	  echo "WARN: could not resolve current session log from $LAST_LINK" >&2
        33	fi
        34	exit 0

## tmux sessions

    new-20260608-110524 | attached=0 | last=1780909825 | activity=1780909856
    new-20260608-111103 | attached=0 | last=1780913519 | activity=1780913519
    new-20260608-121343 | attached=0 | last=1780914315 | activity=1780914315
    new-20260608-122546 | attached=0 | last=1780914346 | activity=1780914548
    new-20260608-141408 | attached=0 | last=1780920848 | activity=1780920850
    new-20260608-165538 | attached=0 | last=1780930538 | activity=1780930538
    new-20260608-170154 | attached=0 | last=1780930914 | activity=1780930914
    new-20260608-170204 | attached=0 | last=1780930938 | activity=1780930938
    new-20260608-170229 | attached=0 | last=1780930949 | activity=1780930985
    new-20260608-174514 | attached=0 | last=1780933514 | activity=1780933539
    new-20260609-074224 | attached=0 | last=1780983744 | activity=1780983760
    new-20260609-074440 | attached=0 | last=1780983880 | activity=1780983939
    new-20260609-083534 | attached=0 | last=1780986934 | activity=1780986950
    new-20260609-093243 | attached=0 | last=1780990363 | activity=1780990363
    new-20260609-094231 | attached=1 | last=1780990951 | activity=1780990962
    pr-test | attached=0 | last=1780913600 | activity=1780913600
    tasks | attached=1 | last=1780946155 | activity=1780947207

## newest session logs

    1780990963.1610289600 2026-06-09 09:42:43.1610289600 15422 /home/alex/logs/sessions/session-20260609-094231.log
    1780990363.3987386070 2026-06-09 09:32:43.3987386070 24 /home/alex/logs/sessions/session-20260609-093243.log
    1780990160.5055057700 2026-06-09 09:29:20.5055057700 22619 /home/alex/logs/sessions/session-20260609-092152.log
    1780986950.2389209520 2026-06-09 08:35:50.2389209520 15864 /home/alex/logs/sessions/session-20260609-083534.log
    1780983939.4160268810 2026-06-09 07:45:39.4160268810 13187 /home/alex/logs/sessions/session-20260609-074440.log
    1780983748.2085931830 2026-06-09 07:42:28.2085931830 13725 /home/alex/logs/sessions/session-20260609-074224.log
    1780983202.7179356670 2026-06-09 07:33:22.7179356670 22985 /home/alex/logs/sessions/session-20260608-182651.log
    1780982372.1222501990 2026-06-09 07:19:32.1222501990 14422 /home/alex/logs/sessions/session-20260609-071910.log
    1780947006.8652232510 2026-06-08 21:30:06.8652232510 12027 /home/alex/logs/sessions/session-20260608-212958.log
    1780946784.5629740480 2026-06-08 21:26:24.5629740480 33149 /home/alex/logs/sessions/session-20260608-212612.log
    1780946552.2430352390 2026-06-08 21:22:32.2430352390 160 /home/alex/logs/sessions/session-20260608-212222.log
    1780940404.9972484800 2026-06-08 19:40:04.9972484800 13903 /home/alex/logs/sessions/session-20260608-194002.log
    1780940383.2691230770 2026-06-08 19:39:43.2691230770 38234 /home/alex/logs/sessions/session-20260608-183625.log
    1780938407.7974950810 2026-06-08 19:06:47.7974950810 301 /home/alex/logs/sessions/session-20260608-190628.log
    1780936484.8578719520 2026-06-08 18:34:44.8578719520 9541 /home/alex/logs/sessions/session-20260608-183442.log
    1780936223.0278352910 2026-06-08 18:30:23.0278352910 17393 /home/alex/logs/sessions/session-20260608-183020.log
    1780933547.6166605060 2026-06-08 17:45:47.6166605060 16227 /home/alex/logs/sessions/session-20260608-174514.log
    1780931349.6963224290 2026-06-08 17:09:09.6963224290 25608 /home/alex/logs/sessions/session-20260608-170905.log
    1780930993.5804556130 2026-06-08 17:03:13.5804556130 24132 /home/alex/logs/sessions/session-20260608-170229.log
    1780930924.8831873740 2026-06-08 17:02:04.8831873740 24 /home/alex/logs/sessions/session-20260608-170204.log
    1780930915.0041488020 2026-06-08 17:01:55.0041488020 24 /home/alex/logs/sessions/session-20260608-170154.log
    1780930893.1300633890 2026-06-08 17:01:33.1300633890 104 /home/alex/logs/sessions/session-20260608-165538.log
    1780929793.9604558170 2026-06-08 16:43:13.9604558170 26136 /home/alex/logs/sessions/session-20260608-161027.log
    1780927289.9383513570 2026-06-08 16:01:29.9383513570 20975 /home/alex/logs/sessions/session-20260608-160059.log
    1780926062.6397402260 2026-06-08 15:41:02.6397402260 37877 /home/alex/logs/sessions/session-20260608-153919.log
    1780925549.9680352890 2026-06-08 15:32:29.9680352890 207723 /home/alex/logs/sessions/session-20260608-153211.log
    1780925524.3359258240 2026-06-08 15:32:04.3359258240 219854 /home/alex/logs/sessions/session-20260608-153116.log
    1780925259.7868571090 2026-06-08 15:27:39.7868571090 20975 /home/alex/logs/sessions/session-20260608-152725.log
    1780925235.1167578390 2026-06-08 15:27:15.1167578390 15918 /home/alex/logs/sessions/session-20260608-130645.log
    1780924979.9049519600 2026-06-08 15:22:59.9049519600 20975 /home/alex/logs/sessions/session-20260608-151938.log
    1780920848.5195272430 2026-06-08 14:14:08.5195272430 24 /home/alex/logs/sessions/session-20260608-141408.log
    1780916673.3317864690 2026-06-08 13:04:33.3317864690 20975 /home/alex/logs/sessions/session-20260608-130427.log
    1780916589.8047603940 2026-06-08 13:03:09.8047603940 20876 /home/alex/logs/sessions/session-20260608-130251.log
    1780916565.5411039910 2026-06-08 13:02:45.5411039910 101146 /home/alex/logs/sessions/session-20260608-105037.log
    1780914548.1748355440 2026-06-08 12:29:08.1748355440 1074 /home/alex/logs/sessions/session-20260608-122546.log
    1780913819.6829510790 2026-06-08 12:16:59.6829510790 9204 /home/alex/logs/sessions/session-20260608-121343.log
    1780913600.9936788940 2026-06-08 12:13:20.9936788940 24 /home/alex/logs/sessions/session-20260608-121320.log
    1780913435.6196878130 2026-06-08 12:10:35.6196878130 13523 /home/alex/logs/sessions/session-20260608-111104.log
    1780909856.4397090220 2026-06-08 11:10:56.4397090220 31 /home/alex/logs/sessions/session-20260608-110524.log
    1780905405.8734270600 2026-06-08 09:56:45.8734270600 86129 /home/alex/logs/sessions/session-20260607-124257.log
    1780905394.6463862230 2026-06-08 09:56:34.6463862230 30772 /home/alex/logs/sessions/session-20260608-081001.log
    1780898994.4664775280 2026-06-08 08:09:54.4664775280 15318 /home/alex/logs/sessions/session-20260608-080720.log
    1780898581.6873734240 2026-06-08 08:03:01.6873734240 132850 /home/alex/logs/sessions/session-20260608-080234.log
    1780898545.4141461510 2026-06-08 08:02:25.4141461510 174108 /home/alex/logs/sessions/session-20260608-075530.log
    1780897337.6559684190 2026-06-08 07:42:17.6559684190 543 /home/alex/logs/sessions/session-20260608-074150.log
    1780897279.3497321570 2026-06-08 07:41:19.3497321570 495 /home/alex/logs/sessions/session-20260608-074055.log
    1780897241.4756297490 2026-06-08 07:40:41.4756297490 16387 /home/alex/logs/sessions/session-20260608-072420.log
    1780896245.8222040600 2026-06-08 07:24:05.8222040600 275743 /home/alex/logs/sessions/session-20260607-204932.log
    1780857965.8300117920 2026-06-07 20:46:05.8300117920 22151 /home/alex/logs/sessions/session-20260607-204318.log
    1780857664.4629893360 2026-06-07 20:41:04.4629893360 26330 /home/alex/logs/sessions/session-20260607-204059.log
    1780857584.7405050450 2026-06-07 20:39:44.7405050450 34343 /home/alex/logs/sessions/session-20260607-201802.log
    1780854804.1545342110 2026-06-07 19:53:24.1545342110 8504 /home/alex/logs/sessions/session-20260607-195319.log
    1780852469.7741794320 2026-06-07 19:14:29.7741794320 17223 /home/alex/logs/sessions/session-20260607-191308.log
    1780837805.6891915270 2026-06-07 15:10:05.6891915270 8806 /home/alex/logs/sessions/session-20260607-150947.log
    1780835104.3058088760 2026-06-07 14:25:04.3058088760 24075 /home/alex/logs/sessions/session-20260607-142501.log
    1780834907.1496600280 2026-06-07 14:21:47.1496600280 9065 /home/alex/logs/sessions/session-20260607-142143.log
    1780834453.6433325100 2026-06-07 14:14:13.6433325100 12014 /home/alex/logs/sessions/session-20260607-141351.log
    1780834358.8737693820 2026-06-07 14:12:38.8737693820 2694 /home/alex/logs/sessions/session-20260607-141236.log
    1780834311.7254887470 2026-06-07 14:11:51.7254887470 5195 /home/alex/logs/sessions/session-20260607-141150.log
    1780834253.4221399000 2026-06-07 14:10:53.4221399000 6476 /home/alex/logs/sessions/session-20260607-141050.log

## SSH commands found in session logs

    ssh heimserver
    ssh alex@192.168.178.60
    ssh alex@heimberry.local
    ssh alex@192.168.178.X
    ssh alex@raspberrypi.local
    ssh alex@heimberry
    ssh heimberry
    ssh -o BatchMode=yes -o ConnectTimeout=5 alex@heimberry 'hostname; ip -br addr; uname -a' 2> /dev/null
    ssh -o BatchMode=yes -o ConnectTimeout=5 alex@heimberry.local 'hostname; ip -br addr; uname -a' 2> /dev/null
    ssh -o BatchMode=yes -o ConnectTimeout=5 pi@raspberrypi.local 'hostname; ip -br addr; uname -a' 2> /dev/null
    ssh alex@heimberry.local '
    ssh -G heimberry
    ssh heimberry 'hostname; ip -br addr'
    ssh heimberry '
    ssh heimberry 'bash -s' <<'SH'
    ssh -G heimserver
    ssh heimberry 'hostname; hostname -f 2>/dev/null || true; ip -br addr'
    ssh heimserver 'hostname; hostname -f 2>/dev/null || true; ip -br addr'
    ssh -G acs
    ssh heimserver 'hostname; ip -br addr'
    ssh heimserver '
    ssh alex@heimserver.home.arpa 'bash -s' <<'EOF'
    ssh -tt alex@heimserver.home.arpa 'bash -lc '"'"'
    ssh alex@heimserver.home.arpa 'sudo reboot'
    ssh -tt alex@heimserver.home.arpa 'sudo /sbin/reboot'
    ssh alex@heimserver.home.arpa 'ssh-keygen -l -f /etc/ssh/ssh_host_ed25519_key.pub'
    ssh alex@heimserver.home.arpa "bash -s" <<EOF
    ssh -T git@github.com
    ssh -T heimserver 'bash -s' <<'REMOTE'
    ssh -T heimserver 'python3 - <<'"'"'PY'"'"'
    ssh -T heimberry 'bash -s' <<'REMOTE'
    ssh -T heim-pc 'bash -s' <<'REMOTE'
    ssh alex@heimberry.home.arpa
    ssh heimserver 'cd /opt/weltgewebe && git status --short && git pull --ff-only'
    ssh heimserver "BREVO_SMTP_\1=<redacted> bash -s" <<'REMOTE'
    ssh -o BatchMode=yes -o ConnectTimeout=5 heimberry 'mkdir -p "$HOME/.local/bin"'
    ssh -o BatchMode=yes -o ConnectTimeout=5 heimberry '
    ssh -t -o ConnectTimeout=5 heimberry '
    ssh -T heim-pc 'crash path'
    ssh -tt heim-pc 'cat > /tmp/crashclip <<'"'"'BASH'"'"'
    ssh -T heim-pc 'bash -s' <<'BASH'
    ssh -T heim-pc 'crash why'
    ssh -T heim-pc crashclip
    //' \ | sort \ | uniq -c \ | sort -nr \ | sed -n '1,120p' echo '’BASHecho “$OUT”```bashcat "$OUT"mkdir -p ./docs/ssh-workflowcp "$OUT" ./docs/ssh-workflow/ls -l ./docs/ssh-workflow/ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc "mkdir -p ~/docs/ssh-workflow && cat > ~/docs/ssh-workflow/$(basename "$OUT")" < "$OUT"ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc 'ls -l ~/docs/ssh-workflow && tail -n 20 ~/docs/ssh-workflow/ssh-workflow-commands-*.md'if [ -d "$HOME/repos/infra" ]; then  mkdir -p "$HOME/repos/infra/docs/ssh-workflow"  cp "$OUT" "$HOME/repos/infra/docs/ssh-workflow/"  git -C "$HOME/repos/infra" status --shortfifor h in heim-pc pcclip pcnew pclatest; do  echo "===== $h ====="  ssh -G "$h" 2>/dev/null | grep -Ei '^(hostname|user|port|requesttty|remotecommand|identityfile|preferredauthentications|passwordauthentication|connecttimeout|serveraliveinterval|serveralivecountmax) '  echodonefor h in heim-pc pcclip pcnew pclatest; do  echo "===== $h ====="  ssh -G "$h" 2>/dev/null | sed -n '1,220p'  echodone > "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt"cat "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt"cp "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt" ./docs/ssh-workflow/ 2>/dev/null || truessh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc "cat > ~/docs/ssh-workflow/blink-ssh-G-hosts-$STAMP.txt" < "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt"
    ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc 'bash -s' <<'BASH' > "$OUT"
    //' \ | awk '!seen[$0]++' \ | sed -n '1,300p' echo '’
    //' \ | sort \ | uniq -c \ | sort -nr \ | sed -n '1,120p' echo '’
    //' \  | sort \  | uniq -c \  | sort -nr \  | sed -n '1,160p' \  | sed 's/^/    /' >> "$OUT" || truecat >> "$OUT" <<'EOF'## Suggested Blink configs### heim-pc    Hostname: 100.68.88.111    User: alex    Port: 22    SSH Config:      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      # no RemoteCommand### pcclip    Hostname: heim-pc    User: alex    Port: 22    SSH Config:      RequestTTY no      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      RemoteCommand crashclip### pcnew    Hostname: heim-pc    User: alex    Port: 22    SSH Config:      RequestTTY force      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      RemoteCommand new### pclatest[7m    Hostname: heim-pc[27m[7m    User: alex[27m[7m    Port: 22[27m[7m    SSH Config:[27m[7m      RequestTTY force[27m[7m      ConnectTimeout 8[27m[7m      ServerAliveInterval 3[27m[7m      ServerAliveCountMax 1[27m[7m      RemoteCommand latest[27m[7mEOF[27m[7mmkdir -p "$HOME/docs/ssh-workflow"[27m[7mcp "$OUT" "$HOME/docs/ssh-workflow/"[27m[7mfor repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do[27m[7m  if [ -d "$repo" ]; then[27m[7m    mkdir -p "$repo/docs/ssh-workflow"[27m[7m    cp "$OUT" "$repo/docs/ssh-workflow/"[27m[7m  fi[27m[7mdone[27m[7mecho "OUT=$OUT"[27m[7mecho[27m[7mecho "== preview =="[27m[7msed -n '1,220p' "$OUT"[27m[7mecho[27m[7mecho "== copied targets =="[27m[7mls -l "$HOME/docs/ssh-workflow/" 2>/dev/null || true[27m[7mfor repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do[27m[7m  if [ -d "$repo" ]; then[27m[7m    echo "--- $repo ---"[27m[7m    git -C "$repo" status --short || true[27m[7m    ls -l "$repo/docs/ssh-workflow/" 2>/dev/null || true[27m[7m  fi[27m[7mdone[27m    Hostname: heim-pc    User: alex    Port: 22    SSH Config:      RequestTTY force      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      RemoteCommand latestEOFmkdir -p "$HOME/docs/ssh-workflow"cp "$OUT" "$HOME/docs/ssh-workflow/"for repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do  if [ -d "$repo" ]; then    mkdir -p "$repo/docs/ssh-workflow"    cp "$OUT" "$repo/docs/ssh-workflow/"  fidoneecho "OUT=$OUT"echoecho "== preview =="sed -n '1,220p' "$OUT"echoecho "== copied targets =="ls -l "$HOME/docs/ssh-workflow/" 2>/dev/null || truefor repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do  if [ -d "$repo" ]; then    echo "--- $repo ---"    git -C "$repo" status --short || true    ls -l "$repo/docs/ssh-workflow/" 2>/dev/null || true  fidone
    ssh ' "$HOME/logs/sessions"/session-*.log 2> /dev/null

## SSH command frequency from session logs

         36 ssh heimserver
         35 ssh heimserver '
         20 ssh -T heimserver 'bash -s' <<'REMOTE'
         16 ssh alex@heimberry.local
         11 ssh heimberry '
          9 ssh heimberry
          8 ssh -T heimberry 'bash -s' <<'REMOTE'
          6 ssh alex@heimberry.local '
          4 ssh -G heimberry
          3 ssh -tt alex@heimserver.home.arpa 'bash -lc '"'"'
          3 ssh -T heim-pc 'crash path'
          3 ssh heimserver "BREVO_SMTP_\1=<redacted> bash -s" <<'REMOTE'
          3 ssh -G heimserver
          3 ssh alex@heimberry.home.arpa
          2 ssh -T heimserver 'python3 - <<'"'"'PY'"'"'
          2 ssh -T heim-pc 'bash -s' <<'BASH'
          2 ssh -T git@github.com
          2 ssh heimberry 'hostname; ip -br addr'
          2 ssh ' "$HOME/logs/sessions"/session-*.log 2> /dev/null
          1 ssh -tt heim-pc 'cat > /tmp/crashclip <<'"'"'BASH'"'"'
          1 ssh -tt alex@heimserver.home.arpa 'sudo /sbin/reboot'
          1 ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc 'bash -s' <<'BASH' > "$OUT"
          1 ssh -t -o ConnectTimeout=5 heimberry '
          1 ssh -T heim-pc 'crash why'
          1 ssh -T heim-pc crashclip
          1 ssh -T heim-pc 'bash -s' <<'REMOTE'
          1 ssh -o BatchMode=yes -o ConnectTimeout=5 pi@raspberrypi.local 'hostname; ip -br addr; uname -a' 2> /dev/null
          1 ssh -o BatchMode=yes -o ConnectTimeout=5 heimberry 'mkdir -p "$HOME/.local/bin"'
          1 ssh -o BatchMode=yes -o ConnectTimeout=5 heimberry '
          1 ssh -o BatchMode=yes -o ConnectTimeout=5 alex@heimberry.local 'hostname; ip -br addr; uname -a' 2> /dev/null
          1 ssh -o BatchMode=yes -o ConnectTimeout=5 alex@heimberry 'hostname; ip -br addr; uname -a' 2> /dev/null
          1 ssh heimserver 'hostname; ip -br addr'
          1 ssh heimserver 'hostname; hostname -f 2>/dev/null || true; ip -br addr'
          1 ssh heimserver 'cd /opt/weltgewebe && git status --short && git pull --ff-only'
          1 ssh heimberry 'hostname; hostname -f 2>/dev/null || true; ip -br addr'
          1 ssh heimberry 'bash -s' <<'SH'
          1 ssh -G acs
          1 ssh alex@raspberrypi.local
          1 ssh alex@heimserver.home.arpa 'sudo reboot'
          1 ssh alex@heimserver.home.arpa 'ssh-keygen -l -f /etc/ssh/ssh_host_ed25519_key.pub'
          1 ssh alex@heimserver.home.arpa 'bash -s' <<'EOF'
          1 ssh alex@heimserver.home.arpa "bash -s" <<EOF
          1 ssh alex@heimberry
          1 ssh alex@192.168.178.X
          1 ssh alex@192.168.178.60
          1 //' \  | sort \  | uniq -c \  | sort -nr \  | sed -n '1,160p' \  | sed 's/^/    /' >> "$OUT" || truecat >> "$OUT" <<'EOF'## Suggested Blink configs### heim-pc    Hostname: 100.68.88.111    User: alex    Port: 22    SSH Config:      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      # no RemoteCommand### pcclip    Hostname: heim-pc    User: alex    Port: 22    SSH Config:      RequestTTY no      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      RemoteCommand crashclip### pcnew    Hostname: heim-pc    User: alex    Port: 22    SSH Config:      RequestTTY force      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      RemoteCommand new### pclatest[7m    Hostname: heim-pc[27m[7m    User: alex[27m[7m    Port: 22[27m[7m    SSH Config:[27m[7m      RequestTTY force[27m[7m      ConnectTimeout 8[27m[7m      ServerAliveInterval 3[27m[7m      ServerAliveCountMax 1[27m[7m      RemoteCommand latest[27m[7mEOF[27m[7mmkdir -p "$HOME/docs/ssh-workflow"[27m[7mcp "$OUT" "$HOME/docs/ssh-workflow/"[27m[7mfor repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do[27m[7m  if [ -d "$repo" ]; then[27m[7m    mkdir -p "$repo/docs/ssh-workflow"[27m[7m    cp "$OUT" "$repo/docs/ssh-workflow/"[27m[7m  fi[27m[7mdone[27m[7mecho "OUT=$OUT"[27m[7mecho[27m[7mecho "== preview =="[27m[7msed -n '1,220p' "$OUT"[27m[7mecho[27m[7mecho "== copied targets =="[27m[7mls -l "$HOME/docs/ssh-workflow/" 2>/dev/null || true[27m[7mfor repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do[27m[7m  if [ -d "$repo" ]; then[27m[7m    echo "--- $repo ---"[27m[7m    git -C "$repo" status --short || true[27m[7m    ls -l "$repo/docs/ssh-workflow/" 2>/dev/null || true[27m[7m  fi[27m[7mdone[27m    Hostname: heim-pc    User: alex    Port: 22    SSH Config:      RequestTTY force      ConnectTimeout 8      ServerAliveInterval 3      ServerAliveCountMax 1      RemoteCommand latestEOFmkdir -p "$HOME/docs/ssh-workflow"cp "$OUT" "$HOME/docs/ssh-workflow/"for repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do  if [ -d "$repo" ]; then    mkdir -p "$repo/docs/ssh-workflow"    cp "$OUT" "$repo/docs/ssh-workflow/"  fidoneecho "OUT=$OUT"echoecho "== preview =="sed -n '1,220p' "$OUT"echoecho "== copied targets =="ls -l "$HOME/docs/ssh-workflow/" 2>/dev/null || truefor repo in "$HOME/repos/infra" "$HOME/repos/pc" "$HOME/repos/metarepo"; do  if [ -d "$repo" ]; then    echo "--- $repo ---"    git -C "$repo" status --short || true    ls -l "$repo/docs/ssh-workflow/" 2>/dev/null || true  fidone
          1 //' \ | sort \ | uniq -c \ | sort -nr \ | sed -n '1,120p' echo '’BASHecho “$OUT”```bashcat "$OUT"mkdir -p ./docs/ssh-workflowcp "$OUT" ./docs/ssh-workflow/ls -l ./docs/ssh-workflow/ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc "mkdir -p ~/docs/ssh-workflow && cat > ~/docs/ssh-workflow/$(basename "$OUT")" < "$OUT"ssh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc 'ls -l ~/docs/ssh-workflow && tail -n 20 ~/docs/ssh-workflow/ssh-workflow-commands-*.md'if [ -d "$HOME/repos/infra" ]; then  mkdir -p "$HOME/repos/infra/docs/ssh-workflow"  cp "$OUT" "$HOME/repos/infra/docs/ssh-workflow/"  git -C "$HOME/repos/infra" status --shortfifor h in heim-pc pcclip pcnew pclatest; do  echo "===== $h ====="  ssh -G "$h" 2>/dev/null | grep -Ei '^(hostname|user|port|requesttty|remotecommand|identityfile|preferredauthentications|passwordauthentication|connecttimeout|serveraliveinterval|serveralivecountmax) '  echodonefor h in heim-pc pcclip pcnew pclatest; do  echo "===== $h ====="  ssh -G "$h" 2>/dev/null | sed -n '1,220p'  echodone > "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt"cat "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt"cp "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt" ./docs/ssh-workflow/ 2>/dev/null || truessh -T -o ConnectTimeout=8 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 heim-pc "cat > ~/docs/ssh-workflow/blink-ssh-G-hosts-$STAMP.txt" < "$HOME/ssh-workflow-audit/blink-ssh-G-hosts-$STAMP.txt"
          1 //' \ | sort \ | uniq -c \ | sort -nr \ | sed -n '1,120p' echo '’
          1 //' \ | awk '!seen[$0]++' \ | sed -n '1,300p' echo '’

## Suggested Blink configs

### heim-pc

    Hostname: 100.68.88.111
    User: alex
    Port: 22
    SSH Config:
      ConnectTimeout 8
      ServerAliveInterval 3
      ServerAliveCountMax 1
      # no RemoteCommand

### pcclip

    Hostname: heim-pc
    User: alex
    Port: 22
    SSH Config:
      RequestTTY no
      ConnectTimeout 8
      ServerAliveInterval 3
      ServerAliveCountMax 1
      RemoteCommand crashclip

### pcnew

    Hostname: heim-pc
    User: alex
    Port: 22
    SSH Config:
      RequestTTY force
      ConnectTimeout 8
      ServerAliveInterval 3
      ServerAliveCountMax 1
      RemoteCommand new

### pclatest

    Hostname: heim-pc
    User: alex
    Port: 22
    SSH Config:
      RequestTTY force
      ConnectTimeout 8
      ServerAliveInterval 3
      ServerAliveCountMax 1
      RemoteCommand latest
