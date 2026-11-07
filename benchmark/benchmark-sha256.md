# SHA-256 Benchmark

Date: 2026-11-06

## Scope

This benchmark compares the Bagron implementation in
`hashlib/modules/SHA_256.bg` with an equivalent scalar implementation written
directly in C. The C version does not use OpenSSL, a platform crypto API, or a
precompiled hashing library.

Both programs hash the same fixed 64-byte message, containing the values `0`
through `63`, exactly `100,000` times. Each call processes the message block
and its SHA-256 padding block. A checksum derived from the digest and the loop
counter is accumulated so the benchmark has an observable result.

## Environment

- OS: Windows 10.0.19045
- CPU: Intel(R) Core(TM) i3-4150 CPU @ 3.50GHz
- Bagron: 1.1.1
- Clang: 21.1.0
- C optimization: `clang -O2`
- Samples: 5 independent process executions per implementation
- Timer: PowerShell wall-clock process timing

The timing includes process startup. It is therefore an end-to-end executable
comparison, not a cycle-accurate measurement of the hash function alone.

## Results

| Implementation | Samples (ms) | Minimum (ms) | Median (ms) | Mean (ms) |
|---|---:|---:|---:|---:|
| Bagron | 111.112, 98.990, 101.418, 103.746, 109.117 | 98.990 | 103.746 | 104.877 |
| C (`clang -O2`) | 83.563, 74.755, 86.365, 73.569, 76.188 | 73.569 | 76.188 | 78.888 |

The median ratio is:

```text
Bagron / C = 1.362x
```

For this workload, Bagron was approximately `36.2%` slower than the C
baseline by median wall-clock time. The median difference was `27.558 ms` per
100,000 hashes, or approximately `0.276 microseconds` per hash.

## In-process measurement

The preferred follow-up benchmark runs the same hashing loop inside each
executable and measures it with the Windows monotonic `GetTickCount` clock.
Process startup is outside the measured interval. The workload was increased
to `1,000,000` hashes and the measurement was repeated 10 times per
implementation.

| Implementation | Samples (ms) | Minimum (ms) | Median (ms) | Mean (ms) |
|---|---:|---:|---:|---:|
| Bagron | 1032, 922, 922, 937, 937, 954, 938, 1015, 969, 922 | 922 | 937 | 954.8 |
| C (`clang -O2`) | 672, 625, 625, 687, 657, 687, 641, 625, 625, 672 | 625 | 641 | 651.6 |

The in-process median ratio is:

```text
Bagron / C = 1.462x
```

This corresponds to approximately `46.2%` more wall-clock time for Bagron,
or about `0.296 microseconds` per hash in this workload. This measurement is
more representative than the initial process-level table because it excludes
executable startup.

## Correctness

Both benchmark executables returned exit code `0`. The benchmark harness was
compiled from temporary files outside `BagronLab`; no executable, object file,
or temporary source was retained in the laboratory.

## Source optimization follow-up

After the recorded run, `SHA_256.bg` was optimized in three safe steps:

1. Message words load directly through explicit `byte as uint8` conversions;
   the temporary `OctetView` mold is no longer involved.
2. The generic path updates the eight-byte message length once per complete
   64-byte block instead of once per input byte. Only a short final block uses
   byte-at-a-time accounting.
3. `sha256_block64(const byte[64])` was added for callers that already own a
   fixed 64-byte block. It performs the message compression and fixed padding
   compression directly, without generic ingestion or padding loops.

The public arbitrary-length `sha256(byte[])` API remains unchanged. The fixed
block entry point is intentionally separate because Bagron's safe array model
must not reinterpret a runtime-sized array as `byte[64]` without a compile-time
bound.

The existing SHA-256 regression suite, including the fixed-block digest vector,
returns exit code `0`.

## Specialized fixed-block follow-up

The optimized and generic Bagron entry points were each run in a temporary
executable. Both programs hashed the same `0..63` 64-byte message `1,000,000`
times and checked an accumulated digest value. Ten process timings were
collected after one warm-up run; process startup is included, but is small
relative to the workload.

| Bagron entry point | Samples (ms) | Median (ms) |
|---|---:|---:|
| `sha256(byte[])` | 1016.274, 945.484, 911.912, 1171.099, 901.971, 915.579, 896.680, 893.174, 926.913, 911.440 | 911.912 |
| `sha256_block64(const byte[64])` | 918.475, 751.630, 752.499, 756.080, 764.258, 768.304, 775.906, 755.776, 967.523, 752.518 | 756.080 |

The specialized route is approximately `1.206x` faster for this exact fixed
block workload, or about `17.1%` less wall-clock time. This gain applies only
when the caller can provide a statically bounded 64-byte array; arbitrary
length messages continue through the generic API.

## Interpretation

The result is useful as a baseline for the current scalar implementation. It
does not establish that Bagron is intrinsically slower than C: the comparison
uses the installed Bagron compiler's default backend settings while the C
baseline explicitly uses `-O2`. The in-process measurement confirms a real
gap for this workload, but equivalent compiler optimization settings and LLVM
profiling are still needed before drawing instruction-level conclusions.

