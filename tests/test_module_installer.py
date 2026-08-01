from pathlib import Path
from unittest.mock import call, patch

from advanced_hello_world.module_installer import install_modules
from advanced_hello_world.module_manifest import load_manifest


def test_release_install_uses_immutable_git_requirements() -> None:
    manifest = load_manifest(Path("modules.json"))

    with patch("advanced_hello_world.module_installer.subprocess.run") as run:
        install_modules(manifest)

    assert run.call_count == 2
    for selection, invocation in zip(manifest.selections, run.call_args_list, strict=True):
        assert invocation == call(
            [
                __import__("sys").executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                f"git+{selection.repository}@{selection.ref}",
            ],
            check=True,
        )


def test_local_root_prefers_editable_sibling_repositories(tmp_path) -> None:
    manifest = load_manifest(Path("modules.json"))
    for selection in manifest.selections:
        repository_name = selection.repository.removesuffix(".git").rsplit("/", 1)[-1]
        (tmp_path / repository_name).mkdir()

    with patch("advanced_hello_world.module_installer.subprocess.run") as run:
        install_modules(manifest, local_root=tmp_path)

    for selection, invocation in zip(manifest.selections, run.call_args_list, strict=True):
        repository_name = selection.repository.removesuffix(".git").rsplit("/", 1)[-1]
        assert invocation == call(
            [
                __import__("sys").executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--editable",
                str((tmp_path / repository_name).resolve()),
            ],
            check=True,
        )
