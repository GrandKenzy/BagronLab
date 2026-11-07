"""Build win32gui.lib on Windows x64; do not publish cross-built empty packages."""
import argparse
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Build native Windows GUI library")
    parser.add_argument("--bagron", default="bagron")
    parser.add_argument("--version", default="0.0.1")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "win32gui.lib")
    args = parser.parse_args()
    if platform.system() != "Windows" or platform.machine().lower() not in {"amd64", "x86_64"}:
        parser.error("win32gui must be built and validated on native Windows x64")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [args.bagron, "library", "--v1", str(ROOT / "win32gui"), "-o",
         str(output), "--name", "win32gui", "--version", args.version],
        cwd=ROOT, check=True,
    )
    subprocess.run([args.bagron, "verify", str(output)], cwd=ROOT, check=True)
    subprocess.run([args.bagron, "inspect", str(output)], cwd=ROOT, check=True)
    print(f"Package generated and structurally verified: {output}")
    print("You must still compile and run examples/win32gui/message_box.bg on Windows.")


if __name__ == "__main__":
    main()
