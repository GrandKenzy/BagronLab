# x11gui — pruebas Linux AMD64

Las pruebas usan `x11gui.lib` y un `gnulibrary.lib` actualizado. El runtime
Bagron **no** requiere Python; la prueba `send_event.py` usa `ctypes`
solo para enviar mensajes sintéticos a Xvfb.

| Archivo | Comprobación |
| --- | --- |
| `smoke.bg` | Crea ventana, detecta Expose, dibuja y cierra |
| `click.bg` | Lee un ButtonPress en (60,30) y acierta hit_test |
| `close.bg` | Recibe ClientMessage WM_DELETE_WINDOW en wait() |
| `send_event.py` | Envía evento click/close con Xlib por ctypes |
| `keyboard.bg` | Pulsación, liberación, Shift+A y Escape mediante `wait()` |
| `keyboard_poll.bg` | Pulsación sin bloqueo mediante `poll()` |
| `send_keyboard.py` | Envía eventos de teclado sintéticos usando keycodes del servidor |

## Ejecución

```sh
# Primero instalar desde las fuentes las versiones actuales de gnulibrary y x11gui.
bagron tests/x11gui/smoke.bg -o build/x11-smoke
bagron tests/x11gui/click.bg -o build/x11-click
bagron tests/x11gui/close.bg -o build/x11-close
bagron tests/x11gui/keyboard.bg -o build/x11-keyboard
bagron tests/x11gui/keyboard_poll.bg -o build/x11-keyboard-poll

xvfb-run -a ./build/x11-smoke

# El script corre dentro de la misma sesión Xvfb que el ejecutable.
xvfb-run -a sh -c './build/x11-click & pid=$!; python3 tests/x11gui/send_event.py --event click; wait $pid'
xvfb-run -a sh -c './build/x11-close & pid=$!; python3 tests/x11gui/send_event.py --event close --title "Bagron close test"; wait $pid'
xvfb-run -a sh -c './build/x11-keyboard & pid=$!; python3 tests/x11gui/send_keyboard.py --mode sequence; wait $pid'
xvfb-run -a sh -c './build/x11-keyboard-poll & pid=$!; python3 tests/x11gui/send_keyboard.py --mode poll; wait $pid'
```

Todas las pruebas deben terminar con código **0**. La primera prueba de
dibujo usa un plazo de sondeo acotado. Las otras envían un evento desde un
segundo proceso para comprobar las interfaces reales de Xlib.

Se han ejecutado con Bagron 1.1.4 en Linux x86_64. También se probó
`gnulibrary` reconstruida a partir de todos los módulos del paquete local
previamente instalado, más los tres módulos X11 nuevos; todas las pruebas
continuaron pasando. Queda pendiente reconstruir desde las fuentes completas
más recientes de GitHub antes de publicar una release oficial.
El compilador necesitó el ajuste PIC local conocido.

## Teclado

La suite comprueba el layout de `XKeyEvent` para Linux AMD64, los
eventos `KeyPress` y `KeyRelease`, la traducción de teclas mediante
`XLookupString`, el estado de Shift y el símbolo `Escape`.
`keyboard.bg` verifica `wait()`; `keyboard_poll.bg` verifica `poll()`.

Para ejecutar con un límite de tiempo y evitar bloqueos durante fallos de
inyección, se pueden añadir `timeout 15` a los comandos `xvfb-run`.

**Pruebas de regresión confirmadas:** las dos nuevas pruebas de teclado,
las tres pruebas anteriores de ventana/ratón/cierre y los tamaños y offsets
de las estructuras X11 contra las cabeceras C del sistema, en Linux AMD64.
Las pruebas de texto no cubren todavía Unicode/IME ni combinaciones
compuestas mediante XIM.
