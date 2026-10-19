# Edge'i görünmez açar, test sayfasını yükler, title 'HAZIR' olana kadar bekler; sonra adımları uygular.
# Adım: "js:<kod>" (çalıştır, sonucu yaz) | "shot:<dosya.png>" | "wait:<ms>"
param([string]$hash = 'n=5', [string[]]$steps = @('shot:cdp.png'), [int]$w = 1920, [int]$h = 1080, [string]$page = 'test.html', [int]$port = 9333, [string]$root = '')
$ErrorActionPreference = 'Stop'
$d = Split-Path -Parent $MyInvocation.MyCommand.Path
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$url = $(if ($root) { "$root/araclar/test/$page" } else { ([System.Uri](Join-Path $d $page)).AbsoluteUri }) + '#' + $hash   # -root http://127.0.0.1:8765: sunucudan aç
$prof = Join-Path $env:TEMP 'dnd-test-edge'      # geçici tarayıcı profili (proje klasörüne yazılmasın)
$proc = Start-Process -FilePath $edge -ArgumentList @('--headless=new', "--user-data-dir=$prof", '--no-first-run', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required', "--window-size=$w,$h", "--remote-debugging-port=$port", 'about:blank') -PassThru
$ws = $null
try {
  $list = $null
  for ($i = 0; $i -lt 50 -and -not $list; $i++) { Start-Sleep -Milliseconds 200; try { $list = Invoke-RestMethod "http://127.0.0.1:$port/json/list" -TimeoutSec 2 } catch {} }
  $target = @($list | Where-Object { $_.type -eq 'page' })[0]
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ws.Options.KeepAliveInterval = [TimeSpan]::FromSeconds(30)
  $ws.ConnectAsync([Uri]$target.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  $script:id = 0
  function Recv() {
    $buf = New-Object byte[] 1048576; $ms = New-Object System.IO.MemoryStream
    do { $seg = New-Object System.ArraySegment[byte] -ArgumentList @(, $buf); $r = $ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result; $ms.Write($buf, 0, $r.Count) } while (-not $r.EndOfMessage)
    [Text.Encoding]::UTF8.GetString($ms.ToArray())
  }
  function Cdp([string]$method, $params = @{}) {
    $script:id++; $myId = $script:id
    $msg = @{ id = $myId; method = $method; params = $params } | ConvertTo-Json -Depth 10 -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($msg)
    $ws.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(, $bytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
    while ($true) { $txt = Recv; if ($txt -match ('^\{"id":' + $myId + ',')) { return ($txt | ConvertFrom-Json) } }
  }
  function Js([string]$code) { $r = Cdp 'Runtime.evaluate' @{ expression = $code; returnByValue = $true; awaitPromise = $true }; if ($r.result.exceptionDetails) { 'JS HATA: ' + $r.result.exceptionDetails.exception.description } else { $r.result.result.value } }
  Cdp 'Emulation.setDeviceMetricsOverride' @{ width = $w; height = $h; deviceScaleFactor = 1; mobile = $false } | Out-Null
  Cdp 'Page.navigate' @{ url = $url } | Out-Null
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while ($sw.Elapsed.TotalSeconds -lt 150) { Start-Sleep -Milliseconds 500; if ((Js 'document.title') -eq 'HAZIR') { break } }
  "hazır: $([int]$sw.Elapsed.TotalSeconds) sn"
  foreach ($s in $steps) {
    if ($s.StartsWith('js:')) { "js> " + (Js $s.Substring(3)) }
    elseif ($s.StartsWith('wait:')) { Start-Sleep -Milliseconds ([int]$s.Substring(5)) }
    elseif ($s.StartsWith('shot:')) { $r = Cdp 'Page.captureScreenshot' @{ format = 'png' }; [IO.File]::WriteAllBytes((Join-Path $d $s.Substring(5)), [Convert]::FromBase64String($r.result.data)); "foto: $($s.Substring(5))" }
  }
  "log:`n" + (Js "(document.getElementById('testlog')||{}).textContent")
} finally {
  try { if ($ws) { Cdp 'Browser.close' | Out-Null } } catch {}
  Start-Sleep -Milliseconds 500
  if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
}

