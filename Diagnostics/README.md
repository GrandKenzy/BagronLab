# Diagnostics

`Diagnostics` is a standalone, allocation-free diagnostic buffer for Bagron
programs. It does not depend on the Bagron compiler or on a C library.

It stores diagnostic records, copies their UTF-8 messages into caller-owned
storage, applies severity overrides, counts dropped records, and reports when
an error policy requests a halt.

## Quick start

```bg
library Diagnostics as Diag

import {
    Diagnostic,
    DiagnosticBuffer,
    SeverityError,
    PolicyStopOnError,
    buffer_init,
    buffer_set_message_arena,
    emit,
    buffer_read,
    buffer_message_copy
} from Diag

@unsafe
func main() int32:
    ; EN : Stores one diagnostic and reads its copied UTF-8 message.
    ;
    ; ES : Guarda un diagnóstico y lee su mensaje UTF-8 copiado.
    records: Diagnostic[8]
    arena: char[4096]
    output: char[64]
    state: DiagnosticBuffer
    record: Diagnostic

    buffer_init($state, $records[0], 8, PolicyStopOnError)
    buffer_set_message_arena($state, 4096)

    if not emit($state, 1001, SeverityError, 0, 9, 1, 0, "bad token", arena):
        return 1
    if not buffer_read($state, 0, $record):
        return 2
    if buffer_message_copy($state, 0, arena, output) != 9:
        return 3
    return 0
```

`buffer_set_message_arena` records the arena capacity. Pass the same `char[]`
to `emit` and `buffer_message_copy`. The arena must have one extra byte for the
terminating NUL; `char[4096]` can store at most 4095 message bytes.

## Main types

`Diagnostic` contains:

- `code`: diagnostic identifier;
- `severity`: effective severity after overrides;
- `start` and `end`: source span in bytes or token positions;
- `line` and `column`: source location;
- `message_offset` and `message_length`: position and byte length in the arena.

`DiagnosticBuffer` contains the records, counters, policy, overrides, and arena
usage. The records array and the message arena belong to the caller; they must
remain alive while the buffer or its records are used.

## Emitting diagnostics

```bg
if not emit($state, code, severity, start, end, line, column, text, arena):
    ; The record was not stored.
```

`emit` returns `true` only when the record is stored. It returns `false` when
the record limit, arena capacity, or configured emission limit prevents storage.
The `total_emitted` and `dropped_count` fields expose those results.

Messages are UTF-8 byte sequences. `buffer_message_copy` copies a message into
caller-owned `char[]` storage, adds a terminating NUL, and returns the number of
copied bytes. If the destination is smaller than the message, the result is
truncated safely.

## Policies and severities

Severities are ordered from least to most severe:

`SeverityDebug`, `SeverityAdvice`, `SeverityWarning`, `SeverityError`,
`SeverityFatal`.

Policies:

- `PolicyRecover`: never marks the buffer halted;
- `PolicyStopOnError`: marks it halted at error or fatal severity;
- `PolicyStopOnFatal`: marks it halted only at fatal severity.

Use `buffer_is_halted` to query the state. The halt flag is advisory; callers
decide when to stop their own work.

Use `buffer_set_overrides` to replace the caller-owned override table. Use
`buffer_set_max_limit` to limit the number of emission attempts; zero disables
that limit.

Built-in diagnostic codes range from `CodeNone` through
`CodeInvalidCommentSymbol`. Custom codes should start at `CodeCustomBase`.

## Reusing a buffer

Call `buffer_reset` before starting a new compilation or processing unit. It
clears records, counters, halt state, and arena usage while preserving the
caller-owned storage, policy, override table, and configured limits.

Configure the arena before the first emission or after `buffer_reset`; changing
its capacity resets the used byte count and invalidates existing message offsets.

The current version exposes direct buffer operations. It does not provide Gram
callback sinks because Bagron does not yet have callable function values.
