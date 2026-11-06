# BagronLab

BagronLab is the developer laboratory for Bagron libraries, target APIs,
experiments, and integration examples. The Bagron compiler repository remains
the source of truth for the language, compiler, frontend, backend, and general
language documentation.

This repository intentionally excludes the experimental `net/` and `Brixel/`
projects. Generated `build/` directories and compiler binaries are ignored;
source modules, library packages deliberately kept outside `build/`, and
library-specific documentation belong here.

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
| `windows/` | Native Microsoft x64 declarations, currently centered on `kernel32.dll`. |
| `os/` | Cross-platform file and path operations built on `gnulibrary` and `windows`. |
| `io/` | Standard text and byte input/output helpers. |
| `time/` | Standard time and clock helpers. |
| `mem/` | Buffer and memory experiments. |
| `mmap/` | Memory-mapping library area. |
| `string/` | String and character-array helpers, including `alphabet`. |
| `hashlib/` | Hashing algorithms implemented in Bagron. |
| `math/` | Mathematical algorithms and constants. |
| `types/` | Reusable type experiments and integer helpers. |
| `standard/` | Historical compatibility project and dependency artifacts. |
| `docs/` | Documentation specific to laboratory libraries. |

## Tooling

Use the installed Bagron compiler from this repository:

```text
bagron <source.bg> -o <output> [--execute]
```

Do not use the compiler repository's `vnma` entry point for laboratory
projects. Build and smoke-test a module with the installed `bagron` command.
Keep generated output under a library's `build/` directory so it remains
ignored by Git.

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
bagron library --v1 gnulibrary -o gnulibrary/gnulibrary.lib \
    --name gnulibrary --version 1.1.1
```

Use `lib2` only when a compiled, target-specific package is explicitly needed.
Do not commit generated intermediate files from `build/`.

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
- `docs/standard/` documents the standard-library laboratory layout.

When adding a library, create its documentation directory under `docs/` and
keep the public API, target assumptions, ownership rules, and smoke commands
there.
