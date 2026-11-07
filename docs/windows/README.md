# Windows ABI

La carpeta `windows` es la API nativa de Windows para Bagron. Su módulo base
es `windows/modules/kernel32.bg`.

## `kernel32.bg`

`kernel32.bg` declara símbolos exportados por `kernel32.dll` mediante:

```bg
extern windows "kernel32":
```

Esto usa directamente la ABI Microsoft x64 de Windows. No es una libc, no
declara `extern c` y no implementa wrappers C. Las funciones de alto nivel de
Bagron se construirán en módulos posteriores sobre estas declaraciones ABI.

## Variantes de texto

Las funciones `A` reciben texto ANSI mediante `char`; las funciones `W`
reciben unidades UTF-16 mediante `uint16`. `kernel32.bg` expone ambas variantes
sin convertir cadenas ni imponer una política de texto de alto nivel.
`GetFileAttributesA/W` y `MoveFileExA/W` completan las operaciones de rutas y
los flags de movimiento expuestos por el módulo.

## Límites

Este módulo cubre la base de archivos, handles, consola, procesos, tiempo y
depuración y memoria virtual. `windows/modules/memory.bg` ofrece wrappers
propios de Bagron para reservar, liberar, proteger y consultar regiones de
memoria sin depender de `malloc` ni de una libc.

Las regiones se exponen como el descriptor opaco `MEMORY_REGION`; la API no
filtra punteros crudos desde funciones propias de Bagron. `VirtualQuery` recibe
un buffer nativo proporcionado por el llamador porque su estructura depende del
layout de Windows x64. `release` requiere la dirección base retornada por
`allocate`, pasa tamaño cero con `MEM_RELEASE` y deja inválida la región al
tener éxito.

Los módulos `windows/modules/process.bg` y `windows/modules/time.bg` son la
primera capa de utilidades propias de Bagron sobre `kernel32.bg`. `process.trap`
termina el proceso mediante `ExitProcess`; no declara una nueva ABI ni depende
de la CRT.

## Winsock

`windows/modules/sockets.bg` expone la ABI de `ws2_32.dll`, incluidos
`WSAStartup`, creación y cierre de sockets, envío, recepción y resolución de
direcciones. `WSADATA` conserva el layout de Windows x64; un `Socket` sólo se
marca cerrado cuando `closesocket` confirma éxito, para que un error pueda
gestionarse o reintentarse sin perder el handle.

No incluye syscalls internas de Windows, NT Native API, GUI, COM, registro ni
wrappers C.
