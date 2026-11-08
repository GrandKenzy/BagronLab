# BagronLab

BagronLab is the developer laboratory for Bagron libraries, target APIs,
experiments, and integration examples. The Bagron compiler repository remains
the source of truth for the language, compiler, frontend, backend, and general
language documentation.

This repository intentionally excludes the experimental `net/` and `Brixel/`projects from this cleanup. The `string/` library now keeps its complete text,alphabet, and hexadecimal API in `string/main.bg`. The root `build/` directoryis the single clean location for
all precompiled `lib1` packages; source modules and library documentation
remain outside it.

## Goals

- Build Bagron-owned target libraries without making libc or C wrappers the
  default foundation.
- Keep Linux raw compatibility in `gnulibrary/` and native Windows ABI
  declarations in `windows/`.
- Develop higher-level libraries such as `os/`, `io/`, `time/`, `mem/`,
  `mmap/`, and `string/` on top of those target layers.
- Keep experiments reproducible for Bagron and VSIX development.

## Repository layout

| Directory | Responsibility |
| --- | --- |
| `gnulibrary/` | Linux x86_64 raw syscalls and shared Linux constants. It is not libc and does not expose C wrappers. |
| `windows/` | Native Microsoft x64 ABI modules: `kernel32`, `user32`, `gdi32`, `comctl32`, sockets, and more. || `androidlib/` | Native Android ABI layer reserved for Android-specific runtime operations. |
| `os/` | Cross-platform file and path operations built on `gnulibrary` and `windows`. |
| `io/` | Standard text and byte input/output helpers. |
| `time/` | Standard time and clock helpers. |
| `mem/` | Portable, checked byte-array and buffer operations (`mem 0.1.0` source). |
| `mmap/` | Native anonymous virtual-memory mapping and page protection (`mmap 0.1.0`). |
| `x11gui/` | Linux AMD64 X11 graphical backend (Xlib): windows, events, drawing and button hit-testing. |
| `win32gui/` | Windows-only GUI backend with a validated `win32gui 0.0.1` package. |
| `string/` | String and character-array helpers, including `alphabet`. |
| `hashlib/` | Hashing algorithms implemented in Bagron. |
| `math/` | Numerical algorithms: roots, trig, statistics, number theory, interpolation and geometry (`math 1.2.0`). |
| `types/` | Reusable type experiments and integer helpers. |
| `standard/` | Historical compatibility project and dependency artifacts. |
| `build/` | Precompiled, validated `lib1` packages ready for consumers. |
| `docs/` | Documentation specific to laboratory libraries. |

## Tooling

Use the installed Bagron compiler from this repository:

```text
bagron <source.bg> -o <output> [--execute]
```

Do not use the compiler repository entry point `vnma` for laboratory
projects. Build and validate a module with the installed `bagron` command.
Keep every precompiled library in the root `build/` directory. Do not leave
published output packages in source trees or nested build caches. Libraries now
consume global libraries directly (library windows as Win, library gnulibrary as
Gnu) from the compiler canonical `libs/` directory, keeping library
repositories clean without local nested `libs/` directories.

## Central integration (`discentra_central/`)

As a hosting monorepo for the standard library suite, `BagronLab` centralizes
package declarations and cryptographic manifests under `discentra_central/`
rather than using per-directory metadata files:

- `discentra_central/packages.toml`: Declarative package metadata for all packages exposed in `build/`.
- `discentra_central/manifest.toml`: Cryptographic integrity layer (SHA-256 hashes, artifact sizes, and author signatures).
- `discentra_central/package.toml`: Repository descriptor for Central integration.

> [!NOTE]
> All BagronLab libraries specify `min_bagron = "1.1.4"` by default, as the
> language and library API is intended to remain stable from version 1.1.4
> onwards. Author attribution defaults to `"Discentra Community"` with
> contact undefined.

## Library packages

`lib1` is the recommended package format for BagronLab libraries. It preserves
validated Bagron source, frontend metadata, symbols, and the information needed
for consumers to inspect and revalidate the package:

```text
bagron library --v1 <library-source> -o <library>.lib \
    --name <Name> --version <version>
```

For example:

```text
bagron library --v1 gnulibrary -o build/gnulibrary.lib \
    --name gnulibrary --version 1.1.3
```

Use `lib2` only when a compiled, target-specific package is explicitly needed.

The validated packages currently exposed by this lab are:

- `build/androidlib.lib`, `build/gnulibrary.lib`, and `build/windows.lib` -
  canonical native targets.
- `build/io.lib`, `build/mem.lib`, `build/os.lib`, and `build/time.lib` -
  cross-platform runtime helpers.
- `build/hashlib.lib`, `build/math.lib`, and `build/x11gui.lib` - portable
  or target-specific Bagron libraries.
- `build/string.lib` - precompiled string package whose API is exported from
  `source/main.bg`.

`types` and the historical `standard` tree are not published until their
completeness and targets are confirmed. `net/` and `Brixel/` remain explicitly
omitted from this cleanup; `string/` is maintained as a single entry module
while `gnulibrary/` and `windows/` own native operations.


## API documentation and VSIX support

Every exposed function should have a concise sequential comment immediately
before its declaration so the Bagron VSIX can show useful hover documentation.
Use English first, Spanish second, and a comment-only separator between them:

```bg
; EN: Reads bytes from the caller-owned buffer.
; ES: Lee bytes desde el buffer propiedad del llamador.
;
public func read_bytes(...) bool:
    ...
```

Document the contract, ownership, units, error result, target limitations, and
whether the function is unsafe. Keep library-specific API documentation under
`docs/<library>/`; do not move it into the general Bagron documentation.

## Native boundaries

`gnulibrary` and `windows` are the canonical target boundaries:

- `gnulibrary` communicates with Linux through raw x86_64 syscalls.
- `windows` communicates with Windows through public native DLL ABIs.
- Higher-level modules should consume those libraries instead of redeclaring
  ABI functions with local `extern` blocks.
- C and libc wrappers remain optional interoperability mechanisms, not the
  default implementation strategy for Bagron libraries.

For `os`, `path.bg` performs path analysis and normalization without opening
descriptors, while `file.bg` owns file and directory operations. Target clauses
belong in each library's `main.bg`; modules inherit the selected target.

## Documentation map

- `docs/gnulibrary/` documents Linux compatibility APIs.
- `docs/windows/` documents the Windows native API.
- `docs/string/` documents the consolidated string API and alphabet constants.
- `docs/standard/` documents the standard-library laboratory layout.

When adding a library, create its documentation directory under `docs/` and
keep the public API, target assumptions, ownership rules, and validation
commands there.

## Mem library (0.1.0)

`mem/` now provides portable, allocation-free buffer and byte-array
utilities, including checked fill, zero, copy, overlap-safe moves,
comparisons, search, reverse, and byte[]/buffer[] conversion. The original
microbenchmark was moved to `mem/benchmarks/`.

Use `python3 scripts/build_mem.py` to produce and verify `build/mem.lib`.
The published binary and Central integrity manifests must be updated together
when releasing: this source change does not itself publish a new binary.
See `docs/mem/README.md` and `tests/mem/README.md` for contracts and tests.

## mmap library (0.1.0)

`mmap/` now contains a portable `Mapping` class for anonymous private
virtual-memory pages with checked byte/buffer access, read-only protection,
read/write restoration, and explicit release.

Linux uses `gnulibrary` (`mmap`/`munmap`/`mprotect`); Windows uses
`VirtualAlloc`/`VirtualFree`/`VirtualProtect` through `windows`.
The native helpers live in the respective platform libraries, not in `mmap`.
The Linux AMD64 runtime passed the regression suite, and the Windows x64
package and regression executable now pass on the native host.
Run `python3 scripts/build_mmap.py` to generate and verify the target-specific
`build/mmap.lib`. The published package and its integrity digest are recorded
in the Central manifests.
See `docs/mmap/README.md` and `tests/mmap/README.md`.

## win32gui backend (0.0.1)
`win32gui/` is a **Windows x64-only** graphical backend. It keeps the high-level
window, event-loop, controls, drawing, dialog and text modules separate. Native
DLL declarations belong only in `windows/modules/user32.bg`,
`windows/modules/gdi32.bg`, `windows/modules/comctl32.bg` and
`windows/modules/kernel32.bg`.

The name `guilib` is reserved for the future cross-platform facade, not the
Windows backend. See `docs/win32gui/README.md`. A native Windows test exists
at `examples/win32gui/message_box.bg`. Build on Windows with
`python scripts/build_win32gui.py`. The package and the `MessageBoxW` consumer
compile on native Windows x64; the `WNDPROC` callback ABI still needs a runtime
test.
## x11gui backend

`x11gui/` implements an Xlib-based GUI backend on Linux AMD64 and corresponds
to the existing `win32gui/` backend on Windows x64. It uses
`gnulibrary/modules/x11_{display,events,draw}.bg` for native ABI declarations;
`x11gui` itself declares no external functions.

The backend opens X11 windows, renders basic shapes and text, handles mouse
clicks and WM_DELETE_WINDOW, and provides blocking or non-blocking event loops.
It was compiled and tested under Xvfb with Bagron 1.1.4 and the local PIC
workaround. See `docs/x11gui/README.md` and `tests/x11gui/`.

`guilib` remains reserved for the future platform-neutral facade. Native
Wayland support is **not** implemented yet. The validated packages are
published as `build/gnulibrary.lib` and `build/x11gui.lib`; their hashes
and versions are recorded in the Central manifests.

## x11gui keyboard support (source update)

`x11gui` now handles X11 KeyPress/KeyRelease through `Window.wait()` and
`Window.poll()`, exposing keycode, KeySym, modifier masks and the first
Latin-1 byte of `XLookupString`. The `keyboard.bg` module defines special
keys and Shift/Ctrl/Mod1 helpers. The existing window, pointer and drawing
interfaces are preserved.

See `docs/x11gui/README.md` and `tests/x11gui/README.md`. Tested with
Bagron 1.1.4 on Linux AMD64 under Xvfb, including two keyboard integration
tests and the previous graphical regressions. Native Wayland and Unicode text
input remain future work.

## math 1.2.0
The existing `math` library now includes checked integer arithmetic,
deterministic uint64 primality, modular arithmetic, statistics, inverse
trigonometry, geometry, hyperbolic functions, IEEE-754 classification and
domain-checked wrappers for legacy functions. The existing API was
preserved; `usqrt` now handles the maximum uint64 boundary safely.

Build with `python3 scripts/build_math.py`, and run the Bagron tests in
`tests/math/`. See `docs/math/README.md` for API details, limitations and
compatibility. The validated `build/math.lib` package and its Central
integrity metadata are up to date.
