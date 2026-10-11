# Papyrus syntax check (Linux, no Creation Kit)

Compiles the mod's scripts with [Caprica](https://github.com/nikitalita/Caprica), an MIT-licensed Papyrus compiler, against **declaration-only stubs** of the Fallout 4 API in `stubs/`.

```
./build-caprica.sh   # once: clones Caprica, applies caprica-linux.patch, builds with clang
./check.sh           # compiles every script; non-zero exit on any error
```

- Catches syntax errors, typos in function names, wrong argument counts and type errors.
- Does **not** prove the scripts work in game. The stubs are hand-written from the
  Creation Kit wiki (only the functions this mod uses), not Bethesda's sources. The CK compile is the real test.
- `stubs/f4se/` overlays F4SE additions, and is used only for `CMB_HotkeyF4SE.psc`.
- When a script starts using a new engine function, add its declaration to the stubs.

`caprica-linux.patch` + `compat/` make upstream Caprica (MSVC-only) build with clang on Linux. The patch also fixes two crashes:
error messages with string arguments crashed (a varargs layout difference outside MSVC), and passing too many arguments to a function crashed instead of reporting an error.
