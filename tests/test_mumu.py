import threading
from pathlib import Path

import pytest

import mumu.config as config
from mumu.api.screen.gui import Gui
from mumu.mumu import Mumu


def test_init_with_explicit_path_updates_config(fake_manager_path):
    Mumu(fake_manager_path)
    assert config.MUMU_PATH == fake_manager_path
    assert config.ADB_PATH == str(Path(fake_manager_path).with_name("adb.exe"))


def test_init_rejects_missing_path(tmp_path):
    missing = tmp_path / "MuMuManager.exe"
    with pytest.raises(RuntimeError, match="not found"):
        Mumu(str(missing))


def test_init_rejects_non_manager_exe(tmp_path):
    wrong_exe = tmp_path / "MuMuNxMain.exe"
    wrong_exe.write_text("fake", encoding="utf-8")
    with pytest.raises(RuntimeError, match="must point to MuMuManager.exe"):
        Mumu(str(wrong_exe))


def test_init_prefers_existing_cached_path(tmp_path):
    cached = tmp_path / "MuMuManager.exe"
    cached.write_text("fake", encoding="utf-8")
    config.MUMU_PATH = str(cached)

    Mumu()
    assert config.MUMU_PATH == str(cached)


def test_init_scans_default_paths(monkeypatch, tmp_path):
    p1 = tmp_path / "MuMuManager.exe"
    p1.write_text("fake", encoding="utf-8")
    monkeypatch.setattr(Mumu, "_Mumu__default_manager_paths", (str(p1), r"C:\not-exist\MuMuManager.exe"))

    Mumu()
    assert config.MUMU_PATH == str(p1)


def test_select_supports_int_str_iterables_and_args(fake_manager_path):
    mm = Mumu(fake_manager_path)

    mm.select(1)
    assert mm.generate_utils().get_vm_id() == "1"

    mm.select("2")
    assert mm.generate_utils().get_vm_id() == "2"

    mm.select([1, 1, 2])
    assert mm.generate_utils().get_vm_id() == "1,2"

    mm.select((3, 4, 3))
    assert mm.generate_utils().get_vm_id() == "3,4"

    mm.select([1, 2], 3, 2)
    assert mm.generate_utils().get_vm_id() == "1,2,3"


def test_select_invalid_type_raises(fake_manager_path):
    mm = Mumu(fake_manager_path)
    with pytest.raises(TypeError):
        mm.select(3.14)
    with pytest.raises(TypeError):
        mm.select(3.14, 1)


def test_select_none_and_all_choose_all(fake_manager_path):
    mm = Mumu(fake_manager_path)
    mm.select()
    assert mm.generate_utils().get_vm_id() == "all"
    mm.all()
    assert mm.generate_utils().get_vm_id() == "all"


def test_generate_utils_carries_vm_root_and_paths(fake_manager_path):
    mm = Mumu(fake_manager_path).select(5)
    u = mm.generate_utils()
    assert u.get_vm_id() == "5"
    assert u.get_mumu_root_object() is mm
    assert u.get_mumu_path() == fake_manager_path
    assert u.get_adb_path() == str(Path(fake_manager_path).with_name("adb.exe"))


def test_vm_index_is_thread_local(fake_manager_path):
    mm = Mumu(fake_manager_path)
    results = {}
    lock = threading.Lock()
    done = threading.Event()

    def worker(name, vm):
        for _ in range(5):
            mm.select(vm)
            current = mm.generate_utils().get_vm_id()
            with lock:
                results.setdefault(name, []).append(current)
        if len(results) == 2:
            done.set()

    t1 = threading.Thread(target=worker, args=("t1", 1))
    t2 = threading.Thread(target=worker, args=("t2", 2))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert done.is_set()
    assert set(results["t1"]) == {"1"}
    assert set(results["t2"]) == {"2"}


def test_instances_with_different_paths_do_not_conflict(tmp_path):
    path1 = tmp_path / "a" / "MuMuManager.exe"
    path1.parent.mkdir(parents=True, exist_ok=True)
    path1.write_text("fake", encoding="utf-8")

    path2 = tmp_path / "b" / "MuMuManager.exe"
    path2.parent.mkdir(parents=True, exist_ok=True)
    path2.write_text("fake", encoding="utf-8")

    m1 = Mumu(str(path1)).select(1)
    m2 = Mumu(str(path2)).select(2)

    # Global path now points to m2, but m1 utilities should still use path1.
    assert config.MUMU_PATH == str(path2)
    assert m1.generate_utils().get_mumu_path() == str(path1)
    assert m2.generate_utils().get_mumu_path() == str(path2)
    assert m1.generate_utils().get_vm_id() == "1"
    assert m2.generate_utils().get_vm_id() == "2"


def test_copy_keeps_vm_index_without_sharing_context(fake_manager_path):
    import copy

    m1 = Mumu(fake_manager_path).select(1)
    m2 = copy.copy(m1)

    assert m2.generate_utils().get_vm_id() == "1"
    m2.select(2)
    assert m2.generate_utils().get_vm_id() == "2"
    assert m1.generate_utils().get_vm_id() == "1"


def test_auto_property_returns_gui(fake_manager_path):
    mm = Mumu(fake_manager_path).select(0)
    assert isinstance(mm.auto, Gui)
