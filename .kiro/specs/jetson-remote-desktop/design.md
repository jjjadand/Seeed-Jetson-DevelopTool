# Design Document: Jetson Remote Desktop

## Overview

为客户端新增"远程桌面"功能，通过 SSH 在 Jetson 上部署 x11vnc + noVNC 服务，让用户可以从 PC 查看和操控 Jetson 的图形桌面。

架构原则：**客户端做控制面，Jetson 做服务面**。客户端不内嵌桌面渲染，而是通过 SSH 部署/管理远端服务，然后引导用户通过浏览器（noVNC）或外部 VNC 客户端访问。

这与现有的 VS Code Server (Web) 和 Jupyter Lab 部署模式完全一致：SSH 安装 → 启动服务 → 给出访问地址。

## Architecture

```mermaid
graph LR
    subgraph PC Client (PyQt5)
        A[Desktop_Dialog] --> B[Desktop_Deployer]
        B --> C[SSHRunner]
    end
    subgraph Jetson
        D[x11vnc :5900]
        E[websockify :6080]
        F[noVNC Web UI]
        E --> D
        F --> E
    end
    C -->|SSH commands| D
    C -->|SSH commands| E
    G[Browser / VNC Viewer] -->|VNC protocol| D
    G -->|HTTP/WebSocket| F
```

部署流程：
1. 客户端通过 SSHRunner 检测 x11vnc 是否已安装
2. 未安装则通过 SSH 执行 `apt-get install -y x11vnc`
3. 启动 x11vnc 绑定到 `:0` 显示器
4. 可选：安装 noVNC + websockify，启动 WebSocket 代理
5. 客户端显示访问地址，用户通过浏览器或 VNC 客户端连接

## Components and Interfaces

### 1. Desktop_Deployer 模块

新建文件 `seeed_jetson_develop/modules/remote/desktop_remote.py`，包含纯逻辑函数：

```python
def check_vnc_installed(runner: SSHRunner) -> bool:
    """检测 x11vnc 是否已安装"""

def check_novnc_installed(runner: SSHRunner) -> bool:
    """检测 noVNC/websockify 是否已安装"""

def check_vnc_running(runner: SSHRunner) -> tuple[bool, str]:
    """检测 x11vnc 是否在运行，返回 (running, pid_or_empty)"""

def check_novnc_running(runner: SSHRunner) -> tuple[bool, str]:
    """检测 websockify 是否在运行，返回 (running, pid_or_empty)"""

def build_install_vnc_cmd(sudo_password: str) -> str:
    """生成安装 x11vnc 的命令"""

def build_start_vnc_cmd(password: str = "", display: str = ":0") -> str:
    """生成启动 x11vnc 的命令"""

def build_install_novnc_cmd(sudo_password: str) -> str:
    """生成安装 noVNC + websockify 的命令"""

def build_start_novnc_cmd(vnc_port: int = 5900, web_port: int = 6080) -> str:
    """生成启动 websockify + noVNC 的命令"""

def build_stop_cmd() -> str:
    """生成停止 x11vnc 和 websockify 的命令"""

def format_vnc_address(ip: str, port: int = 5900) -> str:
    """格式化 VNC 访问地址"""

def format_novnc_url(ip: str, port: int = 6080) -> str:
    """格式化 noVNC 浏览器访问 URL"""

def get_vnc_launch_cmd(ip: str, port: int = 5900) -> str | None:
    """返回当前平台打开 VNC 客户端的命令，找不到返回 None"""
```

### 2. Desktop_Dialog 对话框

新建文件 `seeed_jetson_develop/modules/remote/desktop_dialog.py`，包含 `DesktopRemoteDialog(QDialog)` 类。

UI 布局：
- 标题 + 说明文字
- 状态卡片：VNC 状态 / noVNC 状态 / 访问地址
- VNC 密码输入框（可选，默认无密码）
- 操作按钮行：部署 VNC / 部署 noVNC / 停止服务 / 刷新状态
- 访问按钮行：打开桌面 (VNC) / 打开桌面 (浏览器)
- 实时日志区域

复用现有的 `_SshCmdThread` 模式执行后台 SSH 命令。

### 3. page.py 集成

在 `tool_defs` 列表中新增一项：
```python
(
    "🖥",
    "远程桌面",
    "通过 VNC/noVNC 查看和操控 Jetson 图形桌面",
    "ℹ  需要先连接设备，Jetson 需有图形桌面环境",
    "打开",
    "remote_desktop",
)
```

在 `_on_click` 中新增 `remote_desktop` 分支，检查 SSHRunner 后打开 `DesktopRemoteDialog`。

## Data Models

### 服务状态

```python
@dataclass
class DesktopServiceStatus:
    vnc_installed: bool
    vnc_running: bool
    vnc_pid: str
    novnc_installed: bool
    novnc_running: bool
    novnc_pid: str
```

### SSH 命令定义

```python
# 检测命令
CHECK_VNC_CMD = "which x11vnc 2>/dev/null || dpkg -l x11vnc 2>/dev/null | grep '^ii'"
CHECK_NOVNC_CMD = "which websockify 2>/dev/null || pip3 show websockify 2>/dev/null | grep -i name"
CHECK_VNC_RUNNING_CMD = "pgrep -a x11vnc 2>/dev/null"
CHECK_NOVNC_RUNNING_CMD = "pgrep -a websockify 2>/dev/null"

# 安装命令
INSTALL_VNC_TPL = "echo '{password}' | sudo -S apt-get update && echo '{password}' | sudo -S apt-get install -y x11vnc"
INSTALL_NOVNC_TPL = "echo '{password}' | sudo -S apt-get install -y novnc websockify"

# 启动命令
START_VNC_TPL = "x11vnc -display {display} -forever -shared -rfbport 5900 {auth_flag} -bg -o /tmp/x11vnc.log 2>&1 && echo 'x11vnc started'"
START_NOVNC_TPL = "websockify --web=/usr/share/novnc {web_port} localhost:{vnc_port} --daemon && echo 'noVNC started'"

# 停止命令
STOP_CMD = "pkill x11vnc 2>/dev/null; pkill websockify 2>/dev/null; echo 'stopped'"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Property 1: Service status detection
*For any* SSH command output string (including empty, whitespace-only, multi-line, or error output), the status parsing functions (`check_vnc_installed`, `check_novnc_installed`, `check_vnc_running`, `check_novnc_running`) SHALL return a boolean that correctly classifies the output as positive (installed/running) when the output contains expected markers, and negative otherwise.
**Validates: Requirements 1.1, 2.1, 3.1, 3.2**

Property 2: SSH command generation
*For any* valid configuration parameters (sudo password containing special characters, VNC password, display name, port numbers), the generated SSH command strings SHALL be syntactically valid shell commands that do not contain unescaped special characters that would break execution.
**Validates: Requirements 1.3, 2.3**

Property 3: Access address formatting
*For any* valid IPv4 address string and port number, `format_vnc_address` SHALL produce a string in the format `IP:PORT` and `format_novnc_url` SHALL produce a string in the format `http://IP:PORT/vnc.html`.
**Validates: Requirements 1.4, 2.4**

Property 4: Platform-specific VNC launch command
*For any* platform (linux/win32) and valid IP address, `get_vnc_launch_cmd` SHALL return either a non-empty command string appropriate for that platform, or None if no VNC client is detected.
**Validates: Requirements 7.1, 7.2**

## Error Handling

| 场景 | 处理方式 |
|------|---------|
| SSH 未连接 | 弹窗提示"请先连接设备" |
| x11vnc 安装失败 | 显示 apt 错误日志，提示检查网络或手动安装 |
| x11vnc 启动失败（无显示器） | 提示"Jetson 需要有图形桌面环境（GNOME/XFCE），且需连接 HDMI 或 HDMI 假负载" |
| noVNC 安装失败 | 显示错误日志，提示可单独使用 VNC 客户端 |
| websockify 端口被占用 | 提示端口冲突，建议先停止已有服务 |
| VNC 客户端未安装（PC 端） | 显示推荐客户端列表（RealVNC Viewer, TigerVNC, Remmina） |
| 停止服务失败 | 显示错误日志，提示手动 SSH 执行 `pkill x11vnc` |

## Testing Strategy

### 单元测试

- 测试 `check_vnc_installed` / `check_novnc_installed` 对各种 SSH 输出的解析
- 测试 `build_*_cmd` 函数生成的命令字符串格式
- 测试 `format_vnc_address` / `format_novnc_url` 的地址格式化
- 测试 `get_vnc_launch_cmd` 在不同平台的行为

### 属性测试

使用 `hypothesis` 库进行属性测试，每个属性至少运行 100 次迭代。

- **Feature: jetson-remote-desktop, Property 1: Service status detection** — 生成随机字符串作为 SSH 输出，验证解析函数不会崩溃且返回布尔值
- **Feature: jetson-remote-desktop, Property 2: SSH command generation** — 生成包含特殊字符的密码和参数，验证命令字符串格式正确
- **Feature: jetson-remote-desktop, Property 3: Access address formatting** — 生成随机 IP 和端口，验证输出格式
- **Feature: jetson-remote-desktop, Property 4: Platform-specific VNC launch command** — 对不同平台和 IP 组合，验证返回值类型正确
