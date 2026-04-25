import customtkinter as ctk
import os
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog

# Παλέτα χρωμάτων
COLOR_BG = "#111214"
COLOR_ACCENT = "#6F4A8E" # Μωβ για τον Labeler
COLOR_TEXT_DIM = "#888888"

class LabelerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IMAGE ANNOTATOR")
        self.geometry("1400x900")
        self.configure(fg_color=COLOR_BG)

        # Κατάσταση εφαρμογής (State)
        self.image_folder = ""
        self.images = []
        self.current_idx = 0
        self.rects = [] # Λίστα από (x1, y1, x2, y2, class_id)
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.keyframes = {} 
        self.classes = ["Object"] # Προεπιλογή
        self.current_class_id = 0
        self.last_keyframe_idx = None
        
        self.setup_ui()

    def setup_ui(self):
        # Πάνω μπάρα (Top Bar)
        self.top_bar = ctk.CTkFrame(self, height=60, fg_color="#181A1D")
        self.top_bar.pack(side="top", fill="x")
        
        ctk.CTkLabel(self.top_bar, text="IMAGE ANNOTATOR", font=("Consolas", 18, "bold")).pack(side="left", padx=20)
        
        self.btn_open = ctk.CTkButton(self.top_bar, text="OPEN DATASET", fg_color=COLOR_ACCENT, command=self.open_folder)
        self.btn_open.pack(side="left", padx=10)

        ctk.CTkLabel(self.top_bar, text="CLASS:", text_color=COLOR_TEXT_DIM).pack(side="left", padx=(20, 5))
        self.class_menu = ctk.CTkOptionMenu(self.top_bar, values=self.classes, command=self.change_class)
        self.class_menu.pack(side="left")

        self.lbl_info = ctk.CTkLabel(self.top_bar, text="No images loaded", text_color="#888")
        self.lbl_info.pack(side="right", padx=20)

        # Κύριο Layout
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Αριστερά: Καμβάς (Canvas)
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.canvas_frame.pack(side="left", fill="both", expand=True)
        
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Δεξιά: Πάνελ Ελέγχου (Control Panel)
        self.ctrl_panel = ctk.CTkFrame(self.main_frame, width=300, fg_color="#181A1D")
        self.ctrl_panel.pack(side="right", fill="y", padx=(10, 0))
        
        ctk.CTkLabel(self.ctrl_panel, text="LABELS", font=("Consolas", 14, "bold")).pack(pady=10)
        
        self.labels_list = ctk.CTkTextbox(self.ctrl_panel, height=300, fg_color="#0C0D0E")
        self.labels_list.pack(fill="x", padx=10)

        self.btn_save = ctk.CTkButton(self.ctrl_panel, text="SAVE (S)", fg_color="#4C8C72", command=self.save_labels)
        self.btn_save.pack(fill="x", padx=10, pady=20)
        
        self.btn_next = ctk.CTkButton(self.ctrl_panel, text="NEXT (D)", command=self.next_image)
        self.btn_next.pack(fill="x", padx=10, pady=5)
        
        self.btn_prev = ctk.CTkButton(self.ctrl_panel, text="PREV (A)", command=self.prev_image)
        self.btn_prev.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.ctrl_panel, text="SMART TOOLS", font=("Consolas", 14, "bold")).pack(pady=(20, 10))
        
        self.btn_keyframe = ctk.CTkButton(self.ctrl_panel, text="SET KEYFRAME (K)", fg_color=COLOR_ACCENT, command=self.set_keyframe)
        self.btn_keyframe.pack(fill="x", padx=10, pady=5)
        
        self.btn_interpolate = ctk.CTkButton(self.ctrl_panel, text="INTERPOLATE (I)", fg_color="#3A6EA5", command=self.run_interpolation)
        self.btn_interpolate.pack(fill="x", padx=10, pady=5)

        # Συντομεύσεις Πληκτρολογίου
        self.bind("<s>", lambda e: self.save_labels())
        self.bind("<d>", lambda e: self.next_image())
        self.bind("<a>", lambda e: self.prev_image())
        self.bind("<k>", lambda e: self.set_keyframe())
        self.bind("<i>", lambda e: self.run_interpolation())

    def open_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.image_folder = path
            valid_exts = (".jpg", ".png", ".webp")
            self.images = [f for f in os.listdir(path) if f.lower().endswith(valid_exts)]
            self.current_idx = 0
            if self.images:
                self.load_image()

    def load_image(self):
        img_path = os.path.join(self.image_folder, self.images[self.current_idx])
        self.img = Image.open(img_path)
        self.orig_w, self.orig_h = self.img.size
        
        # Προσαρμογή μεγέθους στον καμβά
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cw < 100: cw, ch = 1000, 700 
        
        # Υπολογισμός αναλογιών (aspect ratio)
        ratio = min(cw/self.orig_w, ch/self.orig_h)
        self.display_w = int(self.orig_w * ratio)
        self.display_h = int(self.orig_h * ratio)
        
        img_resized = self.img.resize((self.display_w, self.display_h), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_resized)
        
        self.canvas.delete("all")
        # Κεντράρισμα εικόνας
        self.offset_x = (cw - self.display_w) // 2
        self.offset_y = (ch - self.display_h) // 2
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.tk_img, anchor="nw")
        
        self.lbl_info.configure(text=f"Image {self.current_idx + 1}/{len(self.images)}: {self.images[self.current_idx]}")
        self.rects = []
        self.load_existing_labels()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="yellow", width=2)

    def on_drag(self, event):
        self.canvas.coords(self.current_rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        self.rects.append((self.start_x, self.start_y, event.x, event.y, self.current_class_id))
        self.update_labels_list()

    def change_class(self, val):
        self.current_class_id = self.classes.index(val)

    def update_labels_list(self):
        self.labels_list.delete("1.0", "end")
        for i, r in enumerate(self.rects):
            self.labels_list.insert("end", f"Box {i}: {r[0]},{r[1]} -> {r[2]},{r[3]}\n")

    def save_labels(self):
        if not self.images: return
        self.save_yolo_labels(self.current_idx, self.rects)
        self.btn_save.configure(text="SAVED!", fg_color="white", text_color="black")
        self.after(1000, lambda: self.btn_save.configure(text="SAVE (S)", fg_color="#4C8C72", text_color="white"))

    def next_image(self):
        if self.current_idx < len(self.images) - 1:
            self.save_yolo_labels(self.current_idx, self.rects) # Αυτόματη αποθήκευση
            self.current_idx += 1
            self.load_image()

    def prev_image(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.load_image()

    def load_existing_labels(self):
        # Λογική για ανάγνωση υπαρχόντων αρχείων .txt
        pass

    def set_keyframe(self):
        if not self.rects: return
        self.keyframes[self.current_idx] = [r for r in self.rects]
        self.log(f"Keyframe set at index {self.current_idx}")
        self.btn_keyframe.configure(text="KEYFRAME SET!", fg_color="white", text_color="black")
        self.after(1000, lambda: self.btn_keyframe.configure(text="SET KEYFRAME (K)", fg_color=COLOR_ACCENT, text_color="white"))

    def run_interpolation(self):
        if len(self.keyframes) < 2:
            self.log("ERROR: Need at least 2 keyframes to interpolate.")
            return

        sorted_keys = sorted(self.keyframes.keys())
        self.log("Interpolating all gaps...")
        
        for i in range(len(sorted_keys) - 1):
            start_idx = sorted_keys[i]
            end_idx = sorted_keys[i+1]
            
            start_rects = self.keyframes[start_idx]
            end_rects = self.keyframes[end_idx]
            
            if len(start_rects) != len(end_rects):
                self.log(f"SKIP: Keyframe {start_idx} and {end_idx} have different number of boxes.")
                continue

            num_steps = end_idx - start_idx
            for step in range(1, num_steps):
                current_step_idx = start_idx + step
                interp_rects = []
                
                alpha = step / num_steps
                for r_start, r_end in zip(start_rects, end_rects):
                    # Γραμμική παρεμβολή συντεταγμένων
                    nx1 = r_start[0] + (r_end[0] - r_start[0]) * alpha
                    ny1 = r_start[1] + (r_end[1] - r_start[1]) * alpha
                    nx2 = r_start[2] + (r_end[2] - r_start[2]) * alpha
                    ny2 = r_start[3] + (r_end[3] - r_start[3]) * alpha
                    interp_rects.append((nx1, ny1, nx2, ny2, r_start[4]))
                
                self.save_yolo_labels(current_step_idx, interp_rects)

        self.log("Interpolation complete.")

    def save_yolo_labels(self, idx, rects):
        if not rects: return
        img_name = self.images[idx]
        txt_name = os.path.splitext(img_name)[0] + ".txt"
        txt_path = os.path.join(self.image_folder, txt_name)

        yolo_lines = []
        for r in rects:
            # Μετατροπή συντεταγμένων καμβά σε κανονικοποιημένες συντεταγμένες εικόνας
            rx1 = (r[0] - self.offset_x) / self.display_w
            ry1 = (r[1] - self.offset_y) / self.display_h
            rx2 = (r[2] - self.offset_x) / self.display_w
            ry2 = (r[3] - self.offset_y) / self.display_h

            # Κέντρο και μέγεθος πλαισίου (Bounding box)
            w = abs(rx2 - rx1)
            h = abs(ry2 - ry1)
            cx = (rx1 + rx2) / 2
            cy = (ry1 + ry2) / 2
            
            yolo_lines.append(f"{r[4]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        with open(txt_path, "w") as f:
            f.write("\n".join(yolo_lines))

    def load_classes(self):
        # Αναζήτηση αρχείου dataset.yaml στον γονικό κατάλογο
        parent = os.path.dirname(os.path.dirname(self.image_folder))
        yaml_path = os.path.join(parent, "dataset.yaml")
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, "r") as f:
                    content = f.read()
                    if "names:" in content:
                        classes_part = content.split("names:")[1].strip()
                        self.classes = []
                        for line in classes_part.split("\n"):
                            if ":" in line:
                                self.classes.append(line.split(":")[1].strip())
                        self.class_menu.configure(values=self.classes)
                        self.class_menu.set(self.classes[0])
            except: pass

    def log(self, msg):
        print(f"[Annotator] {msg}")

def main():
    app = LabelerApp()
    app.mainloop()

if __name__ == "__main__":
    main()

