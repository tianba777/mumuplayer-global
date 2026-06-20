import pytest

from mumu.api.develop.androidevent import AndroidEvent
from conftest import FakeUtils


def test_rotate_and_rotates_are_compatible_aliases():
    fu = FakeUtils(responses=[(0, ""), (0, "")])
    ae = AndroidEvent(fu)

    assert ae.rotate() is True
    assert ae.rotates() is True
    assert fu.call_history[0]["command"] == ["tool", "func", "-n", "rotate"]
    assert fu.call_history[1]["command"] == ["tool", "func", "-n", "rotate"]


def test_common_toolbar_actions():
    actions = ["go_home", "go_back", "top_most", "fullscreen", "shake", "screenshot", "volume_up", "volume_down", "volume_mute"]
    fu = FakeUtils(responses=[(0, "")] * len(actions))
    ae = AndroidEvent(fu)

    for action in actions:
        assert getattr(ae, action)() is True

    expected = [["tool", "func", "-n", action] for action in actions]
    assert [x["command"] for x in fu.call_history] == expected


def test_go_task_uses_adb_operate():
    fu = FakeUtils(responses=[(0, "")])
    ae = AndroidEvent(fu)
    assert ae.go_task() is True
    assert fu.operate_history[-1] == "adb"
    assert fu.call_history[-1]["command"] == ["-c", "go_task"]


def test_location_validates_range():
    ae = AndroidEvent(FakeUtils())
    with pytest.raises(ValueError, match="longitude"):
        ae.location(181, 0)
    with pytest.raises(ValueError, match="latitude"):
        ae.location(0, 91)


def test_location_and_gyro_build_commands():
    fu = FakeUtils(responses=[(0, ""), (0, "")])
    ae = AndroidEvent(fu)

    assert ae.location(120.1, 30.2) is True
    assert ae.gyro(1.0, 2.0, 3.0) is True
    assert fu.call_history[0]["command"] == ["tool", "location", "-lon", "120.1", "-lat", "30.2"]
    assert fu.call_history[1]["command"] == ["tool", "gyro", "-gx", "1.0", "-gy", "2.0", "-gz", "3.0"]
