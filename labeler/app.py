import customtkinter as ctk
import os
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog

# Παλέτα χρωμάτων
COLOR_BG = "#0C0D0E"
COLOR_ACCENT = "#00E5FF" # Neon Cyan for high visibility
COLOR_ACCENT_DIM = "#00838F"
COLOR_TEXT_DIM = "#B0B0B0"
COLOR_TEXT_BRIGHT = "#FFFFFF"

class LabelerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SMART IMAGE ANNOTATOR")
        self.geometry("1200x800")
        self.minsize(1200, 800)
        self.configure(fg_color=COLOR_BG)

        # Κατάσταση εφαρμογής (State)
        self.image_folder = ""
        self.images = []
        self.current_idx = 0
        self.rects = [] # Λίστα από [x1, y1, x2, y2, class_id, canvas_id, text_id]
        self.selected_idx = None # Δείκτης του επιλεγμένου box
        self.start_x = None
        self.start_y = None
        self.is_moving = False # Αν μετακινούμε ένα υπάρχον box
        self.is_resizing = False # Αν αλλάζουμε μέγεθος
        self.resize_corner = None # Ποια γωνία πιάσαμε (0: top-left, 1: top-right, 2: bot-right, 3: bot-left)
        self.current_rect = None
        self.keyframes = {} 
        self.classes = ["Object"] # Προεπιλογή
        self.current_class_id = 0
        self.last_keyframe_idx = None
        
        # UI Elements for Crosshair and HUD
        self.crosshair_v = None
        self.crosshair_h = None
        self.prev_rects = [] # Για το Onion Skinning
        
        self.setup_ui()

    def setup_ui(self):
        # Πάνω μπάρα (Top Bar)
        self.top_bar = ctk.CTkFrame(self, height=60, fg_color="#181A1D")
        self.top_bar.pack(side="top", fill="x")
        
        ctk.CTkLabel(self.top_bar, text="IMAGE ANNOTATOR", font=("Consolas", 18, "bold")).pack(side="left", padx=20)
        
        self.open_btn = ctk.CTkButton(self.top_bar, text="OPEN DATASET", fg_color="#6F4A8E", hover_color="#5B3C75", command=self.open_folder)
        self.open_btn.pack(side="left", padx=10)

        ctk.CTkLabel(self.top_bar, text="CLASS:", text_color=COLOR_TEXT_DIM).pack(side="left", padx=(20, 5))
        self.class_menu = ctk.CTkOptionMenu(self.top_bar, values=self.classes, command=self.change_class)
        self.class_menu.pack(side="left")

        self.lbl_info = ctk.CTkLabel(self.top_bar, text="No images loaded", text_color="#888")
        self.lbl_info.pack(side="right", padx=20)

        # Κύριο Layout
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Αριστερή Μπάρα Οδηγιών (Help Sidebar)
        self.help_sidebar = ctk.CTkFrame(self.main_frame, width=220, fg_color="#181A1D")
        self.help_sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.setup_help_sidebar()

        # Υπόλοιπο μέρος: Καμβάς + Πάνελ
        self.upper_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.upper_frame.pack(side="left", fill="both", expand=True)

        # Αριστερά (στο κέντρο πλέον): Καμβάς (Canvas)
        self.canvas_frame = ctk.CTkFrame(self.upper_frame, fg_color="black")
        self.canvas_frame.pack(side="left", fill="both", expand=True)
        
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.update_crosshair)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        # Δεξιά: Πάνελ Ελέγχου (Control Panel)
        self.ctrl_panel = ctk.CTkFrame(self.upper_frame, width=300, fg_color="#181A1D")
        self.ctrl_panel.pack(side="right", fill="y", padx=(10, 0))
        
        self.guidance_lbl = ctk.CTkLabel(self.ctrl_panel, text="DRAW A BOX TO START", text_color=COLOR_ACCENT, font=("Consolas", 11, "italic"), wraplength=250)
        self.guidance_lbl.pack(pady=(10, 0))
        
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
        
        self.btn_keyframe = ctk.CTkButton(self.ctrl_panel, text="SET KEYFRAME (K)", fg_color="#6F4A8E", hover_color="#5B3C75", command=self.set_keyframe)
        self.btn_keyframe.pack(fill="x", padx=10, pady=5)
        
        self.btn_interpolate = ctk.CTkButton(self.ctrl_panel, text="INTERPOLATE (I)", fg_color="#3A6EA5", command=self.run_interpolation)
        self.btn_interpolate.pack(fill="x", padx=10, pady=5)

        self.save_status_lbl = ctk.CTkLabel(self.ctrl_panel, text="● SYSTEM READY", text_color="#888", font=("Consolas", 10))
        self.save_status_lbl.pack(pady=20)

        # Κάτω μέρος: Timeline
        self.timeline_frame = ctk.CTkScrollableFrame(self, height=120, orientation="horizontal", fg_color="#0C0D0E", corner_radius=0)
        self.timeline_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        self.thumb_btns = []

    def setup_help_sidebar(self):
        # Header
        ctk.CTkLabel(self.help_sidebar, text="COMMAND CENTER", font=("Consolas", 18, "bold"), text_color=COLOR_ACCENT).pack(pady=(20, 15))
        
        # Section 1: Manual Mode
        s1 = self.create_help_section("🖱️ MANUAL LABELING", [
            "• DRAW: Click & Drag",
            "• NAME: Type in Popup",
            "• SAVE: Auto on Release",
            "• CLASS: Keys [1-9]"
        ])
        s1.pack(fill="x", padx=15, pady=8)

        # Section 2: Video Mode
        s2 = self.create_help_section("🎥 VIDEO AUTOMATION", [
            "• START: Press 'K'",
            "• END FRAME: Move Box",
            "• MARK END: Press 'K'",
            "• RUN: Press 'I' (Interp)"
        ])
        s2.pack(fill="x", padx=15, pady=8)

        # Section 3: Editing
        s3 = self.create_help_section("🔧 EDITING TOOLS", [
            "• SELECT: Click Box",
            "• MOVE: Drag Center",
            "• RESIZE: Drag Dots",
            "• RENAME: Double Click",
            "• DELETE: [Backspace]"
        ])
        s3.pack(fill="x", padx=15, pady=8)

        # Section 4: Hotkeys
        s4 = self.create_help_section("⌨️ QUICK ACTIONS", [
            "• [D]: Next Image",
            "• [A]: Prev Image",
            "• [S]: Manual Save",
            "• [K]: Set Keyframe",
            "• [I]: Interpolate"
        ])
        s4.pack(fill="x", padx=15, pady=8)

    def create_help_section(self, title, items):
        # Frame με ελαφρύ border για να "ξεχωρίζει"
        f = ctk.CTkFrame(self.help_sidebar, fg_color="#121417", border_width=1, border_color="#2A2D32")
        
        # Τίτλος με έντονο χρώμα
        ctk.CTkLabel(f, text=title, font=("Consolas", 13, "bold"), text_color=COLOR_ACCENT).pack(pady=(8, 4), padx=10, anchor="w")
        
        # Στοιχεία με υψηλή αντίθεση
        for item in items:
            ctk.CTkLabel(f, text=item, font=("Consolas", 11), text_color=COLOR_TEXT_BRIGHT, justify="left").pack(padx=15, anchor="w", pady=1)
        return f

        # Συντομεύσεις Πληκτρολογίου
        self.bind("<s>", lambda e: self.save_labels())
        self.bind("<d>", lambda e: self.next_image())
        self.bind("<a>", lambda e: self.prev_image())
        self.bind("<k>", lambda e: self.set_keyframe())
        self.bind("<i>", lambda e: self.run_interpolation())
        self.bind("<Delete>", lambda e: self.delete_selected())
        self.bind("<BackSpace>", lambda e: self.delete_selected())
        
        # Αριθμητικά Hotkeys για κλάσεις
        for i in range(1, 10):
            self.bind(str(i), lambda e, i=i: self.quick_change_class(i-1))

    def quick_change_class(self, idx):
        if idx < len(self.classes):
            self.current_class_id = idx
            self.class_menu.set(self.classes[idx])
            self.log(f"Αλλαγή κλάσης σε: {self.classes[idx]}")

    def update_crosshair(self, event):
        # Ενημέρωση των γραμμών του σταυρονήματος
        if self.crosshair_v: self.canvas.delete(self.crosshair_v)
        if self.crosshair_h: self.canvas.delete(self.crosshair_h)
        
        # Μόνο αν είμαστε πάνω στην εικόνα
        self.crosshair_v = self.canvas.create_line(event.x, 0, event.x, self.canvas.winfo_height(), fill="#444", dash=(4, 4))
        self.crosshair_h = self.canvas.create_line(0, event.y, self.canvas.winfo_width(), event.y, fill="#444", dash=(4, 4))

    def open_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.image_folder = path
            valid_exts = (".jpg", ".png", ".webp")
            self.images = [f for f in os.listdir(path) if f.lower().endswith(valid_exts)]
            self.current_idx = 0
            if self.images:
                self.load_classes_from_folder()
                self.update_timeline()
                self.load_image()

    def load_classes_from_folder(self):
        # Έλεγχος για αρχείο classes.txt στον τρέχοντα κατάλογο
        classes_path = os.path.join(self.image_folder, "classes.txt")
        if os.path.exists(classes_path):
            with open(classes_path, "r") as f:
                self.classes = [line.strip() for line in f if line.strip()]
                self.class_menu.configure(values=self.classes)
                if self.classes:
                    self.class_menu.set(self.classes[0])
                self.log("Οι κλάσεις φορτώθηκαν από το classes.txt")

    def update_timeline(self):
        # Καθαρισμός timeline
        for btn in self.thumb_btns: btn.destroy()
        self.thumb_btns = []
        
        for i, img_name in enumerate(self.images):
            # Δημιουργία ενός "indicator" κουμπιού για κάθε frame
            text = str(i+1)
            color = "#333"
            border_w = 0
            
            if i in self.keyframes: 
                color = COLOR_ACCENT
                text = f"⬥ {i+1}" # Σύμβολο για Keyframe
                border_w = 2
            
            btn = ctk.CTkButton(
                self.timeline_frame, text=text, width=50, height=60, 
                fg_color=color, hover_color="#555", border_width=border_w, border_color="white",
                command=lambda idx=i: self.jump_to_image(idx)
            )
            btn.pack(side="left", padx=2)
            self.thumb_btns.append(btn)
            
        # Ενημέρωση οδηγιών
        self.update_guidance()

    def update_guidance(self):
        kf_count = len(self.keyframes)
        if kf_count == 0:
            self.guidance_lbl.configure(text="STEP 1: Draw a box and press 'K' to set a Keyframe.")
        elif kf_count == 1:
            self.guidance_lbl.configure(text="STEP 2: Go to another frame, adjust the box, and press 'K' again.")
        else:
            self.guidance_lbl.configure(text="STEP 3: Press 'I' to auto-calculate movement between Keyframes.")

    def jump_to_image(self, idx):
        self.save_yolo_labels(self.current_idx, self.rects)
        self.current_idx = idx
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
        
        self.draw_onion_skin() # Προβολή προηγούμενων boxes
        self.lbl_info.configure(text=f"Image {self.current_idx + 1}/{len(self.images)}: {self.images[self.current_idx]}")
        self.rects = []
        self.selected_idx = None # Reset selection
        self.load_existing_labels()
        self.redraw_all()

    def draw_onion_skin(self):
        # Onion Skinning: Προβολή προηγούμενου frame boxes αν υπάρχουν
        if self.current_idx > 0:
            prev_idx = self.current_idx - 1
            # Εδώ θα μπορούσαμε να διαβάσουμε το προηγούμενο αρχείο .txt
            # Για την ώρα χρησιμοποιούμε τα keyframes αν υπάρχουν
            if prev_idx in self.keyframes:
                for r in self.keyframes[prev_idx]:
                    self.canvas.create_rectangle(r[0], r[1], r[2], r[3], outline=COLOR_ACCENT, dash=(2, 2), width=1)

    def redraw_all(self):
        # Καθαρισμός προηγούμενων boxes
        for r in self.rects:
            if len(r) > 5:
                self.canvas.delete(r[5])
                self.canvas.delete(r[6])
        
        # Επανασχεδιασμός όλων των boxes και των HUD labels
        for i, r in enumerate(self.rects):
            color = "yellow"
            width = 2
            if i == self.selected_idx:
                color = "#00FF00" # Πράσινο για το επιλεγμένο
                width = 3
            
            # Box
            cid = self.canvas.create_rectangle(r[0], r[1], r[2], r[3], outline=color, width=width)
            # HUD Label
            class_name = self.classes[r[4]] if r[4] < len(self.classes) else "Unknown"
            tid = self.canvas.create_text(r[0], r[1]-10, text=f"[{r[4]}] {class_name}", fill=color, font=("Consolas", 10, "bold"), anchor="sw")
            
            # Handles για Resize αν είναι επιλεγμένο
            if i == self.selected_idx:
                self.draw_resize_handles(r)
            
            # Αποθήκευση των IDs για διαχείριση
            if len(self.rects[i]) == 5:
                self.rects[i] = list(self.rects[i]) + [cid, tid]
            else:
                self.rects[i][5] = cid
                self.rects[i][6] = tid

    def draw_resize_handles(self, r):
        # 4 μικρά τετράγωνα στις γωνίες
        h_size = 5
        coords = [
            (r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])
        ]
        for idx, (x, y) in enumerate(coords):
            self.canvas.create_rectangle(x-h_size, y-h_size, x+h_size, y+h_size, fill="#00FF00", outline="white", tags="handle")

    def on_press(self, event):
        # Έλεγχος για handles (resize)
        clicked_handles = self.canvas.find_withtag("handle")
        items_at_click = self.canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        
        for h_id in items_at_click:
            if h_id in clicked_handles:
                self.is_resizing = True
                # Βρίσκουμε ποια γωνία είναι (βάσει θέσης)
                r = self.rects[self.selected_idx]
                if abs(event.x - r[0]) < 10 and abs(event.y - r[1]) < 10: self.resize_corner = 0
                elif abs(event.x - r[2]) < 10 and abs(event.y - r[1]) < 10: self.resize_corner = 1
                elif abs(event.x - r[2]) < 10 and abs(event.y - r[3]) < 10: self.resize_corner = 2
                elif abs(event.x - r[0]) < 10 and abs(event.y - r[3]) < 10: self.resize_corner = 3
                self.start_x = event.x
                self.start_y = event.y
                return

        # Έλεγχος αν κάναμε κλικ σε υπάρχον box
        for i, r in enumerate(self.rects):
            if r[5] in items_at_click:
                self.selected_idx = i
                self.is_moving = True
                self.is_resizing = False
                self.start_x = event.x
                self.start_y = event.y
                self.redraw_all()
                self.update_labels_list()
                return # Επιλογή και έξοδος
        
        # Αν όχι, ξεκινάμε νέο box
        self.selected_idx = None
        self.is_moving = False
        self.is_resizing = False
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="white", width=2)

    def on_drag(self, event):
        if self.is_resizing and self.selected_idx is not None:
            r = self.rects[self.selected_idx]
            if self.resize_corner == 0: # top-left
                r[0], r[1] = event.x, event.y
            elif self.resize_corner == 1: # top-right
                r[2], r[1] = event.x, event.y
            elif self.resize_corner == 2: # bot-right
                r[2], r[3] = event.x, event.y
            elif self.resize_corner == 3: # bot-left
                r[0], r[3] = event.x, event.y
            self.redraw_all()
        elif self.is_moving and self.selected_idx is not None:
            # Μετακίνηση υπάρχοντος box
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            r = self.rects[self.selected_idx]
            r[0] += dx
            r[1] += dy
            r[2] += dx
            r[3] += dy
            self.start_x = event.x
            self.start_y = event.y
            self.redraw_all()
        elif self.current_rect:
            self.canvas.coords(self.current_rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.is_resizing:
            self.is_resizing = False
        elif self.is_moving:
            self.is_moving = False
        elif self.current_rect:
            # Προσθήκη νέου box μόνο αν έχει μέγεθος
            if abs(event.x - self.start_x) > 5 and abs(event.y - self.start_y) > 5:
                # Αντί για άμεση προσθήκη, ανοίγουμε popup
                self.ask_class_name(self.start_x, self.start_y, event.x, event.y)
            self.canvas.delete(self.current_rect)
            self.current_rect = None
            
        self.redraw_all()
        self.update_labels_list()

    def on_double_click(self, event):
        # Έλεγχος αν κάναμε διπλό κλικ σε υπάρχον box
        items_at_click = self.canvas.find_overlapping(event.x-2, event.y-2, event.x+2, event.y+2)
        for i, r in enumerate(self.rects):
            if r[5] in items_at_click:
                self.selected_idx = i
                self.rename_selected()
                return

    def rename_selected(self):
        if self.selected_idx is not None:
            r = self.rects[self.selected_idx]
            current_name = self.classes[r[4]]
            dialog = ctk.CTkInputDialog(text=f"Αλλαγή ονόματος (τρέχον: {current_name}):", title="Rename Object")
            new_name = dialog.get_input()
            
            if new_name:
                if new_name not in self.classes:
                    self.classes.append(new_name)
                    self.class_menu.configure(values=self.classes)
                
                r[4] = self.classes.index(new_name)
                self.redraw_all()
                self.update_labels_list()
                self.save_labels()
                self.log(f"Το αντικείμενο μετονομάστηκε σε: {new_name}")

    def ask_class_name(self, x1, y1, x2, y2):
        # Δημιουργία ενός απλού popup παραθύρου
        dialog = ctk.CTkInputDialog(text="Δώσε όνομα για το αντικείμενο:", title="Class Name")
        name = dialog.get_input()
        
        if name:
            if name not in self.classes:
                self.classes.append(name)
                self.class_menu.configure(values=self.classes)
                self.log(f"Νέα κλάση προστέθηκε: {name}")
            
            cid = self.classes.index(name)
            self.rects.append([x1, y1, x2, y2, cid])
            self.selected_idx = len(self.rects) - 1
            self.redraw_all()
            self.update_labels_list()
            self.save_labels() # Αυτόματη αποθήκευση για σιγουριά

    def delete_selected(self):
        if self.selected_idx is not None and 0 <= self.selected_idx < len(self.rects):
            self.rects.pop(self.selected_idx)
            self.selected_idx = None
            self.redraw_all()
            self.update_labels_list()
            self.log("Το box διαγράφηκε.")
        else:
            self.selected_idx = None

    def change_class(self, val):
        self.current_class_id = self.classes.index(val)

    def update_labels_list(self):
        self.labels_list.delete("1.0", "end")
        for i, r in enumerate(self.rects):
            self.labels_list.insert("end", f"Box {i}: {r[0]},{r[1]} -> {r[2]},{r[3]}\n")

    def save_labels(self):
        if not self.images: return
        self.save_yolo_labels(self.current_idx, self.rects)
        self.save_status_lbl.configure(text="● DATA SAVED", text_color="#4CAF50")
        self.after(2000, lambda: self.save_status_lbl.configure(text="● SYSTEM READY", text_color="#888"))

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
        self.update_timeline() # Ενημέρωση χρωμάτων στο timeline

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

        # Αποθήκευση και των κλάσεων σε classes.txt για να μην χάνονται
        classes_path = os.path.join(self.image_folder, "classes.txt")
        with open(classes_path, "w") as f:
            f.write("\n".join(self.classes))

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

