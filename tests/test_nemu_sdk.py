import ctypes
from pathlib import Path

import numpy as np
import pytest

from mumu.api.screen.nemu_sdk import NemuSDK, NemuSDKError


class FakeCFunc:
    def __init__(self, impl):
        self.impl = impl
        self.argtypes = None
        self.restype = None

    def __call__(self, *args, **kwargs):
        return self.impl(*args, **kwargs)


class FakeDLL:
    def __init__(self, connect_impl, disconnect_impl, capture_impl):
        self.nemu_connect = FakeCFunc(connect_impl)
        self.nemu_disconnect = FakeCFunc(disconnect_impl)
        self.nemu_capture_display = FakeCFunc(capture_impl)


def test_resolve_paths_and_session_capture(monkeypatch, tmp_path):
    root = tmp_path / "MuMu"
    nx_main = root / "nx_main"
    nx_main.mkdir(parents=True, exist_ok=True)
    manager = nx_main / "MuMuManager.exe"
    manager.write_text("m", encoding="utf-8")
    dll = nx_main / "sdk" / "external_renderer_ipc.dll"
    dll.parent.mkdir(parents=True, exist_ok=True)
    dll.write_text("d", encoding="utf-8")

    state = {"disconnected": []}

    def connect_impl(path, index):
        assert Path(path) == root
        assert index == 0
        return 1

    def disconnect_impl(handle):
        state["disconnected"].append(handle)

    def capture_impl(handle, display_id, buffer_size, w_ptr, h_ptr, pixels):
        w = ctypes.cast(w_ptr, ctypes.POINTER(ctypes.c_int))
        h = ctypes.cast(h_ptr, ctypes.POINTER(ctypes.c_int))
        w[0] = 4
        h[0] = 3
        if buffer_size == 0:
            return 0
        for i in range(0, buffer_size, 4):
            pixels[i] = 10   # B
            pixels[i + 1] = 20  # G
            pixels[i + 2] = 30  # R
            pixels[i + 3] = 255
        return 0

    monkeypatch.setattr("mumu.api.screen.nemu_sdk.ctypes.WinDLL", lambda _: FakeDLL(connect_impl, disconnect_impl, capture_impl))

    sdk = NemuSDK(str(manager))
    assert sdk.install_root == root
    assert sdk.dll_path == dll

    session = sdk.create_session(vm_index=0)
    frame = session.capture_frame()
    assert frame.shape == (3, 4, 3)
    assert np.all(frame[0, 0] == np.array([10, 20, 30], dtype=np.uint8))
    session.close()
    assert state["disconnected"] == [1]


def test_connect_failure_raises(monkeypatch, tmp_path):
    root = tmp_path / "MuMu"
    nx_main = root / "nx_main"
    nx_main.mkdir(parents=True, exist_ok=True)
    manager = nx_main / "MuMuManager.exe"
    manager.write_text("m", encoding="utf-8")
    dll = nx_main / "sdk" / "external_renderer_ipc.dll"
    dll.parent.mkdir(parents=True, exist_ok=True)
    dll.write_text("d", encoding="utf-8")

    def connect_impl(path, index):
        return 0

    def disconnect_impl(handle):
        return None

    def capture_impl(handle, display_id, buffer_size, w_ptr, h_ptr, pixels):
        return 0

    monkeypatch.setattr("mumu.api.screen.nemu_sdk.ctypes.WinDLL", lambda _: FakeDLL(connect_impl, disconnect_impl, capture_impl))

    sdk = NemuSDK(str(manager))
    with pytest.raises(NemuSDKError, match="nemu_connect failed"):
        sdk.create_session(vm_index=0)
