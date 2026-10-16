param([string]$cfg = '{}', [string]$out = 'd.png', [string]$extra = '', [int]$w = 1920, [int]$h = 1080, [int]$n = 5)
$d = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$d\test_kur.py" | Out-Null
$hash = 'n=' + $n + '&nolog=1&cfg=' + [Uri]::EscapeDataString($cfg) + $extra
& "$d\cdp.ps1" -hash $hash -steps @('wait:1200', "shot:$out") -w $w -h $h

