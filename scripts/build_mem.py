"""Build mem.lib from source using the installed Bagron compiler.

This script never modifies other packages, and only touches build/mem.lib.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bagron", default="bagron")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "mem.lib")
    args = parser.parse_args()
    artifact = args.output.resolve()
    artifact.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            args.bagron, "library", "--v1", str(ROOT / "mem"),
            "-o", str(artifact), "--name", "mem", "--version", args.version,
        ],
        cwd=ROOT, check=True
    )
    subprocess.run([args.bagron, "verify", str(artifact)], cwd=ROOT, check=True)
    print(f"Validated: {artifact}")


if __name__ == "__main__":
    main()
