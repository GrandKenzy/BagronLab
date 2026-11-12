# mmap 0.1.0 — Memoria virtual y mapeo de archivos en Bagron

`mmap` administra regiones anónimas y vistas de archivos de memoria virtual
proporcionadas por el sistema operativo. Complementa a `mem`: `mem` manipula
buffers que ya existen; `mmap` reserva, protege, mapea y libera páginas nativas.

La versión `0.1.0` cubre **Linux x86_64** y **Windows x64**. El paquete
`build/mmap.lib` se genera para el target del compilador que lo construye y
no usa `malloc` ni declara `extern` propias: consume `gnulibrary` en Linux
y `windows` en Windows.

## API pública

`Mapping` es un objeto propietario de un único mapeo. Su constructor solo
inicializa el estado; la reserva se hace con `open(size)`.

| Método | Función |
| --- | --- |
| `open(bytes)` | Reserva páginas privadas anónimas en modo lectura/escritura |
| `open_file(path, bytes)` | Mapea un archivo existente en modo solo lectura |
| `is_open()` | Indica si la región está activa |
| `is_file_backed()` | Indica si la región proviene de un archivo |
| `size()` | Cantidad de bytes solicitados |
| `get(index, $byte)` | Lee un octeto, comprobando límites |
| `set(index, byte)` | Escribe un octeto en modo escritura |
| `read(target, start, count)` | Copia desde el mapeo a `byte[]` |
| `write(source, start, count)` | Copia desde `byte[]` al mapeo |
| `read_buffer(target, start, count)` | Copia al almacenamiento `buffer[]` |
| `write_buffer(source, start, count)` | Copia desde `buffer[]` |
| `fill(start, count, byte)` | Rellena con un octeto |
| `zero(start, count)` | Escribe ceros; no es borrado seguro |
| `move_within(dst, src, count)` | Movimiento solapado dentro del mismo mapeo |
| `readonly()` | Activa protección nativa de solo lectura |
| `readwrite()` | Restaura protección de lectura/escritura |
| `raw_address()` | Entrega una dirección prestada para interoperabilidad |
| `close()` | Libera la región; es idempotente si ya estaba cerrada |

Los accesos comprueban los rangos mediante `start <= size` y
`count <= size - start`. Una operación con tamaño cero en el extremo final
es válida. Los métodos devuelven `false` ante operaciones inválidas.

## Ejemplo

```bg
clause System "auto"
clause Arch "amd"

library mmap as MM
import { Mapping } from MM

@unsafe
func main() int32:
    region: Mapping = Mapping()
    if not region.open(4096):
        return 1

    if not region.set(0, 65):
        region.close()
        return 2

    letter: byte = 0
    if not region.get(0, $letter) || letter != 65:
        region.close()
        return 3

    if not region.readonly():
        region.close()
        return 4

    if not region.readwrite():
        region.close()
        return 5

    if not region.close():
        return 6
    return 0
```

## ABI nativas

- **Linux**: `gnulibrary` implementa `vm_map_rw`, `vm_unmap` y
  `vm_protect` mediante las syscalls `mmap`, `munmap` y `mprotect`.
  `MAP_PRIVATE | MAP_ANONYMOUS` y `PROT_READ | PROT_WRITE` se utilizan
  inicialmente; el descriptor de archivo es `-1`.
- **Windows**: `windows/modules/memory.bg` implementa los mismos helpers
  mediante `VirtualAlloc`, `VirtualFree` y `VirtualProtect`.
- Se limita deliberadamente a **AMD64**. No se anuncia compatibilidad
  con ARM32, ARM64 o x86 de 32 bits todavía.

No se generan rutas nativas duplicadas dentro de `mmap`.

## Restricciones de ownership y seguridad

1. **No copies un `Mapping` abierto**: Bagron 1.1.4 no impone propiedad
   lineal sobre estas clases. Copiarlo puede duplicar la responsabilidad
   de liberar la misma dirección.
2. Cierra explícitamente con `close()`. El destructor intenta liberar
   la región como respaldo, pero no sustituye el control explícito de errores.
3. El puntero de `raw_address()` es **prestado**. No es válido después de
   `close()`, no debe liberarse por otra API y no verifica límites.
4. Los métodos `get` y `set` están marcados `@unsafe`: un puntero
   de salida inválido o la manipulación externa del mapeo puede causar fallos.
5. `readonly()` protege las páginas en el sistema operativo. La memoria
   se administra por páginas, aunque `size()` devuelve los bytes solicitados.
   La biblioteca no habilita memoria ejecutable (política RW/R).
6. `open_file()` usa vistas de solo lectura. El backend libera el descriptor o
   handle auxiliar después de crear la vista; `close()` libera la vista activa.
   No ofrece todavía sincronización, memoria compartida, resize ni borrado
   criptográfico seguro.
7. No se conservan automáticamente los códigos de error `errno`/Win32:
   las operaciones fallidas devuelven `false` o `0`.

## Construcción y pruebas

Requiere Bagron **1.1.4+** y las bibliotecas nativas de BagronLab
**regeneradas con los nuevos helpers `vm_*`**.

```sh
python3 scripts/build_mmap.py
bagron verify build/mmap.lib
bagron inspect build/mmap.lib

# Instalar mmap desde fuente para hacerlo accesible globalmente.
bagron install --library --v1 mmap --name mmap --version 0.1.0

bagron tests/mmap/main.bg -o build/test-mmap
./build/test-mmap
echo $?
```

El resultado esperado del test es el código de salida **0**. La suite pasó en
Windows x64 con Bagron 1.1.4 después de reconstruir `windows.lib` y `mmap.lib`;
la validación Linux conserva el mismo backend basado en syscalls.

## Próxima etapa

La siguiente etapa puede añadir sincronización, offsets alineados, vistas
parciales y errores nativos detallados.
