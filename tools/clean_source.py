import os

def clean_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
        
    with open(filename, 'rb') as f:
        content = f.read()
    
    # Remove null bytes
    clean_content = content.replace(b'\x00', b'')
    
    # Force write as UTF-8
    with open(filename, 'wb') as f:
        f.write(clean_content)
    
    print(f"Cleaned {filename}")

if __name__ == "__main__":
    clean_file("orchestrator.py")
    clean_file("package_app.py")
    clean_file("generator/app.py")
    clean_file("labeler/app.py")
    clean_file("inspector/app.py")
    clean_file("trainer/app.py")
