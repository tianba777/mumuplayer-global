import ctypes
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


class NemuSDKError(RuntimeError):
    pass


class NemuSDK:
    def __init__(self, mumu_manager_path: str):
        if not mumu_manager_path:
            raise NemuSDKError("MuMu manager path is empty")

        self.mumu_manager_path = Path(mumu_manager_path)
        if not self.mumu_manager_path.exists():
            raise NemuSDKError(f"MuMuManager.exe not found: {self.mumu_manager_path}")

        self.install_root = self._resolve_install_root(self.mumu_manager_path)
        self.dll_path = self._resolve_dll_path(self.mumu_manager_path)
        if self.dll_path is None:
            raise NemuSDKError("external_renderer_ipc.dll not found under MuMu install directory")

        self._dll = ctypes.WinDLL(str(self.dll_path))

        self._connect = self._dll.nemu_connect
        self._connect.argtypes = [ctypes.c_wchar_p, ctypes.c_int]
        self._connect.restype = ctypes.c_int

        self._disconnect = self._dll.nemu_disconnect
        self._disconnect.argtypes = [ctypes.c_int]
        self._disconnect.restype = None

        self._capture_display = self._dll.nemu_capture_display
        self._capture_display.argtypes = [
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        self._capture_display.restype = ctypes.c_int

    @staticmethod
    def _resolve_install_root(mumu_manager_path: Path) -> Path:
        parent = mumu_manager_path.parent
        if parent.name.lower() in {"shell", "nx_main"} and parent.parent.exists():
            return parent.parent
        return parent

    @staticmethod
    def _resolve_dll_path(mumu_manager_path: Path) -> Optional[Path]:
        manager_dir = mumu_manager_path.parent
        install_root = NemuSDK._resolve_install_root(mumu_manager_path)
        candidates = [
            manager_dir / "sdk" / "external_renderer_ipc.dll",
            manager_dir / "shell" / "sdk" / "external_renderer_ipc.dll",
            install_root / "sdk" / "external_renderer_ipc.dll",
            install_root / "shell" / "sdk" / "external_renderer_ipc.dll",
            install_root / "nx_main" / "sdk" / "external_renderer_ipc.dll",
            install_root / "nx_device" / "12.0" / "shell" / "sdk" / "external_renderer_ipc.dll",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def create_session(self, vm_index: int, display_id: int = 0):
        handle = self._connect(str(self.install_root), int(vm_index))
        if handle <= 0:
            raise NemuSDKError(f"nemu_connect failed for vm_index={vm_index}")
        return NemuSession(self, handle=handle, vm_index=vm_index, display_id=display_id)

    def disconnect(self, handle: int):
        self._disconnect(handle)

    def capture_display_size(self, handle: int, display_id: int = 0):
        width = ctypes.c_int(0)
        height = ctypes.c_int(0)
        ret = self._capture_display(handle, display_id, 0, ctypes.byref(width), ctypes.byref(height), None)
        if ret != 0 or width.value <= 0 or height.value <= 0:
            raise NemuSDKError(
                f"nemu_capture_display(size) failed: ret={ret}, width={width.value}, height={height.value}"
            )
        return width.value, height.value

    def capture_display(self, handle: int, display_id: int, buffer_size: int, pixels, width: int, height: int):
        w = ctypes.c_int(width)
        h = ctypes.c_int(height)
        ret = self._capture_display(handle, display_id, buffer_size, ctypes.byref(w), ctypes.byref(h), pixels)
        if ret != 0:
            raise NemuSDKError(f"nemu_capture_display(frame) failed: ret={ret}")
        return w.value, h.value


class NemuSession:
    def __init__(self, sdk: NemuSDK, handle: int, vm_index: int, display_id: int = 0):
        self.sdk = sdk
        self.handle = handle
        self.vm_index = vm_index
        self.display_id = display_id
        self.width = 0
        self.height = 0
        self.buffer_size = 0
        self.pixels = None
        self._reallocate_buffer()

    def _reallocate_buffer(self):
        self.width, self.height = self.sdk.capture_display_size(self.handle, self.display_id)
        self.buffer_size = self.width * self.height * 4
        self.pixels = (ctypes.c_ubyte * self.buffer_size)()

    def capture_frame(self):
        width, height = self.sdk.capture_display(
            self.handle,
            self.display_id,
            self.buffer_size,
            self.pixels,
            self.width,
            self.height,
        )
        if width != self.width or height != self.height:
            self._reallocate_buffer()
            width, height = self.sdk.capture_display(
                self.handle,
                self.display_id,
                self.buffer_size,
                self.pixels,
                self.width,
                self.height,
            )

        arr = np.ctypeslib.as_array(self.pixels).reshape((height, width, 4))
        return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

    def close(self):
        self.sdk.disconnect(self.handle)
