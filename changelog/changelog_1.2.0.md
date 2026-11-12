# Changelog 1.2.0

## Windows

- The `windows` library now provides the Windows GUI window, event-loop,
  controls, drawing, dialog, and text helpers.
- The standalone `win32gui` package has been removed; existing Windows GUI
  consumers should import these helpers from `windows`.

## Process arguments

- `windows` and `gnulibrary` now expose the native Bagron process-argument
  bridge without depending on a C runtime.
- `io` now exports `arg_count()` and `arg_copy(index, buffer)`. The buffer's
  declared array length is used as the safe copy capacity, and the result
  excludes the terminating NUL byte.

## Memory mapping

- `mmap` now provides `Mapping.open_file(path, size)` for read-only,
  file-backed mappings on Windows and Linux. The native backend releases its
  temporary file handle after creating the view, and `close()` releases the
  active view.
