# BagronLab

BagronLab is the developer laboratory for Bagron libraries, target APIs,
experiments, and integration examples. The Bagron compiler repository remains
the source of truth for the language, compiler, frontend, backend, and general
language documentation.

This repository intentionally excludes the experimental `net/` and `Brixel/`
projects from this cleanup. The `string/` and `alphabet` sources are also
left untouched. The root `build/` directory is the single clean location for
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
| `build/` | Precompiled, validated `lib1` packages ready for consumers. |
| `docs/` | Documentation specific to laboratory libraries. |

## Tooling

Use the installed Bagron compiler from this repository:

```text
bagron <source.bg> -o <output> [--execute]
```

Do not use the compiler repository's `vnma` entry point for laboratory
projects. Build and smoke-test a module with the installed `bagron` command.
Keep every precompiled library in the root `build/` directory. Do not leave
published output packages in source trees or nested build caches. Libraries now consume global libraries directly (`library windows as Win`,
`library gnulibrary as Gnu`) from the compiler's canonical `libs/` directory,
keeping library repositories clean without local nested `libs/` directories.

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

- `build/gnulibrary.lib` and `build/windows.lib` — canonical native targets.
- `build/io.lib` — cross-platform system I/O helpers.
- `build/hashlib.lib` and `build/math.lib` — portable Bagron libraries.
- `build/string.lib` — retained precompiled string package.

`mmap`, `time`, `mem`, `types`, and the historical `standard` tree are not
published until their completeness and targets are confirmed. `net/` and `Brixel/`
remain explicitly omitted from this cleanup; the `string/` and `alphabet`
sources were not modified.

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
- `docs/string/` documents string operations and the `alphabet` constants.
- `docs/standard/` documents the standard-library laboratory layout.

When adding a library, create its documentation directory under `docs/` and
keep the public API, target assumptions, ownership rules, and smoke commands
there.
