# Prueba de androidlib

Smoke test ARM64/API 35 para `androidlib`. Requiere publicar o instalar
`androidlib.lib` y tener un NDK configurado:

```powershell
bagron tests/androidlib/main.bg -o build/androidlib-test
adb push build/androidlib-test /data/local/tmp/bagron-androidlib-test
adb shell chmod 755 /data/local/tmp/bagron-androidlib-test
adb shell /data/local/tmp/bagron-androidlib-test
```

El proceso debe imprimir `Hola` y terminar con código 0.
