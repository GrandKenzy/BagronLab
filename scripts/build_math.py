"""Build and verify the BagronLab math 1.2.0 source package.

No third-party Python packages, C math libraries, or system calls are needed.
The script only writes its --output path. It never overwrites installed libs.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bagron", default="bagron")
    parser.add_argument("--version", default="1.2.0")
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "math.lib")
    args = parser.parse_args()

    target = args.output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            args.bagron, "library", "--v1", str(ROOT / "math"), "-o",
            str(target), "--name", "math", "--version", args.version,
        ],
        cwd=ROOT, check=True,
    )
    subprocess.run([args.bagron, "verify", str(target)], cwd=ROOT, check=True)
    print(f"Verified math lib1: {target}")


if __name__ == "__main__":
    main()
