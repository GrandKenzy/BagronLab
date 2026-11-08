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

`process.process_arg_count()` y `process.process_arg_copy()` exponen los
argumentos capturados por el arranque nativo de Bagron. Linux no ofrece un
syscall que recupere `argv` después del arranque, así que esta interfaz usa el
ABI interno de Bagron y no introduce una dependencia de glibc. El índice cero
es la ruta del ejecutable; la copia termina en NUL y devuelve bytes copiados.

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

## Seguridad de rutas en Net

`files.bg` expone `open_read_beneath(root, relative)`, una operación de
solo lectura basada en la syscall Linux x86_64 `openat2` (Linux 5.6+).
Usa `RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS`; rechaza enlaces que salgan de
la raíz, enlaces mágicos y enlaces simbólicos en cualquier componente.
Devuelve un descriptor no negativo o `-errno`, sin abrir fuera del root.
**No** se debe reemplazar por `openat` simple como fallback: en kernels
antiguos el servidor debe fallar de forma segura.

`sockets.bg` ofrece `OpenTcpHost` con iteración por las direcciones que
proporciona `getaddrinfo`, liberación de cada socket fallido y de la lista
DNS, y `ReuseAddress` para listeners que deban reiniciarse rápidamente.
`set_timeout` configura E/S pero **no** garantiza un timeout para un
`connect` bloqueante; queda pendiente implementar nonblocking connect.

## Integración con mmap

`gnulibrary/modules/system.bg` incorpora las operaciones nativas
`vm_map_rw`, `vm_unmap` y `vm_protect`. La reserva es un
`mmap` privado/anónimo (`PROT_READ | PROT_WRITE`), la liberación usa
`munmap` y el cambio de protección usa `mprotect`. Los helpers
utilizan `usize` para las direcciones y devuelven 0/false en caso de fallo.
Se usan únicamente en Linux AMD64 y no requieren libc.

La biblioteca `mmap` administra el ownership; **no** llames estos helpers
sobre una región administrada por un objeto `Mapping` sin transferir la
propiedad de forma segura.

## X11: backend gráfico opcional

Los módulos `x11_display.bg`, `x11_events.bg` y `x11_draw.bg`
encapsulan la ABI de `libX11.so.6` para el proyecto `x11gui`.

- `x11_display.bg`: display, ventanas, protocolo de cierre y máscara de eventos.
- `x11_events.bg`: estructura `XEvent` de 192 bytes en AMD64,
  `XPending`, `XNextEvent` y extracción de clic/cierre.
- `x11_draw.bg`: GC, líneas, rectángulos, texto y colores de píxel.

Se mantienen **separados de las syscalls** de Linux: Xlib requiere un
servidor X11 (o XWayland) y es una biblioteca de X.Org, no del kernel.
Los usuarios de funciones raw sin interfaz gráfica no necesitan abrir un
display; `x11gui` exige que `libX11.so.6` esté presente.

Se verificó localmente el layout de `XEvent` contra las cabeceras Xlib de
Linux x86_64. No usar ese layout para otras arquitecturas sin revalidación.
Pruebas de Xvfb y API pública en `docs/x11gui/README.md`.

### Entrada de teclado X11

`x11_events.bg` incorpora `X11PollInput` (no bloqueante) y
`X11WaitInput` (bloqueante), con `XLookupString` para traducir
`XKeyEvent` al `KeySym` y primer byte Latin-1. Las funciones existentes
`X11PollEvent` y `X11WaitEvent` permanecen disponibles.

El layout `XEvent` de Xlib en Linux AMD64 es de 192 bytes, con
`XKeyEvent.state` en el offset 80 y `keycode` en el offset 84.
Las nuevas salidas de los helpers tienen la forma `mouse: int32[2]`,
`key: usize[3]` (keycode, keysym y estado de modificadores) y
`translated: char[1]`. La capa `x11gui` expone
`last_keycode`, `last_keysym`, `last_modifiers` y
`last_character: uint8`.

No se implementa todavía XIM, texto Unicode/UTF-8, o tratamiento
de composición multicaracter. Todos los accesos Xlib permanecen en
la frontera nativa y no se añaden `extern c` a `x11gui`.
