#!/usr/bin/env python3
"""Checks a build's two package zips from the outside: what package.sh wrote, re-opened and proved again.

    python3 -I tools/package/verify_zips.py <CommonwealthMotorbike_<build>.zip> <CommonwealthMotorbike_MO2.zip>
        --repo <repository> --commit <the packaged commit> --previous <the previous package's folder>
        [--manifest tools/package/builds/<build>.json] [--list-changes]

Standard library only (and pkglib.py beside this file); the zips and the previous package are read as data, never
unpacked to disk. One PASS or FAIL line per check, then "<n> PASS, <m> FAIL"; exit 0 only with no FAIL (2 for a
usage error or an unreadable input).

  the zips       each opens, every member is a plain file with a plain relative ASCII name and reads back with its
                 CRC; the first has the one top folder CommonwealthMotorbike_<build>/ (README.txt, Data/), the MO2
                 one is Data's contents at its root with no README.txt; both hold the same files with the same
                 bytes; members in the packager's order, deflated, with the packager's times and modes
  the content    pkglib.content_checks, the packager's own guard, over the first zip: the layout, no
                 CMB_BikeFit.json, no "optional" folder, tracked files against the commit (but the four engine
                 WAVs, which must not be the commit's fallbacks), no copy of a script source, one stamped .pex per
                 source, every path a nif / material / the plugin / look_options.json names shipped or in
                 game_paths.txt, every shipped DDS and BGSM named, README.txt (line 1, placeholder, ASCII, the
                 heading, the credit block against CREDITS.txt), the plugin's header (record count, next object
                 ID) and the manifest's records, each WAV's format, the counts per extension
  the previous   every file that is not the commit's or README.txt (the assets, the compiled scripts) against
  package        --previous by sha256: the ones that differ, appear or are gone must be exactly the manifest's
                 vs_previous lists (with its sha256 where given). A compiled script is compared by its code (its
                 header's compile time and source folder aside).

--list-changes also prints the vs_previous block as found, to read and paste into a new build's manifest.
--previous is a package folder (the one holding README.txt and Data/), e.g. a zip unpacked with
"package.sh --extract"; the manifest's "previous" must be the build its name ends in.
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))    # pkglib.py: python3 -I leaves this folder out
import pkglib as L  # noqa: E402


def zip_checks(rep, tree, label, commit, manifest, names_of):
    """A zip's own shape: its problems, then the packager's order, times, modes and compression."""
    rep.check(not tree.problems, "%s: opens, %d plain members, every one reads back with its CRC (%d bytes)"
              % (label, len(tree.names), sum(i.file_size for i in tree.infos.values())), L.some(tree.problems))
    want = [n for n in L.zip_order(names_of(tree.names))]
    rep.check([names_of([n])[0] for n in tree.order] == want,
              "%s: members in the packager's order (README.txt first, then a walk of Data)" % label,
              "first out of place: %s" % next((a for a, b in zip(tree.order, want) if names_of([a])[0] != b), "?"))
    bad = []
    for n in tree.names:
        info, name = tree.infos[n], names_of([n])[0]
        mode = commit.tracked[name][0] if name in commit.shipped else 0o644
        if info.compress_type != 8:
            bad.append("%s: compression %d, not deflate" % (n, info.compress_type))
        elif info.date_time != L.zip_time(manifest, commit, name)[:5] + (L.zip_time(manifest, commit, name)[5] // 2 * 2,):
            bad.append("%s: time %04d-%02d-%02d %02d:%02d:%02d" % ((n,) + info.date_time))
        elif (info.external_attr >> 16) & 0o777 != mode:
            bad.append("%s: mode %o, not %o" % (n, (info.external_attr >> 16) & 0o777, mode))
        elif info.extra or info.comment:
            bad.append("%s: an extra field or a comment" % n)
    rep.check(not bad, "%s: every member deflated, with the packager's time and mode, no extra field" % label, L.some(bad))


def previous_checks(rep, tree, prev, commit, manifest, label):
    """The assets and the compiled scripts against the previous package; returns the differences found."""
    vs = manifest["vs_previous"]
    kinds = {n: L.classify(n, commit) for n in tree.names}
    ours = sorted(n for n, k in kinds.items() if k in ("asset", "pex"))
    theirs = sorted(n for n in prev.names if n not in commit.shipped
                    and L.classify(n, commit) in ("asset", "pex"))
    same, changed, added, header_only, unreadable = [], [], [], [], []
    for n in ours:
        if n not in prev.names:
            added.append(n)
        elif tree.sha(n) == prev.sha(n):
            same.append(n)
        elif kinds[n] == "pex":
            try:
                if L.pex_code(tree.read(n)) == L.pex_code(prev.read(n)):
                    header_only.append(n)
                else:
                    changed.append(n)
            except L.Fail as e:
                unreadable.append("%s: %s" % (n, e))
        else:
            changed.append(n)
    removed = [n for n in theirs if n not in tree.names]

    assets = [n for n in ours if kinds[n] == "asset"]
    rep.check(not unreadable, "against %s: %d of %d asset files and %d of %d compiled scripts are its, byte for byte%s"
              % (label, sum(1 for n in same if kinds[n] == "asset"), len(assets),
                 sum(1 for n in same if kinds[n] == "pex"), len(ours) - len(assets),
                 "; %d more compiled scripts have its code under another header" % len(header_only) if header_only else ""),
              L.some(unreadable))

    def exact(found, listed, what):
        extra = sorted(set(found) - set(listed))
        absent = sorted(set(listed) - set(found))
        rep.check(not extra and not absent,
                  "against %s: the files %s are exactly the manifest's %d%s"
                  % (label, what, len(listed), " (%s)" % L.some(sorted(listed), 4) if listed else ""),
                  "; ".join(x for x in ("%s and not in the manifest: %s" % (what, L.some(extra)) if extra else "",
                                        "in the manifest and not %s: %s" % (what, L.some(absent)) if absent else "") if x))

    exact(changed, vs["changed"], "that differ")
    exact(added, vs["added"], "that are new")
    exact(removed, vs["removed"], "that are gone")
    pins = dict(vs["changed"], **vs["added"])
    wrong = sorted(n for n, digest in pins.items() if digest and n in tree.names and tree.sha(n) != digest)
    rep.check(not wrong, "against %s: the manifest's %d sha256 of changed and new files hold"
              % (label, sum(1 for d in pins.values() if d)), L.some(wrong))
    return {"changed": {n: tree.sha(n) for n in changed}, "added": {n: tree.sha(n) for n in added}, "removed": removed}


def main(argv):
    ap = argparse.ArgumentParser(description="Verify a build's two package zips (see this file's header).")
    ap.add_argument("zip", help="CommonwealthMotorbike_<build>.zip")
    ap.add_argument("mo2", help="CommonwealthMotorbike_MO2.zip")
    ap.add_argument("--repo", required=True, help="the repository")
    ap.add_argument("--commit", required=True, help="the commit the package was made from")
    ap.add_argument("--previous", required=True, help="the previous package's folder (README.txt, Data/)")
    ap.add_argument("--manifest", help="default: builds/<build>.json beside this file, <build> from the zip's name")
    ap.add_argument("--list-changes", action="store_true", help="also print the vs_previous block as found")
    args = ap.parse_args(argv)

    try:
        stem = os.path.basename(args.zip)
        if not (stem.startswith(L.NAME + "_") and stem.endswith(".zip")):
            raise L.Fail("%s is not named %s_<build>.zip" % (stem, L.NAME))
        build = stem[len(L.NAME) + 1:-4]
        manifest = L.load_manifest(args.manifest or os.path.join(L.HERE, "builds", build + ".json"), build)
        commit = L.Commit(args.repo, args.commit)
        prev = L.DirTree(args.previous)
        prev_name = os.path.basename(os.path.abspath(args.previous))
        if "Data/" + L.NAME + ".esp" not in prev.names:
            raise L.Fail("%s is not a package folder (no Data/%s.esp)" % (args.previous, L.NAME))
        if "previous" in manifest and not prev_name.endswith("_" + manifest["previous"]):
            raise L.Fail("the manifest's previous build is %s, --previous is %s" % (manifest["previous"], prev_name))
        top = L.NAME + "_" + build + "/"
        full, mo2 = L.ZipTree(args.zip, top), L.ZipTree(args.mo2, "")
    except (L.Fail, OSError) as e:
        print("cannot verify: %s" % e, file=sys.stderr)
        return 2
    except Exception as e:                          # zipfile.BadZipFile and the like: a file that is no zip at all
        print("cannot verify: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2

    print("verifying build %s, commit %s, against %s" % (build, commit.sha7, prev_name))
    rep = L.Report(ok="PASS  ")

    zip_checks(rep, full, os.path.basename(args.zip), commit, manifest, lambda names: list(names))
    zip_checks(rep, mo2, os.path.basename(args.mo2), commit, manifest, lambda names: ["Data/" + n for n in names])
    a = {n[5:]: full.sha(n) for n in full.names if n.startswith("Data/")}
    b = {n: mo2.sha(n) for n in mo2.names}
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    differ = sorted(n for n in a if n in b and a[n] != b[n])
    rep.check(not only_a and not only_b and not differ,
              "both zips hold the same %d Data files with the same bytes (the MO2 one at its root, no README.txt)" % len(a),
              "; ".join(x for x in ("only in the first: " + L.some(only_a) if only_a else "",
                                    "only in the MO2 zip: " + L.some(only_b) if only_b else "",
                                    "different bytes: " + L.some(differ) if differ else "") if x))

    L.content_checks(rep, full, commit, manifest, wavs_each=True)
    found = previous_checks(rep, full, prev, commit, manifest, prev_name)

    if args.list_changes:
        print("vs_previous as found:")
        print(json.dumps({"vs_previous": found}, indent=2, sort_keys=True))
    print("%d PASS, %d FAIL" % (rep.passed, rep.failed))
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
