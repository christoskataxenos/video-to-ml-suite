import os
import sys
import subprocess
import json

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, 
                               QTextEdit, QLineEdit, QFileDialog, QComboBox)
from PySide6.QtGui import QIcon, QPixmap, QCursor
from PySide6.QtCore import Qt, QThread, Signal, QSize

from shared.strings import get_string
from shared.utils import get_resource_path, load_config, save_config

def resource_path(relative_path):
    return get_resource_path(relative_path)

class TrainingWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            process = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in process.stdout:
                self.log_signal.emit(line.strip())
            
            return_code = process.wait()
            if return_code == 0:
                self.log_signal.emit("\n✅ Η ΕΚΠΑΙΔΕΥΣΗ ΟΛΟΚΛΗΡΩΘΗΚΕ ΕΠΙΤΥΧΩΣ!")
            else:
                self.log_signal.emit(f"\n❌ Η ΕΚΠΑΙΔΕΥΣΗ ΔΙΑΚΟΠΗΚΕ (Error Code: {return_code})")
                
        except Exception as e:
            self.log_signal.emit(f"⚠️ ΚΡΙΣΙΜΟ ΣΦΑΛΜΑ: {e}")
        self.finished_signal.emit()

class TrainerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TRAINING LAUNCHER")
        self.resize(900, 800)
        self.setMinimumSize(900, 800)

        # Set Window Icon
        try:
            icon_p = resource_path(os.path.join("shared", "icon_trainer.ico"))
            if os.path.exists(icon_p):
                self.setWindowIcon(QIcon(icon_p))
        except: pass

        self.config = load_config()

        # Εφαρμογή QSS StyleSheet
        try:
            with open(resource_path("shared/style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

        self.is_training = False
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        if self.config.get("mode") == "guided":
            from shared.guided_panel import GuidedPanel
            steps = [
                {"action": "guided_tra_step1", "edu": "guided_tra_step1_edu"},
                {"action": "guided_tra_step2", "edu": "guided_tra_step2_edu"},
                {"action": "guided_tra_step3", "edu": "guided_tra_step3_edu"},
                {"action": "guided_tra_step4", "edu": "guided_tra_step4_edu"}
            ]
            self.help_sidebar = GuidedPanel("training", "trainer_title", "guided_tra_why", steps, on_complete=self.close)
            main_layout.addWidget(self.help_sidebar)

        # Main Area
        self.main_area = QWidget()
        area_layout = QVBoxLayout(self.main_area)
        area_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (Standard with Logo + Toggle)
        self.header = QFrame()
        self.header.setObjectName("ElevatedFrame")
        self.header.setFixedHeight(80)
        self.header.setStyleSheet("border-radius: 0px;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(30, 0, 30, 0)

        # Logo
        try:
            logo_p = resource_path(os.path.join("shared", "logo.png"))
            if os.path.exists(logo_p):
                lbl_logo = QLabel()
                pixmap = QPixmap(logo_p).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_logo.setPixmap(pixmap)
                h_layout.addWidget(lbl_logo)
        except: pass

        lbl_title = QLabel(get_string("trainer_title").upper())
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00E5FF; margin-left: 10px;")
        h_layout.addWidget(lbl_title)
        h_layout.addStretch()

        # Help & Language
        h_layout.addSpacing(20)
        circle_btn_style = """
            QPushButton { 
                background-color: #1A1C1E; 
                border: 1px solid #333; 
                border-radius: 20px; 
                color: #555; 
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #2A2D32; border: 1px solid #00E5FF; color: white; }
        """
        
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(40, 40)
        self.help_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.help_btn.setStyleSheet(circle_btn_style)
        self.help_btn.clicked.connect(self.show_help)
        h_layout.addWidget(self.help_btn)

        lang_text = "ΕΛ" if self.config.get("language") == "el" else "EN"
        self.lang_btn = QPushButton(lang_text)
        self.lang_btn.setFixedSize(40, 40)
        self.lang_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.lang_btn.setStyleSheet(circle_btn_style)
        self.lang_btn.clicked.connect(self.toggle_language)
        h_layout.addWidget(self.lang_btn)
        
        area_layout.addWidget(self.header)

        # Content Area with Padding
        content_pane = QWidget()
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(40, 20, 40, 20)

        # Config Group
        self.config_group = QFrame()
        self.config_group.setObjectName("ElevatedFrame")
        cg_layout = QVBoxLayout(self.config_group)
        cg_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_cfg_title = QLabel("TRAINING CONFIGURATION")
        lbl_cfg_title.setObjectName("AccentLabel")
        cg_layout.addWidget(lbl_cfg_title)
        cg_layout.addSpacing(10)
        
        # YAML Selection
        f1 = QWidget()
        l1 = QHBoxLayout(f1)
        l1.setContentsMargins(0, 0, 0, 0)
        l1.addWidget(QLabel("Dataset YAML:"))
        self.yaml_entry = QLineEdit()
        l1.addWidget(self.yaml_entry, 1)
        btn_browse = QPushButton(get_string("gen_browse_btn"))
        btn_browse.clicked.connect(self.browse_yaml)
        l1.addWidget(btn_browse)
        cg_layout.addWidget(f1)
        
        # Model Size
        f2 = QWidget()
        l2 = QHBoxLayout(f2)
        l2.setContentsMargins(0, 0, 0, 0)
        l2.addWidget(QLabel("Model Size:"))
        self.model_menu = QComboBox()
        self.model_menu.addItems(["yolov8n.pt (Nano)", "yolov8s.pt (Small)", "yolov8m.pt (Medium)"])
        l2.addWidget(self.model_menu, 1)
        cg_layout.addWidget(f2)
        
        # Epochs
        f3 = QWidget()
        l3 = QHBoxLayout(f3)
        l3.setContentsMargins(0, 0, 0, 0)
        l3.addWidget(QLabel("Epochs:"))
        self.epochs_entry = QLineEdit("50")
        self.epochs_entry.setFixedWidth(80)
        l3.addWidget(self.epochs_entry)
        l3.addStretch()
        cg_layout.addWidget(f3)

        content_layout.addWidget(self.config_group)
        
        self.btn_train = QPushButton(get_string("gen_start_btn"))
        self.btn_train.setObjectName("AccentButton")
        self.btn_train.setFixedHeight(60)
        self.btn_train.clicked.connect(self.start_training)
        content_layout.addWidget(self.btn_train)

        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #111214; font-size: 11px; color: #888888; border: none; border-radius: 8px; padding: 10px;")
        content_layout.addWidget(self.console, 1)
        
        area_layout.addWidget(content_pane, 1)
        main_layout.addWidget(self.main_area, 1)

    def toggle_language(self):
        new_lang = "en" if self.config.get("language") == "el" else "el"
        self.config["language"] = new_lang
        save_config(self.config)
        self.setup_ui()

    def show_help(self):
        from shared.help_wizard import HelpWizard
        wizard = HelpWizard(self, app_type="trainer")
        wizard.exec()

    def setup_help_sidebar(self, layout):
        lbl = QLabel("TRAINING GUIDE")
        lbl.setObjectName("AccentLabel")
        lbl.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl)
        
        s1 = QFrame()
        s1.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px;")
        l1 = QVBoxLayout(s1)
        l1.addWidget(QLabel("📊 CONFIG"))
        l1.addWidget(QLabel("• YAML: Select dataset.yaml\n• Path: Must be absolute\n• Split: Verified in YAML"))
        layout.addWidget(s1)
        
        s2 = QFrame()
        s2.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px;")
        l2 = QVBoxLayout(s2)
        l2.addWidget(QLabel("🧠 MODEL"))
        l2.addWidget(QLabel("• Nano: Fastest training\n• Small: Good balance\n• Medium: High accuracy\n• Epochs: 50-100 recommended"))
        layout.addWidget(s2)
        
        layout.addStretch()

    def browse_yaml(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select dataset.yaml", "", "YAML Files (*.yaml *.yml)")
        if path:
            self.yaml_entry.setText(path)

    def log(self, msg):
        self.console.append(msg)

    def fix_dataset_structure(self, yaml_path):
        """Εξασφαλίζει ότι οι ετικέτες είναι στον σωστό φάκελο (labels) για την YOLO"""
        try:
            import yaml
            import shutil
            base_dir = os.path.dirname(yaml_path)
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            for split in ['train', 'val']:
                img_path = data.get(split)
                if not img_path: continue
                
                # Ο πλήρης φάκελος των εικόνων
                full_img_path = os.path.join(base_dir, img_path)
                if not os.path.exists(full_img_path): continue
                
                # Ο φάκελος των ετικετών (αντικατάσταση images με labels στο μονοπάτι)
                full_lab_path = full_img_path.replace("images", "labels")
                os.makedirs(full_lab_path, exist_ok=True)
                
                # Μετακίνηση τυχόν .txt αρχείων από το images στο labels
                for f in os.listdir(full_img_path):
                    if f.lower().endswith(".txt") and f != "classes.txt":
                        shutil.move(os.path.join(full_img_path, f), os.path.join(full_lab_path, f))
            
            self.log("✅ Dataset structure verified and fixed (Labels moved to /labels)")
        except Exception as e:
            self.log(f"⚠️ Warning during dataset fix: {e}")

    def start_training(self):
        if self.is_training: return
        
        yaml_path = self.yaml_entry.text()
        if not yaml_path:
            self.log("ERROR: Please select a dataset.yaml")
            return

        # Αυτόματη διόρθωση της δομής του dataset πριν την εκκίνηση
        self.fix_dataset_structure(yaml_path)

        self.is_training = True
        self.btn_train.setEnabled(False)
        self.btn_train.setText("TRAINING IN PROGRESS...")
        
        model_name = self.model_menu.currentText().split()[0]
        epochs = self.epochs_entry.text()

        self.log(f"Initializing YOLO Training with {model_name}...")
        self.log(f"Dataset: {yaml_path}")
        self.log(f"Epochs: {epochs}")
        
        # Χρήση του python -c για απευθείας κλήση της βιβλιοθήκης ultralytics
        python_code = f"from ultralytics import YOLO; model = YOLO('{model_name}'); model.train(data='{yaml_path}', epochs={epochs}, imgsz=640, exist_ok=True)"
        cmd = [sys.executable, "-c", python_code]

        self.worker = TrainingWorker(cmd)
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.reset_ui)
        self.worker.start()

    def reset_ui(self):
        self.is_training = False
        self.btn_train.setEnabled(True)
        self.btn_train.setText("START TRAINING")

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = TrainerApp()
    window.show()
    if not QApplication.instance().activeWindow():
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
