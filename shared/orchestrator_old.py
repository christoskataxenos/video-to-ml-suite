import os
import sys
import subprocess

def print_status(msg):
    print(f"[Orchestrator] {msg}")

def check_dependencies():
    """Ελέγχει αν είναι εγκατεστημένα τα απαραίτητα εργαλεία (Python libraries)."""
    try:
        import customtkinter
    except ImportError:
        print_status("Το customtkinter δεν βρέθηκε. Γίνεται εγκατάσταση...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
        print_status("Η εγκατάσταση ολοκληρώθηκε.")

def run_gui():
    """Εκκινεί το GUI."""
    gui_path = os.path.join(os.path.dirname(__file__), "launcher", "app.py")
    if not os.path.exists(gui_path):
        print_status(f"Σφάλμα: {gui_path} not found")
        return

    print_status("Εκκίνηση...")
    # Τρέχουμε το GUI
    subprocess.Popen([sys.executable, gui_path])

def main():
    print_status("Έναρξη...")
    check_dependencies()
    
    engine_path = os.path.join(os.path.dirname(__file__), "build", "Debug", "engine.exe")
    if not os.path.exists(engine_path):
        print_status(f"Προσοχή: Λείπει το {engine_path}.")
    
    run_gui()

if __name__ == "__main__":
    main()
