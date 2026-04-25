import customtkinter as ctk
import subprocess
import json
import os
import sys
from datetime import datetime

# Διαχείριση διαδρομών για τη δημιουργία ενιαίου εκτελέσιμου (PyInstaller)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Παλέτα χρωμάτων Industrial Dark
COLOR_BG_PRIMARY = "#111214"
COLOR_BG_ELEVATED = "#181A1D"
COLOR_ACCENT_BLUE = "#3A6EA5"
COLOR_ACCENT_PURPLE = "#6F4A8E"
COLOR_ACCENT_GREEN = "#4C8C72"
COLOR_TEXT_PRIMARY = "#E0E0E0"

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VIDEO TO ML SUITE")
        self.geometry("800x600")
        self.configure(fg_color=COLOR_BG_PRIMARY)
        
        self.config_path = "config.json"
        self.load_config()
        self.setup_ui()
        
        # Ορισμός εικονιδίου εφαρμογής
        try:
            icon_p = resource_path(os.path.join("shared", "icon.ico"))
            if os.path.exists(icon_p):
                self.iconbitmap(icon_p)
        except: pass

        self.log("Το σύστημα αρχικοποιήθηκε. Καλώς ήρθατε στο Video to ML Suite.")

    def load_config(self):
        default_config = {
            "output_path": "./frames",
            "default_split": 80,
            "engine_path": "./engine/build/Debug/engine.exe"
        }
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config

    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)
        self.log("Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς.")

    def setup_ui(self):
        # Πλευρική μπάρα κατάστασης
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=COLOR_BG_ELEVATED, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SUITE STATUS", font=("Consolas", 14, "bold"), text_color=COLOR_ACCENT_BLUE).pack(pady=(20, 10), padx=20)
        self.status_lbl = ctk.CTkLabel(self.sidebar, text="● ALL SYSTEMS OK", text_color="#4CAF50", font=("Consolas", 11))
        self.status_lbl.pack(padx=20)

        # Κύριο περιεχόμενο
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        self.header = ctk.CTkLabel(self.main_frame, text="VIDEO TO ML SUITE", font=("Consolas", 28, "bold"))
        self.header.pack(anchor="w", pady=(0, 10))
        
        # Λογότυπο εφαρμογής
        try:
            logo_p = resource_path(os.path.join("shared", "logo.png"))
            if os.path.exists(logo_p):
                from PIL import Image
                logo_img = ctk.CTkImage(light_image=Image.open(logo_p), dark_image=Image.open(logo_p), size=(100, 100))
                self.logo_lbl = ctk.CTkLabel(self.main_frame, image=logo_img, text="")
                self.logo_lbl.pack(anchor="w", pady=(0, 20))
        except: pass

        # Πλέγμα κουμπιών για τα modules
        self.grid = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid.pack(fill="both", expand=True)

        self.btn_generator = self.create_module_btn(
            self.grid, "1. FRAME EXTRACTOR", 
            "Εξαγωγή frames από βίντεο και προετοιμασία δομής YOLO.",
            COLOR_ACCENT_BLUE, self.launch_generator
        )
        self.btn_generator.pack(fill="x", pady=10)

        self.btn_labeler = self.create_module_btn(
            self.grid, "2. IMAGE ANNOTATOR", 
            "Σχολιασμός εικόνων και χρήση έξυπνης παρεμβολής.",
            COLOR_ACCENT_PURPLE, self.launch_labeler
        )
        self.btn_labeler.pack(fill="x", pady=10)

        self.btn_inspector = self.create_module_btn(
            self.grid, "3. DATASET INSPECTOR", 
            "Ανάλυση κατανομής κλάσεων και υγείας του dataset.",
            COLOR_ACCENT_BLUE, self.launch_inspector
        )
        self.btn_inspector.pack(fill="x", pady=10)

        self.btn_trainer = self.create_module_btn(
            self.grid, "4. TRAINING LAUNCHER", 
            "Εκπαίδευση μοντέλου YOLO στο προετοιμασμένο dataset.",
            COLOR_ACCENT_GREEN, self.launch_trainer
        )
        self.btn_trainer.pack(fill="x", pady=10)

        self.btn_settings = self.create_module_btn(
            self.grid, "SYSTEM SETTINGS", 
            "Ρύθμιση διαδρομών μηχανής και καθολικών προτιμήσεων.",
            "#444", self.show_settings
        )
        self.btn_settings.pack(fill="x", pady=10)

        # Περιοχή καταγραφής (logs) στο κάτω μέρος
        self.log_box = ctk.CTkTextbox(self.main_frame, height=150, fg_color="#0C0D0E", text_color="#888", font=("Consolas", 10))
        self.log_box.pack(fill="x", pady=(20, 0))

    def create_module_btn(self, container, title, desc, color, command):
        btn_frame = ctk.CTkFrame(container, fg_color=COLOR_BG_ELEVATED, corner_radius=10, border_width=1, border_color="#333")
        
        f_left = ctk.CTkFrame(btn_frame, fg_color="transparent")
        f_left.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(f_left, text=title, font=("Consolas", 18, "bold"), text_color=color).pack(anchor="w")
        ctk.CTkLabel(f_left, text=desc, font=("Consolas", 12), text_color="#888").pack(anchor="w")
        
        btn = ctk.CTkButton(btn_frame, text="LAUNCH", width=100, height=40, fg_color=color, hover_color="#333", command=command)
        btn.pack(side="right", padx=20)
        
        return btn_frame

    def log(self, msg):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{time_str}] {msg}\n")
        self.log_box.see("end")

    def launch_generator(self):
        self.log(f"Εκκίνηση Generator...")
        subprocess.Popen([sys.executable, sys.argv[0], "--generator"])

    def launch_labeler(self):
        self.log(f"Εκκίνηση Labeler...")
        subprocess.Popen([sys.executable, sys.argv[0], "--labeler"])

    def launch_inspector(self):
        self.log(f"Εκκίνηση Inspector...")
        subprocess.Popen([sys.executable, sys.argv[0], "--inspector"])

    def launch_trainer(self):
        self.log(f"Εκκίνηση Trainer...")
        subprocess.Popen([sys.executable, sys.argv[0], "--trainer"])

    def show_settings(self):
        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("SYSTEM SETTINGS")
        self.settings_window.geometry("500x400")
        self.settings_window.configure(fg_color=COLOR_BG_ELEVATED)
        self.settings_window.attributes("-topmost", True)

        ctk.CTkLabel(self.settings_window, text="GLOBAL CONFIGURATION", font=("Consolas", 16, "bold"), text_color=COLOR_ACCENT_BLUE).pack(pady=20)

        # Διαδρομή εξόδου
        f1 = ctk.CTkFrame(self.settings_window, fg_color="transparent")
        f1.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(f1, text="Default Output:").pack(side="left")
        self.set_out = ctk.CTkEntry(f1, width=200)
        self.set_out.insert(0, self.config["output_path"])
        self.set_out.pack(side="right")

        # Διαχωρισμός (Split)
        f2 = ctk.CTkFrame(self.settings_window, fg_color="transparent")
        f2.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(f2, text="Default Split (%):").pack(side="left")
        self.set_split = ctk.CTkEntry(f2, width=200)
        self.set_split.insert(0, str(self.config["default_split"]))
        self.set_split.pack(side="right")

        btn_save = ctk.CTkButton(self.settings_window, text="SAVE SETTINGS", fg_color=COLOR_ACCENT_GREEN, command=self.apply_settings)
        btn_save.pack(pady=40)

    def apply_settings(self):
        self.config["output_path"] = self.set_out.get()
        self.config["default_split"] = int(self.set_split.get())
        self.save_config()
        self.settings_window.destroy()

if __name__ == "__main__":
    # Έλεγχος αν η εφαρμογή εκτελείται ως υπο-λειτουργία (module)
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
    else:
        app = Dashboard()
        app.mainloop()

