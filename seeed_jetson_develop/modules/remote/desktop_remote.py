"""远程桌面核心逻辑 — 通过 SSH 在 Jetson 上部署/管理 x11vnc + noVNC。

客户端做控制面，Jetson 做服务面。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import webbrowser

from seeed_jetson_develop.core.runner import SSHRunner


# ── SSH 命令模板 ──────────────────────────────────────────────────────────────

CHECK_VNC_CMD = "which x11vnc 2>/dev/null || dpkg -l x11vnc 2>/dev/null | grep '^ii'"
CHECK_NOVNC_CMD = "which websockify 2>/dev/null || pip3 show websockify 2>/dev/null | grep -i name"
CHECK_VNC_RUNNING_CMD = "pgrep -a x11vnc 2>/dev/null"
CHECK_NOVNC_RUNNING_CMD = "pgrep -a websockify 2>/dev/null"
STOP_CMD = "pkill x11vnc 2>/dev/null; pkill websockify 2>/dev/null; echo 'stopped'"


# ── 状态检测 ──────────────────────────────────────────────────────────────────

def check_vnc_installed(runner: SSHRunner) -> bool:
    rc, out = runner.run(CHECK_VNC_CMD, timeout=10)
    return rc == 0 and bool(out.strip())


def check_novnc_installed(runner: SSHRunner) -> bool:
    rc, out = runner.run(CHECK_NOVNC_CMD, timeout=10)
    return rc == 0 and bool(out.strip())


def check_vnc_running(runner: SSHRunner) -> tuple[bool, str]:
    rc, out = runner.run(CHECK_VNC_RUNNING_CMD, timeout=5)
    if rc == 0 and out.strip():
        pid = out.strip().splitlines()[0].split()[0]
        return True, pid
    return False, ""


def check_novnc_running(runner: SSHRunner) -> tuple[bool, str]:
    rc, out = runner.run(CHECK_NOVNC_RUNNING_CMD, timeout=5)
    if rc == 0 and out.strip():
        pid = out.strip().splitlines()[0].split()[0]
        return True, pid
    return False, ""


# ── 命令生成 ──────────────────────────────────────────────────────────────────

def build_install_vnc_cmd(sudo_password: str) -> str:
    escaped = sudo_password.replace("'", "'\\''")
    return (
        f"echo '{escaped}' | sudo -S apt-get update -qq "
        f"&& echo '{escaped}' | sudo -S apt-get install -y x11vnc"
    )


def build_start_vnc_cmd(password: str = "", display: str = "") -> str:
    """启动 x11vnc，自动探测 display，前台启动后放入后台并验证端口。"""
    if password:
        auth = f"-passwd {password}"
    else:
        auth = "-nopw"
    # 自动探测 display：优先用环境变量，fallback 到 :0/:1
    detect_display = (
        'DISP="${DISPLAY:-}"; '
        'if [ -z "$DISP" ]; then '
        '  for d in :0 :1 :2; do '
        '    if xdpyinfo -display $d >/dev/null 2>&1; then DISP=$d; break; fi; '
        '  done; '
        'fi; '
        'if [ -z "$DISP" ]; then DISP=:0; fi; '
        'echo "Using display: $DISP"; '
    )
    start_vnc = (
        f'pkill x11vnc 2>/dev/null; sleep 0.5; '
        f'x11vnc -display $DISP -forever -shared -rfbport 5900 {auth} '
        f'-noxdamage -noxfixes -o /tmp/x11vnc.log -bg 2>&1; '
        f'sleep 2; '
        f'if ss -tlnp 2>/dev/null | grep -q ":5900" || netstat -tlnp 2>/dev/null | grep -q ":5900"; then '
        f'  echo "x11vnc started OK on port 5900"; '
        f'else '
        f'  echo "x11vnc may have failed, check /tmp/x11vnc.log:"; '
        f'  tail -20 /tmp/x11vnc.log 2>/dev/null || echo "(no log)"; '
        f'  exit 1; '
        f'fi'
    )
    return detect_display + start_vnc


def build_install_novnc_cmd(sudo_password: str) -> str:
    escaped = sudo_password.replace("'", "'\\''")
    return (
        f"echo '{escaped}' | sudo -S apt-get install -y novnc websockify python3-websockify"
    )


def build_start_novnc_cmd(vnc_port: int = 5900, web_port: int = 6080) -> str:
    # 探测 novnc web 目录
    return (
        f'pkill websockify 2>/dev/null; sleep 0.3; '
        f'NOVNC_DIR=""; '
        f'for d in /usr/share/novnc /usr/local/share/novnc /opt/novnc; do '
        f'  if [ -f "$d/vnc.html" ] || [ -f "$d/index.html" ]; then NOVNC_DIR=$d; break; fi; '
        f'done; '
        f'if [ -n "$NOVNC_DIR" ]; then '
        f'  websockify --web="$NOVNC_DIR" {web_port} localhost:{vnc_port} --daemon 2>&1; '
        f'else '
        f'  websockify {web_port} localhost:{vnc_port} --daemon 2>&1; '
        f'fi; '
        f'sleep 2; '
        f'if ss -tlnp 2>/dev/null | grep -q ":{web_port}" || netstat -tlnp 2>/dev/null | grep -q ":{web_port}"; then '
        f'  echo "noVNC started OK on port {web_port}"; '
        f'else '
        f'  echo "websockify may have failed"; exit 1; '
        f'fi'
    )


def build_stop_cmd() -> str:
    return STOP_CMD


# ── 地址格式化 ────────────────────────────────────────────────────────────────

def format_vnc_address(ip: str, port: int = 5900) -> str:
    return f"{ip}:{port}"


def format_novnc_url(ip: str, port: int = 6080) -> str:
    return f"http://{ip}:{port}/vnc.html"


# ── 平台工具 ──────────────────────────────────────────────────────────────────

def get_vnc_launch_cmd(ip: str, port: int = 5900) -> str | None:
    """返回当前平台打开 VNC 客户端的命令，找不到返回 None。"""
    addr = f"{ip}:{port}"
    if sys.platform == "win32":
        # Windows: 尝试 vnc:// 协议
        return f'start vnc://{addr}'
    # Linux: 尝试已知 VNC 客户端
    for cmd in ("vncviewer", "remmina", "xdg-open"):
        if shutil.which(cmd):
            if cmd == "remmina":
                return f'remmina -c vnc://{addr}'
            if cmd == "xdg-open":
                return f'xdg-open vnc://{addr}'
            return f'{cmd} {addr}'
    return None


def open_in_browser(url: str) -> None:
    webbrowser.open(url)


def launch_vnc_viewer(ip: str, port: int = 5900) -> bool:
    """尝试启动 VNC 客户端，成功返回 True。"""
    cmd = get_vnc_launch_cmd(ip, port)
    if not cmd:
        return False
    try:
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception:
        return False
