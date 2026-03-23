# Implementation Plan: Jetson Remote Desktop

## Overview

分三步实现：先写核心逻辑模块，再写 GUI 对话框，最后集成到 page.py。测试跟随实现同步进行。

## Tasks

- [x] 1. 创建 desktop_remote.py 核心逻辑模块
  - [x] 1.1 实现服务状态检测函数
    - 创建 `seeed_jetson_develop/modules/remote/desktop_remote.py`
    - 实现 `check_vnc_installed(runner)` — 通过 SSH 检测 x11vnc 是否安装
    - 实现 `check_novnc_installed(runner)` — 通过 SSH 检测 websockify 是否安装
    - 实现 `check_vnc_running(runner)` — 检测 x11vnc 进程是否在运行
    - 实现 `check_novnc_running(runner)` — 检测 websockify 进程是否在运行
    - _Requirements: 1.1, 2.1, 3.1, 3.2_

  - [x] 1.2 实现 SSH 命令生成函数
    - 实现 `build_install_vnc_cmd(sudo_password)` — 生成安装 x11vnc 的命令
    - 实现 `build_start_vnc_cmd(password, display)` — 生成启动 x11vnc 的命令
    - 实现 `build_install_novnc_cmd(sudo_password)` — 生成安装 noVNC 的命令
    - 实现 `build_start_novnc_cmd(vnc_port, web_port)` — 生成启动 websockify 的命令
    - 实现 `build_stop_cmd()` — 生成停止所有服务的命令
    - _Requirements: 1.2, 1.3, 2.2, 2.3, 5.1_

  - [x] 1.3 实现地址格式化和平台工具函数
    - 实现 `format_vnc_address(ip, port)` — 格式化 VNC 地址
    - 实现 `format_novnc_url(ip, port)` — 格式化 noVNC URL
    - 实现 `get_vnc_launch_cmd(ip, port)` — 返回平台对应的 VNC 启动命令
    - 实现 `open_in_browser(url)` — 跨平台打开浏览器
    - _Requirements: 1.4, 2.4, 4.1, 4.2, 7.1, 7.2, 7.3_

  - [ ]* 1.4 编写 desktop_remote.py 属性测试
    - **Property 1: Service status detection**
    - **Validates: Requirements 1.1, 2.1, 3.1, 3.2**
    - **Property 2: SSH command generation**
    - **Validates: Requirements 1.3, 2.3**
    - **Property 3: Access address formatting**
    - **Validates: Requirements 1.4, 2.4**

- [x] 2. Checkpoint - 确认核心逻辑模块
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. 创建 desktop_dialog.py GUI 对话框
  - [x] 3.1 实现 DesktopRemoteDialog 基础布局
    - 创建 `seeed_jetson_develop/modules/remote/desktop_dialog.py`
    - 标题 + 说明文字
    - 状态区域：VNC 状态标签 + noVNC 状态标签 + 访问地址
    - VNC 密码输入框（可选）
    - 操作按钮行：部署 VNC / 部署 noVNC / 停止服务 / 刷新状态
    - 访问按钮行：打开桌面 (VNC) / 打开桌面 (浏览器)
    - 实时日志区域
    - _Requirements: 3.3, 3.4, 4.4, 8.1, 8.2, 8.3_

  - [x] 3.2 实现部署和管理逻辑
    - 对话框打开时自动检测服务状态（调用 desktop_remote 函数）
    - "部署 VNC" 按钮：检测 → 安装 → 启动 → 更新状态
    - "部署 noVNC" 按钮：检测 → 安装 → 启动 → 更新状态
    - "停止服务" 按钮：停止 → 更新状态
    - "刷新状态" 按钮：重新检测
    - 使用 _SshCmdThread 模式执行后台命令
    - _Requirements: 1.2, 1.3, 1.5, 2.2, 2.3, 2.5, 3.5, 5.1, 5.2, 5.3_

  - [x] 3.3 实现桌面访问入口
    - "打开桌面 (VNC)" 按钮：调用 get_vnc_launch_cmd 启动外部 VNC 客户端
    - "打开桌面 (浏览器)" 按钮：调用 open_in_browser 打开 noVNC URL
    - 找不到 VNC 客户端时显示推荐安装提示
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 3.4 实现错误处理
    - 安装失败显示日志 + 排查建议
    - 启动失败提示 HDMI/显示器要求
    - 端口冲突提示
    - _Requirements: 1.5, 2.5, 5.3_

- [x] 4. 集成到 page.py 开发工具卡片
  - [x] 4.1 在 tool_defs 中新增"远程桌面"入口
    - 添加 import desktop_dialog
    - 在 tool_defs 列表新增远程桌面条目
    - 在 _on_click 中新增 remote_desktop 分支
    - 检查 SSHRunner 连接状态，未连接时提示
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 5. Final checkpoint - 全部集成验证
  - All code implemented and diagnostics clean.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- 核心逻辑和 GUI 分离，方便测试和维护
- 复用现有的 _SshCmdThread 模式，保持代码风格一致
- x11vnc 需要 Jetson 有图形桌面环境（GNOME/XFCE）
- noVNC 是可选增强，VNC 客户端直连也能用
