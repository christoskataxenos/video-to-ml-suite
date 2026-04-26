import os
import sys
import glob
import json
import yaml

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, QFileDialog)
from PySide6.QtGui import QIcon, QPixmap, QCursor
from PySide6.QtCore import Qt, QSize

from shared.strings import get_string

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), "..", relative_path)

class InspectorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DATASET INSPECTOR")
        self.resize(900, 700)
        self.setMinimumSize(900, 700)

        # Set Window Icon
        try:
            icon_p = resource_path(os.path.join("shared", "icon_inspector.ico"))
            if os.path.exists(icon_p):
                self.setWindowIcon(QIcon(icon_p))
        except: pass

        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except:
            self.config = {"mode": "expert"}

        # Εφαρμογή QSS StyleSheet
        try:
            with open(resource_path("shared/style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

        self.dataset_path = ""
        self.stats = {} 
        self.class_names = []

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
                {"action": "guided_ins_step1", "edu": "guided_ins_step1_edu"},
                {"action": "guided_ins_step2", "edu": "guided_ins_step2_edu"},
                {"action": "guided_ins_step3", "edu": "guided_ins_step3_edu"},
                {"action": "guided_ins_step4", "edu": "guided_ins_step4_edu"}
            ]
            self.help_sidebar = GuidedPanel(self.config_path, "inspection", "inspector_title", "guided_ins_why", steps, on_complete=self.close)
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

        lbl_title = QLabel(get_string("inspector_title").upper())
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00E5FF; margin-left: 10px;")
        h_layout.addWidget(lbl_title)
        h_layout.addStretch()
        
        # Action Buttons
        self.btn_load = QPushButton(get_string("guided_ins_step1").upper())
        self.btn_load.setObjectName("AccentButton")
        self.btn_load.setFixedHeight(40)
        self.btn_load.clicked.connect(self.load_dataset)
        h_layout.addWidget(self.btn_load)

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

        # Statistics Panel
        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setContentsMargins(40, 40, 40, 40)
        self.stats_layout.setAlignment(Qt.AlignTop)
        
        self.lbl_summary = QLabel(get_string("guided_ins_why"))
        self.lbl_summary.setObjectName("DimLabel")
        self.lbl_summary.setStyleSheet("font-size: 14px;")
        self.lbl_summary.setAlignment(Qt.AlignCenter)
        self.stats_layout.addWidget(self.lbl_summary)
        
        area_layout.addWidget(self.stats_container, 1)
        main_layout.addWidget(self.main_area, 1)

    def toggle_language(self):
        new_lang = "en" if self.config.get("language") == "el" else "el"
        self.config["language"] = new_lang
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
        self.lang_btn.setText("ΕΛ" if new_lang == "el" else "EN")
        # Refresh UI text
        self.centralWidget().deleteLater()
        self.setup_ui()

    def show_help(self):
        from shared.help_wizard import HelpWizard
        wizard = HelpWizard(self, app_type="inspector")
        wizard.exec()

    def load_dataset(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select dataset.yaml", "", "YAML Files (*.yaml *.yml)")
        if path:
            self.dataset_path = path
            self.analyze_dataset()

    def analyze_dataset(self):
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            base_dir = os.path.dirname(self.dataset_path)
            self.class_names = data.get("names", [])
            if isinstance(self.class_names, dict):
                self.class_names = list(self.class_names.values())
            
            # Paths to check
            train_labels = os.path.join(base_dir, data.get("train", "").replace("images", "labels"))
            val_labels = os.path.join(base_dir, data.get("val", "").replace("images", "labels"))
            
            counts = {i: 0 for i in range(len(self.class_names))}
            total_labels = 0
            empty_files = 0
            
            # Φάκελοι προς έλεγχο για ετικέτες
            # YOLO συνήθως έχει train/labels, αλλά ο χρήστης μπορεί να τα έχει σώσει in-place στα images
            search_paths = []
            if os.path.exists(train_labels): search_paths.append(train_labels)
            if os.path.exists(val_labels): search_paths.append(val_labels)
            
            # Προσθήκη των φακέλων images στην αναζήτηση (fallback)
            train_images = os.path.join(base_dir, data.get("train", ""))
            val_images = os.path.join(base_dir, data.get("val", ""))
            if os.path.exists(train_images): search_paths.append(train_images)
            if os.path.exists(val_images): search_paths.append(val_images)
            
            # Αν δεν βρέθηκε κανένας από τους παραπάνω, έλεγχος στο base_dir
            if not search_paths:
                search_paths = [base_dir]

            for folder in search_paths:
                if os.path.exists(folder):
                    txt_files = glob.glob(os.path.join(folder, "**", "*.txt"), recursive=True)
                    for txt in txt_files:
                        if os.path.basename(txt) == "classes.txt": continue
                        has_labels = False
                        try:
                            with open(txt, "r") as f:
                                for line in f:
                                    parts = line.split()
                                    if parts:
                                        try:
                                            # Καταμέτρηση εμφάνισης κάθε κλάσης
                                            cls_id = int(parts[0])
                                            counts[cls_id] = counts.get(cls_id, 0) + 1
                                            total_labels += 1
                                            has_labels = True
                                        except: pass
                        except: pass
                        if not has_labels:
                            empty_files += 1 # Εικόνες χωρίς ετικέτες (blind spots)

            self.update_stats_view(counts, total_labels, empty_files)
        except Exception as e:
            print(f"Error analyzing dataset: {e}")
            self.update_stats_view({}, 0, 0)

    def update_stats_view(self, counts, total, empty_files=0):
        # Clear previous stats
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if total == 0:
            lbl_warn = QLabel("⚠️ NO LABELS FOUND IN THIS DATASET")
            lbl_warn.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF5252;")
            lbl_warn.setAlignment(Qt.AlignCenter)
            self.stats_layout.addWidget(lbl_warn)
            self.stats_layout.addSpacing(10)
            lbl_hint = QLabel("Ensure you have saved your annotations in the Labeler\nand that the dataset path is correct.")
            lbl_hint.setStyleSheet("color: #888;")
            lbl_hint.setAlignment(Qt.AlignCenter)
            self.stats_layout.addWidget(lbl_hint)
            return

        lbl_title = QLabel("CLASS DISTRIBUTION")
        lbl_title.setObjectName("AccentLabel")
        lbl_title.setStyleSheet("font-size: 18px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        self.stats_layout.addWidget(lbl_title)
        self.stats_layout.addSpacing(20)
        
        max_val = max(counts.values()) if counts.values() else 0
        max_count = max_val if max_val > 0 else 1
        
        for i, (cls_id, count) in enumerate(counts.items()):
            name = self.class_names[i] if i < len(self.class_names) else f"ID {i}"
            
            row = QWidget()
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 5, 0, 5)
            
            lbl_name = QLabel(f"{name:.<15}")
            lbl_name.setFixedWidth(150)
            r_layout.addWidget(lbl_name)
            
            bar_width = int((count / max_count) * 400)
            bar = QFrame()
            bar.setFixedSize(max(bar_width, 1), 15)
            bar.setStyleSheet("background-color: #00E5FF; border-radius: 2px;")
            r_layout.addWidget(bar)
            
            r_layout.addStretch()
            
            lbl_count = QLabel(str(count))
            lbl_count.setStyleSheet("font-weight: bold;")
            r_layout.addWidget(lbl_count)
            
            self.stats_layout.addWidget(row)

        self.stats_layout.addSpacing(30)
        
        lbl_total = QLabel(f"TOTAL LABELED OBJECTS: {total}")
        lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        lbl_total.setAlignment(Qt.AlignCenter)
        self.stats_layout.addWidget(lbl_total)

        if empty_files > 0:
            lbl_empty = QLabel(f"⚠️ {empty_files} IMAGES HAVE NO LABELS (BLIND SPOTS)")
            lbl_empty.setStyleSheet("font-size: 12px; color: #FFAB40;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.stats_layout.addWidget(lbl_empty)

        self.stats_layout.addStretch()

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = InspectorApp()
    window.show()
    if not QApplication.instance().activeWindow():
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
