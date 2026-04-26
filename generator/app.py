import subprocess
import threading
import os
import sys
import base64
import io
import json
from PIL import Image
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QFrame, 
                               QTextEdit, QLineEdit, QFileDialog, QCheckBox, 
                               QSlider, QProgressBar)
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal

import shared.strings as strings
from shared.help_wizard import HelpWizard

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), "..", relative_path)

class EngineWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(str)
    thumb_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, cmd, batch_mode, batch_files, is_ml, split_ratio, classes_txt, out_entry):
        super().__init__()
        self.cmd = cmd
        self.batch_mode = batch_mode
        self.batch_files = batch_files
        self.is_ml = is_ml
        self.split_ratio = split_ratio
        self.classes_txt = classes_txt
        self.out_entry = out_entry
        self.start_time = datetime.now()

    def run(self):
        if self.batch_mode:
            for i, vid in enumerate(self.batch_files):
                self.log_signal.emit(f"BATCH [{i+1}/{len(self.batch_files)}]: Processing {os.path.basename(vid)}")
                self.run_single_video(vid, True)
        else:
            self.run_single_video(self.cmd[1], False)
        
        if self.is_ml:
            self.organize_ml_dataset()

        self.finished_signal.emit()

    def run_single_video(self, video_path, is_batch):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        out_path = os.path.join(self.out_entry, video_name).replace("\\", "/")
        os.makedirs(out_path, exist_ok=True)
        self.last_output_path = out_path

        cmd = self.cmd.copy()
        cmd[1] = video_path
        cmd[3] = out_path

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, encoding='utf-8', errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        for line in process.stdout:
            line = line.strip()
            if line.startswith("THUMB:"):
                self.thumb_signal.emit(line[6:])
            elif line.startswith("PROGRESS:"):
                self.progress_signal.emit(line)
            elif line.startswith("REPORT:") or line.startswith("SUCCESS:"):
                self.log_signal.emit(line)
        
        process.wait()

    def organize_ml_dataset(self):
        import random
        import shutil

        base_dir = self.last_output_path
        self.log_signal.emit("ML: Organizing dataset...")

        valid_exts = (".jpg", ".webp", ".png")
        all_frames = [f for f in os.listdir(base_dir) if f.lower().endswith(valid_exts)]
        
        if not all_frames:
            self.log_signal.emit("ML: No frames found to organize.")
            return

        random.shuffle(all_frames)
        
        split_point = int(len(all_frames) * (self.split_ratio / 100))
        train_frames = all_frames[:split_point]
        val_frames = all_frames[split_point:]

        dirs = {
            "train": os.path.join(base_dir, "train", "images"),
            "val": os.path.join(base_dir, "val", "images")
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)

        for f in train_frames:
            shutil.move(os.path.join(base_dir, f), os.path.join(dirs["train"], f))
            # Μετακίνηση και της αντίστοιχης ετικέτας .txt αν υπάρχει
            txt_f = os.path.splitext(f)[0] + ".txt"
            if os.path.exists(os.path.join(base_dir, txt_f)):
                shutil.move(os.path.join(base_dir, txt_f), os.path.join(dirs["train"], txt_f))
                
        for f in val_frames:
            shutil.move(os.path.join(base_dir, f), os.path.join(dirs["val"], f))
            # Μετακίνηση και της αντίστοιχης ετικέτας .txt αν υπάρχει
            txt_f = os.path.splitext(f)[0] + ".txt"
            if os.path.exists(os.path.join(base_dir, txt_f)):
                shutil.move(os.path.join(base_dir, txt_f), os.path.join(dirs["val"], txt_f))

        classes = [c.strip() for c in self.classes_txt.split(",") if c.strip()]
        if not classes: classes = ["Object"]

        yaml_content = f"""# YOLOv8/v11 Dataset Configuration
path: {os.path.abspath(base_dir).replace("\\", "/")}
train: train/images
val: val/images

names:
"""
        for i, cls in enumerate(classes):
            yaml_content += f"  {i}: {cls}\n"

        yaml_path = os.path.join(base_dir, "dataset.yaml")
        with open(yaml_path, "w", encoding="utf-8") as yf:
            yf.write(yaml_content)

        self.log_signal.emit(f"ML: Dataset ready! Train: {len(train_frames)}, Val: {len(val_frames)}")
        self.log_signal.emit(f"ML: Generated {os.path.basename(yaml_path)}")

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FRAME EXTRACTOR")
        self.resize(1200, 850)
        self.setMinimumSize(1200, 850)

        # Set Window Icon
        try:
            icon_p = resource_path(os.path.join("shared", "icon_generator.ico"))
            if os.path.exists(icon_p):
                self.setWindowIcon(QIcon(icon_p))
        except: pass
        
        self.is_running = False
        self.is_batch_mode = False
        self.batch_files = []
        self.start_time = None
        self.lang = strings.get_current_language()

        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except:
            self.config = {"mode": "expert"}

        # Εφαρμογή QSS
        try:
            with open(resource_path("shared/style.qss"), "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.setStyleSheet("""
            #CircleButton { 
                background-color: #1A1C1E; 
                color: #00E5FF; 
                border: 1px solid #333; 
                border-radius: 18px; 
                font-weight: bold; 
                font-size: 11px;
            }
            #CircleButton:hover { background-color: #2A2D32; }
            #GreenButton { background-color: #00E5FF; color: black; border: none; padding: 10px; border-radius: 4px; font-weight: bold; }
            #GreenButton:hover { background-color: #00B8D4; }
        """)

        # Αριστερή Μπάρα (Help / Guided)
        if self.config.get("mode") == "guided":
            from shared.guided_panel import GuidedPanel
            steps = [
                {"action": "guided_gen_step1", "edu": "guided_gen_step1_edu"},
                {"action": "guided_gen_step2", "edu": "guided_gen_step2_edu"},
                {"action": "guided_gen_step3", "edu": "guided_gen_step3_edu"},
                {"action": "guided_gen_step4", "edu": "guided_gen_step4_edu"},
                {"action": "guided_gen_step5", "edu": "guided_gen_step5_edu"}
            ]
            self.help_sidebar = GuidedPanel(self.config_path, "extraction", "gen_title", "guided_gen_why", steps, on_complete=self.close)
            main_layout.addWidget(self.help_sidebar)
        else:
            self.help_sidebar = QFrame()
            self.help_sidebar.setObjectName("HelpSidebar")
            self.help_sidebar.setFixedWidth(240)
            hs_layout = QVBoxLayout(self.help_sidebar)
            self.setup_help_sidebar(hs_layout)
            main_layout.addWidget(self.help_sidebar)

        # Κεντρικό Πάνελ (Επιλογές)
        self.left_panel = QWidget()
        lp_layout = QVBoxLayout(self.left_panel)
        lp_layout.setContentsMargins(30, 30, 30, 30)
        
        self.setup_header(lp_layout)
        
        self.mode_cb = QCheckBox("Batch Mode (Folder)")
        self.mode_cb.stateChanged.connect(self.toggle_mode)
        lp_layout.addWidget(self.mode_cb)
        lp_layout.addSpacing(10)

        self.input_group = self.create_group(lp_layout, get_string("gen_input_group"))
        self.setup_input_controls(self.input_group)

        self.out_group = self.create_group(lp_layout, get_string("gen_output_group"))
        self.setup_output_group(self.out_group)

        self.trim_group = self.create_group(lp_layout, get_string("gen_trim_group"))
        self.setup_trimming_group(self.trim_group)

        self.proc_group = self.create_group(lp_layout, get_string("gen_proc_group"))
        self.setup_processing_group(self.proc_group)

        self.ml_group = self.create_group(lp_layout, get_string("gen_ml_group"))
        self.setup_ml_dataset_group(self.ml_group)
        
        lp_layout.addStretch()

        self.start_btn = QPushButton(get_string("gen_start_btn"))
        self.start_btn.setObjectName("GreenButton")
        self.start_btn.setFixedHeight(50)
        self.start_btn.clicked.connect(self.toggle_engine)
        lp_layout.addWidget(self.start_btn)

        self.open_folder_btn = QPushButton(get_string("gen_open_folder_btn"))
        self.open_folder_btn.hide()
        self.open_folder_btn.clicked.connect(self.open_export_folder)
        lp_layout.addWidget(self.open_folder_btn)

        main_layout.addWidget(self.left_panel, 1)

        # ΔΕΞΙΑ ΣΤΗΛΗ: ΠΡΟΕΠΙΣΚΟΠΗΣΗ
        self.right_panel = QFrame()
        self.right_panel.setObjectName("ElevatedFrame")
        rp_layout = QVBoxLayout(self.right_panel)
        rp_layout.setContentsMargins(20, 20, 20, 20)
        
        self.setup_preview(rp_layout)
        self.setup_telemetry(rp_layout)
        self.setup_log_area(rp_layout)

        main_layout.addWidget(self.right_panel, 1)

        if self.config.get("mode") == "guided":
            self.apply_smart_defaults()

    def apply_smart_defaults(self):
        self.mode_cb.setChecked(False)
        self.out_entry.setText(self.config.get("output_path", "./frames"))
        self.ml_cb.setChecked(True)
        self.split_slider.setValue(80)
        self.resize_entry.setText("1280")

    def setup_header(self, layout):
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(strings.get_string("gen_title").upper())
        lbl.setStyleSheet("font-size: 24px; font-weight: bold;")
        l.addWidget(lbl)
        l.addStretch()
        
        self.status_dot = QLabel(strings.get_string("gen_status_ready"))
        self.status_dot.setStyleSheet("color: #4CAF50; font-weight: bold;")
        l.addWidget(self.status_dot)
        
        l.addSpacing(15)
        
        # Circular Language Button
        self.btn_lang = QPushButton("EN" if self.lang == "en" else "GR")
        self.btn_lang.setFixedSize(36, 36)
        self.btn_lang.setObjectName("CircleButton")
        self.btn_lang.clicked.connect(self.toggle_language)
        l.addWidget(self.btn_lang)
        
        l.addSpacing(10)
        
        # Help Button
        self.btn_help = QPushButton("?")
        self.btn_help.setFixedSize(36, 36)
        self.btn_help.setObjectName("CircleButton")
        self.btn_help.setStyleSheet("color: #888; border-color: #222;")
        self.btn_help.clicked.connect(self.show_help)
        l.addWidget(self.btn_help)
        
        layout.addWidget(f)
        
    def show_help(self):
        wizard = HelpWizard(self, "generator")
        wizard.exec()
        
    def toggle_language(self):
        new_lang = "el" if self.lang == "en" else "en"
        self.lang = new_lang
        
        # Update config.json
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["language"] = new_lang
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except: pass
        
        # Refresh UI
        self.setup_ui()
        if hasattr(self, "log_area"):
            self.log_area.append(f"Language changed to: {new_lang.upper()}")

    def create_group(self, layout, title):
        group = QFrame()
        group.setObjectName("ElevatedFrame")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl = QLabel(title.upper())
        lbl.setObjectName("AccentLabel")
        group_layout.addWidget(lbl)
        
        layout.addWidget(group)
        return group_layout

    def setup_input_controls(self, layout):
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        self.file_entry = QLineEdit()
        self.file_entry.setPlaceholderText("Select video...")
        l.addWidget(self.file_entry, 1)
        
        btn = QPushButton("Browse")
        btn.setObjectName("PurpleButton")
        btn.clicked.connect(self.browse_input)
        l.addWidget(btn)
        
        layout.addWidget(f)

    def setup_output_group(self, layout):
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        self.out_entry = QLineEdit("./frames")
        l.addWidget(self.out_entry, 1)
        
        btn = QPushButton("Select")
        btn.clicked.connect(self.browse_dir)
        l.addWidget(btn)
        
        layout.addWidget(f)

    def setup_trimming_group(self, layout):
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        l.addWidget(QLabel("Start (s):"))
        self.start_trim = QLineEdit("0")
        self.start_trim.setFixedWidth(60)
        l.addWidget(self.start_trim)
        
        l.addWidget(QLabel("End (s):"))
        self.end_trim = QLineEdit("-1")
        self.end_trim.setFixedWidth(60)
        l.addWidget(self.end_trim)
        
        l.addWidget(QLabel("(-1 = End)"))
        l.addStretch()
        
        layout.addWidget(f)

    def setup_processing_group(self, layout):
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        l.addWidget(QLabel("Format:"))
        self.format_entry = QLineEdit(".jpg")
        self.format_entry.setFixedWidth(60)
        l.addWidget(self.format_entry)
        
        l.addWidget(QLabel("Width:"))
        self.resize_entry = QLineEdit("1280")
        self.resize_entry.setFixedWidth(80)
        l.addWidget(self.resize_entry)
        l.addStretch()
        
        layout.addWidget(f)

    def setup_ml_dataset_group(self, layout):
        self.ml_cb = QCheckBox("Enable ML Export Mode")
        layout.addWidget(self.ml_cb)
        
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        l.addWidget(QLabel("Train Split (%):"))
        self.split_slider = QSlider(Qt.Horizontal)
        self.split_slider.setRange(50, 95)
        self.split_slider.setValue(80)
        l.addWidget(self.split_slider)
        
        self.split_label = QLabel("80%")
        self.split_slider.valueChanged.connect(lambda v: self.split_label.setText(f"{v}%"))
        l.addWidget(self.split_label)
        layout.addWidget(f)
        
        f2 = QWidget()
        l2 = QHBoxLayout(f2)
        l2.setContentsMargins(0, 0, 0, 0)
        l2.addWidget(QLabel("Classes:"))
        self.classes_entry = QLineEdit()
        self.classes_entry.setPlaceholderText("e.g. Person, Car, Dog")
        l2.addWidget(self.classes_entry)
        layout.addWidget(f2)

    def setup_preview(self, layout):
        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet("background-color: #000000; border-radius: 10px;")
        self.preview_frame.setMinimumHeight(300)
        p_layout = QVBoxLayout(self.preview_frame)
        
        self.preview_label = QLabel(strings.get_string("gen_preview_lbl"))
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color: #333333; font-size: 16px; font-weight: bold;")
        p_layout.addWidget(self.preview_label)
        
        layout.addWidget(self.preview_frame)

    def setup_telemetry(self, layout):
        self.progress = QProgressBar()
        self.progress.setFixedHeight(15)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        f = QWidget()
        l = QHBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_stats = QLabel(get_string("gen_telemetry_ready"))
        self.lbl_stats.setStyleSheet("font-weight: bold;")
        l.addWidget(self.lbl_stats)
        l.addStretch()
        
        self.lbl_eta = QLabel(get_string("gen_telemetry_eta"))
        self.lbl_eta.setObjectName("DimLabel")
        l.addWidget(self.lbl_eta)
        
        layout.addWidget(f)

    def setup_log_area(self, layout):
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: #111214; font-size: 11px; color: #888888; border: none;")
        layout.addWidget(self.log_box, 1)

    def setup_help_sidebar(self, layout):
        lbl = QLabel("COMMAND CENTER")
        lbl.setObjectName("AccentLabel")
        lbl.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl)
        
        s1 = QFrame()
        s1.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px;")
        l1 = QVBoxLayout(s1)
        l1.addWidget(QLabel("🎥 EXTRACTION"))
        l1.addWidget(QLabel("• Single: Process 1 video\n• Batch: Process folder\n• Trim: Define Start/End\n• FPS: Adjust density"))
        layout.addWidget(s1)
        
        s2 = QFrame()
        s2.setStyleSheet("border: 1px solid #2A2D32; border-radius: 5px;")
        l2 = QVBoxLayout(s2)
        l2.addWidget(QLabel("🤖 ML EXPORT"))
        l2.addWidget(QLabel("• Mode: Auto-organize\n• Split: Train/Val ratio\n• Classes: Define labels\n• YAML: Auto-generated"))
        layout.addWidget(s2)
        
        layout.addStretch()

    def toggle_mode(self):
        self.is_batch_mode = self.mode_cb.isChecked()
        if self.is_batch_mode:
            self.file_entry.setPlaceholderText("Select folder with videos...")
            # We hide trimming inputs in PySide6 by disabling them
            self.start_trim.setEnabled(False)
            self.end_trim.setEnabled(False)
            self.log("MODE: Batch Folder Mode enabled.")
        else:
            self.file_entry.setPlaceholderText("Select video file...")
            self.start_trim.setEnabled(True)
            self.end_trim.setEnabled(True)
            self.log("MODE: Single Video Mode enabled.")

    def browse_input(self):
        if self.is_batch_mode:
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
            if path:
                self.file_entry.setText(path)
                vids = [f for f in os.listdir(path) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
                self.log(f"Found {len(vids)} videos in directory.")
                self.batch_files = [os.path.join(path, v).replace("\\", "/") for v in vids]
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
            if path:
                self.file_entry.setText(path)

    def browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.out_entry.setText(path)

    def toggle_engine(self):
        if self.is_running: return
        
        source = self.file_entry.text()
        if not source: return

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.start_btn.setText("PROCESSING...")
        self.status_dot.setText("● Busy")
        self.status_dot.setStyleSheet("color: #FF9800; font-weight: bold;")
        self.start_time = datetime.now()
        
        if hasattr(sys, '_MEIPASS'):
            engine_exe = resource_path(os.path.join("engine", "engine.exe"))
        else:
            engine_exe = os.path.join(os.path.dirname(__file__), "..", "engine", "build", "Debug", "engine.exe")
            if not os.path.exists(engine_exe): 
                engine_exe = os.path.join(os.path.dirname(__file__), "..", "engine", "build", "engine.exe")

        cmd = [
            engine_exe, source,
            "--output", self.out_entry.text(),
            "--format", self.format_entry.text()
        ]
        
        if not self.is_batch_mode:
            cmd.extend(["--start", self.start_trim.text(), "--end", self.end_trim.text()])
        
        if self.resize_entry.text().isdigit():
            cmd.extend(["--resize", self.resize_entry.text()])

        self.worker = EngineWorker(
            cmd, self.is_batch_mode, self.batch_files, 
            self.ml_cb.isChecked(), self.split_slider.value(), 
            self.classes_entry.text(), self.out_entry.text()
        )
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.thumb_signal.connect(self.update_thumbnail)
        self.worker.finished_signal.connect(self.reset_ui)
        self.worker.start()

    def update_thumbnail(self, b64_data):
        try:
            img_data = base64.b64decode(b64_data)
            img = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(img).scaled(self.preview_frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setText("")
        except: pass

    def update_progress(self, data):
        try:
            parts = data.split(":")
            curr, total = map(int, parts[1].split("/"))
            saved = parts[2]
            p = (curr / total) * 100
            self.progress.setValue(int(p))
            self.lbl_stats.setText(f"Frame: {curr}/{total} | Saved: {saved}")
            
            if curr > 0:
                elapsed = datetime.now() - self.start_time
                rem = (elapsed / curr) * (total - curr)
                self.lbl_eta.setText(f"ETA: {str(rem).split('.')[0]}")
        except: pass

    def log(self, msg):
        self.log_box.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def open_export_folder(self):
        if hasattr(self.worker, 'last_output_path'):
            os.startfile(os.path.normpath(self.worker.last_output_path))

    def reset_ui(self):
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.start_btn.setText(get_string("gen_start_btn"))
        self.status_dot.setText("● Finished")
        self.status_dot.setStyleSheet("color: #00E5FF; font-weight: bold;")
        self.open_folder_btn.show()

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = App()
    window.show()
    if not QApplication.instance().activeWindow():
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
