# androidlib

Native Android target support for Bagron.

This directory is reserved for the Android ABI layer used by higher-level
libraries such as `io`, `mmap`, and `time`. The implementation must support the
explicit Android triples accepted by Bagron:

- `aarch64-linux-android<api>`
- `x86_64-linux-android<api>`

The first module should define the smallest native contract needed by `io`:
byte output, process termination, and any target-specific handle or error
operations required by that contract. Keep the implementation target-native;
do not make `gnulibrary`'s x86_64 Linux syscall numbers the Android default.

The current bootstrap also exposes anonymous read/write mapping and unmapping
through Bionic. The ARM64/API 35 source is the first validated baseline; the
x86-64 triple must be compiled and checked before publishing a second package.

Android libraries currently require an explicit full LLVM triple, including
the API level. Do not add a portable `Arch "auto"` declaration here until the
compiler has a package-level policy for selecting an Android ABI and API.
