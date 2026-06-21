# MuMuPlayerGlobal (海外版) 遥测与广告 — 清理指南

> **版本:** v5.30.2.3616 | **路径:** `C:\Program Files\Netease\MuMuPlayer`
> **日期:** 2026-06-20

---

## 一、遥测/广告组件清单

### 1.1 遥测 DLL（统计 + 崩溃跟踪）

| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| `nemu-statistics.dll` | `nx_main\` | 719 KB | 统计/分析核心，含 9 个上报 URL |
| `nemu-statistics.dll` | `nx_device\12.0\shell\` | 同上 | 同上 |
| `nemu-statistics.dll` | `.backup\main\` | 同上 | 备份副本 |
| `sentry.dll` | `nx_main\` | 269 KB | Sentry 崩溃跟踪 SDK v0.5.0 |
| `sentry.dll` | `nx_device\12.0\shell\` | 同上 | 同上 |
| `sentry.dll` | `.backup\main\` | 同上 | 备份副本 |

### 1.2 遥测可执行文件

| 文件 | 位置 | 大小 | 用途 |
|------|------|------|------|
| `MuMuStatisticsReporter.exe` | `nx_device\12.0\shell\` | 17.2 MB | 统计上报进程 |
| `MuMuNxCrashReporter.exe` | `nx_device\12.0\shell\` | 16.8 MB | 崩溃上报进程 |
| `crashpad_handler.exe` | `nx_main\` | 590 KB | Google Crashpad 崩溃处理 |
| `crashpad_handler.exe` | `nx_device\12.0\shell\` | 同上 | 同上 |
| `MuMuNxUpdater.exe` | `nx_main\` | 18.4 MB | 更新器（会上报） |
| `MuMuNxUpdater.exe` | `backup\` | 18.3 MB | 备份副本 |

### 1.3 广告/消息推送

| 目录 | 位置 | 说明 |
|------|------|------|
| `resources\dist\message_center\` | `nx_main\resources\` | Vue.js 消息中心（广告推送） |
| `resources\dist\nx\message_center\` | `nx_main\resources\` | 同上 |
| `resources\dist\message_center\` | `nx_device\12.0\shell\resources\` | 同上 |
| `resources\dist\nx\message_center\` | `nx_device\12.0\shell\resources\` | 同上 |

### 1.4 远程服务中的遥测（可选清理）

| 文件 | 位置 | 大小 | 说明 |
|------|------|------|------|
| `MuMuRemoteBackend.exe` | `nx_main\` | 32.2 MB | 远程后端，含神策 |
| `MumuRemoteHealthd.exe` | `nx_main\` | 14.2 MB | 远程健康，含神策 |
| `nemu-remote.dll` | `nx_main\` | 23.8 MB | 远程控制 DLL，含神策+NRD |
| `MuMuRemoteService.exe` | `nx_main\` | 2.1 MB | Windows 服务 |

### 1.5 嵌入遥测 URL 的所有文件（共 12 个）

每个都包含 15 个遥测+广告 URL：

| 文件 | 大小 |
|------|------|
| `MuMuNxMain.exe` | 26.4 MB |
| `MuMuNxUpdater.exe` | 18.4 MB |
| `MuMuNxService.exe` | 18.8 MB |
| `MuMuStatisticsReporter.exe` | 17.2 MB |
| `MuMuNxCrashReporter.exe` | 16.8 MB |
| `MuMuNxDeviceCleaner.exe` | 17.9 MB |
| `MuMuManager.exe` | 18.4 MB |
| `mumu-cli.exe` | 18.4 MB |
| `MuMuNxDevice.exe` | 31.3 MB |
| `MuMuRemoteBackend.exe` | 32.2 MB |
| `MumuRemoteHealthd.exe` | 14.2 MB |
| `nemu-remote.dll` | 23.8 MB |

---

## 二、上报 URL 完整清单

### 2.1 神策数据 — 用户行为分析（最核心）

```
https://shence-api.mumu.163.com/sa
```
嵌入 12 个文件。追踪点击、页面浏览、功能使用、留存。

### 2.2 广告投放

```
https://adl.guinfra.com/d/g/stardesk/c/mumu
```
嵌入 9 个 EXE。

### 2.3 统计/指纹上报

| URL | 用途 |
|-----|------|
| `https://report-api.mumuplayer.com/api/collection` | 统计收集 |
| `https://report.mumu.nie.netease.com/api/collection` | 统计收集（内网） |
| `https://fcount-api.webapp.163.com` | 计数/指纹 |
| `https://fcount-api.webapp.easebar.com` | 计数/指纹（海外） |
| `https://fp.ps.netease.com/` | 设备指纹 |
| `https://event.sc.gearupportal.com/sa` | 事件分析 |

### 2.4 崩溃上报

| URL |
|------|
| `https://api.mumuglobal.com/api//crashrpt` |

### 2.5 主 API / 用户中心

| URL | 用途 |
|-----|------|
| `https://api.mumuglobal.com/` | 主 API |
| `https://api.mumuglobal.com/api/` | API 端点 |
| `https://api.mumuglobal.com/api/ip` | 获取公网 IP |
| `https://user-center.mumuplayer.com/api/` | 用户中心 |
| `https://pro-api.mumuplayer.com/api/` | Pro API |
| `https://feedback-system.webapp.easebar.com/` | 反馈系统 |
| `https://www.mumuglobal.com/` | 官网 |

### 2.6 远程操控专属（NRD）

| URL |
|------|
| `https://api-event.nrd.nie.163.com/api/v1/event/report/batch` |
| `https://api.nrd.nie.163.com/api/v1/user/ticket/for/plugin` |
| `https://api.nrd.nie.163.com/api/v1/cloud_pc/queue/` |
| `https://api.nrd.nie.163.com/api/v1/cloud_pc/boot_info/` |
| `https://api-event.nrd.nie.163.com/api/v1/plugin/event/report/batch` |
| `https://api-pro.mumu.163.com` |

---

## 三、配置中的遥测痕迹

### 3.1 设备标识

`nx_main\fcountData.ini`:
```ini
[runtime_data]
device_id=MG-7aba8bc7-f78f-4143-9e51-18e21a98f837
init_timestamp=1775557449616
```

### 3.2 每个 VM 的 `customer_config.json`

`vms\MuMuPlayerGlobal-12.0-*\configs\customer_config.json` 中：
```json
"nxdevice": {
    "report": {
        "close": { "last_timestamp": "..." },
        "launch": { "last_timestamp": "..." },
        "running": { "last_timestamp": "..." }
    }
}
```
24 个 VM 均含此片段。

### 3.3 Sentry 崩溃残留

| 目录 | 数量 |
|------|------|
| `nx_main\nxmain-crash-files\` | 1 个崩溃 |
| `nx_main\nxupdater-crash-files\` | 1 个崩溃 |
| `nx_device\12.0\shell\crash-files\` | 3 个崩溃 |

每个崩溃含：OS 版本、用户 ID、IP 地址、软件版本、breadcrumbs。

### 3.4 调试模式

`HKCU\Software\NemuShell\Debug` → `DebugMode = 1`

---

## 四、系统级痕迹

| 项目 | 状态 | 说明 |
|------|------|------|
| **MuMuRemoteService** | Running (Auto) | 路径指向旧 D: 盘，应删除 |
| 开机自启 `MuMuNxMain` | 已失效 | 指向旧 D: 盘 |
| 开机自启 `MuMuPlayerService` | 已失效 | 指向旧 D: 盘 |
| 防火墙规则 | 多条 | MuMuNxDevice/MuMuNxMain/MuMuVMMHeadless/MuMuVMMSVC/MuMuDownloader |
| 旧安装注册表 | 残留 | `HKLM\...\Uninstall\MuMu模拟器` (D:\) |
| NEAC 内核驱动 | 存在 | `NeacSafe64.sys` (8.2 MB) |

---

## 五、清理操作步骤

> ⚠️ **注意事项：**
> - 操作前关闭所有模拟器窗口
> - 建议先用 `sc stop MuMuRemoteService` 停止服务
> - 重命名 `.bak` 方式可逆，删除不可逆
> - hosts 屏蔽不影响程序运行但阻断上报

### 步骤 1：停止服务 & 进程

```powershell
# 停止 MuMuRemoteService
sc stop MuMuRemoteService
sc config MuMuRemoteService start= disabled

# 确保没有 MuMu 进程在运行
taskkill /f /im MuMuNxMain.exe 2>$null
taskkill /f /im MuMuNxService.exe 2>$null
taskkill /f /im MuMuManager.exe 2>$null
```

### 步骤 2：重命名遥测 DLL（3 个位置 x 2 个文件 = 6 个）

```powershell
$base = "C:\Program Files\Netease\MuMuPlayer"

# nemu-statistics.dll (3 locations)
Rename-Item "$base\nx_main\nemu-statistics.dll" "nemu-statistics.dll.bak"
Rename-Item "$base\nx_device\12.0\shell\nemu-statistics.dll" "nemu-statistics.dll.bak"
Rename-Item "$base\.backup\main\nemu-statistics.dll" "nemu-statistics.dll.bak"

# sentry.dll (3 locations)
Rename-Item "$base\nx_main\sentry.dll" "sentry.dll.bak"
Rename-Item "$base\nx_device\12.0\shell\sentry.dll" "sentry.dll.bak"
Rename-Item "$base\.backup\main\sentry.dll" "sentry.dll.bak"
```

### 步骤 3：重命名遥测 EXE

```powershell
# 统计上报
Rename-Item "$base\nx_device\12.0\shell\MuMuStatisticsReporter.exe" "MuMuStatisticsReporter.exe.bak"

# 崩溃上报
Rename-Item "$base\nx_device\12.0\shell\MuMuNxCrashReporter.exe" "MuMuNxCrashReporter.exe.bak"

# Crashpad 处理器
Rename-Item "$base\nx_main\crashpad_handler.exe" "crashpad_handler.exe.bak"
Rename-Item "$base\nx_device\12.0\shell\crashpad_handler.exe" "crashpad_handler.exe.bak"

# 更新器
Rename-Item "$base\nx_main\MuMuNxUpdater.exe" "MuMuNxUpdater.exe.bak"
Rename-Item "$base\backup\MuMuNxUpdater.exe" "MuMuNxUpdater.exe.bak"
```

### 步骤 4：删除广告消息中心（4 个目录）

```powershell
Remove-Item -Recurse -Force "$base\nx_main\resources\dist\message_center"
Remove-Item -Recurse -Force "$base\nx_main\resources\dist\nx\message_center"
Remove-Item -Recurse -Force "$base\nx_device\12.0\shell\resources\dist\message_center"
Remove-Item -Recurse -Force "$base\nx_device\12.0\shell\resources\dist\nx\message_center"
```

### 步骤 5：清理崩溃残留

```powershell
Remove-Item -Recurse -Force "$base\nx_main\nxmain-crash-files"
Remove-Item -Recurse -Force "$base\nx_main\nxupdater-crash-files"
Remove-Item -Recurse -Force "$base\nx_device\12.0\shell\crash-files"
```

### 步骤 6：清理远程遥测服务（可选 — 不影响本地多开）

```powershell
Rename-Item "$base\nx_main\MuMuRemoteBackend.exe" "MuMuRemoteBackend.exe.bak"
Rename-Item "$base\nx_main\MumuRemoteHealthd.exe" "MumuRemoteHealthd.exe.bak"
Rename-Item "$base\nx_main\nemu-remote.dll" "nemu-remote.dll.bak"

# 删除 Windows 服务
sc delete MuMuRemoteService
```

### 步骤 7：修改配置清除 device_id

```powershell
# 清空设备标识
Set-Content "$base\nx_main\fcountData.ini" "[runtime_data]`ndevice_id=`ninit_timestamp=0"

# 清除调试模式注册表
Remove-ItemProperty -Path "HKCU:\Software\NemuShell\Debug" -Name "DebugMode" -ErrorAction SilentlyContinue
```

### 步骤 8：清理 24 个 VM 的遥测配置

```powershell
$vmsPath = "$base\vms"
Get-ChildItem $vmsPath -Directory | ForEach-Object {
    $configPath = Join-Path $_.FullName "configs\customer_config.json"
    if (Test-Path $configPath) {
        $json = Get-Content $configPath -Raw | ConvertFrom-Json
        # 清除 report 时间戳
        if ($json.nxdevice) {
            $json.nxdevice.report = @{}
        }
        $json | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    }
}
```

### 步骤 9：Hosts 屏蔽（双重保险）

将以下追加到 `C:\Windows\System32\drivers\etc\hosts`：

```
# MuMuPlayer 遥测屏蔽
0.0.0.0 shence-api.mumu.163.com
0.0.0.0 report-api.mumuplayer.com
0.0.0.0 report.mumu.nie.netease.com
0.0.0.0 api.mumuglobal.com
0.0.0.0 user-center.mumuplayer.com
0.0.0.0 pro-api.mumuplayer.com
0.0.0.0 feedback-system.webapp.easebar.com
0.0.0.0 fcount-api.webapp.163.com
0.0.0.0 fcount-api.webapp.easebar.com
0.0.0.0 fp.ps.netease.com
0.0.0.0 event.sc.gearupportal.com
0.0.0.0 adl.guinfra.com
0.0.0.0 api-event.nrd.nie.163.com
0.0.0.0 api.nrd.nie.163.com
0.0.0.0 api-pro.mumu.163.com
```

### 步骤 10：清理系统残留

```powershell
# 删除旧 D: 盘的开机自启项
Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "MuMuNxMain" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "MuMuPlayerService" -ErrorAction SilentlyContinue

# 删除旧注册表卸载信息
Remove-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMu模拟器" -Recurse -ErrorAction SilentlyContinue
```

---

## 六、清理后验证

| 检查项 | 预期 |
|--------|------|
| `nemu-statistics.dll` | 应变为 `.bak` 后缀 |
| `sentry.dll` | 应变为 `.bak` 后缀 |
| `MuMuStatisticsReporter.exe` | 应变为 `.bak` 后缀 |
| `crashpad_handler.exe` | 应变为 `.bak` 后缀 |
| `MuMuNxUpdater.exe` | 应变为 `.bak` 后缀 |
| `message_center/` 目录 | 应不存在 |
| `crash-files/` 目录 | 应不存在 |
| `fcountData.ini` | device_id 应为空 |
| `customer_config.json` | nxdevice.report 应为空 |
| MuMuRemoteService | 应已删除 |
| hosts 屏蔽 | 15 条规则 |
| 模拟器正常启动 | ✅ 应不受影响 |

---

## 七、URL 速查

| # | 完整 URL | 类型 |
|---|----------|------|
| 1 | `https://shence-api.mumu.163.com/sa` | 神策行为分析 |
| 2 | `https://adl.guinfra.com/d/g/stardesk/c/mumu` | 广告投放 |
| 3 | `https://report-api.mumuplayer.com/api/collection` | 统计 |
| 4 | `https://report.mumu.nie.netease.com/api/collection` | 统计 |
| 5 | `https://fcount-api.webapp.163.com` | 指纹计数 |
| 6 | `https://fcount-api.webapp.easebar.com` | 指纹计数 |
| 7 | `https://fp.ps.netease.com/` | 设备指纹 |
| 8 | `https://event.sc.gearupportal.com/sa` | 事件分析 |
| 9 | `https://api.mumuglobal.com/api//crashrpt` | 崩溃上报 |
| 10 | `https://api.mumuglobal.com/` | 主 API |
| 11 | `https://api.mumuglobal.com/api/ip` | 获取 IP |
| 12 | `https://user-center.mumuplayer.com/api/` | 用户中心 |
| 13 | `https://pro-api.mumuplayer.com/api/` | Pro API |
| 14 | `https://feedback-system.webapp.easebar.com/` | 反馈系统 |
| 15 | `https://api-event.nrd.nie.163.com/api/v1/event/report/batch` | NRD 事件 |
| 16 | `https://api.nrd.nie.163.com/api/v1/user/ticket/for/plugin` | NRD 票据 |
| 17 | `https://api.nrd.nie.163.com/api/v1/cloud_pc/queue/` | NRD 队列 |
| 18 | `https://api.nrd.nie.163.com/api/v1/cloud_pc/boot_info/` | NRD 启动 |
| 19 | `https://api-event.nrd.nie.163.com/api/v1/plugin/event/report/batch` | NRD 插件 |
| 20 | `https://api-pro.mumu.163.com` | NRD Pro |
