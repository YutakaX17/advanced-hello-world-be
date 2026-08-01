import argparse
import importlib
import json
import re
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

_MODULE_ID = re.compile(r"^[a-z][a-z0-9-]*$")
_PACKAGE = re.compile(r"^[a-z][a-z0-9-]*$")
_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_IMPORT_PATH = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")
_REPOSITORY = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git$")
_REF = re.compile(r"^[0-9a-f]{40}$")
_FIELDS = {
    "id",
    "package",
    "version",
    "repository",
    "ref",
    "djangoApp",
    "urls",
    "urlPrefix",
}


@dataclass(frozen=True, slots=True)
class ModuleSelection:
    id: str
    package: str
    version: str
    repository: str
    ref: str
    django_app: str
    urls: str
    url_prefix: str


@dataclass(frozen=True, slots=True)
class AssemblyManifest:
    core: ModuleSelection
    modules: tuple[ModuleSelection, ...]

    @property
    def selections(self) -> tuple[ModuleSelection, ...]:
        return (self.core, *self.modules)


def _selection(raw: Any, location: str) -> ModuleSelection:
    if not isinstance(raw, dict) or set(raw) != _FIELDS:
        raise ValueError(f"{location} must contain exactly: {', '.join(sorted(_FIELDS))}")
    if not _MODULE_ID.fullmatch(raw["id"]):
        raise ValueError(f"{location}.id is invalid")
    if not _PACKAGE.fullmatch(raw["package"]):
        raise ValueError(f"{location}.package is invalid")
    if not _VERSION.fullmatch(raw["version"]):
        raise ValueError(f"{location}.version must be an exact semantic version")
    if not _REPOSITORY.fullmatch(raw["repository"]):
        raise ValueError(f"{location}.repository must be an HTTPS GitHub Git URL")
    if not _REF.fullmatch(raw["ref"]):
        raise ValueError(f"{location}.ref must be a full commit SHA")
    if not _IMPORT_PATH.fullmatch(raw["djangoApp"]):
        raise ValueError(f"{location}.djangoApp is invalid")
    if not _IMPORT_PATH.fullmatch(raw["urls"]):
        raise ValueError(f"{location}.urls is invalid")
    if raw["urlPrefix"].startswith("/") or not raw["urlPrefix"].endswith("/"):
        raise ValueError(f"{location}.urlPrefix must be relative and end with '/'")
    return ModuleSelection(
        id=raw["id"],
        package=raw["package"],
        version=raw["version"],
        repository=raw["repository"],
        ref=raw["ref"],
        django_app=raw["djangoApp"],
        urls=raw["urls"],
        url_prefix=raw["urlPrefix"],
    )


def load_manifest(path: Path, *, verify_installed: bool = False) -> AssemblyManifest:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("manifest root must be an object")
    if set(raw) - {"$schema", "schemaVersion", "core", "modules"}:
        raise ValueError("manifest contains unsupported root fields")
    if raw.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError(f"unsupported manifest schema: {raw.get('schemaVersion')}")
    if not isinstance(raw.get("modules"), list):
        raise ValueError("modules must be an array")

    manifest = AssemblyManifest(
        core=_selection(raw.get("core"), "core"),
        modules=tuple(
            _selection(module, f"modules[{index}]") for index, module in enumerate(raw["modules"])
        ),
    )
    ids = [selection.id for selection in manifest.selections]
    packages = [selection.package for selection in manifest.selections]
    if len(ids) != len(set(ids)):
        raise ValueError("module ids must be unique")
    if len(packages) != len(set(packages)):
        raise ValueError("module packages must be unique")

    if verify_installed:
        for selection in manifest.selections:
            try:
                installed = version(selection.package)
            except PackageNotFoundError as error:
                raise ValueError(f"{selection.package} is not installed") from error
            if installed != selection.version:
                raise ValueError(
                    f"{selection.package} {installed} does not match {selection.version}"
                )
        for selection in manifest.modules:
            descriptor = importlib.import_module(f"{selection.django_app}.module").MODULE
            expected = (
                selection.id,
                selection.django_app,
                selection.urls,
                selection.url_prefix,
            )
            actual = (
                descriptor.id,
                descriptor.django_app,
                descriptor.urls,
                descriptor.url_prefix,
            )
            if actual != expected:
                raise ValueError(f"{selection.package} metadata does not match modules.json")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the backend assembly manifest")
    parser.add_argument("manifest", type=Path, nargs="?", default=Path("modules.json"))
    parser.add_argument("--check-installed", action="store_true")
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, verify_installed=args.check_installed)
    print(f"Validated {len(manifest.selections)} backend package selection(s)")


if __name__ == "__main__":
    main()
