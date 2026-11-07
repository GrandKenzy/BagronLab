# x11gui 0.1.0 — Interfaz gráfica para GNU/Linux con Xlib

`x11gui` es el backend de interfaz gráfica **X11** para Bagron. Está separado
de `win32gui`, su equivalente Windows. El nombre `guilib` continúa
reservado para una futura fachada multiplataforma.

Estado: **prototipo funcional en Linux x86_64**. Se han compilado y ejecutado
las pruebas de dibujo, botones y cierre en Xvfb. Aún no se ha publicado un
paquete binario integral junto a `gnulibrary.lib` en `build/`.

## Arquitectura

```text
BagronLab/
├── gnulibrary/
│   └── modules/
│       ├── x11_display.bg  # XOpenDisplay, ventanas y WM_DELETE_WINDOW
│       ├── x11_events.bg   # XPending, XNextEvent, XEvent y eventos
│       └── x11_draw.bg     # GC, líneas, rectángulos y texto
└── x11gui/
    ├── main.bg             # library gnulibrary as XNative
    └── modules/
        ├── window.bg       # Window: display, ventana, GC y cierre
        ├── events.bg       # Tipo de evento y solicitudes de repintado
        ├── drawing.bg      # Dibujo inmediato
        └── controls.bg     # Botón dibujado y hit-testing
```

**Ningún archivo de `x11gui` declara `extern c`.** Toda la frontera
externa vive en `gnulibrary`, que enlaza con `libX11.so.6`.

Xlib pertenece al ecosistema **X.Org**, no es una API propia de GNU ni una
syscall Linux. Requiere un servidor X11 accesible a través de `DISPLAY`.
Puede funcionar sobre XWayland si está disponible; no implementa todavía
el protocolo Wayland nativo.

## API de Window

| Método/campo | Comportamiento |
| --- | --- |
| `Window()` | Inicializa los recursos sin abrir un display |
| `open(title, width, height)` | Crea ventana y GC; `false` si falla |
| `poll()` | Un evento sin bloqueo; 0 si no hay |
| `wait()` | Bloquea eficientemente hasta un evento |
| `pointer_x`, `pointer_y` | Últimas coordenadas de `ButtonPress` |
| `black_pixel`, `white_pixel` | Pixeles nativos de pantalla |
| `display_id`, `window_id`, `gc_id` | Handles prestados para dibujar |
| `close()` | Libera GC, ventana y conexión; cierre repetido permitido |

Los códigos principales: `X11_EXPOSE=12`, `X11_BUTTON_PRESS=4`,
`X11_CLIENT_MESSAGE=33`, y `X11_CLOSE_REQUEST=1001` (código interno
para un `WM_DELETE_WINDOW` válido). `is_close_request`,
`should_repaint` e `is_click` ayudan a interpretar eventos.

La biblioteca también ofrece `line`, `rectangle`, `fill_rectangle`,
`text`, `draw_button` e `hit_test`.

`draw_button` dibuja un control en X11 y `hit_test` comprueba el clic;
Xlib **no** ofrece un widget nativo de botón por defecto. El soporte de texto
en esta etapa es de un byte (ASCII/Latin-1), no renderizado Unicode completo.

## Ejemplo interactivo

El ejemplo está en
[`examples/x11gui/main.bg`](../../examples/x11gui/main.bg).
Crea una ventana con el botón «Salir», dibuja con `XDrawRectangle`,
`XFillRectangle` y `XDrawString`, y termina al pulsar el botón o cerrar
la ventana. El bucle usa `wait()` para no sondear continuamente.

## Construcción

Requisitos: Linux AMD64, Bagron 1.1.4 o posterior,
`libX11.so.6`, un servidor X11/XWayland, y una versión de
`gnulibrary.lib` **regenerada desde los fuentes nuevos**:

```sh
bagron library --v1 gnulibrary -o build/gnulibrary.lib --name gnulibrary --version 1.1.10
bagron verify build/gnulibrary.lib

# Instalar primero gnulibrary.lib actualizado en la instalación de Bagron.
python3 scripts/build_x11gui.py
bagron verify build/x11gui.lib

# Instalar x11gui.lib para la prueba de un consumidor externo.
bagron tests/x11gui/smoke.bg -o build/x11gui-smoke
xvfb-run -a ./build/x11gui-smoke
```

La versión `1.1.10` de `gnulibrary` es un ejemplo de versión de desarrollo:
ajústala a la versión que decidas publicar. **No reemplaces una biblioteca
instalada con un paquete incompleto**. En las pruebas se reconstruyó primero el subconjunto X11 y después el paquete completo a partir de los módulos existentes en el paquete local instalado más los tres módulos X11 nuevos, conservando respaldo de la biblioteca original. Esta prueba no sustituye la reconstrucción con todas las fuentes más recientes de GitHub.

El enlace en Bagron 1.1.4 para ELF Linux requiere actualmente el ajuste PIC
local conocido del backend LLVM. Este repositorio no aplica ese parche al
compilador.

## Validación realizada

- Paquete fuente `lib1` de las nuevas funciones Xlib: generado y verificado.
- Paquete fuente `lib1` de `x11gui`: generado y verificado.
- Ejecutable ELF Linux x86_64 creado y ejecutado con Xvfb: salida 0.
- Repintado tras `Expose`: líneas, rectángulos y texto.
- `ButtonPress`: lectura de coordenadas y `hit_test` correcta.
- `WM_DELETE_WINDOW`: mensaje `ClientMessage` procesado y cierre limpio.
- Botón dibujado con `draw_button`: prueba de ejecución correcta.

## Límites y pendientes

- **Ownership:** no copiar objetos `Window` abiertos: Bagron 1.1.4 no
  garantiza propiedad lineal. Cerrar explícitamente; el destructor es respaldo.
- Los handles expuestos son prestados e inválidos después de `close()`.
- Xlib no se inicializa para acceso concurrente con `XInitThreads`; cada
  `Window` debe utilizarse en su hilo propietario.
- El servidor X puede informar errores de forma asíncrona: una llamada de
  dibujo que devuelve `true` solo confirma que se enviaron comandos.
- La implementación recibe eventos de una ventana principal por instancia.
  El transporte de eventos multi-ventana, teclas Unicode y drag-and-drop
  queda para versiones futuras.
- Accesibilidad, fuentes Unicode, scaling DPI, compositor Wayland nativo,
  controles complejos y respaldo Wayland quedan pendientes.
