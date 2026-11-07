# Diagnostics smoke test

The test uses Windows AMD64 because it needs only the portable Bagron runtime;
the library itself declares `System "auto"` and `Arch "auto"`.

```powershell
bagron library --v1 Diagnostics -o Diagnostics/build/Diagnostics.lib --name Diagnostics --version 0.1.0
bagron install --library --v1 Diagnostics/build/Diagnostics.lib --name Diagnostics --version 0.1.0
bagron Diagnostics/tests/main.bg -o Diagnostics/build/diagnostics-test --execute
```

The process must terminate with exit code `0`.
