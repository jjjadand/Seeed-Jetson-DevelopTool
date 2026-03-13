# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 运行与开发

```bash
# 启动新版 UI（主入口）
python run_v2.py

# 安装依赖
pip install -r requirements.txt
# 运行时必须：PyQt5, paramiko, requests, tqdm, click, rich

# 语法检查
python -m py_compile seeed_jetson_develop/gui/main_window_v2.py

# 快速验证窗口能否创建（无需显示器）
python -c "
import sys, os
os.environ['NO_AT_BRIDGE']='1'; os.environ['QT_ACCESSIBILITY']='0'
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
app = QApplication(sys.argv)
from seeed_jetson_develop.gui.main_window_v2 import MainWindowV2
w = MainWindowV2(); print('OK')
"
```

## 架构

### 分层结构

```
core/          ← 基础层，无任何业务依赖
modules/       ← 6 个功能模块，互不直接 import
gui/           ← 主窗口壳，只负责组装各模块 page
```

### 模块间通信：事件总线（唯一合法跨模块通道）

```python
from seeed_jetson_develop.core import bus
bus.skill_run_requested.emit("usb_wifi")   # 发出
bus.skill_completed.connect(my_callback)   # 监听
```

信号定义在 `core/events.py`：`device_connected`, `flash_completed`, `skill_run_requested`, `skill_completed`, `app_install_requested`, `navigate_to`。

### 每个模块对外只暴露 `build_page()`

```python
from seeed_jetson_develop.modules.apps import build_page as apps_page
stack.addWidget(apps_page())
```

### 命令执行引擎

- `core/runner.py` — `Runner`（本地）/ `SSHRunner`（远程 paramiko）
- `get_runner()` 返回全局活跃 runner，`set_runner()` 切换
- 模块内执行命令统一用 `get_runner().run(cmd)`，不直接调用 subprocess

### 主题系统

`gui/theme.py` 是唯一样式来源，所有模块页面从此 import：

```python
from seeed_jetson_develop.gui.theme import (
    C_BG, C_BG_DEEP, C_CARD, C_CARD_LIGHT,
    C_GREEN, C_BLUE, C_ORANGE, C_RED,
    C_TEXT, C_TEXT2, C_TEXT3,
    pt as _pt, make_label as _lbl, make_button as _btn,
    make_card as _card, make_input_card as _input_card,
    apply_shadow as _shadow,
)
```

设计原则：无边框，用背景色层次区分深度，阴影代替硬边框。

## 关键约定

- **`pt()` 别名**：theme 导入时必须用 `pt as _pt`，页面内统一用 `_pt()`，不能裸调用 `pt()`
- **Windows 开发**：`core.fileMode = false` 已配置，`.sh` 文件权限变化不会出现在 git diff
- **Skills 数据**：`modules/skills/data/skills.json`，通过 `engine.load_skills()` 加载
- **Apps 数据**：`modules/apps/data/apps.json`，通过 `registry.load_apps()` 加载
- **配置持久化**：`core/config.py`，存储路径 `~/.config/seeed-jetson-tool/`
- **日志**：运行时写入 `~/.cache/seeed-jetson/app.log`

## 当前迁移状态

`gui/main_window_v2.py` 仍直接实现了烧录页（`_build_flash_page`）和社区页（`_build_community_page`），其余 4 个页面已迁移到各自 `modules/xxx/page.py`。烧录和社区页待后续迁移。

## P0 待完成功能

- 设备体检真实命令接入（`modules/devices/diagnostics.py`）
- 局域网扫描优化（`modules/remote/connector.py` 当前为逐 IP socket 探测，性能差）
- Skills 参数化执行与失败重试
