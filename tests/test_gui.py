import builtins
import json
import threading
import time

import numpy as np
import pytest

import mumu.config as config
from mumu.api.screen.gui import Gui
from conftest import FakeUtils


class FakeRoot:
    def __init__(self):
        self._Mumu__vm_index = None

    def select(self, vm_id):
        self._Mumu__vm_index = str(vm_id)
        return self


def test_connect_parser_for_single_and_multi_styles():
    fu_single = FakeUtils(responses=[(0, '{"adb_host":"127.0.0.1","adb_port":16384}')]).set_vm_index("all")
    gui_single = Gui(fu_single)
    assert list(gui_single._Gui__connect() or []) == [("127.0.0.1", 16384, "all")]

    payload = json.dumps(
        {
            "2": {"adb_host": "127.0.0.1", "adb_port": 17002},
            "3": {"errcode": -1, "errmsg": "not running"},
        }
    )
    gui_multi = Gui(FakeUtils(responses=[(0, payload)]))
    assert list(gui_multi._Gui__connect() or []) == [("127.0.0.1", 17002, "2")]


def test_create_handle_raises_when_scrcpy_missing(monkeypatch):
    gui = Gui(FakeUtils())
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scrcpy":
            raise ImportError("missing")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="scrcpy backend requires"):
        gui.create_handle(lambda *_: None, backend="scrcpy")


def test_create_handle_rejects_invalid_backend():
    gui = Gui(FakeUtils())
    with pytest.raises(ValueError, match="backend must be one of"):
        gui.create_handle(lambda *_: None, backend="invalid")


def test_vm_handle_frame_uses_thread_local_mumu_context():
    fu = FakeUtils().set_mumu_root_object(FakeRoot())
    gui = Gui(fu)

    config.FRAME_CACHE["2"] = np.zeros((2, 2), dtype=np.uint8)
    config.FRAME_CACHE["3"] = np.zeros((2, 2), dtype=np.uint8)

    lock = threading.Lock()
    records = []
    done = threading.Event()

    def handle(frame, m):
        expected = m._Mumu__vm_index
        time.sleep(0.003)
        actual = m._Mumu__vm_index
        with lock:
            records.append((expected, actual))
            if len(records) >= 60:
                done.set()

    threading.Thread(target=gui._Gui__vm_handle_frame, args=(handle, "2"), daemon=True).start()
    threading.Thread(target=gui._Gui__vm_handle_frame, args=(handle, "3"), daemon=True).start()

    assert done.wait(timeout=2), "frame handler did not process enough frames in time"
    with lock:
        mismatches = [x for x in records if x[0] != x[1]]
    assert mismatches == []

    with config.FRAME_LOCK:
        config.FRAME_CACHE.pop("2", None)
        config.FRAME_CACHE.pop("3", None)


def test_locate_methods_find_expected_pattern():
    gui = Gui(FakeUtils())
    haystack = np.zeros((20, 20), dtype=np.uint8)
    haystack[10, 12] = 255
    needle = np.zeros((3, 3), dtype=np.uint8)
    needle[1, 1] = 255

    box = gui.locateOnScreen(haystack, needle, confidence=0.99)
    center = gui.locateCenterOnScreen(haystack, needle, confidence=0.99)
    all_boxes = gui.locateAllOnScreen(haystack, needle, confidence=0.99)

    assert box.left == 11
    assert box.top == 9
    assert center == (12, 10)
    assert len(all_boxes) >= 1
