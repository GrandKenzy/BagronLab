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

## Ejecución

```sh
# Primero instalar desde las fuentes las versiones actuales de gnulibrary y x11gui.
bagron tests/x11gui/smoke.bg -o build/x11-smoke
bagron tests/x11gui/click.bg -o build/x11-click
bagron tests/x11gui/close.bg -o build/x11-close

xvfb-run -a ./build/x11-smoke

# El script corre dentro de la misma sesión Xvfb que el ejecutable.
xvfb-run -a sh -c './build/x11-click & pid=$!; python3 tests/x11gui/send_event.py --event click; wait $pid'
xvfb-run -a sh -c './build/x11-close & pid=$!; python3 tests/x11gui/send_event.py --event close --title "Bagron close test"; wait $pid'
```

Todas las pruebas deben terminar con código **0**. La primera prueba de
dibujo usa un plazo de sondeo acotado. Las otras envían un evento desde un
segundo proceso para comprobar las interfaces reales de Xlib.

Se han ejecutado con Bagron 1.1.4 en Linux x86_64 y con una biblioteca
`gnulibrary` de prueba compuesta por los tres módulos X11. La generación de
un paquete con todos los módulos de BagronLab se debe verificar antes de su
publicación como release. El compilador necesitó el arreglo PIC local conocido.
