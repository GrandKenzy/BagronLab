"""Xvfb test fixture: send a real X11 ButtonPress or WM_DELETE_WINDOW message.

Requires Linux AMD64, libX11.so.6, and Python standard library only.
Never used by the x11gui runtime.
"""
import argparse
import ctypes as C
import time

U = C.c_ulong
P = C.c_void_p
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
x.XSendEvent.argtypes = [P, U, I, C.c_long, P]
x.XSendEvent.restype = I
x.XInternAtom.argtypes = [P, C.c_char_p, I]
x.XInternAtom.restype = U
x.XFlush.argtypes = [P]
x.XFlush.restype = I
x.XCloseDisplay.argtypes = [P]
x.XCloseDisplay.restype = I


class ButtonEvent(C.Structure):
    _fields_ = [
        ("type", I), ("pad0", I), ("serial", U), ("send_event", I),
        ("pad1", I), ("display", P), ("window", U), ("root", U),
        ("subwindow", U), ("time", U), ("x", I), ("y", I),
        ("x_root", I), ("y_root", I), ("state", C.c_uint),
        ("button", C.c_uint), ("same_screen", I),
        ("padding", C.c_ubyte * (192 - 92)),
    ]


class ClientEvent(C.Structure):
    _fields_ = [
        ("type", I), ("pad0", I), ("serial", U), ("send_event", I),
        ("pad1", I), ("display", P), ("window", U),
        ("message_type", U), ("format", I), ("pad2", I),
        ("data", U * 5), ("padding", C.c_ubyte * (192 - 96)),
    ]


assert C.sizeof(ButtonEvent) == 192
assert C.sizeof(ClientEvent) == 192


def find_window(display, title):
    root = x.XRootWindow(display, x.XDefaultScreen(display))
    for _ in range(300):
        parent_root, parent = U(), U()
        children = C.POINTER(U)()
        count = C.c_uint()
        if x.XQueryTree(
            display, root, C.byref(parent_root), C.byref(parent),
            C.byref(children), C.byref(count)
        ):
            for window in children[:count.value]:
                name = C.c_char_p()
                matches = x.XFetchName(display, window, C.byref(name))
                try:
                    if matches and name.value == title:
                        return root, window
                finally:
                    if name:
                        x.XFree(C.cast(name, P))
            if children:
                x.XFree(C.cast(children, P))
        time.sleep(0.01)
    raise RuntimeError("Test window not found: " + title.decode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", default="Bagron click test")
    parser.add_argument("--event", choices=["click", "close"], default="click")
    args = parser.parse_args()

    display = x.XOpenDisplay(None)
    if not display:
        raise RuntimeError("X display unavailable")
    try:
        root, window = find_window(display, args.title.encode())
        if args.event == "click":
            event = ButtonEvent()
            event.type, event.send_event = 4, 1
            event.display, event.window, event.root = display, window, root
            event.x, event.y, event.button, event.same_screen = 60, 30, 1, 1
            assert x.XSendEvent(display, window, 0, 4, C.byref(event))
        else:
            event = ClientEvent()
            event.type, event.send_event, event.format = 33, 1, 32
            event.display, event.window = display, window
            event.message_type = x.XInternAtom(display, b"WM_PROTOCOLS", 0)
            event.data[0] = x.XInternAtom(display, b"WM_DELETE_WINDOW", 0)
            assert x.XSendEvent(display, window, 0, 0, C.byref(event))
        x.XFlush(display)
    finally:
        x.XCloseDisplay(display)


if __name__ == "__main__":
    main()
