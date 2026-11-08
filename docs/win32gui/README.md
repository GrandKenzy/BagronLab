# win32gui — Base modular para interfaces Windows

Estado: **paquete lib1 validado para Windows x64**. `build/win32gui.lib` se
genera y verifica correctamente, y el ejemplo de `MessageBoxW` compila. La
ejecución interactiva y los callbacks `WNDPROC` todavía requieren validación
manual.

`guilib` queda reservado para la futura biblioteca multiplataforma.
`win32gui` es un backend de Windows que depende de `windows`. No declara
ABI nativa directamente.

## Estructura

```text
BagronLab/
├── windows/
│   └── modules/
│       ├── kernel32.bg   # Módulos/procesos y conversión UTF-8/UTF-16
│       ├── user32.bg     # Ventanas, controles básicos, mensajes, WNDPROC
│       ├── gdi32.bg      # Primitivas de dibujo y objetos GDI
│       └── comctl32.bg   # Inicialización de controles comunes
└── win32gui/
    ├── main.bg           # Dependencia library windows as Win
    └── modules/
        ├── window.bg     # Registro, creación, vida útil y título
        ├── events.bg     # Despacho de mensajes y WM_COMMAND
        ├── controls.bg   # Botón, etiqueta y cuadro de texto
        ├── drawing.bg    # Rectángulos, líneas, texto y COLORREF
        ├── dialogs.bg    # MessageBoxW
        └── text.bg       # UTF-8 a UTF-16
```

Separación de responsabilidades: **solo `windows/modules/*.bg` declara
`extern windows`**; `win32gui` invoca exclusivamente las funciones
exportadas por el namespace `Win`. Las nuevas declaraciones nativas
incluyen `GetModuleHandleW`, `RegisterClassExW`, `CreateWindowExW`,
`GetMessageW`, `TextOutW`, `InitCommonControlsEx` y más.

## Uso

Se empieza por diálogos, que no necesitan implementar `WNDPROC`:

```bg
clause System "windows"
clause Arch "amd"
library win32gui as GUI
import { message_box } from GUI

@unsafe
func main() int32:
    title: uint16[7]
    title[0] = 66
    title[1] = 97
    title[2] = 103
    title[3] = 114
    title[4] = 111
    title[5] = 110
    title[6] = 0

    message: uint16[5]
    message[0] = 72
    message[1] = 111
    message[2] = 108
    message[3] = 97
    message[4] = 0

    if message_box(0, $title[0], $message[0]) == 0:
        return 1
    return 0
```

El helper `utf8_to_utf16()` permite evitar la construcción manual de
arreglos UTF-16 siempre que el origen `char[]` esté terminado en NUL
y el destino tenga espacio suficiente.

## Importante: callbacks y estructura de mensajes

Una ventana personalizada necesita un procedimiento `WNDPROC` con la
**convención Microsoft x64 correcta** y vida útil suficiente. La función
`register_class()` recibe un puntero a callback ya existente; **no** convierte
automáticamente una función Bagron en callback Win32. La compatibilidad del
compilador con callbacks entrantes aún debe verificarse antes de usar
`create_window()` en aplicaciones reales.

Tamaños nativos esperados en Windows x64:

| Tipo | Tamaño | Alineación |
| --- | ---: | ---: |
| `POINT` | 8 bytes | 4 |
| `RECT` | 16 bytes | 4 |
| `MSG` | 48 bytes | 8 |
| `PAINTSTRUCT` | 72 bytes | 8 |
| `WNDCLASSEXW` | 80 bytes | 8 |

`drawing.bg` utiliza `GetDC`/`ReleaseDC` para dibujos inmediatos que
desaparecerán en un repintado. El renderizado persistente deberá hacerse
en `WM_PAINT` con `BeginPaint`/`EndPaint`, tras validar callbacks.

## Construcción y validación

Requiere Bagron 1.1.4 o posterior en Windows x64:

```powershell
python scripts/build_win32gui.py --bagron bagron --version 0.0.1
bagron verify build/win32gui.lib
bagron examples/win32gui/message_box.bg -o build/win32gui-message-box.exe
```

La compilación del ejemplo valida la resolución de la API y el enlace de las
declaraciones nativas. Ejecútalo manualmente si quieres comprobar el diálogo.

## Próximos pasos

1. Definir y validar el callback `WNDPROC` entrante desde Bagron.
2. Probar un ciclo completo de ventana y `WM_DESTROY` → `PostQuitMessage`.
3. Comprobar eventos de botones `WM_COMMAND` y dibujo mediante `WM_PAINT`.
4. Extender con `uxtheme`, `dwmapi`, DPI, layout y accesibilidad.
5. Agregar backend Linux independiente y una API pública común en `guilib`.

La compatibilidad de compilación Windows x64 está comprobada. La compatibilidad
de ejecución de ventanas personalizadas queda pendiente hasta validar `WNDPROC`.
