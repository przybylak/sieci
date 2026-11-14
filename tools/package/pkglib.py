#!/usr/bin/env python3
"""Shared code of the release packager (package.sh) and its verifier (verify_zips.py). Standard library only.

    python3 -I pkglib.py package --repo R --commit C --build B --assets DATA [--overlay DIR ...] --pex DIR --out OUT
    python3 -I pkglib.py check-assets DATA [--list assets.sha256]
    python3 -I pkglib.py write-assets-manifest DATA [--list assets.sha256]
    python3 -I pkglib.py extract PACKAGE.zip NEW_FOLDER

package.sh is the front door (it makes the git checks and compiles the scripts); this file does the rest: it lays
the package folder out, runs the guard over it and writes the two zips. verify_zips.py runs the same guard over the
zips, so nothing here trusts what the packager just did.

What a package is made of
  repository   every file the packaged commit tracks under Data/, read from the commit's own objects (never from
               the working tree), but PUT_MESHES_HERE.txt (not shipped) and the four engine WAVs below
  scripts      one .pex per tracked .psc, compiled by package.sh; their headers are stamped here (PEX HEADERS)
  assets       everything under ASSET_ROOTS in the asset base (the previous package's Data folder), overlaid by the
               OVERLAY folders (a Data-like layout; each overlaid file is logged). The four engine WAVs the
               repository tracks as synthesised fallbacks come from here too: the package's are the recorded ones.
               A CMB_BikeFit.json is never taken. The manifest's vs_previous.removed files are dropped.
  README.txt   README.template.txt with @COMMIT@ on its first line replaced

PEX HEADERS. A compiled script's header holds the compile time and the source file's path (the syntax check
compiles copies in a mktemp folder), so two compiles of one source differ in those bytes and nowhere else. The
packager rewrites both: the time to the packaged commit's committer time and the folder to PEX_SOURCE_DIR, or to
the manifest's pex_header (2026-11-10a.json holds that build's real values, which reproduces its .pex files byte
for byte). The script's code is untouched: nothing after the header moves or changes.

ZIPS. Python's zipfile, deflate level 6, no directory entries, no extra fields; README.txt first, then Data/ as a
directory walk (a folder's files in byte order, then its subfolders in byte order); modes 0644, or the commit's
mode for a tracked file (the DLL is 0755 there); every member's time is the packaged commit's committer time (UTC)
unless the manifest's zip.mtime / zip.mtime_overrides say otherwise. The same inputs give the same bytes with the
same zlib (deflate output can differ between zlib builds; the verifier compares contents, never zip bytes).
<name>_<build>.zip has the top folder <name>_<build>/ (README.txt, Data/); <name>_MO2.zip is Data's contents at
the archive's root and no README.txt (a Mod Organizer 2 mod folder as is).

THE GUARD (content_checks) against the lost packager's, from the notes left of it:
  - tracked files against the commit, no CMB_BikeFit.json, no "optional" folder, no copy of a .psc outside the
    sources, the README's first line / heading / ASCII / credit block: as described.
  - references: the old tool's reader of nif and material files is gone. Here a nif and a .bgsm/.bgem are scanned
    as bytes for printable runs ending in .dds/.bgsm/.bgem (their strings are length-prefixed, so a run starts at
    the string's start); the plugin's records are parsed (groups, compressed records, XXXX sizes) and every
    subrecord scanned for NUL-terminated strings ending in .nif/.bgsm/.bgem/.dds/.wav/.xwm; look_options.json's
    string values with those extensions are its files. Simpler than a field-by-field reader, and on 2026-11-10a
    it finds what the old log printed: 218 mod paths, 408 files of look_options.json, 19 game-archive paths.
    Stricter in one way: a path that is not shipped must be in game_paths.txt (the old tool only listed the
    nif/material ones), so a misspelt folder cannot pass as "the game's".
  - the plugin's paths are counted once each (386 on 2026-11-10a: 9 models, 377 materials; the old log said 394,
    a count this file could not reconstruct), and its sound paths are checked the same way.
  - not reimplemented: any check of what a nif or a material *does* (tools/rider/check_bike_meshes.py is that).
"""
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile
import zlib

NAME = "CommonwealthMotorbike"
MO2_ZIP = NAME + "_MO2.zip"
BUILD_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[a-z]$")
HERE = os.path.dirname(os.path.abspath(__file__))

# Folders under Data/ whose files are assets (never in git, but for the four engine WAVs' fallbacks)
ASSET_ROOTS = (
    "Meshes/CMB",
    "Textures/CMB",
    "Materials/CMB",
    "Sound/FX/CMB",
    "Meshes/Actors/Character/Animations/MT/CMB_Rider",
)
# Tracked in git as synthesised fallbacks; the package ships the ones built from the recording (the asset base's)
ENGINE_WAVS = tuple("Data/Sound/FX/CMB/CMB_Engine%s.wav" % n for n in ("Start", "Stop", "CruiseLP", "IdleLP"))
# Tracked under Data/ and not shipped
TRACKED_NOT_SHIPPED = ("Data/Meshes/CMB/PUT_MESHES_HERE.txt",)
NEVER_SHIPPED = "cmb_bikefit.json"          # a build file (lower case; compared without case)
ESP = "Data/" + NAME + ".esp"
SOURCES = "Data/Scripts/Source/User/"
LOOK_OPTIONS = "tools/esp-generator/look_options.json"

README_LINE1 = "COMMONWEALTH MOTORBIKE - READY-TO-INSTALL FILES (%s, repository commit %s)"
README_HEADING = "WHAT'S NEW IN %s"
COMMIT_MARK = "@COMMIT@"
CREDITS_START = b"These files are partly derived from Bethesda's"

PEX_MAGIC = 0xFA57C0DE
PEX_SOURCE_DIR = "/tmp/tmp.0000000000"      # a mktemp name's shape, as every earlier build's header has

MANIFEST_KEYS = {"build", "previous", "esp", "counts", "vs_previous", "pex_header", "zip"}


class Fail(Exception):
    """A refusal: its text is the message."""


# ----------------------------------------------------------------------------------------------------------- report
class Report:
    """Prints one line per check as it is made and counts the failures."""

    def __init__(self, ok="ok    ", bad="FAIL  "):
        self.ok, self.bad, self.passed, self.failed = ok, bad, 0, 0

    def check(self, good, what, detail=""):
        if good:
            self.passed += 1
            print(self.ok + what)
        else:
            self.failed += 1
            print(self.bad + what + (": " + detail if detail else ""))
        sys.stdout.flush()
        return bool(good)

    @staticmethod
    def info(what):
        print("      " + what)


def some(items, limit=6):
    """A list for a message: its first few and how many more."""
    items = list(items)
    return ", ".join(items[:limit]) + (" and %d more" % (len(items) - limit) if len(items) > limit else "")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# -------------------------------------------------------------------------------------------------------------- git
def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise Fail("git %s: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout


class Commit:
    """The packaged commit: its hash, time and the files it tracks under Data/."""

    def __init__(self, repo, rev):
        self.repo = repo
        self.sha = git(repo, "rev-parse", "--verify", rev + "^{commit}").decode().strip()
        self.sha7 = git(repo, "rev-parse", "--short=7", self.sha).decode().strip()
        self.time = int(git(repo, "show", "-s", "--format=%ct", self.sha).decode().strip())
        self.tracked = {}                    # Data/... -> (mode, blob)
        for entry in git(repo, "ls-tree", "-r", "-z", self.sha, "--", "Data").split(b"\0"):
            if not entry:
                continue
            meta, path = entry.split(b"\t", 1)
            mode, kind, blob = meta.decode().split()
            if kind != "blob" or mode not in ("100644", "100755"):
                raise Fail("%s: Data/ holds %s (%s %s), not a plain file" % (self.sha7, path.decode(), mode, kind))
            self.tracked[path.decode()] = (int(mode, 8) & 0o777, blob)
        self.shipped = sorted(p for p in self.tracked if p not in ENGINE_WAVS and p not in TRACKED_NOT_SHIPPED)
        self._blobs = {}

    def blob(self, path):
        if path not in self._blobs:
            self._blobs[path] = git(self.repo, "cat-file", "blob", self.tracked[path][1])
        return self._blobs[path]

    def file(self, path):
        """Any file of the commit, None when it has none there."""
        r = subprocess.run(["git", "-C", self.repo, "cat-file", "blob", "%s:%s" % (self.sha, path)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return None if r.returncode else r.stdout


# ------------------------------------------------------------------------------------------------------------ trees
def walk_files(root):
    """Every file under root as a /-separated relative path, sorted; a symbolic link or special file is refused."""
    out = []
    for folder, dirs, files in os.walk(root):
        for d in dirs:
            if os.path.islink(os.path.join(folder, d)):
                raise Fail("%s: a symbolic link" % os.path.join(folder, d))
        for f in files:
            full = os.path.join(folder, f)
            if os.path.islink(full) or not os.path.isfile(full):
                raise Fail("%s: not a plain file" % full)
            out.append(os.path.relpath(full, root).replace(os.sep, "/"))
    return sorted(out)


class Tree:
    """A package's files by name (README.txt, Data/...)."""
    names = ()

    def __init__(self):
        self._sha = {}

    def read(self, name):
        raise NotImplementedError

    def sha(self, name):
        if name not in self._sha:
            self._sha[name] = sha256(self.read(name))
        return self._sha[name]


class DirTree(Tree):
    def __init__(self, root):
        Tree.__init__(self)
        if not os.path.isdir(root):
            raise Fail("%s: no such folder" % root)
        self.root, self.names = root, walk_files(root)

    def read(self, name):
        with open(os.path.join(self.root, name), "rb") as f:
            return f.read()


class ZipTree(Tree):
    """A zip's members under a prefix ("" for the MO2 layout). problems lists what is wrong with the archive
    itself; every member is read once here, which checks its CRC. The packager writes no directory entries, so
    a zip that has them is not its work (strict); unpacking one that another tool made just skips them."""

    def __init__(self, path, prefix="", strict=True):
        Tree.__init__(self)
        self.path, self.prefix, self.problems, self.infos = path, prefix, [], {}
        self.zip = zipfile.ZipFile(path)
        names = []
        for info in self.zip.infolist():
            n = info.filename
            kind = (info.external_attr >> 16) & 0o170000
            if n in names:
                self.problems.append("%s twice" % n)
            elif info.is_dir():
                if strict:
                    self.problems.append("%s: a directory entry" % n)
            elif kind not in (0, 0o100000):
                self.problems.append("%s: not a plain file (mode %o)" % (n, info.external_attr >> 16))
            elif info.flag_bits & 0x1:
                self.problems.append("%s: encrypted" % n)
            elif (n.startswith("/") or "\\" in n or ":" in n or any(p in ("", ".", "..") for p in n.split("/"))
                  or any(ord(c) < 32 or ord(c) > 126 for c in n)):
                self.problems.append("%r: not a plain relative ASCII path" % n)
            elif not n.startswith(prefix):
                self.problems.append("%s: outside %s" % (n, prefix or "the archive"))
            else:
                names.append(n)
                self.infos[n[len(prefix):]] = info
        for name in sorted(self.infos):
            try:
                self.sha(name)
            except Exception as e:            # zipfile.BadZipFile (CRC), zlib.error, ...
                self.problems.append("%s: unreadable (%s)" % (name, e))
                del self.infos[name]
        self.order = [n[len(prefix):] for n in names if n[len(prefix):] in self.infos]
        self.names = sorted(self.infos)

    def read(self, name):
        return self.zip.read(self.infos[name])


def is_asset(data_rel):
    return any(data_rel.startswith(root + "/") for root in ASSET_ROOTS)


def classify(name, commit):
    """readme, repo (the commit's bytes), pex, asset - or unexpected."""
    if name == "README.txt":
        return "readme"
    if name in commit.shipped:
        return "repo"
    if re.match(r"^Data/Scripts/[^/]+\.pex$", name):
        return "pex"
    if name.startswith("Data/") and is_asset(name[5:]):
        return "asset"
    return "unexpected"


# --------------------------------------------------------------------------------------------------------- manifest
def strip_comments(value):
    """A manifest without its "_..." keys (JSON has no comments: a key starting with _ is one)."""
    if isinstance(value, dict):
        return {k: strip_comments(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [strip_comments(v) for v in value]
    return value


def load_manifest(path, build=None):
    try:
        with open(path, "rb") as f:
            m = strip_comments(json.loads(f.read().decode("utf-8")))
    except (OSError, ValueError) as e:
        raise Fail("%s: %s (copy builds/TEMPLATE.json to builds/<build>.json and fill it in)" % (path, e))
    unknown = sorted(set(m) - MANIFEST_KEYS)
    if unknown:
        raise Fail("%s: unknown key(s) %s" % (path, ", ".join(unknown)))
    if not BUILD_RE.match(str(m.get("build", ""))):
        raise Fail("%s: \"build\" must look like 2026-11-10a" % path)
    if build is not None and m["build"] != build:
        raise Fail("%s is build %s's, not %s's" % (path, m["build"], build))
    esp = m.get("esp", {})
    if not isinstance(esp.get("records"), int) or not isinstance(esp.get("edids", []), list):
        raise Fail("%s: esp.records must be a number, esp.edids a list" % path)
    try:
        m["_next_id"] = int(str(esp["next_object_id"]), 16)
    except (KeyError, ValueError):
        raise Fail("%s: esp.next_object_id must be a hexadecimal string like \"0xBF7\"" % path)
    counts = m.get("counts")
    if not isinstance(counts, dict) or not counts or not all(isinstance(v, int) for v in counts.values()):
        raise Fail("%s: counts must map each extension to a number" % path)
    vs = m.setdefault("vs_previous", {})
    for key, kind in (("changed", dict), ("added", dict), ("removed", list)):
        if not isinstance(vs.setdefault(key, kind()), kind):
            raise Fail("%s: vs_previous.%s must be %s" % (path, key, "an object" if kind is dict else "a list"))
    for key in ("changed", "added"):
        for name, digest in vs[key].items():
            if digest is not None and not re.match(r"^[0-9a-f]{64}$", str(digest)):
                raise Fail("%s: vs_previous.%s[%s] must be a sha256 or null" % (path, key, name))
    for name in list(vs["changed"]) + list(vs["added"]) + vs["removed"]:
        if not name.startswith("Data/"):
            raise Fail("%s: vs_previous names are package paths (Data/...), not %r" % (path, name))
    pex = m.setdefault("pex_header", {})
    if set(pex) - {"compile_time", "source_dir"} or not isinstance(pex.get("compile_time", 0), int) \
            or not isinstance(pex.get("source_dir", ""), str):
        raise Fail("%s: pex_header holds compile_time (a number) and source_dir (a string)" % path)
    z = m.setdefault("zip", {})
    if set(z) - {"mtime", "mtime_overrides"}:
        raise Fail("%s: zip holds mtime and mtime_overrides" % path)
    if not isinstance(z.get("mtime_overrides", {}), dict):
        raise Fail("%s: zip.mtime_overrides must be an object" % path)
    for when in ([z["mtime"]] if "mtime" in z else []) + list(z.get("mtime_overrides", {}).values()):
        parse_time(when)
    return m


def parse_time(text):
    try:
        t = time.strptime(text, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        raise Fail("a zip time must look like \"2026-11-08 21:03:18\", not %r" % (text,))
    if t.tm_year < 1980:
        raise Fail("a zip cannot hold a time before 1980 (%s)" % text)
    return tuple(t[:6])


def pex_stamp(manifest, commit):
    """(compile time, source folder) the package's .pex headers carry."""
    h = manifest["pex_header"]
    return h.get("compile_time", commit.time), h.get("source_dir", PEX_SOURCE_DIR).rstrip("/")


def zip_time(manifest, commit, name):
    """A member's time: the manifest's for that file, the manifest's for all, else the commit's (UTC)."""
    z = manifest["zip"]
    if name in z.get("mtime_overrides", {}):
        return parse_time(z["mtime_overrides"][name])
    if "mtime" in z:
        return parse_time(z["mtime"])
    return tuple(time.gmtime(commit.time)[:6])


# -------------------------------------------------------------------------------------------------------------- pex
def pex_header(data):
    """(compile time, source path, user, machine, offset of what follows) of a Fallout 4 .pex; Fail otherwise."""
    try:
        magic, major, minor, game, when = struct.unpack_from("<IBBHQ", data, 0)
        if magic != PEX_MAGIC or game != 2:
            raise Fail("not a Fallout 4 compiled script (magic %08X, game %d)" % (magic, game))
        at, texts = 16, []
        for _ in range(3):
            n = struct.unpack_from("<H", data, at)[0]
            if at + 2 + n > len(data):
                raise Fail("a truncated compiled script")
            texts.append(data[at + 2:at + 2 + n].decode("utf-8", "replace"))
            at += 2 + n
    except struct.error:
        raise Fail("a truncated compiled script")
    return when, texts[0], texts[1], texts[2], at


def pex_restamp(data, when, source_dir):
    """The same script with its header's compile time and source folder replaced (the code is not touched)."""
    _, source, user, machine, at = pex_header(data)
    source = source_dir + "/" + "/".join(source.replace("\\", "/").split("/")[-2:])
    head = data[:8] + struct.pack("<Q", when)
    for text in (source, user, machine):
        raw = text.encode("utf-8")
        head += struct.pack("<H", len(raw)) + raw
    return head + data[at:]


def pex_code(data):
    """What two compiles of one source share: everything but the compile time and the three header strings."""
    return data[:8] + data[pex_header(data)[4]:]


# -------------------------------------------------------------------------------------------------------------- esp
def esp_parse(data):
    """(HEDR's record count, HEDR's next object ID, records as (type, form ID, payload), group count)."""
    records, groups = [], [0]

    def walk(at, end):
        while at < end:
            if at + 24 > end:
                raise Fail("the plugin: a truncated record header at %d" % at)
            sig, size = data[at:at + 4], struct.unpack_from("<I", data, at + 4)[0]
            if sig == b"GRUP":
                if size < 24 or at + size > end:
                    raise Fail("the plugin: a group of %d bytes at %d runs past its parent" % (size, at))
                groups[0] += 1
                walk(at + 24, at + size)
                at += size
            else:
                flags, form = struct.unpack_from("<II", data, at + 8)
                if at + 24 + size > end:
                    raise Fail("the plugin: record %s at %d runs past its parent" % (sig.decode("latin-1"), at))
                payload = data[at + 24:at + 24 + size]
                if flags & 0x00040000:
                    try:
                        payload = zlib.decompress(payload[4:])
                    except zlib.error as e:
                        raise Fail("the plugin: record %08X does not decompress (%s)" % (form, e))
                records.append((sig.decode("latin-1"), form, payload))
                at += 24 + size

    walk(0, len(data))
    if not records or records[0][0] != "TES4":
        raise Fail("the plugin does not start with a TES4 record")
    first = next(esp_fields(records[0][2]), None)
    if not first or first[0] != "HEDR" or len(first[1]) != 12:
        raise Fail("the plugin's TES4 record does not start with a 12-byte HEDR")
    _, count, next_id = struct.unpack("<fII", first[1])
    return count, next_id, records, groups[0]


def esp_fields(payload):
    """A record's subrecords as (type, bytes); XXXX gives the next one's real size."""
    at, big = 0, None
    while at + 6 <= len(payload):
        sig, size = payload[at:at + 4].decode("latin-1"), struct.unpack_from("<H", payload, at + 4)[0]
        at += 6
        if sig == "XXXX":
            big = struct.unpack_from("<I", payload, at)[0]
            at += size
            continue
        if big is not None:
            size, big = big, None
        yield sig, payload[at:at + size]
        at += size


# ------------------------------------------------------------------------------------------------------- references
FILE_RE = re.compile(rb"[\x20-\x7e]{1,259}\.(?:dds|bgsm|bgem)", re.I)                         # in a nif or a material
ESP_RE = re.compile(rb"[\x20-\x7e]{1,259}\.(?:nif|bgsm|bgem|dds|wav|xwm)(?=\x00|$)", re.I)    # in a subrecord
DATA_FOLDER = {"dds": "textures", "bgsm": "materials", "bgem": "materials", "nif": "meshes", "wav": "sound",
               "xwm": "sound"}


def game_path(text):
    """A path as the game reads it, relative to Data: lower case, backslashes, its type's folder in front
    (a material names textures without "textures\\", a plugin names models without "meshes\\", ...)."""
    p = text.replace("/", "\\").lower().lstrip("\\")
    if p.startswith("data\\"):
        p = p[5:]
    folder = DATA_FOLDER[p.rsplit(".", 1)[1]]
    return p if p.startswith(folder + "\\") else folder + "\\" + p


def load_game_paths(path=None):
    """game_paths.txt: the paths the mod names and does not ship (lower case, relative to Data)."""
    out = set()
    with open(path or os.path.join(HERE, "game_paths.txt"), encoding="ascii") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.add(line.replace("/", "\\").lower())
    return out


def json_strings(value):
    if isinstance(value, dict):
        for v in value.values():
            for s in json_strings(v):
                yield s
    elif isinstance(value, list):
        for v in value:
            for s in json_strings(v):
                yield s
    elif isinstance(value, str):
        yield value


def reference_checks(rep, tree, commit, allowed):
    shipped = {n[5:].replace("/", "\\").lower(): n for n in tree.names if n.startswith("Data/")}

    def split(named):
        ours = sorted(p for p in named if p in shipped)
        game = sorted(p for p in named if p not in shipped and p in allowed)
        lost = sorted(p for p in named if p not in shipped and p not in allowed)
        return ours, game, lost

    def lost_text(named, lost):
        return some("%s (named by %s)" % (p, some(sorted(named[p]), 2)) for p in lost)

    # nifs and materials
    named = {}
    for name in tree.names:
        if name.lower().endswith((".nif", ".bgsm", ".bgem")):
            for m in FILE_RE.finditer(tree.read(name)):
                named.setdefault(game_path(m.group(0).decode("ascii")), set()).add(name.rsplit("/", 1)[-1])
    ours, game, lost = split(named)

    # the option table
    table, raw = {}, commit.file(LOOK_OPTIONS)
    if raw is not None:
        for s in json_strings(json.loads(raw.decode("utf-8"))):
            if re.search(r"\.(dds|bgsm|bgem|nif)$", s, re.I):
                table.setdefault(game_path(s), set()).add("look_options.json")
    t_ours, t_game, t_lost = split(table)
    rep.check(not lost and not t_lost,
              "references: %d mod paths all shipped, %d files of look_options.json all shipped; "
              "%d game-archive paths (not shipped): %s%s"
              % (len(ours), len(t_ours), len(game), ", ".join(game),
                 "" if raw is not None else " [the commit has no %s]" % LOOK_OPTIONS),
              "neither shipped nor in game_paths.txt: " + lost_text(dict(named, **table), lost + t_lost))
    if t_game:
        rep.info("look_options.json also names %d game-archive paths: %s" % (len(t_game), ", ".join(t_game)))

    unnamed = sorted(n for p, n in shipped.items()
                     if p.endswith((".dds", ".bgsm", ".bgem")) and p not in named and p not in table)
    count = sum(1 for p in shipped if p.endswith((".dds", ".bgsm", ".bgem")))
    rep.check(not unnamed, "every shipped DDS and BGSM (%d) is named by a nif, a material or look_options.json" % count,
              some(unnamed))

    # the plugin
    if ESP not in tree.names:
        return
    try:
        records = esp_parse(tree.read(ESP))[2]
    except Fail as e:
        rep.check(False, "the ESP's paths", str(e))
        return
    by = {}
    for sig, form, payload in records:
        for field, value in esp_fields(payload):
            for m in ESP_RE.finditer(value):
                by.setdefault(game_path(m.group(0).decode("ascii")), set()).add("%s %06X %s" % (sig, form & 0xFFFFFF, field))
    models = {p: w for p, w in by.items() if p.endswith(".nif")}
    mats = {p: w for p, w in by.items() if p.endswith((".bgsm", ".bgem", ".dds"))}
    sounds = {p: w for p, w in by.items() if p.endswith((".wav", ".xwm"))}
    both = dict(models, **mats)
    ours, game, lost = split(both)
    own = [p for p in game if "\\cmb\\" in p]             # the mod's own optional file, never shipped
    theirs = [p for p in game if p not in own]
    rep.check(not lost,
              "the ESP: %d model and material paths (%d models, %d materials), %d shipped, %d of them the game's by "
              "path (%s)%s" % (len(both), len(models), len(mats), len(ours), len(theirs), ", ".join(theirs),
                               ", %d the mod's own and optional, not shipped (%s)" % (len(own), ", ".join(own)) if own else ""),
              "neither shipped nor in game_paths.txt: " + lost_text(both, lost))
    ours, game, lost = split(sounds)
    rep.check(not lost, "the ESP: %d sound paths, %d shipped, %d the game's by path" % (len(sounds), len(ours), len(game)),
              "neither shipped nor in game_paths.txt: " + lost_text(sounds, lost))
    n_nif = [n for p, n in shipped.items() if p.endswith(".nif")]
    n_wav = [n for p, n in shipped.items() if p.endswith(".wav")]
    rep.info("the ESP names %d of the %d shipped nifs and %d of the %d shipped WAVs"
             % (sum(1 for p in shipped if p.endswith(".nif") and p in by), len(n_nif),
                sum(1 for p in shipped if p.endswith(".wav") and p in by), len(n_wav)))


# ----------------------------------------------------------------------------------------------------------- README
def make_readme(template, sha7):
    """The template with @COMMIT@ on its first line replaced; Fail unless that is the only one."""
    text = template.decode("ascii")
    first, _, rest = text.partition("\n")
    if first.count(COMMIT_MARK) != 1 or COMMIT_MARK in rest:
        raise Fail("README.template.txt must hold %s once, on its first line" % COMMIT_MARK)
    return (first.replace(COMMIT_MARK, sha7) + "\n" + rest).encode("ascii")


def credit_block(readme):
    """The README's tail from the line starting CREDITS_START (None when it has no such line, or two)."""
    starts = [m.start() for m in re.finditer(rb"(?m)^" + re.escape(CREDITS_START), readme)]
    return readme[starts[0]:] if len(starts) == 1 else None


def readme_checks(rep, readme, build, sha7, credits):
    lines = readme.split(b"\n")
    want = (README_LINE1 % (build, sha7)).encode("ascii")
    rep.check(lines[0] == want, "README.txt line 1 names build %s and commit %s" % (build, sha7),
              "it reads %r" % lines[0][:120].decode("ascii", "replace"))
    rep.check(COMMIT_MARK.encode("ascii") not in readme and not re.search(rb"@[A-Z_]+@", readme),
              "README.txt: no placeholder left", "a @...@ placeholder is still there")
    bad = sorted(set(readme) - set(range(32, 127)) - {9, 10})
    rep.check(not bad, "README.txt is ASCII (%d lines, no CR)" % readme.count(b"\n"),
              "bytes %s" % ", ".join("0x%02X" % b for b in bad[:8]))
    heading = (README_HEADING % build).encode("ascii")
    rep.check(lines.count(heading) == 1, "README.txt has the heading \"%s\"" % heading.decode(),
              "%d such lines" % lines.count(heading))
    block = credit_block(readme)
    if block is None:
        rep.check(False, "README.txt's credit block", "no single line starting \"%s\"" % CREDITS_START.decode())
    else:
        detail = ""
        if block != credits:
            a, b = block.split(b"\n"), credits.split(b"\n")
            at = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
            detail = "differs at its line %d: %r" % (at + 1, (a[at] if at < len(a) else b"<end>")[:100].decode("ascii", "replace"))
        rep.check(block == credits, "README.txt's credit block is CREDITS.txt byte for byte (%d lines, %d bytes)"
                  % (credits.count(b"\n"), len(credits)), detail)


# -------------------------------------------------------------------------------------------------------------- wav
def wav_format(data):
    """(channels, rate, bits, seconds) of a RIFF PCM WAV; Fail otherwise."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise Fail("not a RIFF WAVE file")
    if struct.unpack_from("<I", data, 4)[0] + 8 != len(data):
        raise Fail("its RIFF size is not the file's")
    at, fmt, frames = 12, None, None
    while at + 8 <= len(data):
        kind, size = data[at:at + 4], struct.unpack_from("<I", data, at + 4)[0]
        if at + 8 + size > len(data):
            raise Fail("chunk %r runs past the end" % kind)
        if kind == b"fmt ":
            fmt = struct.unpack_from("<HHIIHH", data, at + 8)
        elif kind == b"data":
            frames = size
        at += 8 + size + (size & 1)
    if fmt is None or frames is None:
        raise Fail("no fmt or data chunk")
    tag, channels, rate, byte_rate, align, bits = fmt
    if tag != 1:
        raise Fail("format tag %d, not PCM" % tag)
    if not channels or not rate or align != channels * bits // 8 or byte_rate != rate * align or not frames:
        raise Fail("inconsistent format (%d ch, %d Hz, %d bit, align %d)" % (channels, rate, bits, align))
    return channels, rate, bits, frames / float(byte_rate)


# ------------------------------------------------------------------------------------------------------------ guard
def content_checks(rep, tree, commit, manifest, wavs_each=False):
    """Everything that can be said of a package's files alone (the packager's guard, and the verifier's too)."""
    build = manifest["build"]
    kinds = {n: classify(n, commit) for n in tree.names}

    # layout
    odd = sorted(n for n, k in kinds.items() if k == "unexpected")
    rep.check(not odd, "layout: README.txt and Data/ only, every file the commit's, a compiled script or under an "
              "asset folder (%d files)" % len(tree.names), some(odd))
    lower = {}
    for n in tree.names:
        lower.setdefault(n.lower(), []).append(n)
    twice = sorted("/".join(v) for v in lower.values() if len(v) > 1)
    plain = [n for n in tree.names if any(ord(c) < 32 or ord(c) > 126 for c in n)]
    rep.check(not twice and not plain, "names: ASCII, no two alike but for case", some(twice + plain))
    fit = [n for n in tree.names if n.rsplit("/", 1)[-1].lower() == NEVER_SHIPPED]
    rep.check(not fit, "no CMB_BikeFit.json anywhere", some(fit))
    opt = [n for n in tree.names if any(part.lower().startswith("optional") for part in n.split("/")[:-1])]
    rep.check(not opt, "no \"optional\" folder", some(opt))

    # the commit's files
    missing = [n for n in commit.shipped if n not in tree.names]
    differ = [n for n in commit.shipped if n in tree.names and tree.read(n) != commit.blob(n)]
    rep.check(not missing and not differ,
              "tracked files: all %d of commit %s's shipped Data files are there, byte for byte"
              % (len(commit.shipped), commit.sha7),
              "; ".join(x for x in ("missing: " + some(missing) if missing else "",
                                    "differ from the commit: " + some(differ) if differ else "") if x))
    left = [n for n in TRACKED_NOT_SHIPPED if n in tree.names]
    rep.check(not left, "tracked and not shipped: %s" % ", ".join(TRACKED_NOT_SHIPPED), some(left))
    fallback = [n for n in ENGINE_WAVS if n in commit.tracked and n in tree.names and tree.read(n) == commit.blob(n)]
    gone = [n for n in ENGINE_WAVS if n not in tree.names]
    rep.check(not fallback and not gone,
              "the listed exception: the %d engine WAVs the commit tracks are the recorded ones, not its synthesised "
              "fallbacks" % len(ENGINE_WAVS),
              "; ".join(x for x in ("missing: " + some(gone) if gone else "",
                                    "the repository's fallback: " + some(fallback) if fallback else "") if x))

    # scripts
    sources = [n for n in tree.names if n.startswith(SOURCES) and n.endswith(".psc")]
    digests = {tree.sha(n) for n in sources}
    digests.update(sha256(commit.blob(n)) for n in commit.tracked if n.endswith(".psc"))
    copies = [n for n in tree.names if n not in sources and tree.sha(n) in digests]
    stray = [n for n in tree.names if n.lower().endswith(".psc") and n not in sources]
    rep.check(not copies and not stray, "no script source outside %s (%d there), no file that is a copy of one"
              % (SOURCES.rstrip("/"), len(sources)), some(copies + stray))
    pex = sorted(n for n, k in kinds.items() if k == "pex")
    want = sorted("Data/Scripts/" + n[len(SOURCES):-4] + ".pex" for n in sources)
    when, folder = pex_stamp(manifest, commit)
    bad = []
    for n in pex:
        try:
            t, source, user, machine, _ = pex_header(tree.read(n))
        except Fail as e:
            bad.append("%s: %s" % (n, e))
            continue
        base = n.rsplit("/", 1)[-1][:-4]
        if t != when:
            bad.append("%s: compile time %d, not %d" % (n, t, when))
        elif not (source.startswith(folder + "/") and source.endswith("/" + base + ".psc")):
            bad.append("%s: source %s, not %s/.../%s.psc" % (n, source, folder, base))
    rep.check(pex == want and not bad,
              "compiled scripts: one Fallout 4 .pex per source (%d), headers stamped %s UTC, %s"
              % (len(want), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(when)), folder),
              "; ".join(x for x in ("no .pex for: " + some(sorted(set(want) - set(pex))) if set(want) - set(pex) else "",
                                    "no source for: " + some(sorted(set(pex) - set(want))) if set(pex) - set(want) else "",
                                    some(bad)) if x))

    # references
    reference_checks(rep, tree, commit, load_game_paths())

    # README
    if "README.txt" in tree.names:
        with open(os.path.join(HERE, "CREDITS.txt"), "rb") as f:
            credits = f.read()
        readme_checks(rep, tree.read("README.txt"), build, commit.sha7, credits)
    else:
        rep.check(False, "README.txt", "missing")

    # the plugin
    if ESP in tree.names:
        try:
            count, next_id, records, groups = esp_parse(tree.read(ESP))
            held = len(records) + groups          # as the generator counts: TES4, every record, every group
            rep.check(count == manifest["esp"]["records"] and count == held,
                      "the ESP's header: %d records (the file holds %d records with TES4 and %d groups)"
                      % (count, len(records), groups),
                      "HEDR says %d, the manifest %d, the file holds %d" % (count, manifest["esp"]["records"], held))
            masters = sum(1 for field, _ in esp_fields(records[0][2]) if field == "MAST")
            top = max([form & 0xFFFFFF for sig, form, _ in records if sig != "TES4" and form >> 24 == masters] or [0])
            rep.check(next_id == manifest["_next_id"] and top < next_id,
                      "the ESP's header: next object ID 0x%X (highest form ID 0x%X)" % (next_id, top),
                      "HEDR says 0x%X, the manifest 0x%X, the highest form ID is 0x%X" % (next_id, manifest["_next_id"], top))
            have = set()
            for sig, form, payload in records:
                for field, value in esp_fields(payload):
                    if field == "EDID":
                        edid = value.rstrip(b"\0").decode("latin-1")
                        have.update((edid, sig + ":" + edid))
                        break
            absent = [e for e in manifest["esp"].get("edids", []) if e not in have]
            rep.check(not absent, "the ESP's records: all %d the manifest names are there%s"
                      % (len(manifest["esp"].get("edids", [])),
                         " (%s)" % some(manifest["esp"]["edids"], 4) if manifest["esp"].get("edids") else ""), some(absent))
        except Fail as e:
            rep.check(False, "the ESP", str(e))
    else:
        rep.check(False, "the ESP", ESP + " missing")

    # sounds
    wavs, bad, formats = [n for n in tree.names if n.lower().endswith(".wav")], [], {}
    for n in wavs:
        try:
            ch, rate, bits, secs = wav_format(tree.read(n))
            formats.setdefault("%d Hz, %d channel%s, %d bit" % (rate, ch, "" if ch == 1 else "s", bits), []).append(n)
            if wavs_each:
                rep.check(True, "WAV %s: RIFF PCM, %d Hz, %d channel%s, %d bit, %.2f s"
                          % (n.rsplit("/", 1)[-1], rate, ch, "" if ch == 1 else "s", bits, secs))
        except Fail as e:
            bad.append("%s: %s" % (n, e))
            if wavs_each:
                rep.check(False, "WAV %s" % n.rsplit("/", 1)[-1], str(e))
    rep.check(not bad, "the %d WAVs are RIFF PCM (%s)" % (len(wavs), "; ".join("%d of %s" % (len(v), k) for k, v in sorted(formats.items()))),
              some(bad))
    other = [n for n in tree.names if n.lower().endswith((".xwm", ".mp3", ".fuz", ".ogg"))]
    rep.check(not other, "no sound in another format", some(other))

    # counts
    counts = {}
    for n in tree.names:
        leaf = n.rsplit("/", 1)[-1]
        ext = leaf.rsplit(".", 1)[1].lower() if "." in leaf else ""
        counts[ext] = counts.get(ext, 0) + 1
    want = manifest["counts"]
    diff = ["%s %d (the manifest: %d)" % (e or "<none>", counts.get(e, 0), want.get(e, 0))
            for e in sorted(set(counts) | set(want)) if counts.get(e, 0) != want.get(e, 0)]
    rep.check(not diff, "counts: %d files (%s)" % (len(tree.names), ", ".join(
        "%d %s" % (c, e) for e, c in sorted(counts.items(), key=lambda x: (-x[1], x[0])))), "; ".join(diff))


# ------------------------------------------------------------------------------------------------------------- zips
def zip_order(names):
    """README.txt, then Data as a directory walk: a folder's files in byte order, then its subfolders."""
    def key(name):
        parts = name.split("/")
        return [(1, p) for p in parts[:-1]] + [(0, parts[-1])]
    return sorted(names, key=key)


def write_zip(path, tree, names, arc, when, mode):
    """A deterministic zip of the tree's names: arc(name) is the member's name, when(name) its time, mode(name)
    its permission bits."""
    tmp = path + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name in zip_order(names):
            info = zipfile.ZipInfo(arc(name), when(name))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100000 | mode(name)) << 16
            z.writestr(info, tree.read(name), compresslevel=6)
    os.replace(tmp, path)


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------------------- assets
def asset_names(data):
    """The asset files of a Data folder (relative to it)."""
    return [n for n in walk_files(data) if is_asset(n)]


def read_asset_list(path):
    out = {}
    with open(path, encoding="ascii") as f:
        for line in f:
            if line.strip():
                digest, name = line.rstrip("\n").split("  ", 1)
                out[name] = digest
    return out


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_assets(data, listing):
    """Problems of a Data folder as the asset base: a listed file missing or different, an asset not listed."""
    want, have, out = read_asset_list(listing), asset_names(data), []
    for name in sorted(want):
        full = os.path.join(data, name)
        if name not in have:
            out.append("missing: " + name)
        elif file_sha256(full) != want[name]:
            out.append("differs: " + name)
    out += ["not in the list: " + n for n in have if n not in want]
    return len(want), out


def cmd_check_assets(args):
    listing = args.list or os.path.join(HERE, "assets.sha256")
    count, problems = check_assets(args.data, listing)
    for p in problems:
        print("FAIL  " + p)
    print("assets: %s: %s" % (args.data, "all %d files of %s are there, byte for byte, and no other asset"
                              % (count, os.path.basename(listing)) if not problems
                              else "%d problem(s) against %s (%d files listed)" % (len(problems), listing, count)))
    return 1 if problems else 0


def cmd_write_assets(args):
    listing = args.list or os.path.join(HERE, "assets.sha256")
    names = asset_names(args.data)
    bad = [n for n in names if n.rsplit("/", 1)[-1].lower() == NEVER_SHIPPED]
    if bad or not names:
        raise Fail("%s is not a package's Data folder: %s" % (args.data, some(bad) if bad else "no asset file in it"))
    with open(listing, "w", encoding="ascii", newline="\n") as f:
        for n in names:
            f.write("%s  %s\n" % (file_sha256(os.path.join(args.data, n)), n))
    print("wrote %s: %d files of %s" % (listing, len(names), args.data))
    return 0


# ---------------------------------------------------------------------------------------------------------- extract
def cmd_extract(args):
    """A package zip into a new folder, as data: plain files only, inside the folder, nothing executable."""
    if os.path.exists(args.dest) and (not os.path.isdir(args.dest) or os.listdir(args.dest)):
        raise Fail("%s exists and is not an empty folder" % args.dest)
    tree = ZipTree(args.zip, strict=False)
    if tree.problems:
        raise Fail("%s: %s" % (args.zip, some(tree.problems)))
    total = sum(i.file_size for i in tree.infos.values())
    if len(tree.names) > 20000 or total > 4 << 30:
        raise Fail("%s: %d files, %d bytes: not a package" % (args.zip, len(tree.names), total))
    root = os.path.realpath(args.dest)
    for name in tree.names:
        full = os.path.realpath(os.path.join(root, *name.split("/")))
        if not full.startswith(root + os.sep):
            raise Fail("%s would leave %s" % (name, root))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "xb") as f:
            f.write(tree.read(name))
        os.chmod(full, 0o644)
    print("extracted %d files (%d bytes) of %s into %s" % (len(tree.names), total, args.zip, root))
    return 0


# ---------------------------------------------------------------------------------------------------------- package
def cmd_package(args):
    build = args.build
    if not BUILD_RE.match(build):
        raise Fail("BUILD must look like 2026-11-10a, not %r" % build)
    manifest = load_manifest(os.path.join(HERE, "builds", build + ".json"), build)
    commit = Commit(args.repo, args.commit)
    print("packaging build %s from commit %s (%s, committed %s UTC)"
          % (build, commit.sha7, commit.sha, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(commit.time))))

    plan = {}                                 # package name -> bytes or a file's path
    for name in commit.shipped:
        plan[name] = commit.blob(name)
    print("repository: %d tracked files from the commit's objects; not shipped: %s; from the asset base instead: "
          "the %d engine WAVs" % (len(commit.shipped), ", ".join(TRACKED_NOT_SHIPPED), len(ENGINE_WAVS)))

    # compiled scripts
    when, folder = pex_stamp(manifest, commit)
    sources = [n for n in commit.shipped if n.startswith(SOURCES) and n.endswith(".psc")]
    have = sorted(f for f in os.listdir(args.pex) if f.endswith(".pex"))
    want = sorted(n[len(SOURCES):-4] + ".pex" for n in sources)
    if have != want:
        raise Fail("the compile gave %s, the commit's sources need %s" % (some(have, 20), some(want, 20)))
    for f in have:
        with open(os.path.join(args.pex, f), "rb") as h:
            plan["Data/Scripts/" + f] = pex_restamp(h.read(), when, folder)
    print("scripts: %d compiled, headers stamped: compile time %d (%s UTC), source folder %s"
          % (len(have), when, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(when)), folder))

    # the asset base and its overlays
    removed = set(manifest["vs_previous"]["removed"])
    base = asset_names(args.assets)
    taken = dropped = 0
    for n in base:
        name = "Data/" + n
        if n.rsplit("/", 1)[-1].lower() == NEVER_SHIPPED:
            print("asset base: %s is never shipped, left out" % n)
        elif name in commit.shipped:
            print("asset base: %s is the commit's, the asset base's copy left out" % n)
        elif name in removed:
            dropped += 1
            print("asset base: %s dropped (the manifest's vs_previous.removed)" % n)
        else:
            plan[name] = os.path.join(args.assets, n)
            taken += 1
    never = sorted(removed - {"Data/" + n for n in base})
    if never:
        raise Fail("the manifest removes what the asset base does not have: %s" % some(never))
    print("asset base: %s: %d files taken%s" % (args.assets, taken, ", %d dropped" % dropped if dropped else ""))
    for overlay in args.overlay or []:
        if not os.path.isdir(overlay):
            raise Fail("OVERLAY %s: no such folder" % overlay)
        files, ignored, count = walk_files(overlay), [], 0
        for n in files:
            name, full = "Data/" + n, os.path.join(overlay, n)
            if n.rsplit("/", 1)[-1].lower() == NEVER_SHIPPED:
                print("overlay %s: %s is never shipped, left out" % (overlay, n))
            elif not is_asset(n) or name in commit.shipped or name in TRACKED_NOT_SHIPPED:
                ignored.append(n)
            else:
                old = plan.get(name)
                if old is None:
                    state = "new"
                elif file_sha256(old) == file_sha256(full):
                    state = "the same bytes as before"
                else:
                    state = "replaces the %s's" % ("asset base" if old.startswith(args.assets) else "earlier overlay")
                plan[name] = full
                count += 1
                print("overlay %s: %s (%s, %d bytes, sha256 %s)" % (overlay, n, state, os.path.getsize(full), file_sha256(full)))
        if ignored:
            print("overlay %s: %d files outside the asset folders (or the commit's own) ignored: %s"
                  % (overlay, len(ignored), some(ignored)))
        print("overlay %s: %d files" % (overlay, count))

    with open(os.path.join(HERE, "README.template.txt"), "rb") as f:
        plan["README.txt"] = make_readme(f.read(), commit.sha7)

    # the folder
    out = os.path.abspath(args.out)
    top = NAME + "_" + build
    stage = os.path.join(out, top)
    full_zip, mo2_zip = os.path.join(out, top + ".zip"), os.path.join(out, MO2_ZIP)
    for old in (full_zip, mo2_zip):           # an earlier run's zips must not outlive a run that is refused
        if os.path.lexists(old):
            os.remove(old)
    if os.path.lexists(stage):
        if os.path.islink(stage) or sorted(os.listdir(stage)) not in ([], ["Data", "README.txt"]):
            raise Fail("%s exists and is not an earlier run's package folder: remove it yourself" % stage)
        shutil.rmtree(stage)
    for name, source in sorted(plan.items()):
        full = os.path.join(stage, *name.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if isinstance(source, bytes):
            with open(full, "xb") as f:
                f.write(source)
        else:
            shutil.copyfile(source, full)
        os.chmod(full, 0o644)
    print("assembled %d files in %s" % (len(plan), stage))

    # the guard, over what is on disk
    tree = DirTree(stage)
    rep = Report()
    content_checks(rep, tree, commit, manifest)
    if rep.failed:
        raise Fail("the guard refuses this package: %d check(s) failed (the folder is left for inspection, no zip written)"
                   % rep.failed)

    def mode(name):
        return commit.tracked[name][0] if name in commit.shipped else 0o644

    def when_of(name):
        return zip_time(manifest, commit, name)

    write_zip(full_zip, tree, tree.names, lambda n: top + "/" + n, when_of, mode)
    write_zip(mo2_zip, tree, [n for n in tree.names if n.startswith("Data/")], lambda n: n[5:], when_of, mode)
    for path in (full_zip, mo2_zip):
        print("zip   %s  %d bytes  md5 %s" % (path, os.path.getsize(path), md5_of(path)))
    print("packaged commit %s" % commit.sha7)
    return 0


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="The packager's worker (see package.sh and this file's header).")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("package")
    p.add_argument("--repo", required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--build", required=True)
    p.add_argument("--assets", required=True)
    p.add_argument("--overlay", action="append")
    p.add_argument("--pex", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(run=cmd_package)
    for name, run in (("check-assets", cmd_check_assets), ("write-assets-manifest", cmd_write_assets)):
        p = sub.add_parser(name)
        p.add_argument("data")
        p.add_argument("--list")
        p.set_defaults(run=run)
    p = sub.add_parser("extract")
    p.add_argument("zip")
    p.add_argument("dest")
    p.set_defaults(run=cmd_extract)
    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_usage()
        return 2
    try:
        return args.run(args)
    except Fail as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
