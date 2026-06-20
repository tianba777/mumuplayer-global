import mumu.api.core.performance as performance_module
import mumu.api.core.simulation as simulation_module
import mumu.api.network.Network as network_module
import mumu.api.screen.screen as screen_module
from mumu.constant import GPU
from conftest import FakeUtils


class SettingRecorder:
    calls = []
    get_value = None

    def __init__(self, utils):
        self.utils = utils

    def set(self, **kwargs):
        SettingRecorder.calls.append(kwargs)
        return True

    def get(self, key):
        return SettingRecorder.get_value


def test_simulation_actions_build_commands(monkeypatch):
    fu = FakeUtils(responses=[(0, ""), (0, ""), (0, ""), (0, "")])
    sim = simulation_module.Simulation(fu)

    assert sim.mac_address("00:11:22:33:44:55") is True
    assert sim.imei("123456789012345") is True
    assert sim.imsi("460001234567890") is True
    assert sim.android_id("1234567890abcdef") is True
    assert fu.call_history[0]["command"] == ["-sk", "mac_address", "-sv", "00:11:22:33:44:55"]
    assert fu.call_history[1]["command"] == ["-sk", "imei", "-sv", "123456789012345"]
    assert fu.call_history[2]["command"] == ["-sk", "imsi", "-sv", "460001234567890"]
    assert fu.call_history[3]["command"] == ["-sk", "android_id", "-sv", "1234567890abcdef"]

    monkeypatch.setattr(simulation_module.PhoneNumber, "random", staticmethod(lambda: "18888888888"))
    fu2 = FakeUtils(responses=[(0, "")])
    sim2 = simulation_module.Simulation(fu2)
    assert sim2.phone_number() is True
    assert fu2.call_history[0]["command"] == ["-sk", "phone_number", "-sv", "18888888888"]


def test_simulation_gpu_model_modes(monkeypatch):
    SettingRecorder.calls = []
    monkeypatch.setattr(simulation_module, "Setting", SettingRecorder)
    sim = simulation_module.Simulation(FakeUtils())

    assert sim.gpu_model(top_model=True) is True
    assert sim.gpu_model(middle_model=True) is True
    assert sim.gpu_model(low_model=True) is True
    assert sim.gpu_model("RTX", top_model=False, middle_model=False, low_model=False) is True

    assert SettingRecorder.calls[0] == {"gpu_mode": "high", "gpu_model__custom": GPU.TOP_MODEL}
    assert SettingRecorder.calls[1] == {"gpu_mode": "middle", "gpu_model__custom": GPU.MIDDLE_MODEL}
    assert SettingRecorder.calls[2] == {"gpu_mode": "low", "gpu_model__custom": GPU.LOW_MODEL}
    assert SettingRecorder.calls[3] == {"gpu_mode": "custom", "gpu_model__custom": "RTX"}


def test_performance_methods(monkeypatch):
    SettingRecorder.calls = []
    monkeypatch.setattr(performance_module, "Setting", SettingRecorder)
    perf = performance_module.Performance(FakeUtils())

    assert perf.set(cpu_num=20, mem_gb=4) is True
    assert perf.cpu(cpu_num=0) is True
    assert perf.memory(mem_gb=0) is True
    assert perf.force_discrete_graphics(True) is True
    assert perf.renderer_strategy(dis=True) is True
    assert perf.renderer_strategy(perf=True) is True
    assert perf.renderer_strategy(auto=True) is True
    assert perf.disk_readonly(True) is True
    assert perf.disk_writable() is True

    assert SettingRecorder.calls[0]["performance_cpu__custom"] == 16
    assert SettingRecorder.calls[1]["performance_cpu__custom"] == 1
    assert SettingRecorder.calls[2]["performance_mem__custom"] == 1
    assert SettingRecorder.calls[4] == {"renderer_strategy": "dis"}
    assert SettingRecorder.calls[5] == {"renderer_strategy": "perf"}
    assert SettingRecorder.calls[6] == {"renderer_strategy": "auto"}
    assert SettingRecorder.calls[-1] == {"system_disk_readonly": False}


def test_network_bridge_card_parsing_and_setters(monkeypatch):
    SettingRecorder.calls = []
    monkeypatch.setattr(network_module, "Setting", SettingRecorder)
    net = network_module.Network(FakeUtils())

    SettingRecorder.get_value = "[ card1, card2 ]"
    assert net.get_bridge_card() == ["card1", "card2"]

    SettingRecorder.get_value = ["a", "b"]
    assert net.get_bridge_card() == ["a", "b"]

    SettingRecorder.get_value = None
    assert net.get_bridge_card() == []

    assert net.nat() is True
    assert net.bridge(True, "eth0") is True
    assert net.bridge_dhcp() is True
    assert net.bridge_static("1.1.1.1", "255.255.255.0", "1.1.1.254", "8.8.8.8", "1.1.1.1") is True

    assert SettingRecorder.calls[0] == {"net_bridge_open": False}
    assert SettingRecorder.calls[1] == {"net_bridge_open": True, "net_bridge_card": "eth0"}
    assert SettingRecorder.calls[2] == {"net_bridge_ip_mode": "dhcp"}
    assert SettingRecorder.calls[3] == {
        "net_bridge_ip_mode": "static",
        "net_bridge_ip_addr": "1.1.1.1",
        "net_bridge_subnet_mask": "255.255.255.0",
        "net_bridge_gateway": "1.1.1.254",
        "net_bridge_dns1": "8.8.8.8",
        "net_bridge_dns2": "1.1.1.1",
    }


def test_screen_setting_methods(monkeypatch):
    SettingRecorder.calls = []
    monkeypatch.setattr(screen_module, "Setting", SettingRecorder)
    screen = screen_module.Screen(FakeUtils())

    assert screen.resolution(100, 200) is True
    screen.resolution_mobile()
    screen.resolution_tablet()
    screen.resolution_ultrawide()
    assert screen.dpi(320) is True
    assert screen.brightness(101) is True
    assert screen.max_frame_rate(999) is True
    assert screen.dynamic_adjust_frame_rate(True, 15) is True
    assert screen.vertical_sync(False) is True
    assert screen.show_frame_rate(True) is True
    assert screen.window_auto_rotate(False) is True

    assert SettingRecorder.calls[0] == {"resolution_height__custom": 200, "resolution_width__custom": 100}
    assert {"resolution_dpi__custom": 480} in SettingRecorder.calls
    assert {"resolution_dpi__custom": 280} in SettingRecorder.calls
    assert {"resolution_dpi__custom": 400} in SettingRecorder.calls
    assert {"screen_brightness": 100} in SettingRecorder.calls
    assert {"max_frame_rate": 240} in SettingRecorder.calls
