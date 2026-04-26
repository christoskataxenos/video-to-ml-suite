import os
import sys
import json
import shutil

def get_resource_path(relative_path):
    """
    Επιστρέφει την απόλυτη διαδρομή προς έναν πόρο (resource), 
    λαμβάνοντας υπόψη αν τρέχουμε από κώδικα ή από PyInstaller.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundled path
        return os.path.join(sys._MEIPASS, relative_path)
    
    # Development path
    # Αν το utils.py είναι στο shared/, τότε ο root είναι ο γονικός του shared
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, relative_path)

def get_app_data_dir():
    """
    Επιστρέφει τη διαδρομή προς τον φάκελο δεδομένων χρήστη (%APPDATA%).
    Δημιουργεί τον φάκελο αν δεν υπάρχει.
    """
    if sys.platform == 'win32':
        base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base_dir = os.path.expanduser('~')
        
    app_dir = os.path.join(base_dir, "VideoToMLSuite")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_config_path():
    """Επιστρέφει τη διαδρομή του config.json στον φάκελο AppData."""
    return os.path.join(get_app_data_dir(), "config.json")

def load_config():
    """Φορτώνει τις ρυθμίσεις από το AppData."""
    config_path = get_config_path()
    
    # Default τιμές
    default_config = {
        "output_path": os.path.join(os.path.expanduser('~'), "Documents", "VideoToMLSuite", "frames").replace("\\", "/"),
        "default_split": 80,
        "engine_path": "engine/engine.exe", # Σχετική με το resource_path
        "language": "en",
        "mode": "expert",
        "completed_steps": [],
        "bypassed_steps": []
    }
    
    # Προσπάθεια ανάγνωσης υπάρχοντος αρχείου
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
                return {**default_config, **saved_config}
        except:
            return default_config
    
    # Αν δεν υπάρχει, προσπάθεια μετανάστευσης από τον φάκελο του app (αν υπάρχει παλιό)
    old_config = get_resource_path("config.json")
    if os.path.exists(old_config):
        try:
            with open(old_config, "r", encoding="utf-8") as f:
                saved_config = json.load(f)
                config = {**default_config, **saved_config}
                save_config(config) # Αποθήκευση στο νέο σημείο
                return config
        except: pass
        
    return default_config

def save_config(config):
    """Αποθηκεύει τις ρυθμίσεις στο AppData."""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
