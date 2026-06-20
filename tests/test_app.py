import json

import pytest

from mumu.api.core.app import App
from conftest import FakeUtils


def test_install_requires_existing_file(tmp_path):
    app = App(FakeUtils())

    with pytest.raises(FileNotFoundError):
        app.install(str(tmp_path / "missing.apk"))

    folder = tmp_path / "folder"
    folder.mkdir()
    with pytest.raises(FileNotFoundError):
        app.install(str(folder))


def test_install_and_basic_app_commands(tmp_path):
    apk = tmp_path / "a.apk"
    apk.write_text("apk", encoding="utf-8")
    fu = FakeUtils(responses=[(0, ""), (0, ""), (0, ""), (0, "")])
    app = App(fu)

    assert app.install(str(apk)) is True
    assert app.uninstall("pkg.a") is True
    assert app.launch("pkg.a") is True
    assert app.close("pkg.a") is True

    assert fu.call_history[0]["command"] == ["app", "install", "-apk", str(apk)]
    assert fu.call_history[1]["command"] == ["app", "uninstall", "-pkg", "pkg.a"]
    assert fu.call_history[2]["command"] == ["app", "launch", "-pkg", "pkg.a"]
    assert fu.call_history[3]["command"] == ["app", "close", "-pkg", "pkg.a"]


def test_get_installed_filters_active_entry():
    payload = json.dumps(
        {
            "active": "pkg.active",
            "pkg.a": {"app_name": "A", "version": "1.0"},
            "pkg.b": {"app_name": "B", "version": "2.0"},
        }
    )
    app = App(FakeUtils(responses=[(0, payload)]))
    assert app.get_installed() == [
        {"package": "pkg.a", "app_name": "A", "version": "1.0"},
        {"package": "pkg.b", "app_name": "B", "version": "2.0"},
    ]


def test_exists_doesnt_exists_and_state():
    exists_payload = json.dumps({"state": "running"})
    missing_payload = json.dumps({"state": "not_installed"})
    fu = FakeUtils(responses=[(0, exists_payload), (0, missing_payload), (0, exists_payload)])
    app = App(fu)

    assert app.exists("pkg.a") is True
    assert app.doesntExists("pkg.a") is True
    assert app.state("pkg.a") == "running"


def test_app_raises_on_nonzero_return_code():
    app = App(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        app.launch("pkg.a")
