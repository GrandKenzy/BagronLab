# Pruebas de mmap 0.1.0

`main.bg` ejecuta las pruebas contra la biblioteca pública instalada
`mmap.lib`, no contra un módulo suelto. Se comprueba:

- Apertura de 4096 bytes y rechazo de capacidad cero o apertura duplicada.
- Lectura, escritura y comprobación de límites, incluido el último byte.
- Copia de `byte[]` y `buffer[]`, relleno, limpieza a cero y movimiento
  con solapamiento.
- Cambio de protección de lectura/escritura a solo lectura y de vuelta.
- Rechazo de escritura en páginas de solo lectura.
- Liberación, cierre repetido y reapertura de la región.
- Que la dirección prestada deja de exponerse tras `close()`.

Con Bagron 1.1.4+ y `gnulibrary` actualizada (Linux) o `windows`
actualizada (Windows):

```sh
python3 scripts/build_mmap.py
bagron install --library --v1 mmap --name mmap --version 0.1.0
bagron tests/mmap/main.bg -o build/test-mmap
./build/test-mmap
echo $?
```

El test termina en 0 cuando todas las comprobaciones pasan. Otros códigos
corresponden al identificador de una condición fallida en `main.bg`.

**Verificado:** Linux x86_64 y Windows x64, Bagron 1.1.4, exit code 0.
Quedan pendientes los sanitizadores de ownership y los mapeos respaldados por
archivos.
