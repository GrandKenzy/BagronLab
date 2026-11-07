"""X11 keyboard test injector, independent from Bagron runtime.

Sends XKeyEvent sequences using server-provided keycodes. Requires Xvfb (or X11)
and libX11.so.6. Python standard library only.
"""
import argparse
import ctypes as C
import time

P = C.c_void_p
U = C.c_ulong
I = C.c_int
x = C.CDLL("libX11.so.6")
x.XOpenDisplay.argtypes = [C.c_char_p]
x.XOpenDisplay.restype = P
x.XDefaultScreen.argtypes = [P]
x.XDefaultScreen.restype = I
x.XRootWindow.argtypes = [P, I]
x.XRootWindow.restype = U
x.XQueryTree.argtypes = [P, U, C.POINTER(U), C.POINTER(U), C.POINTER(C.POINTER(U)), C.POINTER(C.c_uint)]
x.XQueryTree.restype = I
x.XFetchName.argtypes = [P, U, C.POINTER(C.c_char_p)]
x.XFetchName.restype = I
x.XFree.argtypes = [P]
x.XFree.restype = I
x.XKeysymToKeycode.argtypes = [P, U]
x.XKeysymToKeycode.restype = C.c_ubyte
x.XSendEvent.argtypes = [P, U, I, C.c_long, P]
x.XSendEvent.restype = I
x.XFlush.argtypes = [P]
x.XFlush.restype = I
x.XCloseDisplay.argtypes = [P]
x.XCloseDisplay.restype = I


class KeyEvent(C.Structure):
    _fields_ = [
        ("type", I), ("pad0", I), ("serial", U), ("send_event", I),
        ("pad1", I), ("display", P), ("window", U), ("root", U),
        ("subwindow", U), ("time", U), ("x", I), ("y", I),
        ("x_root", I), ("y_root", I), ("state", C.c_uint),
        ("keycode", C.c_uint), ("same_screen", I),
        ("padding", C.c_ubyte * (192 - 92)),
    ]


assert C.sizeof(KeyEvent) == 192
assert KeyEvent.state.offset == 80
assert KeyEvent.keycode.offset == 84


def find_window(display, title):
    root = x.XRootWindow(display, x.XDefaultScreen(display))
    for _ in range(500):
        parent_root, parent = U(), U()
        children = C.POINTER(U)()
        count = C.c_uint()
        if x.XQueryTree(display, root, C.byref(parent_root), C.byref(parent),
                        C.byref(children), C.byref(count)):
            found = 0
            for window in children[: count.value]:
                name = C.c_char_p()
                match = x.XFetchName(display, window, C.byref(name))
                try:
                    if match and name.value == title:
                        found = window
                        break
                finally:
                    if name:
                        x.XFree(C.cast(name, P))
            if children:
                x.XFree(C.cast(children, P))
            if found:
                return root, found
        time.sleep(0.01)
    raise RuntimeError(f"Could not find X11 window {title!r}")


def send(display, window, root, symbol, event_type, modifiers=0):
    code = x.XKeysymToKeycode(display, symbol)
    if not code:
        raise RuntimeError(f"No keycode for KeySym {symbol}")
    event = KeyEvent()
    event.type = event_type
    event.send_event = 1
    event.display, event.window, event.root = display, window, root
    event.keycode, event.state, event.same_screen = code, modifiers, 1
    mask = 1 if event_type == 2 else 2
    if not x.XSendEvent(display, window, 0, mask, C.byref(event)):
        raise RuntimeError(f"XSendEvent failed: {symbol}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["sequence", "poll"], default="sequence")
    args = parser.parse_args()
    title = b"Bagron keyboard poll" if args.mode == "poll" else b"Bagron keyboard test"
    display = x.XOpenDisplay(None)
    if not display:
        raise RuntimeError("DISPLAY unavailable")
    try:
        root, window = find_window(display, title)
        if args.mode == "poll":
            send(display, window, root, ord("b"), 2)
        else:
            send(display, window, root, ord("a"), 2)
            send(display, window, root, ord("a"), 3)
            send(display, window, root, ord("a"), 2, 1)
            send(display, window, root, 65307, 2)
        x.XFlush(display)
    finally:
        x.XCloseDisplay(display)


if __name__ == "__main__":
    main()
