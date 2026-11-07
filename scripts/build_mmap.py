"""Build the portable mmap lib1 package with the installed Bagron compiler.

Requires gnulibrary.lib on Linux or windows.lib on Windows. The script only
writes build/mmap.lib; it does not overwrite installed native libraries.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bagron", default="bagron")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "mmap.lib")
    args = parser.parse_args()
    target = args.output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            args.bagron,
            "library",
            "--v1",
            str(ROOT / "mmap"),
            "-o",
            str(target),
            "--name",
            "mmap",
            "--version",
            args.version,
        ],
        cwd=ROOT, check=True,
    )
    subprocess.run([args.bagron, "verify", str(target)], cwd=ROOT, check=True)
    print(f"Verified mmap lib1: {target}")


if __name__ == "__main__":
    main()
