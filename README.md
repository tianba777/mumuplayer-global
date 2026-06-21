# MuMu Player Global - Python API

基于 [mumu-python-api](https://github.com/openDreamStudioResearch/mumu-python-api) 适配的 **MuMu Player 海外版 (Global)** Python API。

> A fork of [mumu-python-api](https://github.com/openDreamStudioResearch/mumu-python-api) adapted for **MuMu Player Global** (international/overseas edition).

---

## 适配说明 / Adaptation Notes

原项目仅支持国内版 MuMu Player 12，本项目在其基础上进行了以下适配：

| 改动项 | 说明 |
|--------|------|
| 默认安装路径 | 新增 `MuMuPlayer\nx_main\MuMuManager.exe` 路径自动检测（C盘和D盘） |
| DNS 默认值 | 桥接静态网络的 DNS2 从 `114.114.114.114`（国内）改为 `8.8.4.4`（通用） |

### 兼容性验证

| 功能模块 | 状态 |
|----------|------|
| MuMuManager CLI 命令 | 完全兼容 |
| 模拟器配置读写 (Setting) | 完全兼容 |
| ADB 操作 | 完全兼容 |
| NemuSDK 截图 DLL | 完全兼容 |
| 多实例管理 | 完全兼容 |

### 安装路径对照

| 版本 | 默认安装路径 |
|------|-------------|
| 国内版 MuMu Player 12 | `C:\Program Files\Netease\MuMu Player 12\shell\MuMuManager.exe` |
| 国内版 MuMu (旧版) | `C:\Program Files\Netease\MuMu\nx_main\MuMuManager.exe` |
| **海外版 MuMu Player Global** | **`C:\Program Files\Netease\MuMuPlayer\nx_main\MuMuManager.exe`** |

---

## 快速开始 / Quick Start

### 安装

```bash
pip install mumu-python-api-wlkjyy
```

如需 GUI 自动化（OpenCV + scrcpy）：

```bash
pip install "mumu-python-api-wlkjyy[auto]"
```

### 使用

```python
from mumu.mumu import Mumu

# 海外版会自动检测，无需手动指定路径
mumu = Mumu()

# 选择模拟器实例
mumu.select(0)

# 读取版本号
print(mumu.setting.get('product_version'))

# 启动模拟器
mumu.power.start()

# 安装应用
mumu.app.install(r'C:\your_app.apk')
```

如果自动检测失败，可手动指定路径：

```python
mumu = Mumu(r'C:\Program Files\Netease\MuMuPlayer\nx_main\MuMuManager.exe')
```

---

## API 参考

本项目完整保留了原项目的所有 API，详见下方分类。

### 电源类 (power)

```python
mumu.select(0).power.start()        # 启动
mumu.select(0).power.shutdown()      # 关闭
mumu.select(0).power.restart()       # 重启
```

### 应用类 (app)

```python
mumu.select(0).app.install(r'C:\app.apk')          # 安装
mumu.select(0).app.uninstall('com.example.app')     # 卸载
mumu.select(0).app.launch('com.example.app')        # 启动应用
mumu.select(0).app.close('com.example.app')         # 关闭应用
mumu.select(0).app.get_installed()                  # 已安装列表
mumu.select(0).app.exists('com.example.app')        # 判断是否安装
mumu.select(0).app.state('com.example.app')         # 应用状态
```

### ADB 类 (adb)

```python
mumu.select(0).adb.get_connect_info()               # ADB连接信息
mumu.select(0).adb.click(100, 200)                   # 点击
mumu.select(0).adb.swipe(100, 200, 300, 400, 500)   # 滑动
mumu.select(0).adb.input_text('Hello')               # 输入文字
mumu.select(0).adb.key_event(3)                      # 模拟按键
mumu.select(0).adb.push(r'C:\file.txt', '/sdcard/')  # 上传文件
mumu.select(0).adb.pull('/sdcard/file.txt', r'C:\')  # 下载文件
```

### 窗口类 (window)

```python
mumu.select(0).window.show()                         # 显示窗口
mumu.select(0).window.hidden()                       # 隐藏窗口
mumu.select(0).window.layout(0, 0, 800, 600)         # 调整大小/位置
```

### 配置类 (setting)

```python
mumu.select(0).setting.all()                         # 获取所有配置
mumu.select(0).setting.get('product_version')        # 获取配置项
mumu.select(0).setting.set(window_size_fixed=True)   # 修改配置
```

### 核心类 (core)

```python
mumu.core.create()                    # 创建模拟器
mumu.select(0).core.clone()           # 克隆模拟器
mumu.select(0).core.delete()          # 删除模拟器
mumu.select(0).core.rename('test')    # 重命名
mumu.select(0).core.limit_cpu(50)     # 限制CPU
```

### 性能类 (performance)

```python
mumu.select(0).performance.set(4, 4)                    # CPU+内存
mumu.select(0).performance.cpu(4)                        # CPU核数
mumu.select(0).performance.memory(4)                     # 内存(GB)
mumu.select(0).performance.force_discrete_graphics(True) # 独立显卡
```

### 屏幕类 (screen)

```python
mumu.select(0).screen.resolution(1080, 1920)     # 分辨率
mumu.select(0).screen.dpi(480)                    # DPI
mumu.select(0).screen.max_frame_rate(60)          # 最大帧率
```

### 网络类 (network)

```python
mumu.select(0).network.nat()                      # NAT模式
mumu.select(0).network.bridge(True, 'adapter')    # 桥接模式
mumu.select(0).network.bridge_dhcp()              # DHCP
mumu.select(0).network.bridge_static('192.168.1.10', '255.255.255.0', '192.168.1.1')
```

### 机型模拟类 (simulation)

```python
mumu.select(0).simulation.mac_address()           # 随机MAC
mumu.select(0).simulation.imei()                   # 随机IMEI
mumu.select(0).simulation.model('Pixel 7')         # 设备型号
mumu.select(0).simulation.brand('Google')           # 品牌
```

### GUI 自动化类 (auto)

```python
def handle(frame, mumu):
    pos = mumu.auto.locateOnScreen(frame, r'C:\target.png', confidence=0.8)
    if pos:
        x, y = mumu.auto.center(pos)
        mumu.adb.click(x, y)

mumu.select(0).auto.create_handle(handle)
```

### 多实例操作

```python
# 选择多个实例
mumu.select(0, 1, 2).power.start()

# 选择所有实例
mumu.all().power.shutdown()
```

---

## 去遥测 / Telemetry Cleanup

MuMu Player Global 内置了大量遥测、广告和崩溃上报组件。本项目提供了完整的清理方案：

- [遥测清理指南 (docs/telemetry_cleanup_guide.md)](docs/telemetry_cleanup_guide.md) — 详细的遥测组件清单、上报 URL 列表及手动清理步骤
- [一键清理脚本 (scripts/mumu_cleanup.ps1)](scripts/mumu_cleanup.ps1) — PowerShell 自动化脚本，以管理员身份运行即可

### 快速使用

以管理员身份打开 PowerShell，执行：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
& ".\scripts\mumu_cleanup.ps1"
```

脚本会自动完成：停止进程/服务 → 重命名遥测 DLL/EXE → 删除广告消息中心 → 清理崩溃残留 → 清除设备标识 → 添加 hosts 屏蔽 → 清理远程遥测组件。

所有重命名操作均使用 `.bak` 后缀，可随时恢复。

---

## 要求

- MuMu Player Global >= 4.0.0
- Python >= 3.7

## 致谢

- 原项目：[openDreamStudioResearch/mumu-python-api](https://github.com/openDreamStudioResearch/mumu-python-api)
- 作者：wlkjyy
