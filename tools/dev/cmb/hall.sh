#!/usr/bin/env bash
# hall.sh <worktree> <outdir> [mode...] - every mode of the worktree's run.sh (or the ones named)
# through hrun.sh, all queued at once (hrun.sh lets two run at a time, full and climb never
# together); logs in <outdir>/<mode>.log, the table in <outdir>/SUMMARY.txt and on stdout.
# Exit status 0 only if every mode passed. The queue is $CMB_ROOT/hrun.sh (CMB_ROOT default /opt/cmb).
set -euo pipefail
WT="$(cd "$1" && pwd)"; OUT="$2"; shift 2
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
if [ $# -gt 0 ]; then MODES="$*"; else
  MODES="$(grep -Eo '^run [a-z0-9_]+ [0-9]+ ' "$WT/tools/f4se-slope/test/run.sh" | cut -d' ' -f2 | tr '\n' ' ')"
fi
t0=$(date +%s)
for m in $MODES; do
  ( HRUN_QUIET=1 "${CMB_ROOT:-/opt/cmb}/hrun.sh" "$WT" "$m" "$OUT/$m.log" > "$OUT/$m.result" 2>&1 || true ) &
done
wait
t1=$(date +%s)
{
  printf '%-14s %5s %5s %3s %6s %6s\n' mode ok FAIL rc wait run
  tok=0; tfail=0; bad=0; n=0
  for m in $MODES; do
    r="$(tail -1 "$OUT/$m.result")"
    ok="$(sed -n 's/.* ok=\([0-9]*\) .*/\1/p' <<<"$r")"; fail="$(sed -n 's/.* fail=\([0-9]*\) .*/\1/p' <<<"$r")"
    rc="$(sed -n 's/.* rc=\([0-9]*\) .*/\1/p' <<<"$r")"; w="$(sed -n 's/.* wait=\([0-9]*s\) .*/\1/p' <<<"$r")"; ru="$(sed -n 's/.* run=\([0-9]*s\) .*/\1/p' <<<"$r")"
    if [ -z "$ok" ]; then printf '%-14s %s\n' "$m" "NO RESULT: $r"; bad=1; continue; fi
    printf '%-14s %5s %5s %3s %6s %6s\n' "$m" "$ok" "$fail" "$rc" "$w" "$ru"
    tok=$((tok+ok)); tfail=$((tfail+fail)); n=$((n+1))
    if [ "$rc" != 0 ] || [ "$fail" != 0 ] || [ "$ok" = 0 ]; then bad=1; fi
  done
  printf '%-14s %5s %5s     %s modes, wall %ss\n' TOTAL "$tok" "$tfail" "$n" "$((t1-t0))"
  [ "$bad" = 0 ] && echo "ALL PASS" || echo "NOT ALL PASS"
} | tee "$OUT/SUMMARY.txt"
grep -q '^ALL PASS$' "$OUT/SUMMARY.txt"
