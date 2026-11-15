#!/usr/bin/env bash
# hrun_selftest.sh - tries hrun.sh's queue with dummy commands and a dummy worktree, on locks of its
# own (HRUN_DIR = a new folder under $CMB_ROOT/tmp, left there), so it can run beside real harness runs.
# About 45 s. Prints PASS/FAIL per test; exit 0 only if all pass.
#   hrun_selftest.sh [hrun.sh to test]     (default $CMB_ROOT/hrun.sh; CMB_ROOT default /opt/cmb)
set -uo pipefail
CMB="${CMB_ROOT:-/opt/cmb}"
H="${1:-$CMB/hrun.sh}"
mkdir -p "$CMB/tmp"
T="$(mktemp -d "$CMB/tmp/selftest.XXXXXX")"; cd "$T"
export HRUN_DIR="$T/hd" HRUN_QUIET=1
bad=0
verdict() { if [ "$1" = 0 ]; then echo "  PASS"; else echo "  FAIL"; bad=1; fi; }
stamp() { echo "$1 $2 $(date +%s.%N)"; }; export -f stamp
job() { # <name> <seconds> [HRUN_HEAVY=1]: a --cmd job that logs its start and end, in the background
  ( env ${3:-HRUN_X=0} "$H" --cmd bash -c "stamp start $1; sleep $2; stamp end $1" > "$4.$1.out" 2>/dev/null & )
}
ev() { # <glob> <heavy names> <want max together> <want max heavy together> [<want start order>]
  python3 -I - "$@" <<'PY'
import glob, sys
ev = []
for f in sorted(glob.glob(sys.argv[1])):
    for l in open(f):
        k, i, t = l.split(); ev.append((float(t), k, i))
ev.sort(); t0 = ev[0][0]; run = mx = hv = mh = 0; order = ''
for t, k, i in ev:
    d = 1 if k == 'start' else -1; run += d; mx = max(mx, run)
    if i in sys.argv[2]: hv += d; mh = max(mh, hv)
    if k == 'start': order += i
    print('    %5.2fs %s %s (running %d)' % (t - t0, k, i, run))
print('    max together %d, max heavy together %d, start order %s' % (mx, mh, order))
ok = mx == int(sys.argv[3]) and mh == int(sys.argv[4]) and run == 0
if len(sys.argv) > 5: ok = ok and order.startswith(sys.argv[5])
sys.exit(0 if ok else 1)
PY
}
echo "1. three jobs, two slots: the third starts when the first ends"
for i in 1 2 3; do job $i 2 "" t1; sleep 0.2; done; sleep 5.5; ev 't1.*.out' '' 2 0 123; verdict $?
echo "2. slot 1 busy 5 s, slot 2 busy 1.5 s: a waiter takes slot 2 at about 1.5 s"
job a 5 "" t2; sleep 0.3; job b 1.5 "" t2; sleep 0.3
s=$(date +%s.%N); HRUN_QUIET= "$H" --cmd true 2> t2.c.err; e=$(date +%s.%N); sed 's/^/    /' t2.c.err
python3 -I -c "import sys; w=$e-$s; print('    waited %.2f s' % w); sys.exit(0 if 0.7 < w < 2.3 else 1)" && grep -q 'slot 2' t2.c.err; verdict $?
sleep 4.2
echo "3. slots busy; light c d e wait, then heavy X and Y come: X takes the first slot that frees, Y only after X"
job a 2.5 "" t3; sleep 0.2; job b 3.2 "" t3; sleep 0.3; for i in c d e; do job $i 1 "" t3; done; sleep 0.5
job X 2 HRUN_HEAVY=1 t3; sleep 0.2; job Y 2 HRUN_HEAVY=1 t3; sleep 0.5; "$H" --status | cut -c1-70 | sed 's/^/    /'
sleep 9.5; ev 't3.*.out' 'XY' 2 1 abX; verdict $?
echo "4. a command's status comes back; bad usage is 2"
"$H" --cmd bash -c 'exit 7'; a=$?; "$H" 2>/dev/null; b=$?; echo "    $a $b"; [ "$a" = 7 ] && [ "$b" = 2 ]; verdict $?
echo "5. TERM to hrun.sh stops the job's whole group and frees the slot"
"$H" --cmd bash -c 'sleep 301 & sleep 301; wait' & hp=$!; sleep 1; kill -TERM $hp; wait $hp; a=$?; sleep 0.5
n=$(pgrep -fc '^sleep 301' || true); echo "    status $a, sleepers left $n"; [ "$a" = 143 ] && [ "$n" = 0 ] && ! "$H" --status | grep -q BUSY; verdict $?
# a dummy worktree: run.sh with the real one's shape (ONLY, HERE, the DLL three folders up, last_<mode>.log)
W="$T/fakewt"; mkdir -p "$W/tools/f4se-slope/test" "$W/Data/F4SE/Plugins"; echo dll-v1 > "$W/Data/F4SE/Plugins/CMB_Slope.dll"; echo '/* fake */' > "$W/tools/f4se-slope/test/fake_game.c"
R="$W/tools/f4se-slope/test/run.sh"
cat > "$R" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ONLY="${ONLY:-}"
run() { if [ -n "$ONLY" ] && [ "$ONLY" != "$1" ]; then return; fi
  echo "== $1 user=$USER nice=$(nice) tmpdir=${TMPDIR:-unset} dll=$(cat "$HERE/../../../Data/F4SE/Plugins/CMB_Slope.dll")"
  sleep 1.5
  echo "  ok first (version ONE)"
  sleep 1.5
  echo "  ok second (version ONE)"
  if [ "$1" = bad ]; then echo "  FAIL third"; fi
  echo plugin-log > "$HERE/last_$1.log"
}
run alpha 0 "x"
run full 1 "x"
run climb 2 "x"
run bad 3 "x"
exit 0
SH
echo "6. run.sh and the DLL replaced mid-run: the run finishes from its snapshot, as root, nice 19, no TMPDIR"
USER=nobody TMPDIR="$CMB/tmp" "$H" "$W" alpha "$T/t6.log" > t6.out & sleep 0.7
sed -i 's/version ONE/version TWO/; s/sleep 1.5/exit 9/' "$R"; echo dll-v2 > "$W/Data/F4SE/Plugins/CMB_Slope.dll"; wait $!; a=$?
sed 's/^/    /' t6.out t6.log
[ "$a" = 0 ] && [ "$(grep -c 'version ONE' t6.log)" = 2 ] && grep -q 'user=root nice=19 tmpdir=unset dll=dll-v1' t6.log && grep -q 'alpha ok=2 fail=0 rc=0' t6.out && [ -f "$W/tools/f4se-slope/test/last_alpha.log" ]; verdict $?
echo "7. a queued run tests the tree as it was when it was queued"
sed -i 's/exit 9/sleep 1.5/' "$R"; job a 2 "" t7; job b 2 "" t7; sleep 0.3
"$H" "$W" alpha "$T/t7.log" > t7.out & sleep 0.7; sed -i 's/version TWO/version THREE/' "$R"; echo dll-v3 > "$W/Data/F4SE/Plugins/CMB_Slope.dll"; wait $!; a=$?
sed 's/^/    /' t7.out; [ "$a" = 0 ] && [ "$(grep -c 'version TWO' t7.log)" = 2 ] && grep -q 'dll=dll-v2' t7.log; verdict $?
echo "8. a FAIL line, a non-zero run.sh and an unknown mode each fail the call; the default log path"
"$H" "$W" bad > t8a.out; a=$?; sed -i 's/^exit 0$/exit 1/' "$R"; "$H" "$W" alpha "$T/t8b.log" > t8b.out; b=$?; sed -i 's/^exit 1$/exit 0/' "$R"
"$H" "$W" nosuchmode 2> t8c.err; c=$?; sed 's/^/    /' t8a.out t8b.out t8c.err
[ "$a" = 1 ] && [ "$b" = 1 ] && [ "$c" = 2 ] && grep -q 'bad ok=2 fail=1 rc=0' t8a.out && grep -q 'alpha ok=2 fail=0 rc=1' t8b.out && [ -f "$HRUN_DIR/logs/fakewt/bad.log" ]; verdict $?
echo "9. full and climb never together, another mode beside them"
for m in full climb alpha; do ( "$H" "$W" $m "$T/t9.$m.log" > t9.$m.out & ); sleep 0.1; done; sleep 7.5
python3 -I - <<'PY'
import re, sys, datetime
t = {}
for m in ('full', 'climb', 'alpha'):
    s = open('t9.%s.log' % m).read()
    st = datetime.datetime.strptime(re.search(r'started (\S+)Z', s).group(1), '%Y-%m-%dT%H:%M:%S').timestamp()
    t[m] = (st, st + int(re.search(r' run=(\d+)s', s).group(1)))
    print('    %s: %d..%d' % (m, t[m][0] - min(v[0] for v in t.values()), t[m][1] - min(v[0] for v in t.values())))
a, b = sorted((t['full'], t['climb']))
sys.exit(0 if a[1] <= b[0] and t['alpha'][0] < a[1] else 1)
PY
verdict $?
echo "10. hrun.sh itself overwritten while a run of it waits and runs"
cp "$H" "$T/hrun_copy.sh"; job a 1.5 "" t10; job b 1.5 "" t10; sleep 0.3
"$T/hrun_copy.sh" "$W" alpha "$T/t10.log" > t10.out & sleep 0.5; printf '#!/bin/bash\necho BROKEN; exit 99\n' > "$T/hrun_copy.sh"; wait $!; a=$?
sed 's/^/    /' t10.out; [ "$a" = 0 ] && grep -q 'alpha ok=2 fail=0 rc=0' t10.out; verdict $?
left=$(ls "$HRUN_DIR/tmp" | wc -l); echo "snapshots left behind: $left"; [ "$left" = 0 ] || bad=1
if [ "$bad" = 0 ]; then echo "SELFTEST PASS ($T)"; else echo "SELFTEST FAIL ($T)"; fi
exit $bad
