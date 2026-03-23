# Seeed Jetson Develop Tool

面向 Seeed Studio Jetson 全系列产品的 AI 开发工作台，覆盖从刷机到应用部署的完整流程。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

![UI Preview](assets/reference-UI.png)

---

## 功能概览

| 模块 | 状态 | 说明 |
|------|------|------|
| 烧录 | ✅ | 全系列 Jetson 固件下载、SHA256 校验、一键刷写 |
| 设备管理 | ✅ | 快速诊断、外设检测、设备信息采集 |
| Skills | ✅ | 50+ 内置技能 + OpenClaw 社区技能，覆盖驱动、AI 部署、系统优化 |
| 环境配置 | 🚧 | 一键配置 PyTorch、Docker、jtop 等开发环境 |
| 应用市场 | 🚧 | AI 应用一键安装（YOLOv8、Ollama、DeepSeek 等） |
| 远程开发 | 🚧 | SSH 连接管理、VS Code Remote 集成 |

---

## 安装

**系统要求**：Ubuntu 20.04 / 22.04，Python 3.8+，PyQt5

```bash
git clone https://github.com/Seeed-Studio/seeed-jetson-develop.git
cd seeed-jetson-develop
pip install -r requirements.txt
```

启动 GUI：

```bash
python3 run_v2.py
```

---

## 支持设备

### reComputer Super
J4012s / J4011s / J3011s / J3010s — L4T 36.4.3

### reComputer Mini
J4012mini / J4011mini — L4T 36.3.0, 35.5.0
J3011mini / J3010mini — L4T 36.4.3, 36.3.0, 35.5.0

### reComputer Robotics
J4012robotics / J4011robotics / J3011robotics / J3010robotics — L4T 36.4.3

### reComputer Classic
J4012classic / J4011classic / J3011classic / J3010classic — L4T 36.4.3, 36.4.0, 36.3.0, 35.5.0

### reComputer Industrial
J4012industrial / J4011industrial / J3011industrial / J3010industrial — L4T 36.4.3, 36.4.0, 36.3.0, 35.5.0, 35.3.1
J2012industrial / J2011industrial (Xavier NX) — L4T 35.5.0, 35.3.1

### reServer Industrial
J4012reserver / J4011reserver / J3011reserver / J3010reserver — L4T 36.4.3, 36.4.0, 36.3.0

### J501 系列（AGX Orin）
64GB / 32GB，含 GMSL 版本 — L4T 36.4.3, 36.3.0, 35.5.0

---

## CLI

```bash
# 列出支持的产品
python3 -m seeed_jetson_develop.cli list-products

# 查看 Recovery 教程
python3 -m seeed_jetson_develop.cli recovery -p j4012mini

# 刷写固件
python3 -m seeed_jetson_develop.cli flash -p j4012mini -l 36.3.0
```

---

## Skills

内置 50+ 技能，覆盖以下方向：

- **驱动 & 系统修复**：USB-WiFi、5G 模块、蓝牙冲突、NVMe 启动、Docker 清理
- **AI & 大模型**：PyTorch、Ollama、DeepSeek、Qwen2、LeRobot、vLLM
- **视觉 / YOLO**：YOLOv8、DeepStream、NVBLOX、深度估计
- **网络 & 远程**：VS Code Server、VNC、SSH 密钥、代理配置
- **系统优化**：最大性能模式、Swap 配置、风扇控制、缓存清理

同时支持 [OpenClaw](https://github.com/Seeed-Studio/openclaw) 格式的社区技能，放入 `skills/openclaw/` 目录后自动加载。

---

## 文档

- [QUICKSTART.md](docs/QUICKSTART.md) — 快速上手
- [USAGE.md](docs/USAGE.md) — CLI 详细用法
- [GUI_GUIDE.md](docs/GUI_GUIDE.md) — GUI 使用指南
- [CONTEXT.md](CONTEXT.md) — 工程架构说明

---

## 技术支持

- Wiki：https://wiki.seeedstudio.com/
- 论坛：https://forum.seeedstudio.com/
- Discord：https://discord.gg/eWkprNDMU7

## License

MIT
