import customtkinter as ctk
import os
import glob

# Palette
COLOR_BG = "#111214"
COLOR_ACCENT = "#3A6EA5"

class InspectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DATASET INSPECTOR")
        self.geometry("900x700")
        self.configure(fg_color=COLOR_BG)

        self.dataset_path = ""
        self.stats = {} # class_id: count
        self.class_names = []

        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, height=80, fg_color="#181A1D")
        self.header.pack(side="top", fill="x")
        ctk.CTkLabel(self.header, text="DATASET ANALYZER", font=("Consolas", 22, "bold")).pack(side="left", padx=30)
        
        self.btn_load = ctk.CTkButton(self.header, text="LOAD DATASET.YAML", fg_color=COLOR_ACCENT, command=self.load_dataset)
        self.btn_load.pack(side="right", padx=30)

        # Main Layout
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # Statistics Panel
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="#0C0D0E", corner_radius=15)
        self.stats_frame.pack(fill="both", expand=True)
        
        self.lbl_summary = ctk.CTkLabel(self.stats_frame, text="Load a dataset to see statistics...", font=("Consolas", 14), text_color="#888")
        self.lbl_summary.pack(pady=100)

    def load_dataset(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("YAML Files", "*.yaml")])
        if path:
            self.dataset_path = path
            self.analyze_dataset()

    def analyze_dataset(self):
        import yaml
        try:
            with open(self.dataset_path, "r") as f:
                data = yaml.safe_load(f)
            
            base_dir = os.path.dirname(self.dataset_path)
            self.class_names = data.get("names", [])
            if isinstance(self.class_names, dict):
                self.class_names = list(self.class_names.values())
            
            train_labels = os.path.join(base_dir, data.get("train", "").replace("images", "labels"))
            val_labels = os.path.join(base_dir, data.get("val", "").replace("images", "labels"))
            
            counts = {i: 0 for i in range(len(self.class_names))}
            total_labels = 0

            # Scan files
            for folder in [train_labels, val_labels]:
                if os.path.exists(folder):
                    for txt in glob.glob(os.path.join(folder, "*.txt")):
                        with open(txt, "r") as f:
                            for line in f:
                                parts = line.split()
                                if parts:
                                    cls_id = int(parts[0])
                                    counts[cls_id] = counts.get(cls_id, 0) + 1
                                    total_labels += 1

            self.update_stats_view(counts, total_labels)
        except Exception as e:
            print(f"Error analyzing dataset: {e}")

    def update_stats_view(self, counts, total):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.stats_frame, text="CLASS DISTRIBUTION", font=("Consolas", 18, "bold"), text_color=COLOR_ACCENT).pack(pady=20)
        
        max_count = max(counts.values()) if counts.values() else 1
        
        for i, (cls_id, count) in enumerate(counts.items()):
            name = self.class_names[i] if i < len(self.class_names) else f"ID {i}"
            
            row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=5)
            
            ctk.CTkLabel(row, text=f"{name:.<15}", font=("Consolas", 12)).pack(side="left")
            
            # Progress bar as a bar chart
            bar_width = (count / max_count) * 400
            bar = ctk.CTkFrame(row, width=bar_width, height=15, fg_color=COLOR_ACCENT, corner_radius=2)
            bar.pack(side="left", padx=10)
            
            ctk.CTkLabel(row, text=str(count), font=("Consolas", 12, "bold")).pack(side="left")

        ctk.CTkLabel(self.stats_frame, text=f"\nTOTAL LABELED OBJECTS: {total}", font=("Consolas", 14, "bold"), text_color="#4CAF50").pack(pady=20)

def main():
    app = InspectorApp()
    app.mainloop()

if __name__ == "__main__":
    main()
