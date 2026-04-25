import customtkinter as ctk
import subprocess
import threading
import os
import sys
import base64
import io
from PIL import Image, ImageTk
from tkinter import filedialog
from datetime import datetime, timedelta

# Παλέτα χρωμάτων Industrial Dark
COLOR_BG_PRIMARY = "#111214"
COLOR_BG_ELEVATED = "#181A1D"
COLOR_BG_SUNKEN = "#0C0D0E"
COLOR_ACCENT_BLUE = "#3A6EA5"
COLOR_ACCENT_PURPLE = "#6F4A8E"
COLOR_ACCENT_GREEN = "#4C8C72"
COLOR_TEXT_PRIMARY = "#E0E0E0"
COLOR_TEXT_DIM = "#808080"

# Διαχείριση διαδρομών για τη δημιουργία ενιαίου εκτελέσιμου (PyInstaller)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), "..", relative_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FRAME EXTRACTOR")
        self.geometry("1200x850")
        self.configure(fg_color=COLOR_BG_PRIMARY)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.is_running = False
        self.is_batch_mode = False
        self.batch_files = []
        self.current_video_duration = 0.0

        self.setup_ui()

    def setup_ui(self):
        # --- ΑΡΙΣΤΕΡΗ ΣΤΗΛΗ: ΕΛΕΓΧΟΣ & BATCH ---
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.setup_header(self.left_panel)
        
        # Επιλογή λειτουργίας
        self.mode_frame = ctk.CTkFrame(self.left_panel, fg_color=COLOR_BG_ELEVATED, corner_radius=10)
        self.mode_frame.pack(fill="x", pady=(0, 10))
        self.mode_switch = ctk.CTkSwitch(
            self.mode_frame, text="Batch Mode (Folder)", 
            command=self.toggle_mode, progress_color=COLOR_ACCENT_PURPLE
        )
        self.mode_switch.pack(side="left", padx=20, pady=10)

        # Ομάδα εισαγωγής αρχείων
        self.input_group = self.create_group(self.left_panel, "Input Sources")
        self.setup_input_controls(self.input_group)

        # Ομάδες εξόδου και επεξεργασίας
        self.setup_output_group(self.left_panel)
        self.setup_trimming_group(self.left_panel)
        self.setup_processing_group(self.left_panel)
        self.setup_ml_dataset_group(self.left_panel)
        
        self.start_btn = ctk.CTkButton(
            self.left_panel, text="START EXTRACTION", height=60,
            fg_color=COLOR_ACCENT_GREEN, hover_color="#3D705B",
            font=("Consolas", 18, "bold"), command=self.toggle_engine
        )
        self.start_btn.pack(fill="x", pady=(20, 0))

        self.open_folder_btn = ctk.CTkButton(
            self.left_panel, text="OPEN LAST EXPORT", height=40,
            fg_color=COLOR_BG_ELEVATED, border_width=1, border_color=COLOR_ACCENT_BLUE,
            command=self.open_export_folder
        )
        self.open_folder_btn.pack_forget()

        # --- ΔΕΞΙΑ ΣΤΗΛΗ: ΠΡΟΕΠΙΣΚΟΠΗΣΗ & ΤΗΛΕΜΕΤΡΙΑ ---
        self.right_panel = ctk.CTkFrame(self, fg_color=COLOR_BG_SUNKEN, corner_radius=15)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        
        self.setup_preview(self.right_panel)
        self.setup_telemetry(self.right_panel)
        self.setup_log_area(self.right_panel)

    def setup_header(self, container):
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="FRAME EXTRACTOR", font=("Consolas", 24, "bold")).pack(side="left")
        self.status_dot = ctk.CTkLabel(header, text="● Ready", text_color="#4CAF50")
        self.status_dot.pack(side="right")

    def create_group(self, container, title):
        group = ctk.CTkFrame(container, fg_color=COLOR_BG_ELEVATED, corner_radius=10)
        group.pack(fill="x", pady=5)
        ctk.CTkLabel(group, text=title.upper(), font=("Consolas", 12, "bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=15, pady=(10, 5))
        return group

    def setup_input_controls(self, group):
        self.file_frame = ctk.CTkFrame(group, fg_color="transparent")
        self.file_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Select video...", fg_color=COLOR_BG_SUNKEN, border_width=0)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(self.file_frame, text="Browse", width=80, fg_color=COLOR_ACCENT_PURPLE, command=self.browse_input)
        self.browse_btn.pack(side="right")

    def setup_output_group(self, container):
        group = self.create_group(container, "Output Settings")
        f1 = ctk.CTkFrame(group, fg_color="transparent")
        f1.pack(fill="x", padx=15, pady=(0, 15))
        self.out_entry = ctk.CTkEntry(f1, placeholder_text="Base Folder...", fg_color=COLOR_BG_SUNKEN, border_width=0)
        self.out_entry.insert(0, "./frames")
        self.out_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(f1, text="Select", width=80, command=self.browse_dir).pack(side="right")

    def setup_trimming_group(self, container):
        self.trim_group = self.create_group(container, "Video Trimming (Single Mode)")
        
        f = ctk.CTkFrame(self.trim_group, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(f, text="Start (s):", text_color=COLOR_TEXT_DIM).pack(side="left")
        self.start_trim = ctk.CTkEntry(f, width=60, fg_color=COLOR_BG_SUNKEN, border_width=0)
        self.start_trim.insert(0, "0")
        self.start_trim.pack(side="left", padx=5)
        
        ctk.CTkLabel(f, text="End (s):", text_color=COLOR_TEXT_DIM).pack(side="left", padx=(10, 0))
        self.end_trim = ctk.CTkEntry(f, width=60, fg_color=COLOR_BG_SUNKEN, border_width=0)
        self.end_trim.insert(0, "-1")
        self.end_trim.pack(side="left", padx=5)
        
        ctk.CTkLabel(f, text="(-1 = End)", font=("Consolas", 10), text_color=COLOR_TEXT_DIM).pack(side="left")

    def setup_processing_group(self, container):
        group = self.create_group(container, "Processing Options")
        
        f = ctk.CTkFrame(group, fg_color="transparent")
        f.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(f, text="Format:", text_color=COLOR_TEXT_DIM).pack(side="left")
        self.format_menu = ctk.CTkOptionMenu(f, values=[".jpg", ".webp", ".png"], width=100)
        self.format_menu.pack(side="left", padx=5)

        ctk.CTkLabel(f, text="Width:", text_color=COLOR_TEXT_DIM).pack(side="left", padx=(10, 0))
        self.resize_entry = ctk.CTkEntry(f, width=80, placeholder_text="1280", fg_color=COLOR_BG_SUNKEN, border_width=0)
        self.resize_entry.pack(side="left", padx=5)

    def setup_ml_dataset_group(self, container):
        self.ml_group = self.create_group(container, "ML Dataset Generator")
        
        # Διακόπτης ενεργοποίησης
        self.ml_mode_var = ctk.BooleanVar(value=False)
        self.ml_switch = ctk.CTkSwitch(
            self.ml_group, text="Enable ML Export Mode", 
            variable=self.ml_mode_var, progress_color=COLOR_ACCENT_BLUE
        )
        self.ml_switch.pack(anchor="w", padx=15, pady=5)

        # Αναλογία διαχωρισμού (Split Ratio)
        f_split = ctk.CTkFrame(self.ml_group, fg_color="transparent")
        f_split.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_split, text="Train Split (%):", text_color=COLOR_TEXT_DIM).pack(side="left")
        self.split_slider = ctk.CTkSlider(f_split, from_=50, to=95, number_of_steps=45, width=150)
        self.split_slider.set(80)
        self.split_slider.pack(side="left", padx=10)
        self.split_label = ctk.CTkLabel(f_split, text="80%", width=40)
        self.split_label.pack(side="left")
        self.split_slider.configure(command=lambda v: self.split_label.configure(text=f"{int(v)}%"))

        # Κλάσεις (Classes)
        f_classes = ctk.CTkFrame(self.ml_group, fg_color="transparent")
        f_classes.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(f_classes, text="Classes:", text_color=COLOR_TEXT_DIM).pack(side="left")
        self.classes_entry = ctk.CTkEntry(
            f_classes, placeholder_text="e.g. Person, Car, Dog", 
            fg_color=COLOR_BG_SUNKEN, border_width=0
        )
        self.classes_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def setup_preview(self, container):
        self.preview_frame = ctk.CTkFrame(container, fg_color="black", height=250, corner_radius=10)
        self.preview_frame.pack(fill="x", padx=20, pady=20)
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="LIVE PREVIEW", text_color="#333", font=("Consolas", 16, "bold"))
        self.preview_label.pack(expand=True, fill="both")

    def setup_telemetry(self, container):
        tel = ctk.CTkFrame(container, fg_color="transparent")
        tel.pack(fill="x", padx=20, pady=(0, 20))
        
        self.progress = ctk.CTkProgressBar(tel, height=15, progress_color=COLOR_ACCENT_GREEN)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=10)
        
        f = ctk.CTkFrame(tel, fg_color="transparent")
        f.pack(fill="x")
        self.lbl_stats = ctk.CTkLabel(f, text="Ready", font=("Consolas", 14), text_color=COLOR_TEXT_PRIMARY)
        self.lbl_stats.pack(side="left")
        self.lbl_eta = ctk.CTkLabel(f, text="ETA: --:--", font=("Consolas", 12), text_color=COLOR_TEXT_DIM)
        self.lbl_eta.pack(side="right")

    def setup_log_area(self, container):
        self.log_box = ctk.CTkTextbox(container, fg_color=COLOR_BG_SUNKEN, font=("Consolas", 11), text_color="#AAA")
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def toggle_mode(self):
        self.is_batch_mode = self.mode_switch.get()
        if self.is_batch_mode:
            self.file_entry.configure(placeholder_text="Select folder with videos...")
            self.trim_group.pack_forget()
            self.log("MODE: Batch Folder Mode enabled.")
        else:
            self.file_entry.configure(placeholder_text="Select video file...")
            self.trim_group.pack(fill="x", pady=5)
            self.log("MODE: Single Video Mode enabled.")

    def browse_input(self):
        if self.is_batch_mode:
            path = filedialog.askdirectory()
            if path:
                self.file_entry.delete(0, "end")
                self.file_entry.insert(0, path)
                # Αναζήτηση βίντεο
                vids = [f for f in os.listdir(path) if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov'))]
                self.log(f"Βρέθηκαν {len(vids)} βίντεο στον κατάλογο.")
                self.batch_files = [os.path.join(path, v).replace("\\", "/") for v in vids]
        else:
            path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov")])
            if path:
                self.file_entry.delete(0, "end")
                self.file_entry.insert(0, path)

    def browse_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, path)

    def toggle_engine(self):
        if self.is_running: return
        
        source = self.file_entry.get()
        if not source: return

        self.is_running = True
        self.start_btn.configure(state="disabled", text="PROCESSING...")
        self.status_dot.configure(text="● Busy", text_color="#FF9800")
        
        threading.Thread(target=self.engine_worker, daemon=True).start()

    def engine_worker(self):
        if self.is_batch_mode:
            for i, vid in enumerate(self.batch_files):
                self.log(f"BATCH [{i+1}/{len(self.batch_files)}]: Processing {os.path.basename(vid)}")
                self.run_single_video(vid)
        else:
            self.run_single_video(self.file_entry.get())
        
        if self.ml_mode_var.get():
            self.organize_ml_dataset()

        self.reset_ui()

    def run_single_video(self, video_path):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        out_path = os.path.join(self.out_entry.get(), video_name).replace("\\", "/")
        os.makedirs(out_path, exist_ok=True)
        self.last_output_path = out_path

        # Καθορισμός σωστής διαδρομής μηχανής (Bundled vs Dev)
        if hasattr(sys, '_MEIPASS'):
            engine_exe = resource_path(os.path.join("engine", "engine.exe"))
        else:
            engine_exe = os.path.join(os.path.dirname(__file__), "..", "engine", "build", "Debug", "engine.exe")
            if not os.path.exists(engine_exe): 
                engine_exe = os.path.join(os.path.dirname(__file__), "..", "engine", "build", "engine.exe")

        if not os.path.exists(engine_exe):
            self.log(f"CRITICAL ERROR: Engine not found at {engine_exe}")
            return
        
        cmd = [
            engine_exe, video_path,
            "--output", out_path,
            "--format", self.format_menu.get()
        ]
        
        if not self.is_batch_mode:
            cmd.extend(["--start", self.start_trim.get(), "--end", self.end_trim.get()])
        
        if self.resize_entry.get().isdigit():
            cmd.extend(["--resize", self.resize_entry.get()])

        self.start_time = datetime.now()
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, encoding='utf-8', errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        for line in process.stdout:
            line = line.strip()
            if line.startswith("THUMB:"):
                self.update_thumbnail(line[6:])
            elif line.startswith("PROGRESS:"):
                self.update_progress(line)
            elif line.startswith("REPORT:") or line.startswith("SUCCESS:"):
                self.log(line)
        
        process.wait()

    def update_thumbnail(self, b64_data):
        try:
            img_data = base64.b64decode(b64_data)
            img = Image.open(io.BytesIO(img_data))
            # Προσαρμογή στο πλαίσιο προεπισκόπησης
            img.thumbnail((400, 250))
            ctk_img = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=ctk_img, text="")
            self.preview_label.image = ctk_img
        except: pass

    def update_progress(self, data):
        try:
            parts = data.split(":")
            curr, total = map(int, parts[1].split("/"))
            saved = parts[2]
            p = curr / total
            self.progress.set(p)
            self.lbl_stats.configure(text=f"Frame: {curr}/{total} | Saved: {saved}")
            
            if p > 0:
                elapsed = datetime.now() - self.start_time
                rem = (elapsed / p) - elapsed
                self.lbl_eta.configure(text=f"ETA: {str(rem).split('.')[0]}")
        except: pass

    def log(self, msg):
        self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")

    def open_export_folder(self):
        if hasattr(self, 'last_output_path'):
            os.startfile(os.path.normpath(self.last_output_path))

    def reset_ui(self):
        self.is_running = False
        self.start_btn.configure(state="normal", text="START EXTRACTION")
        self.status_dot.configure(text="● Finished", text_color=COLOR_ACCENT_BLUE)
        self.open_folder_btn.pack(fill="x", pady=10)

    def organize_ml_dataset(self):
        """Οργάνωση των εξαγόμενων frames σε φακέλους Train/Val και δημιουργία του dataset.yaml."""
        import random
        import shutil

        base_dir = self.last_output_path
        self.log("ML: Organizing dataset...")

        # Ανάκτηση όλων των εξαγόμενων εικόνων
        valid_exts = (".jpg", ".webp", ".png")
        all_frames = [f for f in os.listdir(base_dir) if f.lower().endswith(valid_exts)]
        
        if not all_frames:
            self.log("ML: No frames found to organize.")
            return

        random.shuffle(all_frames)
        
        split_point = int(len(all_frames) * (self.split_slider.get() / 100))
        train_frames = all_frames[:split_point]
        val_frames = all_frames[split_point:]

        # Δημιουργία δομής φακέλων
        dirs = {
            "train": os.path.join(base_dir, "train", "images"),
            "val": os.path.join(base_dir, "val", "images")
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)

        # Μετακίνηση αρχείων
        for f in train_frames:
            shutil.move(os.path.join(base_dir, f), os.path.join(dirs["train"], f))
        for f in val_frames:
            shutil.move(os.path.join(base_dir, f), os.path.join(dirs["val"], f))

        # Δημιουργία dataset.yaml
        classes = [c.strip() for c in self.classes_entry.get().split(",") if c.strip()]
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

        self.log(f"ML: Dataset ready! Train: {len(train_frames)}, Val: {len(val_frames)}")
        self.log(f"ML: Generated {os.path.basename(yaml_path)}")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

