"""Reusable AI chat panel and floating assistant entry."""

import os

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject, QEvent, QPoint, QRect
from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
)

from seeed_jetson_develop.core.config import load as load_config, save as save_config
from seeed_jetson_develop.gui.theme import (
    C_BG_DEEP,
    C_CARD,
    C_CARD_LIGHT,
    C_GREEN,
    C_BLUE,
    C_TEXT,
    C_TEXT2,
    C_TEXT3,
    pt as _pt,
    make_label as _lbl,
    make_button as _btn,
)


_DEFAULT_SYSTEM = (
    "你是 Seeed Jetson Develop Tool 的 AI 助手，专注于 NVIDIA Jetson 开发板的开发、配置和问题排查。"
    "你了解 Jetson Nano、Orin Nano、Orin NX 等型号，熟悉 JetPack、L4T、CUDA、TensorRT、ROS 等技术。"
    "回答尽量简洁，需要给命令时使用代码块格式。默认使用中文回答。"
)


def build_ai_system_prompt(limit: int = 30) -> str:
    system = _DEFAULT_SYSTEM
    try:
        from seeed_jetson_develop.modules.skills.engine import load_skills
        skills = load_skills()
        skills_text = "\n".join(
            f"- {s.name}（{s.category}）：{s.desc}"
            for s in skills[:limit]
        )
        if skills_text:
            system += (
                "\n\n可用 Skills 列表（供参考，用户可在 Skills 页面一键运行）：\n"
                f"{skills_text}"
            )
    except Exception:
        pass
    return system


def _get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        key = load_config().get("anthropic_api_key", "")
    return key


def _get_base_url() -> str:
    url = os.environ.get("ANTHROPIC_BASE_URL", "")
    if not url:
        url = load_config().get("anthropic_base_url", "")
    return url


class _AiThread(QThread):
    token = pyqtSignal(str)
    done = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, messages: list, system: str, api_key: str, base_url: str = ""):
        super().__init__()
        self._messages = messages
        self._system = system
        self._api_key = api_key
        self._base_url = base_url
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            import anthropic
            base_url = self._base_url or "https://api.anthropic.com"
            client = anthropic.Anthropic(api_key=self._api_key, base_url=base_url)
            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=2048,
                system=self._system,
                messages=self._messages,
            ) as stream:
                for text in stream.text_stream:
                    if self._cancel:
                        break
                    self.token.emit(text)
        except Exception as exc:
            base_url = self._base_url or "https://api.anthropic.com"
            self.error.emit(f"{exc}\n[base_url: {base_url}]")
        finally:
            self.done.emit()


class _MsgBubble(QFrame):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        bg = "rgba(122,179,23,0.12)" if is_user else C_CARD
        color = C_TEXT if is_user else C_TEXT2
        self.setStyleSheet(f"background:{bg}; border:none; border-radius:10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(0)

        self._label = QLabel(text)
        self._label.setWordWrap(True)
        self._label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._label.setStyleSheet(
            f"color:{color}; font-size:{_pt(11)}pt; background:transparent; border:none;"
        )
        layout.addWidget(self._label)

    def set_text(self, text: str):
        self._label.setText(text)


class AIChatPanel(QWidget):
    def __init__(self, system_prompt: str = "", title: str = "AI 助手", parent=None):
        super().__init__(parent)
        self._system = system_prompt or _DEFAULT_SYSTEM
        self._history = []
        self._thread = None
        self._cur_bubble = None
        self._cur_text = ""
        self._setup_ui(title)

    def _setup_ui(self, title: str):
        self.setStyleSheet(f"background:{C_BG_DEEP}; border:none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{C_GREEN}; font-size:{_pt(8)}pt; background:transparent;")
        title_row.addWidget(dot)
        title_row.addSpacing(6)
        title_row.addWidget(_lbl(title, 13, C_TEXT, bold=True))
        title_row.addStretch()

        has_key = bool(_get_api_key())
        if not has_key:
            key_btn = QPushButton("配置 Key")
            key_btn.setCursor(Qt.PointingHandCursor)
            key_btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(44,123,229,0.15);
                    border: none;
                    border-radius: 6px;
                    color: {C_BLUE};
                    font-size: {_pt(10)}pt;
                    padding: 3px 8px;
                }}
                QPushButton:hover {{ background: rgba(44,123,229,0.25); }}
            """)
            key_btn.clicked.connect(self._toggle_key_frame)
            title_row.addWidget(key_btn)
        layout.addLayout(title_row)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("background:transparent; border:none;")

        self._msg_widget = QWidget()
        self._msg_widget.setStyleSheet("background:transparent;")
        self._msg_layout = QVBoxLayout(self._msg_widget)
        self._msg_layout.setContentsMargins(0, 4, 0, 4)
        self._msg_layout.setSpacing(8)
        self._msg_layout.addStretch()
        self._scroll.setWidget(self._msg_widget)
        layout.addWidget(self._scroll, 1)

        self._key_frame = QFrame()
        self._key_frame.setStyleSheet(f"background:{C_CARD}; border:none; border-radius:8px;")
        key_layout = QHBoxLayout(self._key_frame)
        key_layout.setContentsMargins(10, 6, 10, 6)
        key_layout.setSpacing(8)
        key_layout.addWidget(_lbl("API Key:", 10, C_TEXT3))

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("sk-ant-...")
        self._key_input.setEchoMode(QLineEdit.Password)
        self._key_input.setStyleSheet(f"""
            QLineEdit {{
                background:{C_CARD_LIGHT};
                border:none;
                border-radius:6px;
                padding:4px 10px;
                color:{C_TEXT};
                font-size:{_pt(10)}pt;
            }}
        """)
        self._key_input.setFixedHeight(_pt(30))
        save_btn = _btn("保存", primary=True, small=True)
        save_btn.setFixedWidth(_pt(52))
        save_btn.clicked.connect(self._save_key)
        key_layout.addWidget(self._key_input, 1)
        key_layout.addWidget(save_btn)
        self._key_frame.setVisible(False)
        layout.addWidget(self._key_frame)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("输入问题，按 Enter 发送")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background:{C_CARD_LIGHT};
                border:none;
                border-radius:8px;
                padding:8px 14px;
                color:{C_TEXT};
                font-size:{_pt(11)}pt;
            }}
            QLineEdit:focus {{ background:{C_CARD}; }}
        """)
        self._input.setFixedHeight(_pt(40))
        self._input.returnPressed.connect(self._on_send)

        self._send_btn = _btn("发送", primary=True, small=True)
        self._send_btn.setFixedWidth(_pt(60))
        self._send_btn.clicked.connect(self._on_send)

        input_row.addWidget(self._input, 1)
        input_row.addWidget(self._send_btn)
        layout.addLayout(input_row)

        if not has_key:
            self._add_ai_bubble("请先配置 Anthropic API Key，然后再使用 AI 助手。")
        else:
            self._add_ai_bubble("你好，我是 Jetson 开发助手。你可以直接问我 Jetson、Skills、环境配置和排障问题。")

    def set_system(self, prompt: str):
        self._system = prompt

    def inject_context(self, skill_name: str, skill_desc: str, commands: list):
        commands_text = ""
        if commands:
            preview = "\n".join(commands[:8])
            commands_text = f"\n\n命令预览：\n```bash\n{preview}\n```"
        text = f"帮我介绍一下这个 Skill：**{skill_name}**\n\n描述：{skill_desc}{commands_text}"
        self._add_user_bubble(text)
        self._fire_ai()

    def _toggle_key_frame(self):
        self._key_frame.setVisible(not self._key_frame.isVisible())

    def _save_key(self):
        key = self._key_input.text().strip()
        if not key:
            return
        cfg = load_config()
        cfg["anthropic_api_key"] = key
        save_config(cfg)
        self._key_frame.setVisible(False)
        self._key_input.clear()
        self._add_ai_bubble("API Key 已保存，现在可以开始对话了。")

    def _on_send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._add_user_bubble(text)
        self._fire_ai()

    def _add_user_bubble(self, text: str):
        self._history.append({"role": "user", "content": text})
        self._insert_bubble(text, is_user=True)

    def _add_ai_bubble(self, text: str = ""):
        return self._insert_bubble(text, is_user=False)

    def _insert_bubble(self, text: str, is_user: bool):
        bubble = _MsgBubble(text, is_user, self._msg_widget)
        self._msg_layout.insertWidget(self._msg_layout.count() - 1, bubble)
        QTimer.singleShot(30, self._scroll_to_bottom)
        return bubble

    def _scroll_to_bottom(self):
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _fire_ai(self):
        api_key = _get_api_key()
        if not api_key:
            self._add_ai_bubble("未找到 API Key，请先点击「配置 Key」。")
            return
        if self._thread and self._thread.isRunning():
            return

        self._cur_bubble = self._add_ai_bubble("")
        self._cur_text = ""
        self._send_btn.setEnabled(False)
        self._input.setEnabled(False)

        self._thread = _AiThread(
            messages=list(self._history),
            system=self._system,
            api_key=api_key,
            base_url=_get_base_url(),
        )
        self._thread.token.connect(self._on_token)
        self._thread.done.connect(self._on_done)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_token(self, token: str):
        self._cur_text += token
        if self._cur_bubble:
            self._cur_bubble.set_text(self._cur_text)
        self._scroll_to_bottom()

    def _on_done(self):
        self._send_btn.setEnabled(True)
        self._input.setEnabled(True)
        if self._cur_text:
            self._history.append({"role": "assistant", "content": self._cur_text})
        self._cur_bubble = None
        self._cur_text = ""

    def _on_error(self, msg: str):
        if self._cur_bubble:
            self._cur_bubble.set_text(f"请求失败：{msg}")
        self._send_btn.setEnabled(True)
        self._input.setEnabled(True)


class FloatingAIAssistant(QObject):
    def __init__(self, host: QWidget, system_prompt: str = "", title: str = "AI 助手"):
        super().__init__(host)
        self._host = host
        self._title = title
        self._system = system_prompt or build_ai_system_prompt()
        self._ball_size = _pt(60)
        self._panel_w = _pt(420)
        self._panel_h = _pt(560)
        self._margin = _pt(24)
        self._gap = _pt(14)
        self._top_safe = _pt(84)
        self._dragging = False
        self._drag_moved = False
        self._drag_offset = QPoint()
        self._ball_pos = QPoint()
        self._expanded = False
        self._build_ui()
        self._host.installEventFilter(self)
        self._ball.installEventFilter(self)
        self._snap_to_corner()
        self._update_positions()

    def _build_ui(self):
        self._panel = QFrame(self._host)
        self._panel.setObjectName("FloatingAIPanel")
        self._panel.setStyleSheet(f"""
            QFrame#FloatingAIPanel {{
                background: {C_BG_DEEP};
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 18px;
            }}
        """)
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        header = QFrame(self._panel)
        header.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 12, 10)
        header_layout.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet(f"color:{C_GREEN}; font-size:{_pt(9)}pt; background:transparent;")
        header_layout.addWidget(dot)
        header_layout.addWidget(_lbl(self._title, 13, C_TEXT, bold=True))
        header_layout.addWidget(_lbl("Jetson 开发助手", 10, C_TEXT3))
        header_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(_pt(28), _pt(28))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.05);
                border: none;
                border-radius: 14px;
                color: {C_TEXT2};
                font-size: {_pt(14)}pt;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.10);
                color: {C_TEXT};
            }}
        """)
        close_btn.clicked.connect(self.hide_panel)
        header_layout.addWidget(close_btn)
        panel_layout.addWidget(header)

        self._chat = AIChatPanel(system_prompt=self._system, title=self._title, parent=self._panel)
        panel_layout.addWidget(self._chat, 1)
        self._panel.resize(self._panel_w, self._panel_h)
        self._panel.hide()

        self._ball = QPushButton("AI", self._host)
        self._ball.setCursor(Qt.PointingHandCursor)
        self._ball.setFixedSize(self._ball_size, self._ball_size)
        self._ball.setStyleSheet(f"""
            QPushButton {{
                background: qradialgradient(cx:0.35, cy:0.30, radius:0.9,
                    fx:0.35, fy:0.30,
                    stop:0 #A8D93A,
                    stop:0.58 #7AB317,
                    stop:1 #496F0E);
                border: 1px solid rgba(255,255,255,0.20);
                border-radius: {self._ball_size // 2}px;
                color: #071200;
                font-size: {_pt(12)}pt;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: qradialgradient(cx:0.35, cy:0.30, radius:0.9,
                    fx:0.35, fy:0.30,
                    stop:0 #B7E34B,
                    stop:0.58 #89C420,
                    stop:1 #587F14);
            }}
        """)
        self._ball.raise_()

    def eventFilter(self, obj, event):
        if obj is self._host and event.type() in {QEvent.Resize, QEvent.Show}:
            self._constrain_ball()
            self._update_positions()
        elif obj is self._ball:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._dragging = True
                self._drag_moved = False
                self._drag_offset = event.pos()
                return True
            if event.type() == QEvent.MouseMove and self._dragging:
                new_pos = self._ball.mapToParent(event.pos() - self._drag_offset)
                if (new_pos - self._ball_pos).manhattanLength() > 3:
                    self._drag_moved = True
                self._set_ball_pos(new_pos)
                return True
            if event.type() == QEvent.MouseButtonRelease and self._dragging:
                self._dragging = False
                if self._drag_moved:
                    self._snap_to_side()
                else:
                    self.toggle_panel()
                return True
        return super().eventFilter(obj, event)

    def toggle_panel(self):
        if self._expanded:
            self.hide_panel()
        else:
            self.show_panel()

    def show_panel(self):
        self._expanded = True
        self._panel.show()
        self._update_positions()
        self._panel.raise_()
        self._ball.raise_()

    def hide_panel(self):
        self._expanded = False
        self._panel.hide()
        self._ball.raise_()

    def _set_ball_pos(self, pos: QPoint):
        rect = self._safe_ball_rect()
        x = min(max(pos.x(), rect.left()), rect.right())
        y = min(max(pos.y(), rect.top()), rect.bottom())
        self._ball_pos = QPoint(x, y)
        self._update_positions()

    def _snap_to_corner(self):
        rect = self._safe_ball_rect()
        self._ball_pos = QPoint(rect.right(), rect.bottom())

    def _snap_to_side(self):
        rect = self._safe_ball_rect()
        center_x = self._ball_pos.x() + self._ball_size / 2
        target_x = rect.left() if center_x < self._host.width() / 2 else rect.right()
        self._ball_pos = QPoint(target_x, min(max(self._ball_pos.y(), rect.top()), rect.bottom()))
        self._update_positions()

    def _constrain_ball(self):
        if self._ball_pos.isNull():
            self._snap_to_corner()
            return
        self._set_ball_pos(self._ball_pos)

    def _safe_ball_rect(self) -> QRect:
        left = self._margin
        top = self._top_safe
        right = max(left, self._host.width() - self._margin - self._ball_size)
        bottom = max(top, self._host.height() - self._margin - self._ball_size)
        return QRect(left, top, max(1, right - left + 1), max(1, bottom - top + 1))

    def _update_positions(self):
        self._ball.move(self._ball_pos)
        self._ball.raise_()
        if not self._expanded:
            return

        ball_x = self._ball_pos.x()
        ball_y = self._ball_pos.y()
        host_w = self._host.width()
        host_h = self._host.height()

        if ball_x + (self._ball_size // 2) >= host_w / 2:
            panel_x = ball_x + self._ball_size - self._panel_w
        else:
            panel_x = ball_x
        panel_y = ball_y - self._panel_h - self._gap

        panel_x = max(self._margin, min(panel_x, host_w - self._panel_w - self._margin))
        min_y = self._top_safe
        max_y = max(min_y, host_h - self._panel_h - self._ball_size - self._gap - self._margin)
        panel_y = max(min_y, min(panel_y, max_y))

        self._panel.move(panel_x, panel_y)
        self._panel.raise_()
