import os
import json
import glob
import ctypes
import subprocess


class Cleanup:

    TELEMETRY_DOMAINS = [
        "shence-api.mumu.163.com",
        "report-api.mumuplayer.com",
        "report.mumu.nie.netease.com",
        "api.mumuglobal.com",
        "user-center.mumuplayer.com",
        "pro-api.mumuplayer.com",
        "feedback-system.webapp.easebar.com",
        "fcount-api.webapp.163.com",
        "fcount-api.webapp.easebar.com",
        "fp.ps.netease.com",
        "event.sc.gearupportal.com",
        "adl.guinfra.com",
        "api-event.nrd.nie.163.com",
        "api.nrd.nie.163.com",
        "api-pro.mumu.163.com",
    ]

    def __init__(self, install_root):
        self._root = install_root
        self._results = []

    def _log(self, ok, msg):
        self._results.append((ok, msg))

    def _rename_bak(self, path):
        bak = path + ".bak"
        if os.path.exists(bak):
            self._log(True, f"already done: {os.path.basename(path)}")
            return True
        if os.path.exists(path):
            try:
                os.rename(path, bak)
                self._log(True, f"renamed: {os.path.basename(path)} -> .bak")
                return True
            except OSError as e:
                self._log(False, f"failed to rename {os.path.basename(path)}: {e}")
                return False
        self._log(True, f"not found: {os.path.basename(path)}")
        return True

    def _rmtree(self, path):
        if not os.path.exists(path):
            self._log(True, f"not found: {path.replace(self._root, '')}")
            return True
        try:
            import shutil
            shutil.rmtree(path)
            self._log(True, f"removed: {path.replace(self._root, '')}")
            return True
        except OSError as e:
            self._log(False, f"failed to remove {path.replace(self._root, '')}: {e}")
            return False

    def disable_telemetry_dlls(self):
        paths = [
            os.path.join(self._root, "nx_main", "nemu-statistics.dll"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "nemu-statistics.dll"),
            os.path.join(self._root, ".backup", "main", "nemu-statistics.dll"),
            os.path.join(self._root, "nx_main", "sentry.dll"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "sentry.dll"),
            os.path.join(self._root, ".backup", "main", "sentry.dll"),
        ]
        for p in paths:
            self._rename_bak(p)
        return self

    def disable_telemetry_exes(self):
        paths = [
            os.path.join(self._root, "nx_device", "12.0", "shell", "MuMuStatisticsReporter.exe"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "MuMuNxCrashReporter.exe"),
            os.path.join(self._root, "nx_main", "crashpad_handler.exe"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "crashpad_handler.exe"),
            os.path.join(self._root, "nx_main", "MuMuNxUpdater.exe"),
            os.path.join(self._root, "backup", "MuMuNxUpdater.exe"),
        ]
        for p in paths:
            self._rename_bak(p)
        return self

    def remove_ad_message_center(self):
        dirs = [
            os.path.join(self._root, "nx_main", "resources", "dist", "message_center"),
            os.path.join(self._root, "nx_main", "resources", "dist", "nx", "message_center"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "resources", "dist", "message_center"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "resources", "dist", "nx", "message_center"),
        ]
        for d in dirs:
            self._rmtree(d)
        return self

    def clean_crash_files(self):
        dirs = [
            os.path.join(self._root, "nx_main", "nxmain-crash-files"),
            os.path.join(self._root, "nx_main", "nxupdater-crash-files"),
            os.path.join(self._root, "nx_device", "12.0", "shell", "crash-files"),
        ]
        for d in dirs:
            self._rmtree(d)
        return self

    def clean_device_id(self):
        fcount = os.path.join(self._root, "nx_main", "fcountData.ini")
        if os.path.exists(fcount):
            try:
                with open(fcount, "w", encoding="utf-8") as f:
                    f.write("[runtime_data]\ndevice_id=\ninit_timestamp=0\n")
                self._log(True, "fcountData.ini cleared")
            except OSError as e:
                self._log(False, f"failed to clear fcountData.ini: {e}")
        else:
            self._log(True, "fcountData.ini not found")
        return self

    def clean_vm_report_timestamps(self):
        vms_path = os.path.join(self._root, "vms")
        if not os.path.isdir(vms_path):
            self._log(True, "vms directory not found")
            return self
        count = 0
        for vm_dir in os.listdir(vms_path):
            cfg = os.path.join(vms_path, vm_dir, "configs", "customer_config.json")
            if not os.path.isfile(cfg):
                continue
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "nxdevice" in data and "report" in data["nxdevice"]:
                    data["nxdevice"]["report"] = {}
                    with open(cfg, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    count += 1
            except (json.JSONDecodeError, OSError):
                pass
        self._log(True, f"cleaned report timestamps in {count} VMs")
        return self

    def disable_remote_telemetry(self):
        paths = [
            os.path.join(self._root, "nx_main", "MuMuRemoteBackend.exe"),
            os.path.join(self._root, "nx_main", "MumuRemoteHealthd.exe"),
            os.path.join(self._root, "nx_main", "nemu-remote.dll"),
        ]
        for p in paths:
            self._rename_bak(p)
        return self

    def block_telemetry_hosts(self):
        hosts_path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"),
                                  "System32", "drivers", "etc", "hosts")
        marker = "# MuMuPlayer telemetry block"
        entries = [f"0.0.0.0 {d}" for d in self.TELEMETRY_DOMAINS]
        block = marker + "\n" + "\n".join(entries) + "\n"

        try:
            content = ""
            if os.path.exists(hosts_path):
                with open(hosts_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            if marker in content:
                import re
                content = re.sub(
                    rf"{re.escape(marker)}.*?(?=\n\s*\n|\Z)",
                    block.rstrip(),
                    content,
                    flags=re.DOTALL,
                )
            else:
                content = content.rstrip() + "\n\n" + block

            with open(hosts_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log(True, f"hosts blocked ({len(entries)} domains)")
        except PermissionError:
            self._log(False, "hosts file requires admin privileges")
        except OSError as e:
            self._log(False, f"failed to update hosts: {e}")
        return self

    def stop_processes(self):
        procs = [
            "MuMuNxMain", "MuMuNxService", "MuMuManager", "MuMuNxDevice",
            "MuMuStatisticsReporter", "MuMuNxCrashReporter", "MuMuRemoteBackend",
            "MumuRemoteHealthd", "MuMuRemoteService", "MuMuNxUpdater",
        ]
        for p in procs:
            try:
                subprocess.run(
                    ["taskkill", "/f", "/im", f"{p}.exe"],
                    capture_output=True, timeout=5,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        try:
            subprocess.run(["sc", "stop", "MuMuRemoteService"],
                           capture_output=True, timeout=5)
            subprocess.run(["sc", "config", "MuMuRemoteService", "start=", "disabled"],
                           capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        self._log(True, "processes stopped")
        return self

    def run_all(self, block_hosts=True, disable_remote=True, verbose=True):
        self._results = []

        self.stop_processes()
        self.disable_telemetry_dlls()
        self.disable_telemetry_exes()
        self.remove_ad_message_center()
        self.clean_crash_files()
        self.clean_device_id()
        self.clean_vm_report_timestamps()

        if disable_remote:
            self.disable_remote_telemetry()
        if block_hosts:
            self.block_telemetry_hosts()

        if verbose:
            for ok, msg in self._results:
                prefix = "[OK]" if ok else "[FAIL]"
                print(f"  {prefix} {msg}")
            ok_count = sum(1 for ok, _ in self._results if ok)
            print(f"\nResult: {ok_count}/{len(self._results)} passed")

        return self._results

    def restore_all(self, verbose=True):
        self._results = []
        for root, dirs, files in os.walk(self._root):
            for f in files:
                if f.endswith(".bak"):
                    bak_path = os.path.join(root, f)
                    orig_path = bak_path[:-4]
                    if not os.path.exists(orig_path):
                        try:
                            os.rename(bak_path, orig_path)
                            self._log(True, f"restored: {f[:-4]}")
                        except OSError as e:
                            self._log(False, f"failed to restore {f[:-4]}: {e}")

        if verbose:
            for ok, msg in self._results:
                prefix = "[OK]" if ok else "[FAIL]"
                print(f"  {prefix} {msg}")
            if not self._results:
                print("  Nothing to restore.")

        return self._results
