# Diagnostics test

This test validates the standalone library on Windows AMD64. It covers:

- severity overrides and halt policies;
- caller-owned message arenas;
- message copying and truncation boundaries;
- emission limits and dropped records;
- empty messages, full record storage, and `buffer_reset`.

Run it from `C:\Users\Kentucky\Desktop\BagronLab`:

```powershell
bagron library --v1 Diagnostics -o Diagnostics/build/Diagnostics.lib --name Diagnostics --version 0.1.0
bagron verify Diagnostics/build/Diagnostics.lib
bagron install --library --v1 Diagnostics/build/Diagnostics.lib --name Diagnostics --version 0.1.0
bagron Diagnostics/tests/main.bg -o Diagnostics/build/diagnostics-test --execute
```

The process must terminate with exit code `0`.
