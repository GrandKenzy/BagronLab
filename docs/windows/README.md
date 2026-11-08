# Windows ABI

La carpeta `windows` es la API nativa de Windows para Bagron. Su módulo base
es `windows/modules/kernel32.bg`.

## `kernel32.bg`

`kernel32.bg` declara símbolos exportados por `kernel32.dll` mediante:

```bg
extern windows "kernel32":
```

Esto usa directamente la ABI Microsoft x64 de Windows. No es una libc, no
declara `extern c` y no implementa wrappers C. Los helpers de alto nivel de
Bagron se implementan en `gui_window.bg`, `gui_events.bg`, `gui_controls.bg`,
`gui_drawing.bg`, `gui_dialogs.bg` y `gui_text.bg` sobre estas declaraciones
ABI.

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

`process.process_arg_count()` y `process.process_arg_copy()` consumen el
puente nativo de argumentos que entrega Bagron al proceso. El índice cero es
la ruta del ejecutable; la copia siempre termina en NUL, limita el resultado a
`capacity - 1` bytes y devuelve la cantidad copiada. Esta frontera no usa
`GetCommandLineA`, `CommandLineToArgvW` ni la CRT.

## Winsock

`windows/modules/sockets.bg` expone la ABI de `ws2_32.dll`, incluidos
`WSAStartup`, creación y cierre de sockets, envío, recepción y resolución de
direcciones. `WSADATA` conserva el layout de Windows x64; un `Socket` sólo se
marca cerrado cuando `closesocket` confirma éxito, para que un error pueda
gestionarse o reintentarse sin perder el handle.

No incluye syscalls internas de Windows, NT Native API, GUI, COM, registro ni
wrappers C.

## Integración de Net y WinHTTP

`windows/modules/winhttp.bg` declara la ABI pública de WinHTTP. Su conversión
de texto UTF-8 a UTF-16 usa `MultiByteToWideChar` de `kernel32.bg`, no una
supuesta exportación de WinHTTP. Los helpers públicos de `sockets.bg` incluyen
`OpenTcpHost`, que usa Winsock para resolver y conectar por TCP.

La nueva API debe compilarse y probarse en Windows x64. **No** se debe
publicar como `windows.lib` un paquete compilado en Linux si el empaquetador
produce una tabla de símbolos vacía para el target Windows.

## Extensiones de sockets para Net

`OpenTcpHost` recorre los candidatos de `getaddrinfo` en vez de usar
solo el primero, y libera los sockets fallidos. `ReuseAddress` configura
`SO_REUSEADDR` para listeners. El helper actual sigue utilizando
`connect` bloqueante: un timeout de recepción no basta para limitar el
tiempo de conexión.

La validación nativa de Windows x64 y la seguridad frente a reparse points
intermedios en rutas HTTP siguen pendientes; los checks de fuentes ejecutados
en Windows no equivalen a pruebas de ejecución.

## Integración con mmap

`windows/modules/memory.bg` expone `vm_map_rw`, `vm_unmap` y
`vm_protect` mediante `VirtualAlloc`, `VirtualFree` y `VirtualProtect`.
La región es privada y de lectura/escritura; se puede proteger como solo
lectura y restaurar. El respaldo nativo es Windows x64.

Estos helpers nuevos están listos en las fuentes, pero la compilación desde
Linux **no** verifica las exportaciones Windows: regenerar `windows.lib` y
probar las llamadas en una máquina Windows antes de declararlas compatibles.

## GUI nativa por DLL

La GUI para Windows se mantiene modular, sin poner todas las declaraciones
en `kernel32.bg` ni dentro de la biblioteca gráfica de alto nivel:

- `modules/user32.bg`: `RegisterClassExW`, `CreateWindowExW`,
  `GetMessageW`, `DispatchMessageW`, ventanas, controles básicos,
  mensajes, `BeginPaint`/`EndPaint` y estructuras Win32.
- `modules/gdi32.bg`: primitivas de dibujo, texto y recursos GDI.
- `modules/comctl32.bg`: inicialización de controles comunes e ImageList.
- `modules/kernel32.bg`: `GetModuleHandleW` y conversión UTF-8/UTF-16.

Las estructuras `POINT` y `RECT` tienen alineación de 4 bytes en
Win64; dentro de `MSG` y `PAINTSTRUCT` esto conserva los offsets ABI.
Los tamaños esperados en x64 son `MSG=48`, `PAINTSTRUCT=72` y
`WNDCLASSEXW=80`. Validar el layout con un ejecutable Windows antes de
declarar el soporte estable.

La biblioteca `windows` exporta los helpers `gui_window`, `gui_events`,
`gui_controls`, `gui_drawing`, `gui_dialogs` y `gui_text` sin crear una
segunda biblioteca GUI ni duplicar declaraciones `extern`. `guilib` queda
reservada como futura API multiplataforma.

El punto crítico pendiente es la entrada desde callbacks Win32 `WNDPROC`:
no basta con declarar `RegisterClassExW`; hay que validar la convención
Microsoft x64 y el lifetime de los callbacks Bagron en Windows.
