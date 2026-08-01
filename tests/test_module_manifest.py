import json

import pytest

from advanced_hello_world.module_manifest import load_manifest


def test_repository_manifest_is_valid() -> None:
    manifest = load_manifest(__import__("pathlib").Path("modules.json"))

    assert manifest.core.id == "platform-core"
    assert [module.id for module in manifest.modules] == ["messages"]


def test_duplicate_module_ids_are_rejected(tmp_path) -> None:
    raw = json.loads(__import__("pathlib").Path("modules.json").read_text(encoding="utf-8"))
    raw["modules"] = [{**raw["core"], "package": "another-package"}]
    path = tmp_path / "modules.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="ids must be unique"):
        load_manifest(path)
