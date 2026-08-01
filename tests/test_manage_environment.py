import importlib.util
import os
from pathlib import Path


def load_manage_module():
    manage_path = Path(__file__).resolve().parents[1] / "manage.py"
    spec = importlib.util.spec_from_file_location("manage_for_test", manage_path)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dotenv_loads_without_overriding_exported_values(monkeypatch, tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "POSTGRES_HOST=from-file\nPOSTGRES_PASSWORD=from-file\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("POSTGRES_HOST", "from-shell")
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)

    manage = load_manage_module()
    manage.load_development_environment(env_file)

    assert os.environ["POSTGRES_HOST"] == "from-shell"
    assert os.environ["POSTGRES_PASSWORD"] == "from-file"
