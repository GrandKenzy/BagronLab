# Prueba de io en Android

Smoke test ARM64/API 35 para el backend Android de `io`. Requiere instalar
`androidlib.lib` e `io.lib` en la raíz de bibliotecas de Bagron y tener un NDK
configurado. Alimenta una línea por stdin y debe imprimir `Hola`, seguida de
la línea recibida, y terminar con código 0 en el dispositivo:

```powershell
bagron tests/io/main.bg -o build/io-android-test
adb push build/io-android-test /data/local/tmp/bagron-io-test
adb shell chmod 755 /data/local/tmp/bagron-io-test
adb shell 'printf "test\n" | /data/local/tmp/bagron-io-test'
```
