import json
import os
import locale
from shared.utils import load_config

def get_current_language():
    config = load_config()
    return config.get("language", "en")

STRINGS = {
    # ------------------ ORCHESTRATOR (DASHBOARD) ------------------
    "dashboard_title": {
        "el": "VIDEO TO ML SUITE",
        "en": "VIDEO TO ML SUITE"
    },
    "module_1_title": {
        "el": "1. FRAME EXTRACTOR",
        "en": "1. FRAME EXTRACTOR"
    },
    "module_1_desc": {
        "el": "Εξαγωγή frames από βίντεο και προετοιμασία δομής YOLO.",
        "en": "Extract frames from video and prepare YOLO structure."
    },
    "module_2_title": {
        "el": "2. IMAGE ANNOTATOR",
        "en": "2. IMAGE ANNOTATOR"
    },
    "module_2_desc": {
        "el": "Σχολιασμός εικόνων και χρήση έξυπνης παρεμβολής.",
        "en": "Annotate images and use smart interpolation."
    },
    "module_3_title": {
        "el": "3. DATASET INSPECTOR",
        "en": "3. DATASET INSPECTOR"
    },
    "module_3_desc": {
        "el": "Ανάλυση κατανομής κλάσεων και υγείας του dataset.",
        "en": "Analyze class distribution and dataset health."
    },
    "module_4_title": {
        "el": "4. TRAINING LAUNCHER",
        "en": "4. TRAINING LAUNCHER"
    },
    "module_4_desc": {
        "el": "Εκπαίδευση μοντέλου YOLO στο προετοιμασμένο dataset.",
        "en": "Train YOLO model on the prepared dataset."
    },
    "settings_title": {
        "el": "SYSTEM SETTINGS",
        "en": "SYSTEM SETTINGS"
    },
    "settings_desc": {
        "el": "Ρύθμιση διαδρομών μηχανής και καθολικών προτιμήσεων.",
        "en": "Configure engine paths and global preferences."
    },
    "btn_launch": {
        "el": "ΕΚΚΙΝΗΣΗ",
        "en": "LAUNCH"
    },
    "suite_status": {
        "el": "ΚΑΤΑΣΤΑΣΗ",
        "en": "SUITE STATUS"
    },
    "status_ok": {
        "el": "● ΟΛΑ ΤΑ ΣΥΣΤΗΜΑΤΑ OK",
        "en": "● ALL SYSTEMS OK"
    },
    "workflow_guide": {
        "el": "ΟΔΗΓΟΣ ΡΟΗΣ",
        "en": "WORKFLOW GUIDE"
    },
    "guide_1_title": {
        "el": "1. ΕΞΑΓΩΓΗ",
        "en": "1. EXTRACTION"
    },
    "guide_1_desc": {
        "el": "Εξάγετε καρέ από τα αρχεία βίντεο σας.",
        "en": "Extract frames from your raw video files."
    },
    "guide_2_title": {
        "el": "2. ΣΧΟΛΙΑΣΜΟΣ",
        "en": "2. ANNOTATION"
    },
    "guide_2_desc": {
        "el": "Σχεδιάστε πλαίσια και χρησιμοποιήστε παρεμβολή.",
        "en": "Draw boxes and use Interpolation."
    },
    "guide_3_title": {
        "el": "3. ΕΛΕΓΧΟΣ",
        "en": "3. INSPECTION"
    },
    "guide_3_desc": {
        "el": "Επιβεβαιώστε την υγεία του dataset.",
        "en": "Verify dataset health and balance."
    },
    "guide_4_title": {
        "el": "4. ΕΚΠΑΙΔΕΥΣΗ",
        "en": "4. TRAINING"
    },
    "guide_4_desc": {
        "el": "Ξεκινήστε την εκπαίδευση YOLO στα δεδομένα σας.",
        "en": "Launch YOLO training on your data."
    },
    "pro_tip": {
        "el": "💡 ΣΥΜΒΟΥΛΗ",
        "en": "💡 PRO TIP"
    },
    "pro_tip_desc": {
        "el": "Ελέγξτε τα 'System Settings'\nγια να ρυθμίσετε τις\nδιαδρομές πριν ξεκινήσετε.",
        "en": "Check 'System Settings'\nto configure global paths\nbefore starting."
    },
    "sys_initialized": {
        "el": "Το σύστημα αρχικοποιήθηκε. Καλώς ήρθατε στο Video to ML Suite.",
        "en": "System initialized. Welcome to the Video to ML Suite."
    },
    "config_saved": {
        "el": "Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς.",
        "en": "Settings saved successfully."
    },
    "launching_generator": {
        "el": "Εκκίνηση Generator...",
        "en": "Launching Generator..."
    },
    "launching_labeler": {
        "el": "Εκκίνηση Labeler...",
        "en": "Launching Labeler..."
    },
    "launching_inspector": {
        "el": "Εκκίνηση Inspector...",
        "en": "Launching Inspector..."
    },
    "launching_trainer": {
        "el": "Εκκίνηση Trainer...",
        "en": "Launching Trainer..."
    },
    "settings_global_config": {
        "el": "ΚΑΘΟΛΙΚΕΣ ΡΥΘΜΙΣΕΙΣ",
        "en": "GLOBAL CONFIGURATION"
    },
    "settings_default_out": {
        "el": "Προεπιλεγμένη Έξοδος:",
        "en": "Default Output:"
    },
    "settings_default_split": {
        "el": "Προεπιλεγμένο Split (%):",
        "en": "Default Split (%):"
    },
    "settings_save_btn": {
        "el": "ΑΠΟΘΗΚΕΥΣΗ ΡΥΘΜΙΣΕΩΝ",
        "en": "SAVE SETTINGS"
    },
    "version_label": {
        "el": "v2.0 - DUAL MODE UPDATE",
        "en": "v2.0 - DUAL MODE UPDATE"
    },
    
    # ------------------ GENERATOR (FRAME EXTRACTOR) ------------------
    "gen_title": {
        "el": "ΕΞΑΓΩΓΗ ΚΑΡΕ",
        "en": "FRAME EXTRACTOR"
    },
    "gen_status_ready": {
        "el": "● Έτοιμο",
        "en": "● Ready"
    },
    "gen_status_busy": {
        "el": "● Απασχολημένο",
        "en": "● Busy"
    },
    "gen_status_finished": {
        "el": "● Ολοκληρώθηκε",
        "en": "● Finished"
    },
    "gen_start_btn": {
        "el": "ΕΝΑΡΞΗ ΕΞΑΓΩΓΗΣ",
        "en": "START EXTRACTION"
    },
    "gen_start_btn_proc": {
        "el": "ΕΠΕΞΕΡΓΑΣΙΑ...",
        "en": "PROCESSING..."
    },
    "gen_open_folder_btn": {
        "el": "ΑΝΟΙΓΜΑ ΦΑΚΕΛΟΥ",
        "en": "OPEN LAST EXPORT"
    },
    "gen_batch_mode": {
        "el": "Λειτουργία Φακέλου (Batch Mode)",
        "en": "Batch Mode (Folder)"
    },
    "gen_input_group": {
        "el": "ΠΗΓΕΣ ΕΙΣΟΔΟΥ",
        "en": "INPUT SOURCES"
    },
    "gen_select_video": {
        "el": "Επιλογή βίντεο...",
        "en": "Select video..."
    },
    "gen_select_folder": {
        "el": "Επιλογή φακέλου με βίντεο...",
        "en": "Select folder with videos..."
    },
    "gen_browse_btn": {
        "el": "Αναζήτηση",
        "en": "Browse"
    },
    "gen_output_group": {
        "el": "ΡΥΘΜΙΣΕΙΣ ΕΞΟΔΟΥ",
        "en": "OUTPUT SETTINGS"
    },
    "gen_base_folder": {
        "el": "Βασικός Φάκελος...",
        "en": "Base Folder..."
    },
    "gen_select_btn": {
        "el": "Επιλογή",
        "en": "Select"
    },
    "gen_trim_group": {
        "el": "ΠΕΡΙΚΟΠΗ ΒΙΝΤΕΟ (SINGLE MODE)",
        "en": "VIDEO TRIMMING (SINGLE MODE)"
    },
    "gen_start_s": {
        "el": "Έναρξη (s):",
        "en": "Start (s):"
    },
    "gen_end_s": {
        "el": "Λήξη (s):",
        "en": "End (s):"
    },
    "gen_end_hint": {
        "el": "(-1 = Τέλος)",
        "en": "(-1 = End)"
    },
    "gen_proc_group": {
        "el": "ΕΠΙΛΟΓΕΣ ΕΠΕΞΕΡΓΑΣΙΑΣ",
        "en": "PROCESSING OPTIONS"
    },
    "gen_format": {
        "el": "Μορφή:",
        "en": "Format:"
    },
    "gen_width": {
        "el": "Πλάτος:",
        "en": "Width:"
    },
    "gen_ml_group": {
        "el": "ΔΗΜΙΟΥΡΓΙΑ ML DATASET",
        "en": "ML DATASET GENERATOR"
    },
    "gen_ml_enable": {
        "el": "Ενεργοποίηση ML Export",
        "en": "Enable ML Export Mode"
    },
    "gen_train_split": {
        "el": "Διαχωρισμός Train (%):",
        "en": "Train Split (%):"
    },
    "gen_classes": {
        "el": "Κλάσεις:",
        "en": "Classes:"
    },
    "gen_classes_hint": {
        "el": "π.χ. Person, Car, Dog",
        "en": "e.g. Person, Car, Dog"
    },
    "gen_preview_lbl": {
        "el": "ΖΩΝΤΑΝΗ ΠΡΟΕΠΙΣΚΟΠΗΣΗ",
        "en": "LIVE PREVIEW"
    },
    "gen_telemetry_ready": {
        "el": "Έτοιμο",
        "en": "Ready"
    },
    "gen_telemetry_eta": {
        "el": "Υπολειπόμενος Χρόνος: --:--",
        "en": "ETA: --:--"
    },
    "gen_telemetry_frame": {
        "el": "Καρέ: {0}/{1} | Αποθήκευση: {2}",
        "en": "Frame: {0}/{1} | Saved: {2}"
    },
    
    # ------------------ GUIDED MODE TEXTS ------------------
    "mode_guided": {
        "el": "GUIDED MODE",
        "en": "GUIDED MODE"
    },
    "mode_expert": {
        "el": "EXPERT MODE",
        "en": "EXPERT MODE"
    },
    "step_ready": {
        "el": "ΕΤΟΙΜΟ",
        "en": "READY"
    },
    "step_locked": {
        "el": "ΚΛΕΙΔΩΜΕΝΟ",
        "en": "LOCKED"
    },
    "step_completed": {
        "el": "ΟΛΟΚΛΗΡΩΜΕΝΟ",
        "en": "COMPLETED"
    },
    "step_bypassed": {
        "el": "ΠΑΡΑΚΑΜΨΗ",
        "en": "BYPASSED"
    },
    "bypass_link": {
        "el": "Το έχω ήδη κάνει →",
        "en": "I've already done this →"
    },
    "btn_reopen": {
        "el": "ΑΝΟΙΓΜΑ ΞΑΝΑ",
        "en": "REOPEN"
    },
    "progress_text": {
        "el": "Βήμα {0} από {1} — {2}",
        "en": "Step {0} of {1} — {2}"
    },
    "pipeline_complete": {
        "el": "Η ροή εργασίας ολοκληρώθηκε",
        "en": "Workflow Complete"
    },
    "why_here_title": {
        "el": "ΓΙΑΤΙ ΕΙΜΑΣΤΕ ΕΔΩ",
        "en": "WHY YOU ARE HERE"
    },
    "btn_done_next": {
        "el": "ΟΛΟΚΛΗΡΩΣΗ — ΕΠΟΜΕΝΟ →",
        "en": "DONE — NEXT STEP →"
    },
    
    # Frame Extractor Guided Mode
    "guided_gen_why": {
        "el": "Για να εκπαιδεύσουμε το μοντέλο, χρειαζόμαστε μεμονωμένες εικόνες. Εδώ μετατρέπουμε το βίντεο σε καρέ για να τα σχολιάσουμε αργότερα.",
        "en": "To train a model, we need individual images. This tool breaks your video into frames for labeling later."
    },
    "guided_gen_step1": {
        "el": "Επίλεξε το βίντεο",
        "en": "Select video file"
    },
    "guided_gen_step1_edu": {
        "el": "Οποιοδήποτε αρχείο .mp4, .mov λειτουργεί.",
        "en": "Any .mp4, .mov file works."
    },
    "guided_gen_step2": {
        "el": "Φάκελος Αποθήκευσης",
        "en": "Save location"
    },
    "guided_gen_step2_edu": {
        "el": "Οι εικόνες θα αποθηκευτούν αυτόματα εδώ.",
        "en": "Frames will be saved here automatically."
    },
    "guided_gen_step3": {
        "el": "Εξαγωγή για Τεχνητή Νοημοσύνη",
        "en": "AI Dataset Export"
    },
    "guided_gen_step3_edu": {
        "el": "Διαχωρισμός σε 80% εκπαίδευση και 20% έλεγχο.",
        "en": "Split into 80% training and 20% validation."
    },
    "guided_gen_step4": {
        "el": "Εισάγετε τα ονόματα των κλάσεων",
        "en": "Enter your class names"
    },
    "guided_gen_step4_edu": {
        "el": "π.χ. 'αυτοκίνητο', 'άνθρωπος'",
        "en": "e.g. 'car', 'person'"
    },
    "guided_gen_step5": {
        "el": "Πατήστε ΕΝΑΡΞΗ ΕΞΑΓΩΓΗΣ",
        "en": "Press START EXTRACTION"
    },
    "guided_gen_step5_edu": {
        "el": "Ο C++ κινητήρας θα τα επεξεργαστεί ταχύτατα.",
        "en": "The C++ engine will process it fast."
    },
    # Labeler Guided Mode
    "labeler_title": {"el": "ΣΧΟΛΙΑΣΜΟΣ ΕΙΚΟΝΩΝ", "en": "IMAGE ANNOTATOR"},
    "guided_lab_why": {"el": "Σχεδίασε πλαίσια γύρω από τα αντικείμενα για να διδάξεις το μοντέλο.", "en": "Draw boxes around objects to teach the model."},
    "guided_lab_step1": {"el": "Άνοιγμα Εικόνων", "en": "Open Images"},
    "guided_lab_step1_edu": {"el": "Επίλεξε τον φάκελο που περιέχει τα καρέ σου.", "en": "Select the folder containing your frames."},
    "guided_lab_step2": {"el": "Σχεδίαση Πλαισίου", "en": "Draw a Box"},
    "guided_lab_step2_edu": {"el": "Κλικ και σύρσιμο πάνω στο αντικείμενο.", "en": "Click and drag over the object."},
    "guided_lab_step3": {"el": "Επόμενο Καρέ", "en": "Next Frame"},
    "guided_lab_step3_edu": {"el": "Χρησιμοποιήστε τα (A / D) για πλοήγηση.", "en": "Use (A / D) keys for navigation."},
    "guided_lab_step4": {"el": "Έξυπνη Παρεμβολή", "en": "Smart Interpolation"},
    "guided_lab_step4_edu": {"el": "Ορίστε 2 Keyframes (K) και πατήστε Interpolate (I).", "en": "Set 2 Keyframes (K) and press Interpolate (I)."},
    "guided_lab_step5": {"el": "Ολοκλήρωση", "en": "Finish labeling"},
    "guided_lab_step5_edu": {"el": "Αποθηκεύστε και προχωρήστε στον έλεγχο.", "en": "Save and proceed to inspection."},
    
    # Help Wizard
    "help_title": {"el": "ΟΔΗΓΟΣ ΧΡΗΣΗΣ", "en": "USER GUIDE"},
    "help_close": {"el": "ΚΛΕΙΣΙΜΟ", "en": "CLOSE"},
    "help_next": {"el": "ΕΠΟΜΕΝΟ", "en": "NEXT"},
    "help_prev": {"el": "ΠΡΟΗΓΟΥΜΕΝΟ", "en": "PREVIOUS"},
    
    # Inspector Guided Mode
    "inspector_title": {"el": "ΕΛΕΓΧΟΣ DATASET", "en": "DATASET INSPECTOR"},
    "guided_ins_why": {"el": "Ένα καλό dataset έχει ισορροπημένες κλάσεις και δεν του λείπουν ετικέτες.", "en": "A good dataset has balanced classes and no missing labels."},
    "guided_ins_step1": {"el": "Φόρτωση του dataset.yaml", "en": "Load dataset.yaml"},
    "guided_ins_step1_edu": {"el": "Περιγράφει τη δομή του dataset σας.", "en": "Describes your dataset structure."},
    "guided_ins_step2": {"el": "Ελέγξτε την κατανομή κλάσεων", "en": "Review class distribution"},
    "guided_ins_step2_edu": {"el": "Κάθε κλάση να έχει παρόμοιο αριθμό.", "en": "Each class should have a similar amount."},
    "guided_ins_step3": {"el": "Ελέγξτε για προειδοποιήσεις", "en": "Check for warnings"},
    "guided_ins_step3_edu": {"el": "Εικόνες χωρίς ετικέτες είναι 'τυφλά σημεία'.", "en": "Images without labels are 'blind spots'."},
    "guided_ins_step4": {"el": "Επιβεβαίωση", "en": "Confirm health"},
    "guided_ins_step4_edu": {"el": "Αν είναι εντάξει, προχωρήστε στην εκπαίδευση.", "en": "If okay, proceed to training."},
    
    # Trainer Guided Mode
    "trainer_title": {"el": "ΕΚΚΙΝΗΣΗ ΕΚΠΑΙΔΕΥΣΗΣ", "en": "TRAINING LAUNCHER"},
    "guided_tra_why": {"el": "Τώρα το μοντέλο μαθαίνει. Αυτό μπορεί να διαρκέσει από λεπτά έως ώρες.", "en": "Now the model learns. This step can take minutes or hours."},
    "guided_tra_step1": {"el": "Επιβεβαιώστε το dataset.yaml", "en": "Confirm dataset.yaml"},
    "guided_tra_step1_edu": {"el": "Ο κινητήρας διαβάζει το αρχείο.", "en": "The engine reads this to find your images."},
    "guided_tra_step2": {"el": "Επιλέξτε μέγεθος μοντέλου", "en": "Choose model size"},
    "guided_tra_step2_edu": {"el": "Ξεκινήστε με Nano για γρήγορη εκπαίδευση.", "en": "Start with Nano for fast training."},
    "guided_tra_step3": {"el": "Ορισμός Epochs", "en": "Set Epochs"},
    "guided_tra_step3_edu": {"el": "Ένα 'epoch' είναι ένα πέρασμα απ' όλες τις εικόνες.", "en": "An 'epoch' is one pass through all images."},
    "guided_tra_step4": {"el": "Πατήστε ΕΝΑΡΞΗ ΕΚΠΑΙΔΕΥΣΗΣ", "en": "Press START TRAINING"},
    "guided_tra_step4_edu": {"el": "Παρακολουθήστε το mAP - πάνω από 0.7 είναι καλό.", "en": "Watch for mAP - above 0.7 is good."},

    # Deployer Guided Mode
    "deployer_title": {"el": "AI DEPLOYER & STUDIO", "en": "AI DEPLOYER & STUDIO"},
    "guided_dep_why": {"el": "Το μοντέλο σας είναι έτοιμο! Τώρα μπορείτε να το δείτε στην πράξη και να το ενσωματώσετε στα project σας.", "en": "Your model is ready! Now you can see it in action and use it in your projects."},
    "guided_dep_step1": {"el": "Φόρτωση Μοντέλου", "en": "Load Trained Model"},
    "guided_dep_step1_edu": {"el": "Συνήθως το 'best.pt' βρίσκεται στο runs/detect/train/weights.", "en": "Usually 'best.pt' is in runs/detect/train/weights."},
    "guided_dep_step2": {"el": "Δοκιμή σε Βίντεο/Κάμερα", "en": "Test on Video/Webcam"},
    "guided_dep_step2_edu": {"el": "Δείτε την αναγνώριση αντικειμένων σε πραγματικό χρόνο.", "en": "See object detection in real-time."},
    "guided_dep_step3": {"el": "Εξαγωγή & Κώδικας", "en": "Export & Code"},
    "guided_dep_step3_edu": {"el": "Πάρτε έτοιμο κώδικα Python ή μετατρέψτε σε ONNX.", "en": "Get Python code snippets or convert to ONNX."},
    "guided_dep_step4": {"el": "AI Integration (LM Studio)", "en": "AI Integration (LM Studio)"},
    "guided_dep_step4_edu": {"el": "Συνδέστε την όραση (Vision) με την ευφυΐα (LLM).", "en": "Connect Vision results with LLM intelligence."},

    # Dashboard new strings
    "module_5_title": {"el": "5. AI DEPLOYER & STUDIO", "en": "5. AI DEPLOYER & STUDIO"},
    "module_5_desc": {"el": "Δοκιμή, Εξαγωγή και Διασύνδεση του μοντέλου σας.", "en": "Test, Export and Integrate your trained model."},
    "guide_5_title": {"el": "5. ΕΞΑΓΩΓΗ", "en": "5. DEPLOYMENT"},
    "guide_5_desc": {"el": "Δοκιμάστε το μοντέλο και δείτε οδηγούς ενσωμάτωσης.", "en": "Test your model and view integration guides."}
}

def get_string(key, *args):
    lang = get_current_language()
    
    # Fetch string dictionary for the given key
    string_dict = STRINGS.get(key, {})
    
    # Fallback to English if key or language not found
    text = string_dict.get(lang, string_dict.get("en", f"[{key}]"))
    
    # Format string if arguments are provided
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text

