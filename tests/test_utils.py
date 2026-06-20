from types import SimpleNamespace

import mumu.config as config
from mumu.utils import utils


def test_setters_return_self():
    u = utils()
    assert u.set_vm_index("1") is u
    assert u.set_operate("control") is u
    assert u.set_mumu_root_object(object()) is u
    assert u.set_mumu_path("MuMuManager.exe") is u
    assert u.set_adb_path("adb.exe") is u


def test_run_command_builds_full_mumu_command(monkeypatch):
    recorded = {}

    def fake_run(cmd, shell, check, stdout, stderr, encoding):
        recorded["cmd"] = cmd
        recorded["shell"] = shell
        recorded["check"] = check
        return SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr("mumu.utils.subprocess.run", fake_run)
    config.MUMU_PATH = "MuMuManager.exe"

    u = utils().set_mumu_path("MuMuManager.exe").set_operate(["control", "app"]).set_vm_index("3")
    code, out = u.run_command(["launch"])

    assert code == 0
    assert out == "ok"
    assert recorded["shell"] is False
    assert recorded["check"] is False
    assert recorded["cmd"] == ["MuMuManager.exe", "control", "app", "-v", "3", "launch"]


def test_run_command_with_mumu_false_passes_command_as_is(monkeypatch):
    recorded = {}

    def fake_run(cmd, shell, check, stdout, stderr, encoding):
        recorded["cmd"] = cmd
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("mumu.utils.subprocess.run", fake_run)

    code, out = utils().run_command(["echo", "hello"], mumu=False)
    assert code == 0
    assert out == ""
    assert recorded["cmd"] == ["echo", "hello"]


def test_run_command_uses_stderr_when_stdout_empty(monkeypatch):
    def fake_run(cmd, shell, check, stdout, stderr, encoding):
        return SimpleNamespace(returncode=1, stdout="", stderr="boom\n")

    monkeypatch.setattr("mumu.utils.subprocess.run", fake_run)

    code, out = utils().run_command(["x"], mumu=False)
    assert code == 1
    assert out == "boom"


def test_run_command_handles_oserror(monkeypatch):
    def fake_run(cmd, shell, check, stdout, stderr, encoding):
        raise OSError("not found")

    monkeypatch.setattr("mumu.utils.subprocess.run", fake_run)

    code, out = utils().run_command(["x"], mumu=False)
    assert code == 1
    assert "not found" in out
