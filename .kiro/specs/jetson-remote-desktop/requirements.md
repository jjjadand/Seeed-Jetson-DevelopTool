# Requirements Document

## Introduction

为 Seeed Jetson 开发工具客户端新增"远程桌面"功能，使用户可以通过 PC 客户端查看和操控 Jetson 的图形桌面。采用分阶段架构：第一阶段客户端作为控制面，通过 SSH 在 Jetson 上部署 VNC/noVNC 服务，然后引导用户通过浏览器或外部 VNC 客户端访问桌面；第二阶段可选内嵌 WebView。

当前客户端技术栈为 PyQt5 + paramiko + pyserial，不含 QtWebEngine 或流媒体库，因此第一阶段不在客户端内嵌桌面渲染，而是走"SSH 部署 + 外部访问"路线。

## Glossary

- **Client**: PC 端的 Seeed Jetson 开发工具（PyQt5 应用），运行在 Linux 或 Windows 上
- **Jetson**: 远端 Jetson 设备，通过 SSH 连接
- **SSHRunner**: 客户端中已有的 SSH 命令执行器，通过 paramiko 实现
- **VNC_Server**: 在 Jetson 上运行的 VNC 服务（x11vnc 或 vino）
- **noVNC_Server**: 基于 WebSocket 的 VNC 代理，提供浏览器可访问的 VNC 页面
- **Desktop_Deployer**: 客户端中负责部署和管理远程桌面服务的模块
- **Desktop_Dialog**: 客户端中远程桌面功能的 GUI 对话框

## Requirements

### Requirement 1: 远程桌面服务部署

**User Story:** As a developer, I want to deploy a VNC desktop service on Jetson through the client, so that I can view and control the Jetson graphical desktop remotely.

#### Acceptance Criteria

1. WHEN a user clicks the "部署桌面" button, THE Desktop_Deployer SHALL check if x11vnc is installed on Jetson via SSHRunner
2. IF x11vnc is not installed, THEN THE Desktop_Deployer SHALL install x11vnc via `apt-get install -y x11vnc` using SSHRunner
3. WHEN x11vnc installation completes, THE Desktop_Deployer SHALL start x11vnc bound to the Jetson display (:0) with a user-specified or default password
4. WHEN x11vnc starts successfully, THE Desktop_Deployer SHALL report the VNC access address (Jetson_IP:5900) to the user
5. IF x11vnc installation or startup fails, THEN THE Desktop_Deployer SHALL display the error output and suggest troubleshooting steps

### Requirement 2: noVNC Web 代理部署

**User Story:** As a developer, I want to optionally deploy noVNC on Jetson, so that I can access the desktop through a web browser without installing a VNC client.

#### Acceptance Criteria

1. WHEN a user clicks "部署 noVNC", THE Desktop_Deployer SHALL check if noVNC and websockify are installed on Jetson
2. IF noVNC is not installed, THEN THE Desktop_Deployer SHALL install noVNC and websockify via apt or pip
3. WHEN noVNC is installed, THE Desktop_Deployer SHALL start websockify to proxy VNC port 5900 to a web-accessible port (default 6080)
4. WHEN noVNC starts successfully, THE Desktop_Deployer SHALL report the browser access URL (http://Jetson_IP:6080/vnc.html) to the user
5. IF noVNC deployment fails, THEN THE Desktop_Deployer SHALL display the error output in the log area

### Requirement 3: 远程桌面服务状态检测

**User Story:** As a developer, I want to see the current status of the remote desktop service, so that I know whether VNC/noVNC is running on Jetson.

#### Acceptance Criteria

1. WHEN the desktop dialog opens, THE Desktop_Dialog SHALL check if x11vnc process is running on Jetson via SSHRunner
2. WHEN the desktop dialog opens, THE Desktop_Dialog SHALL check if websockify/noVNC process is running on Jetson via SSHRunner
3. WHEN VNC service is detected as running, THE Desktop_Dialog SHALL display the status as "运行中" with the access address
4. WHEN VNC service is not running, THE Desktop_Dialog SHALL display the status as "未运行"
5. WHEN the user clicks "刷新状态", THE Desktop_Dialog SHALL re-check all service statuses

### Requirement 4: 远程桌面访问入口

**User Story:** As a developer, I want convenient access to the Jetson desktop, so that I can quickly open the desktop view.

#### Acceptance Criteria

1. WHEN VNC is running and user clicks "打开桌面 (VNC)", THE Client SHALL attempt to launch the system default VNC viewer with the Jetson VNC address
2. WHEN noVNC is running and user clicks "打开桌面 (浏览器)", THE Client SHALL open the default web browser with the noVNC URL
3. IF no VNC viewer is found on the system, THEN THE Client SHALL display a message suggesting VNC viewer installation (RealVNC Viewer, TigerVNC, Remmina)
4. THE Desktop_Dialog SHALL display the VNC address and noVNC URL as copyable text for manual access

### Requirement 5: 远程桌面服务停止

**User Story:** As a developer, I want to stop the remote desktop service when I no longer need it, so that Jetson resources are freed.

#### Acceptance Criteria

1. WHEN a user clicks "停止桌面服务", THE Desktop_Deployer SHALL kill x11vnc and websockify processes on Jetson via SSHRunner
2. WHEN the stop command completes, THE Desktop_Dialog SHALL update the status to "已停止"
3. IF the stop command fails, THEN THE Desktop_Dialog SHALL display the error in the log area

### Requirement 6: 开发工具页集成

**User Story:** As a developer, I want to access the remote desktop feature from the development tools page, so that it is consistent with other tools like VS Code and Jupyter.

#### Acceptance Criteria

1. THE Client SHALL add a "远程桌面" entry in the development tools card (卡片 D) of the remote development page
2. WHEN the user clicks the "远程桌面" action button, THE Client SHALL open the Desktop_Dialog
3. WHEN the user has not established an SSH connection, THE Client SHALL warn the user to connect first before opening the Desktop_Dialog

### Requirement 7: 跨平台兼容

**User Story:** As a developer using either Linux or Windows, I want the remote desktop feature to work on both platforms, so that I can use it regardless of my PC's operating system.

#### Acceptance Criteria

1. WHEN running on Linux, THE Client SHALL attempt to launch VNC viewer using `xdg-open` or known VNC client commands (vncviewer, remmina)
2. WHEN running on Windows, THE Client SHALL attempt to launch VNC viewer using the system default handler for vnc:// protocol or suggest downloading a VNC client
3. WHEN opening a browser URL, THE Client SHALL use Python's `webbrowser.open()` for cross-platform compatibility
4. THE Desktop_Deployer SHALL use SSH commands compatible with Ubuntu-based Jetson systems (apt-get, systemctl)

### Requirement 8: 部署日志

**User Story:** As a developer, I want to see the deployment log in real-time, so that I can monitor progress and diagnose issues.

#### Acceptance Criteria

1. WHILE a deployment or service operation is in progress, THE Desktop_Dialog SHALL display real-time command output in a log area
2. WHEN a command completes, THE Desktop_Dialog SHALL append the result status (success/failure) to the log
3. THE Desktop_Dialog SHALL allow the user to scroll through the full log history
