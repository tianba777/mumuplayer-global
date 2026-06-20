from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

import pytest

import mumu.config as config


class FakeUtils:
    def __init__(self, responses: Iterable[Any] | None = None):
        self.responses = list(responses or [])
        self.call_history = []
        self.operate_history = []
        self._operate = None
        self._vm_id = None
        self._root_object = None
        self._mumu_path = None
        self._adb_path = None

    def set_operate(self, operate):
        self._operate = operate
        self.operate_history.append(operate)
        return self

    def set_vm_index(self, vm_index):
        self._vm_id = vm_index
        return self

    def get_vm_id(self):
        return self._vm_id

    def set_mumu_root_object(self, root_object):
        self._root_object = root_object
        return self

    def get_mumu_root_object(self):
        return self._root_object

    def set_mumu_path(self, mumu_path):
        self._mumu_path = mumu_path
        return self

    def get_mumu_path(self):
        return self._mumu_path

    def set_adb_path(self, adb_path):
        self._adb_path = adb_path
        return self

    def get_adb_path(self):
        return self._adb_path

    def run_command(self, command, mumu=True):
        self.call_history.append(
            {
                "command": command,
                "mumu": mumu,
                "operate": self._operate,
            }
        )
        if not self.responses:
            return 0, ""

        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        if callable(response):
            try:
                return response(command, mumu, self)
            except TypeError:
                return response(command, mumu)
        return response


@pytest.fixture(autouse=True)
def reset_global_config():
    snapshot = {
        "MUMU_PATH": config.MUMU_PATH,
        "VM_INDEX": config.VM_INDEX,
        "OPERATE": config.OPERATE,
        "ADB_PATH": config.ADB_PATH,
    }
    config.FRAME_CACHE.clear()
    config.FRAME_UPDATE_TIME.clear()
    yield
    config.MUMU_PATH = snapshot["MUMU_PATH"]
    config.VM_INDEX = snapshot["VM_INDEX"]
    config.OPERATE = snapshot["OPERATE"]
    config.ADB_PATH = snapshot["ADB_PATH"]
    config.FRAME_CACHE.clear()
    config.FRAME_UPDATE_TIME.clear()


@pytest.fixture
def fake_utils():
    return FakeUtils()


@pytest.fixture
def fake_manager_path(tmp_path: Path):
    path = tmp_path / "MuMuManager.exe"
    path.write_text("fake manager", encoding="utf-8")
    return str(path)
