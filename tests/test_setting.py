import json

import pytest

from mumu.api.setting.setting import Setting
from conftest import FakeUtils


def test_all_uses_correct_flag():
    fu = FakeUtils(responses=[(0, '{"a":"1"}'), (0, '{"b":"2"}')])
    s = Setting(fu)

    assert s.all() == {"a": "1"}
    assert fu.call_history[0]["command"] == ["-a"]

    assert s.all(all_writable=True) == {"b": "2"}
    assert fu.call_history[1]["command"] == ["-aw"]


def test_all_raises_on_failure():
    s = Setting(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        s.all()


def test_get_converts_basic_types_and_single_key():
    payload = json.dumps(
        {
            "num": "12",
            "enabled": "true",
            "disabled": "FALSE",
            "text": "abc",
            "list": ["a", "b"],
        }
    )
    fu = FakeUtils(responses=[(0, payload), (0, '{"enabled":"true"}')])
    s = Setting(fu)

    values = s.get("num", "enabled", "disabled", "text", "list")
    assert values["num"] == 12
    assert values["enabled"] is True
    assert values["disabled"] is False
    assert values["text"] == "abc"
    assert values["list"] == ["a", "b"]

    assert s.get("enabled") is True
    assert fu.call_history[0]["command"] == ["-k", "num", "-k", "enabled", "-k", "disabled", "-k", "text", "-k", "list"]


def test_get_raises_on_failure():
    s = Setting(FakeUtils(responses=[(1, "err")]))
    with pytest.raises(RuntimeError, match="err"):
        s.get("a")


def test_set_normalizes_keys_and_values():
    fu = FakeUtils(responses=[(0, "")])
    s = Setting(fu)

    assert s.set(window_size_fixed=True, gpu_model__custom=1, some___key=None) is True
    assert fu.call_history[0]["command"] == [
        "-k",
        "window_size_fixed",
        "-val",
        "true",
        "-k",
        "gpu_model.custom",
        "-val",
        "1",
        "-k",
        "some-key",
        "-val",
        "__null__",
    ]


def test_set_raises_on_failure():
    s = Setting(FakeUtils(responses=[(1, "boom")]))
    with pytest.raises(RuntimeError, match="boom"):
        s.set(k=1)


def test_set_by_json_requires_existing_file(tmp_path):
    s = Setting(FakeUtils())
    with pytest.raises(FileNotFoundError):
        s.set_by_json(str(tmp_path / "missing.json"))


def test_set_by_json_success(tmp_path):
    file_path = tmp_path / "a.json"
    file_path.write_text("{}", encoding="utf-8")
    fu = FakeUtils(responses=[(0, "")])
    s = Setting(fu)

    assert s.set_by_json(str(file_path)) is True
    assert fu.call_history[0]["command"] == ["-p", str(file_path)]


def test_equal_not_equal_and_conditional_set(monkeypatch):
    s = Setting(FakeUtils())

    monkeypatch.setattr(Setting, "get", lambda self, key: "x")
    monkeypatch.setattr(Setting, "set", lambda self, **kwargs: kwargs)

    assert s.equal("k", "x") is True
    assert s.not_equal("k", "y") is True
    assert s.equal_then_set("k", "x", "new") == {"k": "new"}
    assert s.not_equal_then_set("k", "old", None) == {"k": "old"}
    assert s.not_equal_then_set("k", "old", "new") == {"k": "new"}
