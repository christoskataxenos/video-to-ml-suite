import subprocess
import json
import os
import sys
import multiprocessing
import locale
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, 
                               QTextEdit, QLineEdit, QScrollArea, QProgressBar, QDialog, QGridLayout)
from PySide6.QtGui import QIcon, QPixmap, QCursor
from PySide6.QtCore import Qt, QSize, QEvent

from shared.strings import get_string
from shared.utils import get_resource_path, load_config, save_config

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VIDEO TO ML SUITE")
        self.resize(1280, 800)
        self.setMinimumSize(1280, 800)
        
        self.config = load_config()
        
        # Εφαρμογή QSS StyleSheet
        try:
            with open(get_resource_path("shared/style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except:
            pass

        # Ορισμός εικονιδίου εφαρμογής
        try:
            icon_p = get_resource_path(os.path.join("shared", "icon.ico"))
            if os.path.exists(icon_p):
                self.setWindowIcon(QIcon(icon_p))
        except: pass

        self.setup_ui()
        self.log("Το σύστημα αρχικοποιήθηκε. Καλώς ήρθατε στο Video to ML Suite.")

    def event(self, event):
        if event.type() == QEvent.WindowActivate:
            self.config = load_config()
            self.setup_ui()
        return super().event(event)

    def load_config(self):
        # Redirect to shared util
        self.config = load_config()

    def save_config(self):
        if save_config(self.config):
            self.log(get_string("config_saved"))

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Αριστερή Μπάρα (Help & Status)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("HelpSidebar")
        self.sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setAlignment(Qt.AlignTop)
        
        main_layout.addWidget(self.sidebar)
        self.setup_sidebar_content(sidebar_layout)

        # Κύριο περιεχόμενο (Δεξιά)
        self.main_container = QWidget()
        main_area_layout = QVBoxLayout(self.main_container)
        main_area_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.addWidget(self.main_container, 1)

        # Header Frame
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)
        header_layout.setSpacing(15)
        
        lbl_header = QLabel(get_string("dashboard_title"))
        lbl_header.setStyleSheet("font-size: 28px; font-weight: bold;")
        header_layout.addWidget(lbl_header)
        
        header_layout.addStretch()
        
        mode_text = get_string("mode_guided") if self.config.get("mode") == "guided" else get_string("mode_expert")
        self.mode_btn = QPushButton(mode_text)
        self.mode_btn.setObjectName("PurpleButton")
        self.mode_btn.setFixedWidth(120)
        self.mode_btn.clicked.connect(self.toggle_mode)
        
        circle_btn_style = """
            QPushButton {
                background-color: #181A1D;
                border: 1px solid #333333;
                border-radius: 20px;
                color: #888888;
                font-weight: bold;
                font-size: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #222222;
                border: 1px solid #00E5FF;
                color: #00E5FF;
            }
        """
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings_btn.setStyleSheet(circle_btn_style)
        self.settings_btn.clicked.connect(self.show_settings)
        
        lang_text = "ΕΛ" if self.config.get("language") == "el" else "EN"
        self.lang_btn = QPushButton(lang_text)
        self.lang_btn.setFixedSize(40, 40)
        self.lang_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.lang_btn.setStyleSheet(circle_btn_style)
        self.lang_btn.clicked.connect(self.toggle_language)
        
        header_layout.addWidget(self.mode_btn)
        header_layout.addWidget(self.settings_btn)
        header_layout.addWidget(self.lang_btn)
        
        main_area_layout.addWidget(header_frame)
        
        # Λογότυπο εφαρμογής
        try:
            logo_p = get_resource_path(os.path.join("shared", "logo.png"))
            if os.path.exists(logo_p):
                lbl_logo = QLabel()
                pixmap = QPixmap(logo_p).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_logo.setPixmap(pixmap)
                main_area_layout.addWidget(lbl_logo)
        except: pass

        # Grid / Modules Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QVBoxLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(5)
        
        if self.config.get("mode") == "guided":
            self.setup_guided_dashboard()
        else:
            self.setup_expert_dashboard()
            
        self.grid_layout.addStretch()
        scroll_area.setWidget(self.grid_container)
        main_area_layout.addWidget(scroll_area, 1)

        # Logs
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(120)
        self.log_box.setStyleSheet("font-size: 11px; color: #888888; background: #0C0D0E; border: 1px solid #333;")
        main_area_layout.addWidget(self.log_box)

        # Version
        lbl_version = QLabel(get_string("version_label"))
        lbl_version.setAlignment(Qt.AlignRight)
        lbl_version.setStyleSheet("font-size: 10px; color: #444;")
        main_area_layout.addWidget(lbl_version)

    def setup_expert_dashboard(self):
        grid = QGridLayout()
        grid.setSpacing(20)
        
        grid.addWidget(self.create_card_btn(get_string("module_1_title"), get_string("module_1_desc"), "#00E5FF", self.launch_generator), 0, 0)
        grid.addWidget(self.create_card_btn(get_string("module_2_title"), get_string("module_2_desc"), "#6F4A8E", self.launch_labeler), 0, 1)
        grid.addWidget(self.create_card_btn(get_string("module_3_title"), get_string("module_3_desc"), "#00E5FF", self.launch_inspector), 0, 2)
        grid.addWidget(self.create_card_btn(get_string("module_4_title"), get_string("module_4_desc"), "#4C8C72", self.launch_trainer), 1, 0)
        grid.addWidget(self.create_card_btn(get_string("module_5_title"), get_string("module_5_desc"), "#FFD700", self.launch_deployer), 1, 1)
        
        self.grid_layout.addLayout(grid)

    def setup_guided_dashboard(self):
        steps = [
            {"id": "extraction", "title": get_string("module_1_title"), "desc": get_string("module_1_desc"), "cmd": self.launch_generator, "color": "#00E5FF"},
            {"id": "annotation", "title": get_string("module_2_title"), "desc": get_string("module_2_desc"), "cmd": self.launch_labeler, "color": "#6F4A8E"},
            {"id": "inspection", "title": get_string("module_3_title"), "desc": get_string("module_3_desc"), "cmd": self.launch_inspector, "color": "#00E5FF"},
            {"id": "training", "title": get_string("module_4_title"), "desc": get_string("module_4_desc"), "cmd": self.launch_trainer, "color": "#4C8C72"},
            {"id": "deployment", "title": get_string("module_5_title"), "desc": get_string("module_5_desc"), "cmd": self.launch_deployer, "color": "#FFD700"}
        ]
        
        completed = self.config.get("completed_steps", [])
        bypassed = self.config.get("bypassed_steps", [])
        
        current_step_idx = 0
        for i, step in enumerate(steps):
            if step["id"] in completed or step["id"] in bypassed:
                current_step_idx = i + 1
            else:
                break
                
        # Progress
        prog_frame = QFrame()
        prog_layout = QVBoxLayout(prog_frame)
        prog_layout.setContentsMargins(0, 0, 0, 20)
        
        if current_step_idx >= len(steps):
            prog_text = get_string("pipeline_complete")
            progress_val = 100
        else:
            prog_text = get_string("progress_text", current_step_idx + 1, len(steps), steps[current_step_idx]["title"])
            progress_val = int((current_step_idx / len(steps)) * 100)
            
        lbl_prog = QLabel(prog_text)
        lbl_prog.setObjectName("AccentLabel")
        lbl_prog.setStyleSheet("font-size: 14px;")
        prog_layout.addWidget(lbl_prog)
        
        pbar = QProgressBar()
        pbar.setFixedHeight(8)
        pbar.setValue(progress_val)
        prog_layout.addWidget(pbar)
        
        self.grid_layout.addWidget(prog_frame)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        for i, step in enumerate(steps):
            is_completed = step["id"] in completed
            is_bypassed = step["id"] in bypassed
            is_done = is_completed or is_bypassed
            is_current = (i == current_step_idx)
            is_locked = (i > current_step_idx)
            
            card = self.create_guided_card(step, is_done, is_current, is_locked)
            grid.addWidget(card, i // 2, i % 2)
            
        self.grid_layout.addLayout(grid)

    def create_guided_card(self, step, is_done, is_current, is_locked):
        frame = QFrame()
        is_bypassed = step["id"] in self.config.get("bypassed_steps", [])
        
        border_col = step["color"] if is_current else "#333333"
        if is_bypassed: border_col = "#555555"
        
        bg_col = "#181A1D" if (is_current or is_done) else "transparent"
        border_width = "1px" if not is_locked else "0px"
        
        frame.setStyleSheet(f"QFrame {{ background-color: {bg_col}; border: {border_width} solid {border_col}; border-radius: 10px; }}")
        frame.setMinimumHeight(170)
        
        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(10)
        
        title_col = step["color"] if not is_locked else "#555555"
        desc_col = "#888888" if not is_locked else "#444444"
        
        lbl_title = QLabel(step["title"])
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {title_col}; border: none; background: transparent;")
        card_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(step["desc"])
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"font-size: 13px; color: {desc_col}; border: none; background: transparent; line-height: 1.4;")
        lbl_desc.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        card_layout.addWidget(lbl_desc, 1)
        
        bottom_layout = QHBoxLayout()
        
        if is_current:
            lbl_bypass = QLabel(f'<a href="#bypass" style="color:#FFF;">{get_string("bypass_link")}</a>')
            lbl_bypass.setStyleSheet("font-size: 11px; border: none; background: transparent;")
            lbl_bypass.setCursor(QCursor(Qt.PointingHandCursor))
            lbl_bypass.linkActivated.connect(lambda _, s=step["id"]: self.mark_bypassed(s))
            bottom_layout.addWidget(lbl_bypass, alignment=Qt.AlignBottom | Qt.AlignLeft)
            
        bottom_layout.addStretch()
        
        if is_done:
            status_text = get_string("step_bypassed") if is_bypassed else get_string("step_completed")
            lbl_status = QLabel(status_text)
            lbl_status.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {'#4CAF50' if not is_bypassed else '#888888'}; border: none; background: transparent;")
            bottom_layout.addWidget(lbl_status, alignment=Qt.AlignVCenter)
            
            btn_reopen = QPushButton(get_string("btn_reopen"))
            btn_reopen.setStyleSheet("background: transparent; color: #888; border: 1px solid #555; padding: 4px 10px; border-radius: 4px;")
            btn_reopen.setCursor(QCursor(Qt.PointingHandCursor))
            btn_reopen.clicked.connect(step["cmd"])
            bottom_layout.addWidget(btn_reopen, alignment=Qt.AlignVCenter)
            
        elif is_current:
            btn_launch = QPushButton(get_string("btn_launch"))
            btn_launch.setStyleSheet(f"background-color: {step['color']}; color: #0C0D0E; font-size: 13px; font-weight: bold; padding: 8px 18px; border-radius: 6px;")
            btn_launch.setCursor(QCursor(Qt.PointingHandCursor))
            btn_launch.clicked.connect(step["cmd"])
            bottom_layout.addWidget(btn_launch, alignment=Qt.AlignVCenter)
            
        elif is_locked:
            lbl_lock = QLabel(get_string("step_locked"))
            lbl_lock.setStyleSheet("font-size: 12px; font-weight: bold; color: #555555; border: none; background: transparent;")
            bottom_layout.addWidget(lbl_lock, alignment=Qt.AlignVCenter)
            
        card_layout.addLayout(bottom_layout)
        return frame

    def toggle_mode(self):
        current = self.config.get("mode", "expert")
        self.config["mode"] = "guided" if current == "expert" else "expert"
        self.save_config()
        self.setup_ui()

    def toggle_language(self):
        current = self.config.get("language", "en")
        self.config["language"] = "el" if current == "en" else "en"
        self.save_config()
        self.setup_ui()

    def mark_bypassed(self, step_id):
        bypassed = self.config.get("bypassed_steps", [])
        if step_id not in bypassed:
            bypassed.append(step_id)
            self.config["bypassed_steps"] = bypassed
            self.save_config()
            self.setup_ui()

    def setup_sidebar_content(self, layout):
        lbl_guide = QLabel(get_string("workflow_guide"))
        lbl_guide.setObjectName("AccentLabel")
        lbl_guide.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_guide)
        layout.addSpacing(10)
        
        self.create_help_box(layout, get_string("guide_1_title"), get_string("guide_1_desc"))
        self.create_help_box(layout, get_string("guide_2_title"), get_string("guide_2_desc"))
        self.create_help_box(layout, get_string("guide_3_title"), get_string("guide_3_desc"))
        self.create_help_box(layout, get_string("guide_4_title"), get_string("guide_4_desc"))
        self.create_help_box(layout, get_string("guide_5_title"), get_string("guide_5_desc"))
        
        layout.addStretch()
        
        tips = QFrame()
        tips.setStyleSheet("background-color: #121417; border: 1px solid #2A2D32; border-radius: 5px;")
        t_layout = QVBoxLayout(tips)
        t_layout.setContentsMargins(10, 10, 10, 10)
        
        l1 = QLabel(get_string("pro_tip"))
        l1.setStyleSheet("color: #00E5FF; font-weight: bold; border: none; font-size: 11px;")
        t_layout.addWidget(l1)
        
        l2 = QLabel(get_string("pro_tip_desc"))
        l2.setWordWrap(True)
        l2.setStyleSheet("color: #FFFFFF; border: none; font-size: 10px;")
        t_layout.addWidget(l2)
        
        layout.addWidget(tips)

    def create_help_box(self, layout, title, text):
        f = QFrame()
        f.setStyleSheet("background: transparent;")
        l = QVBoxLayout(f)
        l.setContentsMargins(0, 5, 0, 5)
        
        lt = QLabel(title)
        lt.setStyleSheet("font-weight: bold; font-size: 12px;")
        l.addWidget(lt)
        
        ld = QLabel(text)
        ld.setWordWrap(True)
        ld.setStyleSheet("color: #888888; font-size: 10px;")
        l.addWidget(ld)
        
        layout.addWidget(f)

    def create_module_btn(self, layout, title, desc, color, command):
        btn = QPushButton()
        btn.setObjectName("ModuleButton")
        btn.setMinimumHeight(100)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(20, 15, 20, 15)
        
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignVCenter)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; border: none; background: transparent;")
        text_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(desc)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 12px; color: #888888; border: none; background: transparent;")
        text_layout.addWidget(lbl_desc)
        
        btn_layout.addLayout(text_layout)
        btn_layout.addStretch()
        
        action_text = get_string("btn_launch") if color != "#888888" else "OPEN"
        lbl_launch = QLabel(action_text)
        lbl_launch.setStyleSheet(f"background-color: {color}; color: #0C0D0E; font-size: 14px; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        btn_layout.addWidget(lbl_launch, alignment=Qt.AlignVCenter | Qt.AlignRight)
        
        btn.clicked.connect(command)
        layout.addWidget(btn)

    def create_card_btn(self, title, desc, color, command):
        btn = QPushButton()
        btn.setObjectName("ModuleButton")
        btn.setMinimumHeight(140)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        card_layout = QVBoxLayout(btn)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(10)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color}; border: none; background: transparent;")
        card_layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(desc)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 13px; color: #888888; border: none; background: transparent; line-height: 1.4;")
        lbl_desc.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        card_layout.addWidget(lbl_desc, 1)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        lbl_launch = QLabel(get_string("btn_launch"))
        lbl_launch.setStyleSheet(f"background-color: {color}; color: #0C0D0E; font-size: 13px; font-weight: bold; padding: 8px 18px; border-radius: 6px;")
        bottom_layout.addWidget(lbl_launch)
        
        card_layout.addLayout(bottom_layout)
        
        btn.clicked.connect(command)
        return btn

    def log(self, msg):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{time_str}] {msg}")

    def get_launch_cmd(self, module_arg):
        if hasattr(sys, '_MEIPASS'):
            # Όταν είναι πακεταρισμένο, το sys.executable είναι το VideoToMLSuite.exe
            return [sys.executable, module_arg]
        else:
            # Σε development mode
            return [sys.executable, "orchestrator.py", module_arg]

    def launch_generator(self):
        self.log(get_string("launching_generator"))
        self._safe_launch("--generator")

    def launch_labeler(self):
        self.log(get_string("launching_labeler"))
        self._safe_launch("--labeler")

    def launch_inspector(self):
        self.log(get_string("launching_inspector"))
        self._safe_launch("--inspector")

    def launch_trainer(self):
        self.log(get_string("launching_trainer"))
        self._safe_launch("--trainer")

    def launch_deployer(self):
        self.log("Launching AI Deployer...")
        self._safe_launch("--deployer")

    def _safe_launch(self, arg):
        try:
            cmd = self.get_launch_cmd(arg)
            # Ορισμός του working directory στον φάκελο του εκτελεσίμου ή του script
            cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
            subprocess.Popen(cmd, cwd=cwd)
        except Exception as e:
            self.log(f"Error launching module {arg}: {str(e)}")

    def show_settings(self):
        self.settings_window = QDialog(self)
        self.settings_window.setWindowTitle(get_string("settings_title"))
        self.settings_window.resize(500, 400)
        
        layout = QVBoxLayout(self.settings_window)
        layout.setContentsMargins(30, 30, 30, 30)
        
        lbl_title = QLabel(get_string("settings_global_config"))
        lbl_title.setObjectName("AccentLabel")
        lbl_title.setStyleSheet("font-size: 18px;")
        layout.addWidget(lbl_title, alignment=Qt.AlignHCenter)
        layout.addSpacing(30)
        
        f1 = QWidget()
        l1 = QHBoxLayout(f1)
        l1.addWidget(QLabel(get_string("settings_default_out")))
        self.set_out = QLineEdit(self.config.get("output_path", "./frames"))
        l1.addWidget(self.set_out)
        layout.addWidget(f1)
        
        f2 = QWidget()
        l2 = QHBoxLayout(f2)
        l2.addWidget(QLabel(get_string("settings_default_split")))
        self.set_split = QLineEdit(str(self.config.get("default_split", 80)))
        l2.addWidget(self.set_split)
        layout.addWidget(f2)
        
        layout.addStretch()
        
        btn_save = QPushButton(get_string("settings_save_btn"))
        btn_save.setObjectName("GreenButton")
        btn_save.clicked.connect(self.apply_settings)
        layout.addWidget(btn_save, alignment=Qt.AlignHCenter)
        
        self.settings_window.exec()

    def apply_settings(self):
        self.config["output_path"] = self.set_out.text()
        try:
            self.config["default_split"] = int(self.set_split.text())
        except: pass
        self.save_config()
        self.settings_window.accept()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--generator":
            from generator import app
            app.main()
        elif arg == "--labeler":
            from labeler import app
            app.main()
        elif arg == "--inspector":
            from inspector import app
            app.main()
        elif arg == "--trainer":
            from trainer import app
            app.main()
        elif arg == "--deployer":
            from deployer import app
            app.main()
    else:
        q_app = QApplication(sys.argv)
        dashboard = Dashboard()
        dashboard.show()
        sys.exit(q_app.exec())

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--generator":
            from generator import app
            app.main()
        elif arg == "--labeler":
            from labeler import app
            app.main()
        elif arg == "--inspector":
            from inspector import app
            app.main()
        elif arg == "--trainer":
            from trainer import app
            app.main()
        elif arg == "--deployer":
            from deployer import app
            app.main()
    else:
        q_app = QApplication(sys.argv)
        dashboard = Dashboard()
        dashboard.show()
        sys.exit(q_app.exec())
