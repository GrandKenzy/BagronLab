# os

`os` ofrece una capa portátil de archivos y rutas sobre `windows` y
`gnulibrary`. La API pública no expone flags, handles ni syscalls específicos
del target: esas formas permanecen como detalles privados de cada backend.

## Abrir archivos

`File` recibe una ruta NUL-terminada y opciones combinables:

```bg
@unsafe
func example(path: char[]) int32:
    file: File = File(path, FileRead | FileWrite | FileCreate)
    if not file.is_open():
        return 1
    file.close()
    return 0
```

| Opción | Efecto |
| --- | --- |
| `FileRead` | Permite lectura. |
| `FileWrite` | Permite escritura. |
| `FileReadWrite` | Combina lectura y escritura. |
| `FileCreate` | Crea el archivo si no existe. |
| `FileExclusive` | Con `FileCreate`, falla si ya existe. |
| `FileTruncate` | Trunca el archivo al abrirlo; requiere escritura. |
| `FileAppend` | Hace que las escrituras se añadan al final; requiere escritura. |

Se requiere al menos una opción de acceso. `FileExclusive` exige
`FileCreate`; `FileTruncate` y `FileAppend` exigen `FileWrite`.

En Linux, los archivos creados usan modo `0666` antes de aplicar `umask`.
Windows usa rutas ANSI y permite compartir para lectura y escritura. Para
control específico de cada plataforma, utiliza directamente `windows` o
`gnulibrary`.

## I/O y errores

`read_bytes` y `write_bytes` tienen el mismo contrato en ambos sistemas:
aceptan `count: usize`, escriben el resultado en `actual *: usize` y devuelven
`false` con `actual = 0` cuando fallan. El máximo transferible por operación
en Windows es `4_294_967_295` bytes por la ABI de `ReadFile` y `WriteFile`.

`opening_error()` y `closing_error()` devuelven `int64`: un código Win32
positivo en Windows o un `errno` positivo en Linux. `seek` usa
`FileSeekStart`, `FileSeekCurrent` y `FileSeekEnd`, todos de tipo `int32`.

Las funciones de rutas (`exists`, `is_dir`, `is_file`, `is_link`, `suffix`,
`is_absolute`, `basename_index`, `dirname_length` y `osup`) y las operaciones
de archivo/directorio mantienen también la misma firma pública en Windows y
Linux. Targets sin backend nativo conservan la forma de la API y devuelven un
fallo explícito.
