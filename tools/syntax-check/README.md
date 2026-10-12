# Papyrus syntax check (Linux, no Creation Kit)

Compiles the mod's scripts with [Caprica](https://github.com/nikitalita/Caprica), an MIT-licensed Papyrus compiler, against **declaration-only stubs** of the Fallout 4 API in `stubs/`.

```
./build-caprica.sh   # once: clones Caprica, applies caprica-linux.patch, builds with clang
./check.sh           # compiles every script; non-zero exit on any error
```

- Catches syntax errors, typos in function names, wrong argument counts and type errors.
- Does **not** prove the scripts work in game. The stubs are hand-written from the
  Creation Kit wiki (only the functions this mod uses), not Bethesda's sources. The CK compile is the real test.
- `stubs/f4se/` overlays F4SE additions, and is used only for the `*F4SE.psc` scripts.
- When a script starts using a new engine function, add its declaration to the stubs.
- `audit_stubs.py <folder with real .psc files> ...` checks every stub declaration against the
  real ones (the Creation Kit's `Data\Scripts\Source\Base`, or F4SE's repository, `scripts/vanilla` and
  `scripts/modified`). It found that the camera script called a `GetINIFloat` that doesn't exist.

`caprica-linux.patch` + `compat/` make upstream Caprica (MSVC-only) build with clang on Linux. The patch also fixes two crashes:
error messages with string arguments crashed (a varargs layout difference outside MSVC), and passing too many arguments to a function crashed instead of reporting an error.
