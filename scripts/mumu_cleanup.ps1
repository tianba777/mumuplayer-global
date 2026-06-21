# MuMuPlayerGlobal 海外版 — 去遥测/去广告 一键清理脚本
# 以管理员身份运行此脚本

$ErrorActionPreference = "Continue"
$base = "C:\Program Files\Netease\MuMuPlayer"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " MuMuPlayerGlobal 遥测/广告清理脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 步骤 1: 停止相关进程和服务
# ============================================================
Write-Host "[1/8] 停止进程和服务..." -ForegroundColor Yellow

$procs = @("MuMuNxMain","MuMuNxService","MuMuManager","MuMuNxDevice","NemuShell",
           "MuMuStatisticsReporter","MuMuNxCrashReporter","MuMuRemoteBackend",
           "MumuRemoteHealthd","MuMuRemoteService","MuMuNxUpdater")
foreach ($p in $procs) {
    $null = Get-Process $p -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

$svc = Get-Service MuMuRemoteService -ErrorAction SilentlyContinue
if ($svc) {
    if ($svc.Status -eq 'Running') { sc.exe stop MuMuRemoteService 2>$null }
    sc.exe config MuMuRemoteService start= disabled 2>$null
    Write-Host "  ✓ MuMuRemoteService 已禁用" -ForegroundColor Green
} else {
    Write-Host "  - MuMuRemoteService 不存在" -ForegroundColor Gray
}
Start-Sleep 2

# ============================================================
# 步骤 2: 重命名遥测 DLL
# ============================================================
Write-Host "[2/8] 处理遥测 DLL..." -ForegroundColor Yellow

$dlls = @(
    "$base\nx_main\nemu-statistics.dll",
    "$base\nx_device\12.0\shell\nemu-statistics.dll",
    "$base\.backup\main\nemu-statistics.dll",
    "$base\nx_main\sentry.dll",
    "$base\nx_device\12.0\shell\sentry.dll",
    "$base\.backup\main\sentry.dll"
)

foreach ($dll in $dlls) {
    $bak = "$dll.bak"
    if (Test-Path $bak) {
        Write-Host "  - 已处理: $(Split-Path $dll -Leaf)" -ForegroundColor Gray
    } elseif (Test-Path $dll) {
        Rename-Item $dll $bak -ErrorAction SilentlyContinue
        Write-Host "  ✓ $(Split-Path $dll -Leaf) -> .bak" -ForegroundColor Green
    } else {
        Write-Host "  - 不存在: $(Split-Path $dll -Leaf)" -ForegroundColor Gray
    }
}

# ============================================================
# 步骤 3: 重命名遥测 EXE
# ============================================================
Write-Host "[3/8] 处理遥测 EXE..." -ForegroundColor Yellow

$exes = @(
    "$base\nx_device\12.0\shell\MuMuStatisticsReporter.exe",
    "$base\nx_device\12.0\shell\MuMuNxCrashReporter.exe",
    "$base\nx_main\crashpad_handler.exe",
    "$base\nx_device\12.0\shell\crashpad_handler.exe",
    "$base\nx_main\MuMuNxUpdater.exe",
    "$base\backup\MuMuNxUpdater.exe"
)

foreach ($exe in $exes) {
    $bak = "$exe.bak"
    if (Test-Path $bak) {
        Write-Host "  - 已处理: $(Split-Path $exe -Leaf)" -ForegroundColor Gray
    } elseif (Test-Path $exe) {
        Rename-Item $exe $bak -ErrorAction SilentlyContinue
        Write-Host "  ✓ $(Split-Path $exe -Leaf) -> .bak" -ForegroundColor Green
    } else {
        Write-Host "  - 不存在: $(Split-Path $exe -Leaf)" -ForegroundColor Gray
    }
}

# ============================================================
# 步骤 4: 删除广告消息中心
# ============================================================
Write-Host "[4/8] 删除广告消息中心..." -ForegroundColor Yellow

$ads = @(
    "$base\nx_main\resources\dist\message_center",
    "$base\nx_main\resources\dist\nx\message_center",
    "$base\nx_device\12.0\shell\resources\dist\message_center",
    "$base\nx_device\12.0\shell\resources\dist\nx\message_center"
)

foreach ($ad in $ads) {
    if (Test-Path $ad) {
        Remove-Item -Recurse -Force $ad -ErrorAction SilentlyContinue
        Write-Host "  ✓ 已删除: $($ad.Replace($base,''))" -ForegroundColor Green
    } else {
        Write-Host "  - 不存在: $($ad.Replace($base,''))" -ForegroundColor Gray
    }
}

# ============================================================
# 步骤 5: 清理崩溃残留
# ============================================================
Write-Host "[5/8] 清理崩溃残留..." -ForegroundColor Yellow

$crashes = @(
    "$base\nx_main\nxmain-crash-files",
    "$base\nx_main\nxupdater-crash-files",
    "$base\nx_device\12.0\shell\crash-files"
)

foreach ($crash in $crashes) {
    if (Test-Path $crash) {
        Remove-Item -Recurse -Force $crash -ErrorAction SilentlyContinue
        Write-Host "  ✓ 已删除: $($crash.Replace($base,''))" -ForegroundColor Green
    } else {
        Write-Host "  - 不存在: $($crash.Replace($base,''))" -ForegroundColor Gray
    }
}

# ============================================================
# 步骤 6: 清理配置中的遥测痕迹
# ============================================================
Write-Host "[6/8] 清理配置痕迹..." -ForegroundColor Yellow

# 6a. 清空 fcountData.ini
$fcount = "$base\nx_main\fcountData.ini"
if (Test-Path $fcount) {
    Set-Content $fcount "[runtime_data]`r`ndevice_id=`r`ninit_timestamp=0"
    Write-Host "  ✓ fcountData.ini 已清空" -ForegroundColor Green
}

# 6b. 清除每个 VM 的 nxdevice.report 时间戳
$vmsPath = "$base\vms"
$count = 0
Get-ChildItem $vmsPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $cfg = Join-Path $_.FullName "configs\customer_config.json"
    if (Test-Path $cfg) {
        try {
            $json = Get-Content $cfg -Raw | ConvertFrom-Json
            if ($json.nxdevice -and $json.nxdevice.report) {
                $json.nxdevice.report = @{}
                $json | ConvertTo-Json -Depth 10 | Set-Content $cfg -Encoding UTF8
                $count++
            }
        } catch {}
    }
}
Write-Host "  ✓ 已清理 $count 个 VM 的 report 时间戳" -ForegroundColor Green

# 6c. 清除注册表调试模式
$regPath = "HKCU:\Software\NemuShell\Debug"
if (Test-Path $regPath) {
    Remove-ItemProperty -Path $regPath -Name "DebugMode" -ErrorAction SilentlyContinue
    Write-Host "  ✓ 注册表 DebugMode 已清除" -ForegroundColor Green
} else {
    Write-Host "  - 注册表 DebugMode 不存在" -ForegroundColor Gray
}

# ============================================================
# 步骤 7: Hosts 屏蔽（双重保险）
# ============================================================
Write-Host "[7/8] 添加 hosts 屏蔽..." -ForegroundColor Yellow

$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$marker = "# MuMuPlayer telemetry block"
$entries = @(
    "0.0.0.0 shence-api.mumu.163.com",
    "0.0.0.0 report-api.mumuplayer.com",
    "0.0.0.0 report.mumu.nie.netease.com",
    "0.0.0.0 api.mumuglobal.com",
    "0.0.0.0 user-center.mumuplayer.com",
    "0.0.0.0 pro-api.mumuplayer.com",
    "0.0.0.0 feedback-system.webapp.easebar.com",
    "0.0.0.0 fcount-api.webapp.163.com",
    "0.0.0.0 fcount-api.webapp.easebar.com",
    "0.0.0.0 fp.ps.netease.com",
    "0.0.0.0 event.sc.gearupportal.com",
    "0.0.0.0 adl.guinfra.com",
    "0.0.0.0 api-event.nrd.nie.163.com",
    "0.0.0.0 api.nrd.nie.163.com",
    "0.0.0.0 api-pro.mumu.163.com"
)

$hostsContent = Get-Content $hostsPath -Raw -ErrorAction SilentlyContinue
if ($hostsContent -match [regex]::Escape($marker)) {
    # 已存在，替换旧块
    $pattern = "(?s)$marker.*?(?=\r?\n\s*\r?\n|$)"
    $newBlock = "$marker`r`n$($entries -join "`r`n")"
    $hostsContent = $hostsContent -replace $pattern, $newBlock
    Set-Content $hostsPath $hostsContent -Encoding ASCII
    Write-Host "  ✓ hosts 已更新 ($($entries.Count) 条)" -ForegroundColor Green
} else {
    Add-Content $hostsPath "`r`n$marker`r`n$($entries -join "`r`n")" -Encoding ASCII
    Write-Host "  ✓ hosts 已添加 ($($entries.Count) 条)" -ForegroundColor Green
}

# ============================================================
# 步骤 8: 远程服务清理（可选，不影响本地多开）
# ============================================================
Write-Host "[8/8] 清理远程遥测组件（可选）..." -ForegroundColor Yellow

$remoteFiles = @(
    "$base\nx_main\MuMuRemoteBackend.exe",
    "$base\nx_main\MumuRemoteHealthd.exe",
    "$base\nx_main\nemu-remote.dll"
)

foreach ($rf in $remoteFiles) {
    $bak = "$rf.bak"
    if (Test-Path $bak) {
        Write-Host "  - 已处理: $(Split-Path $rf -Leaf)" -ForegroundColor Gray
    } elseif (Test-Path $rf) {
        Rename-Item $rf $bak -ErrorAction SilentlyContinue
        Write-Host "  ✓ $(Split-Path $rf -Leaf) -> .bak" -ForegroundColor Green
    } else {
        Write-Host "  - 不存在: $(Split-Path $rf -Leaf)" -ForegroundColor Gray
    }
}

# 删除 Windows 服务
$svc2 = Get-Service MuMuRemoteService -ErrorAction SilentlyContinue
if ($svc2) {
    sc.exe delete MuMuRemoteService 2>$null
    Write-Host "  ✓ MuMuRemoteService 服务已删除" -ForegroundColor Green
}

# ============================================================
# 完成 & 验证
# ============================================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 清理完成！验证结果：" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$checks = @(
    @{Name="nemu-statistics DLL"; Path="$base\nx_main\nemu-statistics.dll.bak"; Type="file"},
    @{Name="sentry DLL"; Path="$base\nx_main\sentry.dll.bak"; Type="file"},
    @{Name="统计上报 EXE"; Path="$base\nx_device\12.0\shell\MuMuStatisticsReporter.exe.bak"; Type="file"},
    @{Name="崩溃上报 EXE"; Path="$base\nx_device\12.0\shell\MuMuNxCrashReporter.exe.bak"; Type="file"},
    @{Name="Crashpad 处理"; Path="$base\nx_main\crashpad_handler.exe.bak"; Type="file"},
    @{Name="更新器"; Path="$base\nx_main\MuMuNxUpdater.exe.bak"; Type="file"},
    @{Name="消息中心 nx_main"; Path="$base\nx_main\resources\dist\message_center"; Type="absent"},
    @{Name="消息中心 shell"; Path="$base\nx_device\12.0\shell\resources\dist\message_center"; Type="absent"},
    @{Name="崩溃残留 nxmain"; Path="$base\nx_main\nxmain-crash-files"; Type="absent"},
    @{Name="崩溃残留 shell"; Path="$base\nx_device\12.0\shell\crash-files"; Type="absent"},
    @{Name="hosts 屏蔽"; Path="$env:windir\System32\drivers\etc\hosts"; Type="hosts"}
)

$ok = 0; $fail = 0
foreach ($c in $checks) {
    switch ($c.Type) {
        "file" {
            if (Test-Path $c.Path) { Write-Host "  ✓ $($c.Name)" -ForegroundColor Green; $ok++ }
            else { Write-Host "  ✗ $($c.Name) — 未找到 .bak" -ForegroundColor Red; $fail++ }
        }
        "absent" {
            if (-not (Test-Path $c.Path)) { Write-Host "  ✓ $($c.Name) 已删除" -ForegroundColor Green; $ok++ }
            else { Write-Host "  ✗ $($c.Name) 仍存在" -ForegroundColor Red; $fail++ }
        }
        "hosts" {
            $h = Get-Content $c.Path -Raw -ErrorAction SilentlyContinue
            if ($h -match $marker) { Write-Host "  ✓ hosts 屏蔽已生效" -ForegroundColor Green; $ok++ }
            else { Write-Host "  ✗ hosts 屏蔽未添加" -ForegroundColor Red; $fail++ }
        }
    }
}

Write-Host ""
Write-Host "结果: $ok 通过 / $($ok+$fail) 总计" -ForegroundColor $(if($fail -eq 0){'Green'}else{'Yellow'})
Write-Host ""
Write-Host "提示: 如需恢复，将所有 .bak 文件重命名回原名即可。" -ForegroundColor Gray
