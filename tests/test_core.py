import json

import pytest

from mumu.api.core.Core import Core
from conftest import FakeUtils


def test_create_and_clone_parse_success_indexes():
    payload = json.dumps({"1": {"errcode": 0}, "2": {"errcode": -1}, "3": {"errcode": 0}})
    fu = FakeUtils(responses=[(0, payload), (0, payload)])
    core = Core(fu)

    assert core.create(2) == [1, 3]
    assert fu.operate_history[0] == "create"
    assert fu.call_history[0]["command"] == ["-n", "2"]

    assert core.clone(4) == [1, 3]
    assert fu.operate_history[1] == "clone"
    assert fu.call_history[1]["command"] == ["-n", "4"]


def test_create_and_clone_warn_when_number_invalid():
    payload = json.dumps({"1": {"errcode": 0}})
    fu = FakeUtils(responses=[(0, payload), (0, payload)])
    core = Core(fu)

    with pytest.warns(UserWarning):
        assert core.create(0) == [1]
    with pytest.warns(UserWarning):
        assert core.clone(-1) == [1]

    assert fu.call_history[0]["command"] == ["-n", "1"]
    assert fu.call_history[1]["command"] == ["-n", "1"]


def test_delete_rename_export_success():
    fu = FakeUtils(responses=[(0, ""), (0, ""), (0, ""), (0, "")])
    core = Core(fu)

    assert core.delete() is True
    assert core.rename("name") is True
    assert core.export(r"C:\backup", "demo", zip=False) is True
    assert core.export(r"C:\backup", "demo", zip=True) is True

    assert fu.call_history[2]["command"] == ["-d", r"C:\backup", "-n", "demo"]
    assert fu.call_history[3]["command"] == ["-d", r"C:\backup", "-n", "demo", "--zip"]


def test_import_supports_string_and_multiple_paths():
    fu = FakeUtils(responses=[(0, ""), (0, "")])
    core = Core(fu)

    assert core.import_(r"C:\a.mumudata", 2) is True
    assert fu.call_history[0]["command"] == ["-p", r"C:\a.mumudata", "-n", "2"]

    assert core.import_([r"C:\a.mumudata", r"D:\b.mumudata"], 3) is True
    assert fu.call_history[1]["command"] == ["-p", r"C:\a.mumudata", "-p", r"D:\b.mumudata", "-n", "3"]


def test_import_warns_for_invalid_number():
    fu = FakeUtils(responses=[(0, "")])
    core = Core(fu)
    with pytest.warns(UserWarning):
        assert core.import_(r"C:\a.mumudata", 0) is True
    assert fu.call_history[0]["command"] == ["-p", r"C:\a.mumudata", "-n", "1"]


def test_limit_cpu_validates_range_and_builds_command():
    fu = FakeUtils(responses=[(0, "")])
    core = Core(fu)
    assert core.limit_cpu(40) is True
    assert fu.call_history[0]["command"] == ["tool", "downcpu", "-c", "40"]

    with pytest.raises(ValueError):
        core.limit_cpu(-1)
    with pytest.raises(ValueError):
        core.limit_cpu(101)


def test_core_methods_raise_runtime_on_failures():
    core = Core(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        core.delete()
