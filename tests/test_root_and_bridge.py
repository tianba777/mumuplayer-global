import pytest

from mumu.api.driver.bridge import Bridge
from mumu.api.permission.root import Root
from conftest import FakeUtils


def test_root_enable_disable():
    fu = FakeUtils(responses=[(0, ""), (0, "")])
    root = Root(fu)
    assert root.enable() is True
    assert root.disable() is True
    assert fu.call_history[0]["command"] == ["-k", "root_permission", "-val", "true"]
    assert fu.call_history[1]["command"] == ["-k", "root_permission", "-val", "false"]


def test_root_raises_on_failure():
    root = Root(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        root.enable()


def test_bridge_install_uninstall():
    fu = FakeUtils(responses=[(0, ""), (0, "")])
    bridge = Bridge(fu)
    assert bridge.install() is True
    assert bridge.uninstall() is True
    assert fu.operate_history[0] == ["driver", "install"]
    assert fu.call_history[0]["command"] == ["-n", "lwf"]
    assert fu.operate_history[1] == ["driver", "uninstall"]
    assert fu.call_history[1]["command"] == []


def test_bridge_raises_on_failure():
    bridge = Bridge(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        bridge.install()
