# Diagnostics

`Diagnostics` is Bagron's allocation-free diagnostic buffer, modeled after
Gram's `DiagnosticsLite`.

It provides:

- debug, advice, warning, error, and fatal severities;
- recover, stop-on-error, and stop-on-fatal policies;
- code-specific severity overrides;
- caller-owned record storage with dropped-record accounting;
- a fixed message arena owned by each `DiagnosticBuffer`;
- explicit source spans (`start`, `end`, `line`, and `column`).

Bagron does not currently expose callable function values, so this first native
version intentionally omits Gram's callback sink. Consumers inspect records
with `buffer_read` or wrap `emit` in their own application-level reporting
function. No heap allocation, C wrapper, or target-specific runtime is needed.
`Diagnostic.message_offset` identifies the message bytes in the public buffer
arena; combine it with `message_length` to inspect `state.message_storage`
without exporting a raw pointer across a library boundary.

## Quick example

```bg
library Diagnostics as Diag
import { Diagnostic, DiagnosticBuffer } from Diag
import { SeverityError, PolicyStopOnError } from Diag
import { buffer_init, emit, buffer_read } from Diag

records: Diagnostic[8]
state: DiagnosticBuffer
buffer_init($state, $records[0], 8, PolicyStopOnError)
emit($state, 1001, SeverityError, 0, 3, 1, 0, "bad token")
```

`records` must outlive `state` and the diagnostics that refer to them; pass the
first record pointer and its capacity explicitly. Messages
are copied into the buffer's 4096-byte arena. `emit` returns `false` when the
configured limit, record capacity, or message size drops an emission; counters
remain available in the public buffer. A record keeps its message offset and
length, while `DiagnosticBuffer.message_storage` provides bounded access to the
UTF-8 bytes at that offset.
