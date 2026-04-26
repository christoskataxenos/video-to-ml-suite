import os
import sys
import json
import subprocess
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QFrame, 
                                QTextEdit, QLineEdit, QFileDialog, QTabWidget, QScrollArea)
from PySide6.QtGui import QIcon, QPixmap, QImage, QCursor
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer

from shared.strings import get_string

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), "..", relative_path)

class InferenceThread(QThread):
    frame_signal = Signal(np.ndarray)
    status_signal = Signal(str)

    def __init__(self, model_path, source=0):
        super().__init__()
        self.model_path = model_path
        self.source = source
        self.running = False

    def run(self):
        try:
            from ultralytics import YOLO
            model = YOLO(self.model_path)
            cap = cv2.VideoCapture(self.source)
            self.running = True
            
            while self.running:
                ret, frame = cap.read()
                if not ret: break
                
                results = model(frame, stream=True, verbose=False)
                for r in results:
                    annotated_frame = r.plot()
                    self.frame_signal.emit(annotated_frame)
                
            cap.release()
        except Exception as e:
            self.status_signal.emit(f"Error: {e}")

    def stop(self):
        self.running = False
        self.wait()

class DeployerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI DEPLOYER & STUDIO")
        self.resize(1000, 850)
        self.setMinimumSize(1000, 850)
        
        # Set Window Icon
        try:
            icon_p = resource_path(os.path.join("shared", "icon_deployer.ico"))
            if os.path.exists(icon_p):
                self.setWindowIcon(QIcon(icon_p))
        except: pass

        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except: self.config = {"mode": "expert"}

        try:
            with open(resource_path("shared/style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

        self.inference_thread = None
        self.setup_ui()
        self.auto_find_model()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Guided Sidebar
        if self.config.get("mode") == "guided":
            from shared.guided_panel import GuidedPanel
            steps = [
                {"action": "guided_dep_step1", "edu": "guided_dep_step1_edu"},
                {"action": "guided_dep_step2", "edu": "guided_dep_step2_edu"},
                {"action": "guided_dep_step3", "edu": "guided_dep_step3_edu"},
                {"action": "guided_dep_step4", "edu": "guided_dep_step4_edu"}
            ]
            self.help_sidebar = GuidedPanel(self.config_path, "deployment", "deployer_title", "guided_dep_why", steps, on_complete=self.close)
            main_layout.addWidget(self.help_sidebar)

        # Main Area
        self.main_area = QWidget()
        area_layout = QVBoxLayout(self.main_area)
        area_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        self.header = QFrame()
        self.header.setObjectName("ElevatedFrame")
        self.header.setFixedHeight(80)
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(30, 0, 30, 0)
        
        lbl_title = QLabel(get_string("deployer_title").upper())
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
        h_layout.addWidget(lbl_title)
        h_layout.addStretch()
        
        self.lang_btn = QPushButton("EN" if self.config.get("language") == "el" else "ΕΛ")
        self.lang_btn.setFixedSize(40, 40)
        self.lang_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.lang_btn.setStyleSheet("background-color: #1A1C1E; border: 1px solid #333; border-radius: 20px; color: #555;")
        h_layout.addWidget(self.lang_btn)
        
        area_layout.addWidget(self.header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabs")
        
        # Tab 1: Live Testing
        self.tab_test = QWidget()
        test_layout = QVBoxLayout(self.tab_test)
        
        # Model Selection UI
        mod_frame = QFrame()
        mod_frame.setObjectName("ElevatedFrame")
        mod_layout = QHBoxLayout(mod_frame)
        mod_layout.addWidget(QLabel("Current Model (.pt):"))
        self.model_path_entry = QLineEdit()
        mod_layout.addWidget(self.model_path_entry, 1)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_model)
        mod_layout.addWidget(btn_browse)
        test_layout.addWidget(mod_frame)

        # Video Display
        self.video_label = QLabel("LIVE PREVIEW (START TO TEST)")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000; color: #444; border: 2px dashed #222; border-radius: 10px; font-size: 16px;")
        test_layout.addWidget(self.video_label, 1)

        # Controls
        ctrl_layout = QHBoxLayout()
        self.btn_webcam = QPushButton("START WEBCAM")
        self.btn_webcam.setObjectName("AccentButton")
        self.btn_webcam.setFixedHeight(50)
        self.btn_webcam.clicked.connect(self.start_webcam)
        ctrl_layout.addWidget(self.btn_webcam)
        
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setFixedHeight(50)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_test)
        ctrl_layout.addWidget(self.btn_stop)
        test_layout.addLayout(ctrl_layout)

        self.tabs.addTab(self.tab_test, "LIVE TESTING")

        # Tab 2: Integration & LM Studio
        self.tab_guide = QWidget()
        guide_layout = QVBoxLayout(self.tab_guide)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        sc_layout = QVBoxLayout(scroll_content)
        
        sc_layout.addWidget(self.create_guide_section("HOW TO USE THIS MODEL", "Your trained model (best.pt) contains the knowledge of your objects. You can use it in Python, mobile apps, or even connected with LLMs."))
        
        python_code = """import cv2\nfrom ultralytics import YOLO\n\n# Load model\nmodel = YOLO('best.pt')\n\n# Run on video\nresults = model.predict(source='video.mp4', save=True, conf=0.5)"""
        sc_layout.addWidget(self.create_code_section("PYTHON INTEGRATION", python_code))
        
        lm_studio_text = "To use this with LM Studio, you can run a script that detects objects and sends the descriptions to LM Studio's Local Server (Port 1234). This allows your AI to 'talk' about what it sees."
        sc_layout.addWidget(self.create_guide_section("LM STUDIO CONNECTIVITY", lm_studio_text))
        
        sc_layout.addStretch()
        scroll.setWidget(scroll_content)
        guide_layout.addWidget(scroll)
        self.tabs.addTab(self.tab_guide, "STUDIO & INTEGRATION")

        area_layout.addWidget(self.tabs, 1)
        main_layout.addWidget(self.main_area, 1)

    def create_guide_section(self, title, text):
        f = QFrame()
        f.setObjectName("ElevatedFrame")
        l = QVBoxLayout(f)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 14px;")
        l.addWidget(lbl_t)
        lbl_d = QLabel(text)
        lbl_d.setWordWrap(True)
        lbl_d.setStyleSheet("color: #AAA; font-size: 12px;")
        l.addWidget(lbl_d)
        return f

    def create_code_section(self, title, code):
        f = QFrame()
        f.setObjectName("ElevatedFrame")
        l = QVBoxLayout(f)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-weight: bold; color: #FFD700; font-size: 14px;")
        l.addWidget(lbl_t)
        txt = QTextEdit(code)
        txt.setReadOnly(True)
        txt.setFixedHeight(120)
        txt.setStyleSheet("background-color: #000; color: #00FF41; font-family: 'Consolas'; font-size: 11px; border: 1px solid #333;")
        l.addWidget(txt)
        return f

    def auto_find_model(self):
        # Look for the latest best.pt in the current workspace
        runs_dir = os.path.abspath("runs/detect")
        if os.path.exists(runs_dir):
            train_dirs = [d for d in os.listdir(runs_dir) if d.startswith("train")]
            if train_dirs:
                latest_train = sorted(train_dirs)[-1]
                path = os.path.join(runs_dir, latest_train, "weights", "best.pt")
                if os.path.exists(path):
                    self.model_path_entry.setText(path)

    def browse_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select YOLO Model", "", "YOLO Models (*.pt)")
        if path: self.model_path_entry.setText(path)

    def start_webcam(self):
        model_path = self.model_path_entry.text()
        if not os.path.exists(model_path): return
        
        self.btn_webcam.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.inference_thread = InferenceThread(model_path, source=0)
        self.inference_thread.frame_signal.connect(self.update_frame)
        self.inference_thread.start()

    def update_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def stop_test(self):
        if self.inference_thread:
            self.inference_thread.stop()
        self.btn_webcam.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.video_label.clear()
        self.video_label.setText("LIVE PREVIEW (STOPPED)")

def main():
    app = QApplication(sys.argv)
    window = DeployerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
