import argparse
import subprocess
import sys
from pathlib import Path

from .module_manifest import AssemblyManifest, load_manifest


def install_modules(
    manifest: AssemblyManifest,
    *,
    local_root: Path | None = None,
) -> None:
    for selection in manifest.selections:
        repository_name = selection.repository.removesuffix(".git").rsplit("/", 1)[-1]
        local_path = local_root / repository_name if local_root is not None else None
        if local_path is not None and local_path.is_dir():
            requirement = str(local_path.resolve())
            command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--editable",
                requirement,
            ]
        else:
            requirement = f"git+{selection.repository}@{selection.ref}"
            command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                requirement,
            ]
        subprocess.run(command, check=True)  # noqa: S603


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install the exact backend packages selected by modules.json"
    )
    parser.add_argument("manifest", nargs="?", type=Path, default=Path("modules.json"))
    parser.add_argument(
        "--local-root",
        type=Path,
        help="prefer editable sibling repositories found below this directory",
    )
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    install_modules(manifest, local_root=args.local_root)
    load_manifest(args.manifest, verify_installed=True)
    print(f"Installed and verified {len(manifest.selections)} backend packages")


if __name__ == "__main__":
    main()
