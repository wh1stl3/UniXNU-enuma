#!/usr/bin/env bash
set -euo pipefail
export PATH=/home/wh1stl3/.local/bin:$PATH
FAST=/mnt/d/Code/PortingiOS
cd "$FAST/UniXNU"

GW=$(ip route show default 2>/dev/null | awk '{print $3}' | head -1)
# export http_proxy="http://${GW}:7890" https_proxy="http://${GW}:7890" no_proxy="localhost,127.0.0.1"

echo "=== build kernel start $(date +%H:%M:%S) ==="
start=$(date +%s)
./unixnu build kernel -D "$FAST/enuma/UniXNU-enuma" --out "$FAST/UniXNU/out" -j 16
end=$(date +%s)
echo "=== done elapsed=$(( (end-start)/60 ))m$(( (end-start)%60 ))s ==="
ls -la "$FAST/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho" 2>&1
sha256sum "$FAST/UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/kernel/kernel.macho" 2>&1