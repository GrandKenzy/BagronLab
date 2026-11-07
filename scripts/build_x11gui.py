"""Build the Linux X11 graphical backend lib1 package.

Requires Bagron with an up-to-date installed gnulibrary.lib that includes the
x11_display, x11_events and x11_draw modules. Does not overwrite other libs.
"""
import argparse
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bagron", default="bagron")
    parser.add_argument("--version", default="0.1.1")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "x11gui.lib")
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.machine().lower() not in {"x86_64", "amd64"}:
        parser.error("x11gui 0.1.0 currently targets native Linux AMD64 only")
    target = args.output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [args.bagron, "library", "--v1", str(ROOT / "x11gui"), "-o",
         str(target), "--name", "x11gui", "--version", args.version],
        cwd=ROOT, check=True,
    )
    subprocess.run([args.bagron, "verify", str(target)], cwd=ROOT, check=True)
    print(f"Validated source package: {target}")
    print("For a runtime test, install an updated gnulibrary.lib and x11gui.lib,")
    print("compile tests/x11gui/smoke.bg and execute under an X11 display.")


if __name__ == "__main__":
    main()
