# gnulibrary

`gnulibrary` es la capa de compatibilidad Linux raw de Bagron para x86_64.
Expone syscalls directas mediante funciones `@assembler`; no intenta sustituir
las funciones propias de Bagron ni construir una libc C.

## Constantes compartidas

Las constantes Linux se definen exclusivamente en
`gnulibrary/modules/linuxc.bg`. Los consumidores deben importar el módulo y
usar sus nombres mediante el namespace `linuxc`, por ejemplo:

```bg
import linuxc
import files

func open_log(path *: byte) int64:
    return files.openat(linuxc.AT_FDCWD, path, linuxc.O_WRONLY | linuxc.O_CREAT, linuxc.MODE_USER_READ_WRITE)
```

El archivo centraliza descriptores estándar, operaciones relativas a
directorios, flags de apertura, offsets, permisos, memoria mapeada, relojes,
`renameat2` y `getrandom`.

## Contrato raw

Las funciones de `gnulibrary` conservan el contrato del kernel:

- los errores se devuelven como valores negativos `-errno`;
- no se escribe `errno` ni se normaliza el resultado como glibc;
- los buffers, punteros y estructuras apuntadas son responsabilidad del
  llamador;
- las funciones no añaden buffering, ownership ni validación de alto nivel.

Los syscalls de sockets también devuelven su resultado raw. Los adaptadores
`Open`, `Accept`, `Connect`, `Bind`, `Listen`, `Send`, `Recv` y `Close`
normalizan los fallos a sus sentinels de compatibilidad. La resolución DNS sí está disponible en `gnulibrary` mediante el ABI opcional de libc (`getaddrinfo` y `freeaddrinfo`); no existe un syscall de DNS. El helper público `OpenTcpHost` encapsula esa resolución, la conexión y la configuración del timeout.

`system.exit` termina solo la hebra llamadora; `system.exit_group` termina
el proceso completo. Las nuevas operaciones de archivos `fstat`, `pread64`,
`pwrite64`, `fsync`, `fdatasync` y `ftruncate` conservan los resultados raw
del kernel.
Con `O_APPEND`, Linux puede hacer que `pwrite64` escriba al final del archivo.
`system.trap` eleva `SIGABRT` mediante los syscalls raw de proceso y usa
`exit_group` como respaldo, por lo que no depende de libc.

La documentación específica de `gnulibrary` pertenece a esta carpeta. La
documentación del lenguaje y del compilador debe permanecer en el repositorio
principal de Bagron.

## Integración de Net

`net` usa `gnulibrary` para sockets y E/S de archivos, sin redeclarar ABI nativa.
Las entradas añadidas `open_cstr`, `read_chars` y `write_chars` aceptan
punteros de texto de Bagron y mantienen el retorno raw del kernel. Los
wrappers públicos de TCP usan `MSG_NOSIGNAL` al enviar datos para evitar
`SIGPIPE` en conexiones cerradas.

`modules/curl.bg` centraliza los símbolos externos de libcurl y las funciones
C `fopen`/`fclose` usadas por HTTPS. Esta frontera **sí** utiliza libc y
requiere `libcurl.so.4` en Linux. No sustituye a los syscalls raw.
Los descriptores de archivo se cierran con `close`; los sockets usan `Close`.
