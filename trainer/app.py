import customtkinter as ctk
import os
import subprocess
import threading
import sys

# Palette
COLOR_BG = "#111214"
COLOR_ACCENT = "#4C8C72" # Green for Training

class TrainerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TRAINING LAUNCHER")
        self.geometry("900x800")
        self.configure(fg_color=COLOR_BG)

        self.is_training = False
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, height=80, fg_color="#181A1D")
        self.header.pack(side="top", fill="x")
        ctk.CTkLabel(self.header, text="MODEL TRAINER", font=("Consolas", 22, "bold")).pack(side="left", padx=30)
        
        # Settings Panel
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        self.config_group = self.create_group(self.main_frame, "Training Configuration")
        
        # Dataset YAML
        f1 = ctk.CTkFrame(self.config_group, fg_color="transparent")
        f1.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f1, text="Dataset YAML:").pack(side="left")
        self.yaml_entry = ctk.CTkEntry(f1, width=300, fg_color="#0C0D0E")
        self.yaml_entry.pack(side="left", padx=10)
        ctk.CTkButton(f1, text="Browse", width=80, command=self.browse_yaml).pack(side="right")

        # Model Size
        f2 = ctk.CTkFrame(self.config_group, fg_color="transparent")
        f2.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f2, text="Model Size:").pack(side="left")
        self.model_menu = ctk.CTkOptionMenu(f2, values=["yolov8n.pt (Nano)", "yolov8s.pt (Small)", "yolov8m.pt (Medium)"], width=200)
        self.model_menu.pack(side="left", padx=10)

        # Epochs
        f3 = ctk.CTkFrame(self.config_group, fg_color="transparent")
        f3.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f3, text="Epochs:").pack(side="left")
        self.epochs_entry = ctk.CTkEntry(f3, width=80, fg_color="#0C0D0E")
        self.epochs_entry.insert(0, "50")
        self.epochs_entry.pack(side="left", padx=10)

        # Start Button
        self.btn_train = ctk.CTkButton(
            self.main_frame, text="START TRAINING", height=60, 
            fg_color=COLOR_ACCENT, hover_color="#3D705B",
            font=("Consolas", 18, "bold"), command=self.start_training
        )
        self.btn_train.pack(fill="x", pady=30)

        # Console Output
        self.console = ctk.CTkTextbox(self.main_frame, fg_color="#0C0D0E", text_color="#AAA", font=("Consolas", 11))
        self.console.pack(fill="both", expand=True)

    def create_group(self, container, title):
        group = ctk.CTkFrame(container, fg_color="#181A1D", corner_radius=10)
        group.pack(fill="x", pady=10)
        ctk.CTkLabel(group, text=title.upper(), font=("Consolas", 12, "bold"), text_color="#3A6EA5").pack(anchor="w", padx=20, pady=(15, 5))
        return group

    def browse_yaml(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("YAML Files", "*.yaml")])
        if path:
            self.yaml_entry.delete(0, "end")
            self.yaml_entry.insert(0, path)

    def log(self, msg):
        self.console.insert("end", msg + "\n")
        self.console.see("end")

    def start_training(self):
        if self.is_training: return
        
        yaml_path = self.yaml_entry.get()
        if not yaml_path:
            self.log("ERROR: Please select a dataset.yaml")
            return

        self.is_training = True
        self.btn_train.configure(state="disabled", text="TRAINING IN PROGRESS...")
        
        threading.Thread(target=self.training_worker, daemon=True).start()

    def training_worker(self):
        model_name = self.model_menu.get().split()[0]
        epochs = self.epochs_entry.get()
        yaml_path = self.yaml_entry.get()

        self.log(f"Initializing YOLO Training with {model_name}...")
        self.log(f"Dataset: {yaml_path}")
        self.log(f"Epochs: {epochs}")
        
        # Command to run YOLO training
        cmd = [
            sys.executable, "-m", "ultralytics", "train",
            f"model={model_name}",
            f"data={yaml_path}",
            f"epochs={epochs}",
            "imgsz=640"
        ]

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace'
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            self.log("\nTRAINING COMPLETED SUCCESSFULLY!")
        except Exception as e:
            self.log(f"ERROR: {e}")
        
        self.is_training = False
        self.btn_train.configure(state="normal", text="START TRAINING")

def main():
    app = TrainerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
