#!/usr/bin/env bash
# hrun.sh - the harness queue: at most two heavy jobs at once on this machine, and never two of
# the heavy harness modes (full, climb) together.
#
#   hrun.sh <worktree> <mode> [logfile]   one mode of <worktree>/tools/f4se-slope/test/run.sh
#   hrun.sh --cmd <command...>            any other heavy job (a build, a tool) in a slot
#   hrun.sh --status                      who holds the slots
#
# Slots: flock on $DIR/harness.1.lock and $DIR/harness.2.lock (DIR below); a waiter polls both and
# takes whichever frees first. full and climb (and --cmd with HRUN_HEAVY=1) first take
# $DIR/heavy.lock, then a slot (always in that order, so there is no deadlock). While the job
# that holds heavy.lock waits for a slot the others stand back, so the long modes start early and
# the rest fill the other slot beside them.
#
# A mode runs as run.sh expects (USER=root ONLY=<mode>, nice -n 19) from a private snapshot taken
# WHEN hrun.sh IS CALLED (not when its turn comes): run.sh, fake_game.c and
# Data/F4SE/Plugins/CMB_Slope.dll are copied to a temp tree of the same layout, so editing or
# rebuilding in the worktree while the run waits or runs can't change or break it. The plugin's
# log comes back as <worktree>/tools/f4se-slope/test/last_<mode>.log, as run.sh leaves it.
#
# The mode's output goes to the logfile (default $DIR/logs/<worktree's name>/<mode>.log);
# stdout gets one line:  <mode> ok=<n> fail=<n> rc=<run.sh's status> wait=<s> run=<s> log=<path>
# Exit status: 0 only if run.sh returned 0, there is no "  FAIL" line and at least one "  ok " line.
# An unknown mode is refused (run.sh would run nothing and return 0).
#
# TMPDIR is taken out of a mode's environment: Wine 9.0 here aborts ("free(): invalid pointer") with
# TMPDIR set to anything, /tmp included, and every check is then missing. (--cmd keeps it.)
#
# Environment: HRUN_DIR (DIR: where the locks, snapshots and logs live; default $CMB_ROOT, itself
# default /opt/cmb), HRUN_POLL (seconds between tries, default 0.5), HRUN_TIMEOUT (seconds for a
# mode or command, default 7200, 0 = none), HRUN_HEAVY=1 (--cmd only: take heavy.lock too),
# HRUN_QUIET=1 (no "waiting" notes on stderr). Two roots share slots only if their DIR is the same.
set -euo pipefail
main() {   # the whole script is one function, read before it runs: replacing hrun.sh can't break a waiting run
DIR="${HRUN_DIR:-${CMB_ROOT:-/opt/cmb}}"
POLL="${HRUN_POLL:-0.5}"
TMO="${HRUN_TIMEOUT:-7200}"
usage() { sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2; exit 2; }
note() { [ -n "${HRUN_QUIET:-}" ] || echo "hrun[$$]: $*" >&2; }
[ $# -ge 1 ] || usage
SNAPS="$DIR/tmp"   # the snapshots; run.sh's own work folder and Wine prefix stay under /tmp (mktemp -d)
mkdir -p "$DIR" "$SNAPS"

if [ "$1" = "--status" ]; then
  for f in harness.1 harness.2 heavy; do
    if [ -s "$DIR/$f.lock" ] && ! flock -n "$DIR/$f.lock" true 2>/dev/null; then
      echo "$f: BUSY  $(cat "$DIR/$f.lock")"
    else
      echo "$f: free"
    fi
  done
  exit 0
fi

SNAP="" CHILD=""
cleanup() {
  if [ -n "$CHILD" ]; then kill -TERM -- "-$CHILD" 2>/dev/null || true; fi
  if [ -n "$SNAP" ]; then rm -rf "$SNAP"; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

heavy=0
if [ "$1" = "--cmd" ]; then
  shift; [ $# -ge 1 ] || usage
  kind=cmd; what="$*"
  [ "${HRUN_HEAVY:-0}" = 1 ] && heavy=1
else
  [ $# -ge 2 ] && [ $# -le 3 ] || usage
  kind=mode
  WT="$(cd "$1" && pwd)"; MODE="$2"
  TEST="$WT/tools/f4se-slope/test"
  [ -f "$TEST/run.sh" ] || { echo "hrun: no $TEST/run.sh" >&2; exit 2; }
  [ -f "$WT/Data/F4SE/Plugins/CMB_Slope.dll" ] || { echo "hrun: no $WT/Data/F4SE/Plugins/CMB_Slope.dll (build it first)" >&2; exit 2; }
  # the snapshot, now: the files run.sh uses, at the same relative places
  SNAP="$(mktemp -d "$SNAPS/hrun.XXXXXX")"
  mkdir -p "$SNAP/tools/f4se-slope/test" "$SNAP/Data/F4SE/Plugins"
  cp -p "$TEST/run.sh" "$TEST/fake_game.c" "$SNAP/tools/f4se-slope/test/"
  cp -p "$WT/Data/F4SE/Plugins/CMB_Slope.dll" "$SNAP/Data/F4SE/Plugins/"
  if ! grep -Eq "^run $MODE [0-9]+ " "$SNAP/tools/f4se-slope/test/run.sh"; then
    echo "hrun: unknown mode '$MODE'; run.sh has: $(grep -Eo '^run [a-z0-9_]+ ' "$SNAP/tools/f4se-slope/test/run.sh" | cut -d' ' -f2 | tr '\n' ' ')" >&2
    exit 2
  fi
  LOG="${3:-$DIR/logs/$(basename "$WT")/$MODE.log}"
  mkdir -p "$(dirname "$LOG")"
  what="$MODE of $WT"
  case "$MODE" in full|climb) heavy=1;; esac
fi

t0=$(date +%s)
# heavy.lock first (blocking), then a slot
if [ "$heavy" = 1 ]; then
  exec 7>>"$DIR/heavy.lock"
  if ! flock -n 7; then note "waiting for heavy.lock ($what)"; flock 7; fi
  echo "pid $$ waiting for a slot since $(date -u +%H:%M:%SZ): $what" > "$DIR/heavy.lock"
fi
exec 8>>"$DIR/harness.1.lock" 9>>"$DIR/harness.2.lock"
slot=0 told=0
while :; do
  hp="" hs=""
  if [ "$heavy" = 0 ] && [ -s "$DIR/heavy.lock" ]; then read -r _ hp hs _ < "$DIR/heavy.lock" || true; fi
  if [ "$hs" = waiting ] && [ -n "$hp" ] && kill -0 "$hp" 2>/dev/null; then
    :   # the heavy job is waiting for a slot: it goes first
  else
    if flock -n 8; then slot=1; exec 9>&-; break; fi
    if flock -n 9; then slot=2; exec 8>&-; break; fi
  fi
  if [ "$told" = 0 ]; then note "both slots busy, waiting ($what)"; told=1; fi
  sleep "$POLL"
done
echo "pid $$ since $(date -u +%H:%M:%SZ): $what" > "$DIR/harness.$slot.lock"
if [ "$heavy" = 1 ]; then echo "pid $$ in slot $slot since $(date -u +%H:%M:%SZ): $what" > "$DIR/heavy.lock"; fi
t1=$(date +%s)

# The job runs in its own session with the lock descriptors closed: only this shell holds the
# locks, so a lingering wineserver can't keep a slot, and cleanup can stop the whole group.
runjob() { # runs "$@", output to fd 1/2 as given
  local rc=0
  if [ "$TMO" != 0 ]; then set -- timeout -k 30 "$TMO" "$@"; fi
  setsid "$@" 7>&- 8>&- 9>&- &
  CHILD=$!
  wait "$CHILD" || rc=$?
  CHILD=""
  return $rc
}

if [ "$kind" = cmd ]; then
  rc=0; runjob "$@" || rc=$?
  t2=$(date +%s)
  note "slot $slot: wait=$((t1-t0))s run=$((t2-t1))s rc=$rc ($what)"
  exit $rc
fi

{
  echo "## hrun: mode $MODE, slot $slot, worktree $WT ($(git -C "$WT" rev-parse --short HEAD 2>/dev/null || echo '?')$(git -C "$WT" status --porcelain 2>/dev/null | grep -q . && echo ' +changes'))"
  echo "## hrun: dll $(sha256sum < "$SNAP/Data/F4SE/Plugins/CMB_Slope.dll" | cut -c1-16) run.sh $(sha256sum < "$SNAP/tools/f4se-slope/test/run.sh" | cut -c1-16) fake_game.c $(sha256sum < "$SNAP/tools/f4se-slope/test/fake_game.c" | cut -c1-16)"
  echo "## hrun: snapshot $(date -u -d "@$t0" +%FT%TZ), started $(date -u -d "@$t1" +%FT%TZ) after $((t1-t0)) s in the queue"
} > "$LOG"
rc=0
runjob env -u TMPDIR USER=root ONLY="$MODE" nice -n 19 bash "$SNAP/tools/f4se-slope/test/run.sh" >> "$LOG" 2>&1 || rc=$?
t2=$(date +%s)
if [ -f "$SNAP/tools/f4se-slope/test/last_$MODE.log" ]; then
  cp "$SNAP/tools/f4se-slope/test/last_$MODE.log" "$TEST/last_$MODE.log" 2>/dev/null || true
fi
ok=$(grep -c '^  ok ' "$LOG" || true); fail=$(grep -c '^  FAIL' "$LOG" || true)
echo "## hrun: $MODE ok=$ok fail=$fail rc=$rc wait=$((t1-t0))s run=$((t2-t1))s" >> "$LOG"
echo "$MODE ok=$ok fail=$fail rc=$rc wait=$((t1-t0))s run=$((t2-t1))s log=$LOG"
[ "$rc" = 0 ] && [ "$fail" = 0 ] && [ "$ok" -gt 0 ]
}
main "$@"
