import json
import warnings

import pytest

import mumu.config as config
from mumu.api.adb.Adb import Adb
from conftest import FakeUtils


def make_adb(responses=None):
    fu = FakeUtils(responses=responses)
    return Adb(fu), fu


def test_get_connect_info_single_root_style():
    adb, fu = make_adb([(0, '{"adb_host":"127.0.0.1","adb_port":16384}')])
    assert adb.get_connect_info() == ("127.0.0.1", 16384)
    assert fu.operate_history[-1] == "adb"


def test_get_connect_info_multi_vm_style():
    payload = json.dumps(
        {
            "2": {"adb_host": "127.0.0.1", "adb_port": 16385},
            "3": {"errcode": -1, "errmsg": "not running"},
        }
    )
    adb, _ = make_adb([(0, payload)])
    assert adb.get_connect_info() == {"2": ("127.0.0.1", 16385), "3": (None, None)}


def test_get_connect_info_invalid_json_returns_none_tuple():
    adb, _ = make_adb([(0, "not-json")])
    assert adb.get_connect_info() == (None, None)


def test_adb_input_commands_are_wrapped_as_single_c_command():
    adb, fu = make_adb([(0, ""), (0, ""), (0, ""), (0, ""), (0, "")])

    assert adb.click(1, 2) is True
    assert adb.swipe(1, 2, 3, 4, 5) is True
    assert adb.input_text("hello") is True
    assert adb.key_event(3) is True
    assert adb.clear("com.demo.app") is True

    commands = [row["command"] for row in fu.call_history]
    assert commands == [
        ["-c", "shell input tap 1 2"],
        ["-c", "shell input swipe 1 2 3 4 5"],
        ["-c", "input_text hello"],
        ["-c", "shell input keyevent 3"],
        ["-c", "shell pm clear com.demo.app"],
    ]


def test_adb_command_failure_uses_fallback_error_message():
    adb, _ = make_adb([(1, "")])
    with pytest.raises(RuntimeError, match="adb command failed: shell input tap 9 9"):
        adb.click(9, 9)


def test_private_connect_parses_entries():
    single, _ = make_adb([(0, '{"adb_host":"127.0.0.1","adb_port":16384}')])
    assert list(single._Adb__connect()) == [("127.0.0.1", 16384)]

    multi_payload = json.dumps(
        {"1": {"adb_host": "127.0.0.1", "adb_port": 17001}, "2": {"errcode": -1, "errmsg": "x"}}
    )
    multi, _ = make_adb([(0, multi_payload)])
    assert list(multi._Adb__connect()) == [("127.0.0.1", 17001)]


def test_push_missing_source_raises(tmp_path):
    adb, _ = make_adb()
    config.ADB_PATH = str(tmp_path / "adb.exe")
    with pytest.raises(FileNotFoundError, match="File not found"):
        adb.push(str(tmp_path / "missing.txt"), "/sdcard/test.txt")


def test_push_missing_adb_binary_raises(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")

    adb, _ = make_adb()
    config.ADB_PATH = str(tmp_path / "missing-adb.exe")
    with pytest.raises(FileNotFoundError, match="adb not found"):
        adb.push(str(src), "/sdcard/test.txt")


def test_push_raises_when_no_connections(tmp_path, monkeypatch):
    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    adb_path = tmp_path / "adb.exe"
    adb_path.write_text("adb", encoding="utf-8")
    config.ADB_PATH = str(adb_path)

    adb, _ = make_adb()
    monkeypatch.setattr(adb, "_Adb__connect", lambda: iter(()))
    with pytest.raises(RuntimeError, match="No available adb connections found"):
        adb.push(str(src), "/sdcard/test.txt")


def test_push_calls_local_adb_for_each_connection(tmp_path, monkeypatch):
    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    adb_path = tmp_path / "adb.exe"
    adb_path.write_text("adb", encoding="utf-8")
    config.ADB_PATH = str(adb_path)

    adb, fu = make_adb([(0, ""), (0, "")])
    monkeypatch.setattr(adb, "_Adb__connect", lambda: iter([("127.0.0.1", 1001), ("127.0.0.1", 1002)]))

    assert adb.push(str(src), "/sdcard/test.txt") is True
    assert fu.call_history[0]["mumu"] is False
    assert fu.call_history[0]["command"] == [str(adb_path), "-s", "127.0.0.1:1001", "push", str(src), "/sdcard/test.txt"]
    assert fu.call_history[1]["command"] == [str(adb_path), "-s", "127.0.0.1:1002", "push", str(src), "/sdcard/test.txt"]


def test_push_warns_on_single_device_failure(tmp_path, monkeypatch):
    src = tmp_path / "a.txt"
    src.write_text("x", encoding="utf-8")
    adb_path = tmp_path / "adb.exe"
    adb_path.write_text("adb", encoding="utf-8")
    config.ADB_PATH = str(adb_path)

    adb, _ = make_adb([(1, "failed")])
    monkeypatch.setattr(adb, "_Adb__connect", lambda: iter([("127.0.0.1", 1001)]))

    with pytest.warns(UserWarning, match="failed"):
        assert adb.push(str(src), "/sdcard/test.txt") is True


def test_push_download_builds_download_path(monkeypatch):
    adb, _ = make_adb()
    recorded = {}

    def fake_push(src, path):
        recorded["src"] = src
        recorded["path"] = path
        return True

    monkeypatch.setattr(adb, "push", fake_push)
    assert adb.push_download("C:\\tmp\\a.txt", "new.txt") is True
    assert recorded["path"] == "/sdcard/Download/new.txt"


def test_pull_requires_adb_path(tmp_path):
    adb, _ = make_adb()
    config.ADB_PATH = str(tmp_path / "missing-adb.exe")
    with pytest.raises(FileNotFoundError):
        adb.pull("/sdcard/a.txt", str(tmp_path / "a.txt"))


def test_pull_raises_when_no_connections(tmp_path, monkeypatch):
    adb_path = tmp_path / "adb.exe"
    adb_path.write_text("adb", encoding="utf-8")
    config.ADB_PATH = str(adb_path)

    adb, _ = make_adb()
    monkeypatch.setattr(adb, "_Adb__connect", lambda: iter(()))
    with pytest.raises(RuntimeError, match="No available adb connections found"):
        adb.pull("/sdcard/a.txt", str(tmp_path / "a.txt"))


def test_pull_calls_local_adb_for_each_connection(tmp_path, monkeypatch):
    adb_path = tmp_path / "adb.exe"
    adb_path.write_text("adb", encoding="utf-8")
    config.ADB_PATH = str(adb_path)

    adb, fu = make_adb([(0, ""), (0, "")])
    monkeypatch.setattr(adb, "_Adb__connect", lambda: iter([("127.0.0.1", 2001), ("127.0.0.1", 2002)]))

    assert adb.pull("/sdcard/a.txt", str(tmp_path / "a.txt")) is True
    assert fu.call_history[0]["command"] == [
        str(adb_path),
        "-s",
        "127.0.0.1:2001",
        "pull",
        "/sdcard/a.txt",
        str(tmp_path / "a.txt"),
    ]
    assert fu.call_history[1]["command"][2] == "127.0.0.1:2002"
