import pytest

from mumu.api.core.power import Power
from mumu.api.core.shortcut import Shortcut
from mumu.api.core.window import Window
from conftest import FakeUtils


def test_power_start_shutdown_restart_stop_reboot():
    fu = FakeUtils(responses=[(0, ""), (0, ""), (0, ""), (0, ""), (0, "")])
    power = Power(fu)

    assert power.start() is True
    assert fu.call_history[0]["command"] == ["launch"]

    assert power.start("pkg.a") is True
    assert fu.call_history[1]["command"] == ["launch", "-pkg", "pkg.a"]

    assert power.shutdown() is True
    assert power.restart() is True
    assert power.stop() is True
    assert power.reboot() is True


def test_power_raises_on_failure():
    power = Power(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        power.shutdown()


def test_window_show_hidden_and_layout_with_zero_values():
    fu = FakeUtils(responses=[(0, ""), (0, ""), (0, "")])
    window = Window(fu)

    assert window.show() is True
    assert window.hidden() is True
    assert window.layout(x=0, y=0, width=1080, height=1920) is True

    assert fu.call_history[2]["command"] == ["layout_window", "-px", "0", "-py", "0", "-width", "1080", "-height", "1920"]


def test_window_layout_requires_at_least_one_parameter():
    window = Window(FakeUtils())
    with pytest.raises(RuntimeError, match="at least one parameter"):
        window.layout()


def test_window_raises_on_failure():
    window = Window(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        window.show()


def test_shortcut_create_and_delete(tmp_path):
    icon = tmp_path / "a.ico"
    icon.write_text("icon", encoding="utf-8")
    fu = FakeUtils(responses=[(0, ""), (0, "")])
    shortcut = Shortcut(fu)

    assert shortcut.create("name", str(icon), "pkg.a") is True
    assert shortcut.delete() is True
    assert fu.call_history[0]["command"] == ["shortcut", "create", "-n", "name", "-i", str(icon), "-pkg", "pkg.a"]
    assert fu.call_history[1]["command"] == ["shortcut", "delete"]


def test_shortcut_create_requires_icon_file(tmp_path):
    shortcut = Shortcut(FakeUtils())
    with pytest.raises(FileNotFoundError):
        shortcut.create("n", str(tmp_path / "missing.ico"), "pkg.a")
