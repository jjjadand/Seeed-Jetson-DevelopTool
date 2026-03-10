# Seeed Jetson Develop Tool — 上下文文档

## 项目背景

本项目原名 `seeed-jetson-flash`，最初只有烧录（刷机）功能。
根据 PRD 文档（`jetson_Develop_prd.docx`，V0.9），需要大幅扩展为完整的 **Jetson 开发工作台**。

PRD 核心定位：
> 设备管理是入口，Skills 是效率引擎，容器是交付载体，远程开发是长期留存抓手。

---

## 当前文件结构

```
seeed_jetson_flash/
  gui/
    main_window.py          # 原始烧录 UI（已废弃，仅保留兼容）
    main_window_sdk.py      # 重构版烧录 UI（双语，无边框窗口）
    main_window_v2.py       # ★ 新版完整 UI（本次新建，当前主力）
    styles.py               # 原有样式（main_window_v2 未使用，自带样式）
  data/
    l4t_data.json           # 产品 + L4T 版本数据
    product_images.json     # 产品名称 + Wiki 链接
    recovery_guides.json    # Recovery 步骤数据
  flash.py                  # 刷写核心逻辑（JetsonFlasher）
  cli.py                    # CLI 入口
run_v2.py                   # ★ 新版 UI 启动入口
run_gui.py                  # 旧版启动入口
prd_images/                 # 从 PRD docx 提取的参考截图
  image1.png                # 图1：烧录流程界面
  image2.png                # 图2：设备管理首页
  image3.png                # 图3：应用空间
  image4.png                # 图4：示例应用市场
```

---

## main_window_v2.py 设计说明

### 技术栈
- PyQt5，无边框窗口（`FramelessWindowHint`），自定义标题栏可拖动
- 深色主题，Seeed 绿（`#8DC21F`）+ 深蓝配色
- 6 页 `QStackedWidget` + 左侧导航栏

### 6 个页面

| 页面 | 类/方法 | 状态 |
|------|---------|------|
| ⚡ 烧录 | `_build_flash_page` | ✅ 功能完整，复用 `FlashThread` |
| 🖥 设备管理 | `_build_devices_page` | 🎨 UI 完成，逻辑待接入 |
| 📦 应用市场 | `_build_apps_page` | 🎨 UI 完成，数据硬编码 |
| 🤖 Skills | `_build_skills_page` | 🎨 UI 完成，执行逻辑待实现 |
| 💻 远程开发 | `_build_remote_page` | 🎨 UI 完成，连接逻辑待实现 |
| 💬 社区 | `_build_community_page` | ✅ 静态链接，基本完整 |

### 关键类
- `MainWindowV2` — 主窗口
- `FlashThread` — 刷写后台线程（复用自 `main_window_sdk.py`）
- `SidebarButton` — 自定义导航按钮（带激活态高亮）

---

## PRD 要求的功能优先级

### P0（首版必做）
- [x] 烧录功能（已有，已集成到新 UI）
- [ ] 设备体检（网络/GPU Torch/Docker/jtop/摄像头）— 逻辑待实现
- [ ] Skills 执行引擎（参数化执行、状态回传、失败重试）
- [ ] 应用市场（卡片绑定 Demo + Skill + 容器 + 文档）
- [ ] 首批 4 个已验证 Skill 上线：
  - LeRobot 开发环境配置
  - USB-WiFi 驱动适配
  - Qwen Demo 适配
  - 浏览器无法打开修复

### P1（后续版本）
- [ ] 远程开发（VS Code Remote SSH / code-server / Jupyter）
- [ ] 社区内容回流（问题修复结果沉淀）
- [ ] 容器部署（vLLM / Ollama / ROS）

---

## 下一步任务建议

1. **设备体检逻辑**：在 `_build_devices_page` 中接入真实 SSH/本地命令执行，更新诊断项状态
2. **Skills 执行引擎**：设计 Skill 数据结构（JSON），实现参数化执行 + 日志回传
3. **应用市场数据化**：将硬编码的应用列表迁移到 `data/apps.json`
4. **Recovery 指南集成**：在社区页的 Recovery 入口接入 `recovery_guides.json` 数据
5. **样式细化**：对照 `prd_images/` 中的参考截图调整布局细节

---

## 运行方式

```bash
# 新版 UI（推荐）
python3 run_v2.py

# 旧版 UI
python3 run_gui.py
```

## 依赖

```
PyQt5
requests
python-docx  # 仅用于读取 PRD，运行时不需要
```
