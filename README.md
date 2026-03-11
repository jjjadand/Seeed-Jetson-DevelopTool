<<<<<<< HEAD
# Seeed Jetson Flash

一个用于为多款 Seeed Studio Jetson 设备刷机的 Python 命令行工具。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

## 特性

- 🚀 **简单易用**: 一条命令完成固件下载、校验和刷写
- 📦 **自动化**: 自动下载固件、解压、校验 SHA256
- 📖 **详细教程**: 内置各系列产品进入 Recovery 模式的详细教程
- 🎨 **美观输出**: 使用 Rich 库提供彩色、格式化的终端输出
- 🔒 **安全可靠**: SHA256 校验确保固件完整性
- 🌐 **多产品支持**: 支持 Seeed Studio 全系列 Jetson 产品

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install seeed-jetson-flash
```

### 从源码安装

```bash
git clone https://github.com/Seeed-Studio/seeed-jetson-flash.git
cd seeed-jetson-flash
pip install -e .
```

## 快速开始

### 命令行模式

### 1. 查看支持的产品

```bash
seeed-jetson-flash list-products
```

### 2. 查看 Recovery 模式教程

```bash
seeed-jetson-flash recovery -p j4012mini
```

### 3. 刷写固件

```bash
seeed-jetson-flash flash -p j4012mini -l 36.3.0
```

### 图形界面模式

启动 GUI（需要安装 PyQt5）：

```bash
# 安装 PyQt5
pip install PyQt5

# 启动 GUI
seeed-jetson-flash gui
```

GUI 特性：
- 🎨 Seeed Studio 品牌风格设计
- 📱 直观的产品选择界面
- 📊 实时进度显示
- 📝 详细的操作日志
- 🔄 内置 Recovery 模式教程
- 🔗 快速访问相关链接

详细 GUI 使用说明请查看 [GUI_GUIDE.md](GUI_GUIDE.md)

## 支持的设备

### reComputer Super 系列
- J4012s (Orin NX 16GB) - L4T 36.4.3
- J4011s (Orin NX 8GB) - L4T 36.4.3
- J3011s (Orin Nano 8GB) - L4T 36.4.3
- J3010s (Orin Nano 4GB) - L4T 36.4.3

### reComputer Mini 系列
- J4012mini (Orin NX 16GB) - L4T 36.3.0, 35.5.0
- J4011mini (Orin NX 8GB) - L4T 36.3.0, 35.5.0
- J3011mini (Orin Nano 8GB) - L4T 36.4.3, 36.3.0, 35.5.0
- J3010mini (Orin Nano 4GB) - L4T 36.4.3, 36.3.0, 35.5.0

### reComputer Robotics 系列
- J4012robotics (Orin NX 16GB) - L4T 36.4.3
- J4011robotics (Orin NX 8GB) - L4T 36.4.3
- J3011robotics (Orin Nano 8GB) - L4T 36.4.3
- J3010robotics (Orin Nano 4GB) - L4T 36.4.3

### reComputer Classic 系列
- J4012classic (Orin NX 16GB) - L4T 36.4.3, 36.4.0, 36.3.0, 35.5.0
- J4011classic (Orin NX 8GB) - L4T 36.4.3, 36.4.0, 36.3.0, 35.5.0
- J3011classic (Orin Nano 8GB) - L4T 36.4.3, 36.4.0, 36.3.0, 35.5.0
- J3010classic (Orin Nano 4GB) - L4T 36.4.3, 36.4.0, 36.3.0, 35.5.0

### reComputer Industrial 系列
- J4012industrial (Orin NX 16GB)
- J4011industrial (Orin NX 8GB)
- J3011industrial (Orin Nano 8GB)
- J3010industrial (Orin Nano 4GB)
- J2012industrial (Xavier NX 16GB)
- J2011industrial (Xavier NX 8GB)

### reServer Industrial 系列
- J4012reserver, J4011reserver, J3011reserver, J3010reserver

### J501 系列
- J501 Carrier Board (AGX Orin 64GB/32GB)
- J501 Mini (AGX Orin 64GB/32GB)
- J501 Robotics (AGX Orin 64GB/32GB)

## 文档

- 📖 [README.md](README.md) - 项目介绍
- 🚀 [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- 📱 [GUI_GUIDE.md](GUI_GUIDE.md) - GUI 使用指南
- 💻 [USAGE.md](USAGE.md) - 命令行使用指南
- 📦 [INSTALL_GUI.md](INSTALL_GUI.md) - GUI 安装说明
- 📚 [RESOURCES.md](RESOURCES.md) - 资源提取说明
- 📝 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

## 使用说明

详细使用说明请查看 [USAGE.md](USAGE.md)

## 资源说明

本项目从 Seeed Studio 官方文档中提取了以下资源：
- 固件下载链接和 SHA256 校验值
- Recovery 模式进入教程（含图片和视频）
- 产品图片和 Wiki 链接
- 多语言支持（中文、英文、日文、西班牙文）

详细资源说明请查看 [RESOURCES.md](RESOURCES.md)
=======
# jetson-develop

面向 Seeed Studio Jetson 全系列产品的 AI 开发工具集，包含可执行的 Agent Skills 和客户端应用。

## 设计理念

本项目围绕两个核心维度构建：

- **Skills** — 将 Jetson 开发中的高频操作（环境配置、模型部署、驱动适配、故障排查等）封装为 AI Agent 可直接执行的技能包，支持 OpenClaw / Claude Code / Codex (AGENTS.md) 三种主流 Agent 格式
- **Apps** — 提供烧录、诊断、项目脚手架等客户端工具，配合 Skills 实现从刷机到部署的完整开发流程

Skills 覆盖的领域：

| 维度 | 示例 |
|------|------|
| CV / 大模型 / AI 生成 / 机器人 | YOLOv8、DeepSeek、TTS (Dia)、LeRobot |
| 本地部署 / 容器部署 | Ollama、Frigate、NVIDIA Demo 容器 |
| 开发工具链 | PyTorch 安装、vLLM、Docker、jtop |
| 驱动与 BSP | USB-WiFi 适配、SPI、EtherCAT、内核模块编译 |
| 故障排查 | 浏览器修复、SSD 启动、UUID 错误、apt upgrade 防护 |
>>>>>>> f0fd1e47ba44d95427d9a861d3755c67bd92cf7c

## 项目结构

```
<<<<<<< HEAD
seeed-jetson-develop/
├── seeed_jetson_develop/
│   ├── __init__.py          # 包初始化
│   ├── cli.py               # 命令行接口
│   ├── flash.py             # 固件刷写模块
│   ├── recovery.py          # Recovery 教程模块
│   └── data/                # 数据文件
│       ├── l4t_data.json           # 固件信息
│       ├── recovery_guides.json    # Recovery 教程
│       └── product_images.json     # 产品图片
├── setup.py                 # 安装配置
├── requirements.txt         # 依赖包
├── README.md               # 项目说明
├── USAGE.md                # 使用指南
├── RESOURCES.md            # 资源说明
├── LICENSE                 # 许可证
└── MANIFEST.in             # 打包配置
```

## 依赖

- Python 3.6+
- requests
- tqdm
- click
- rich

## 开发

```bash
# 克隆仓库
git clone https://github.com/Seeed-Studio/seeed-jetson-flash.git
cd seeed-jetson-flash

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 技术支持

- 📖 Wiki: https://wiki.seeedstudio.com/
- 💬 论坛: https://forum.seeedstudio.com/
- 📧 邮箱: support@seeedstudio.com
- 💬 Discord: https://discord.gg/eWkprNDMU7

## 相关资源

- [Seeed Jetson 初学者教程](https://github.com/Seeed-Projects/reComputer-Jetson-for-Beginners)
- [Jetson 示例代码](https://github.com/Seeed-Projects/jetson-examples)
- [Seeed L4T 源码](https://github.com/Seeed-Studio/Linux_for_Tegra)
- [NVIDIA Jetson Linux](https://developer.nvidia.com/embedded/jetson-linux)
=======
jetson-develop/
├── SKILLS/
│   ├── openclaw/          # OpenClaw 格式 (SKILL.md) — 优先验证平台
│   ├── claude/            # Claude Code 格式 (CLAUDE.md)
│   ├── codex/             # Codex / AGENTS.md 开放标准格式
│   └── .snapshots/
├── apps/
│   ├── client/            # CLI 入口
│   ├── flashing/          # Jetson 刷机工具 (CLI + GUI)
│   ├── diagnostics/       # 设备诊断日志收集
│   ├── development/       # 项目脚手架生成
│   └── projects/          # 用户项目目录
└── README.md
```

## Skills

当前共 **94 个 Skills**，每个 Skill 同时提供三种 Agent 格式：

| 格式 | 指令文件 | 安装路径 | 说明 |
|------|---------|---------|------|
| OpenClaw | `SKILL.md` | `~/.agents/skills/<name>/` | 优先验证平台 |
| Claude | `CLAUDE.md` | `~/.claude/skills/<name>/` | Claude Code 适配 |
| Codex | `AGENTS.md` | `~/.codex/skills/<name>/` | OpenAI 开放标准 |

每个 Skill 目录结构：

```
<skill-name>/
├── SKILL.md / CLAUDE.md / AGENTS.md   # Agent 指令文件
├── scripts/                            # 可执行脚本（可选）
└── references/                         # 参考数据（可选）
```

### Skill 分类概览

**计算机视觉**：yolov5-object-detection、yolov8-trt、yolov8-deepstream-trt、yolov8-custom-classification、yolov11-depth-distance、yolov26_jetson、train-deploy-yolov8、zero-shot-detection、dashcamnet-xavier-nx-multicamera、traffic-deepstream、maskcam-nano、ai-nvr

**生成式 AI**：deepseek-quick-deploy、deploy-deepseek-mlc、deploy-ollama-anythingllm、deploy-riva-llama2、quantized-llama2-7b-mlc、generative-ai-intro、finetune-llm-llama-factory、local-llm-text-to-image、langchain-output-formatting、local-rag-llamaindex、llama-cpp-rpc-distributed

**多模态 AI**：run-vlm、deploy-live-vlm-webui、speech-vlm、vlm-warehouse-guard、local-chatbot-multimodal、deploy-depth-anything-v3、deploy-efficient-vision-engine

**物理 AI / 机器人**：lerobot-env-setup、gr00t-n1-5-deploy-thor、gr00t-n1-6-deploy-agx、local-chatbot-physical、voice-llm-motor-control、voice-llm-reachy-mini-multimodal、voice-llm-reachy-mini-physical、deploy-nvblox、pinocchio-install、j501-viola-fruit-sorting

**语音 AI**：whisper-realtime-stt、realtime-subtitle-recorder、deploy-dia

**开发工具**：torch-install、jetson-docker-setup、jetson-ai-tools、vnc-setup、gpt-oss-live、llm-interface-control、nvstreamer-setup、no-code-edge-ai

**驱动与 BSP**：bsp-source-build、diy-bsp-build、ko-module-build、spi-enable-jetsonnano、usb-wifi-88x2bu-setup、ethercat-setup、ethercat-communication、imx477-a603-setup、recomputer-veye-compat-fix、l4t-differences

**刷机与系统**：jetpack-flash-wsl2、jetpack-ota-update、jetpack-jetson-overview、jetpack5-ssd-boot-fix、backup-restore、disk-encryption、ota-deploy、software-package-upgrade、fix-browser-snap-jetson、uuid-error-fix、usb-timeout-during-flashing、security-scan、system-log-j30-j40

**第三方平台集成**：allxon-setup、allxon-ota-update、alwaysai-setup、cochl-sense-setup、cvedia-setup、deciai-setup、deploy-frigate、gapi-setup、hardhat-setup、lumeo-setup、neqto-engine-setup、roboflow-setup、scailable-setup

**知识库**：jetson-faq、jetson-resource-index、jetson-project-gallery、jetson-tutorial-exercises

### 编写新 Skill

参考各格式目录下的 `HOW_TO_WRITE_SKILLS.md`：

- [OpenClaw 编写指南](SKILLS/openclaw/HOW_TO_WRITE_SKILLS.md)
- [Claude 编写指南](SKILLS/claude/HOW_TO_WRITE_SKILLS.md)
- [Codex 编写指南](SKILLS/codex/HOW_TO_WRITE_SKILLS.md)

核心原则：
1. 长操作拆分为 Phase，每个 Phase 幂等可重入
2. 使用 `[install]` / `[STOP]` / `[OK]` 日志协议让 Agent 可解析输出
3. 每个 Skill 必须包含 Failure Decision Table

## Apps

### 刷机工具 (`apps/flashing/`)

支持 Seeed 全系列 Jetson 产品的固件刷写，提供 CLI 和 GUI 两种模式。

```bash
# CLI
seeed-jetson-flash flash -p j4012mini -l 36.3.0

# GUI
seeed-jetson-flash gui
```

详见 [apps/flashing/README.md](apps/flashing/README.md)

### 诊断工具 (`apps/diagnostics/`)

一键收集 Jetson 设备的系统信息、日志、硬件状态，打包为 tar.gz 归档。

```bash
bash apps/diagnostics/collect_jetson_logs.sh
```

### 项目脚手架 (`apps/development/`)

按模板（cv / genai / robotics / general）快速创建 Jetson 应用项目结构。

```bash
bash apps/development/create_app_workspace.sh my-app cv
```

### CLI 入口 (`apps/client/`)

统一的交互式命令行入口，整合刷机、脚手架、诊断功能。

```bash
bash apps/client/jetson_dev_cli.sh
```

## 快速开始

```bash
# 克隆仓库
git clone <repo-url>
cd jetson-develop

# 安装刷机工具
pip install -e apps/flashing/

# 使用 CLI
bash apps/client/jetson_dev_cli.sh
```

Skills 的使用取决于你的 Agent 平台：

```bash
# OpenClaw
cp -r SKILLS/openclaw/<skill-name> ~/.agents/skills/<skill-name>

# Claude Code
cp -r SKILLS/claude/<skill-name> ~/.claude/skills/<skill-name>

# Codex / AGENTS.md 兼容 Agent
cp -r SKILLS/codex/<skill-name> ~/.codex/skills/<skill-name>
```


## 技术支持

- Wiki: https://wiki.seeedstudio.com/
- 论坛: https://forum.seeedstudio.com/
- Discord: https://discord.gg/eWkprNDMU7

## License

MIT
>>>>>>> f0fd1e47ba44d95427d9a861d3755c67bd92cf7c
