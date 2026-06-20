#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import statistics
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np

from mumu.api.screen.nemu_sdk import NemuSDK
from mumu.mumu import Mumu


def _resolve_serial(connect_info):
    if isinstance(connect_info, tuple) and len(connect_info) == 2 and connect_info[0] and connect_info[1]:
        return f"{connect_info[0]}:{connect_info[1]}"
    if isinstance(connect_info, dict):
        for _, value in connect_info.items():
            if value and value[0] and value[1]:
                return f"{value[0]}:{value[1]}"
    return None


def _create_adb_capture(mm):
    utils = mm.generate_utils()
    adb_path = utils.get_adb_path()
    connect_info = mm.adb.get_connect_info()
    serial = _resolve_serial(connect_info)
    if not serial:
        raise RuntimeError("ADB serial not found. Ensure emulator is running and adb is connected.")

    def capture():
        proc = subprocess.run(
            [adb_path, "-s", serial, "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", errors="ignore").strip())
        data = np.frombuffer(proc.stdout, dtype=np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if frame is None:
            raise RuntimeError("Failed to decode adb screencap output")
        return frame

    return capture


def _create_sdk_capture(mm, vm_index):
    utils = mm.generate_utils()
    sdk = NemuSDK(utils.get_mumu_path())
    session = sdk.create_session(vm_index=vm_index)

    def capture():
        return session.capture_frame()

    return capture, session


def benchmark(backend, vm_index, manager_path, duration, warmup, save_sample):
    mm = Mumu(manager_path).select(vm_index)
    capture = None
    session = None

    if backend == "mumu_sdk":
        capture, session = _create_sdk_capture(mm, vm_index)
    elif backend == "adb_screencap":
        capture = _create_adb_capture(mm)
    else:
        raise ValueError("Unsupported backend")

    try:
        for _ in range(warmup):
            capture()

        latencies_ms = []
        frame_count = 0
        start = time.perf_counter()
        last_frame = None
        while True:
            now = time.perf_counter()
            if now - start >= duration:
                break

            t0 = time.perf_counter()
            last_frame = capture()
            t1 = time.perf_counter()

            frame_count += 1
            latencies_ms.append((t1 - t0) * 1000)

        elapsed = time.perf_counter() - start
        if frame_count == 0:
            raise RuntimeError("No frame captured during benchmark window.")

        lat_sorted = sorted(latencies_ms)

        def pctl(p):
            idx = int((len(lat_sorted) - 1) * p)
            return lat_sorted[idx]

        fps = frame_count / elapsed
        print(f"backend      : {backend}")
        print(f"vm_index     : {vm_index}")
        print(f"duration_s   : {elapsed:.3f}")
        print(f"frames       : {frame_count}")
        print(f"fps          : {fps:.2f}")
        print(f"latency_mean : {statistics.mean(latencies_ms):.2f} ms")
        print(f"latency_p50  : {pctl(0.50):.2f} ms")
        print(f"latency_p95  : {pctl(0.95):.2f} ms")
        print(f"latency_max  : {max(latencies_ms):.2f} ms")

        if save_sample:
            if last_frame is None:
                raise RuntimeError("No frame to save.")
            sample_path = Path(save_sample).resolve()
            sample_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(sample_path), last_frame)
            print(f"sample_saved : {sample_path}")
    finally:
        if session is not None:
            session.close()


def main():
    parser = argparse.ArgumentParser(description="MuMu screenshot speed benchmark")
    parser.add_argument("--backend", choices=["mumu_sdk", "adb_screencap"], default="mumu_sdk")
    parser.add_argument("--vm-index", type=int, default=0)
    parser.add_argument("--manager-path", default=None, help="Path to MuMuManager.exe")
    parser.add_argument("--duration", type=float, default=10.0, help="Benchmark duration in seconds")
    parser.add_argument("--warmup", type=int, default=30, help="Warmup frame count")
    parser.add_argument("--save-sample", default=None, help="Save the last frame to this path")
    args = parser.parse_args()

    benchmark(
        backend=args.backend,
        vm_index=args.vm_index,
        manager_path=args.manager_path,
        duration=args.duration,
        warmup=args.warmup,
        save_sample=args.save_sample,
    )


if __name__ == "__main__":
    main()
