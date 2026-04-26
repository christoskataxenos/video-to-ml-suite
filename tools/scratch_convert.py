import os
from PIL import Image

def convert_to_ico(png_path, ico_path):
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found")
        return
    img = Image.open(png_path)
    # Create white to transparent mask if needed (optional for white backgrounds)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        # If white-ish, make transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32)])
    print(f"Converted {png_path} to {ico_path}")

# Find the latest deployer icon
brain_dir = r"C:\Users\chris\.gemini\antigravity\brain\76bcb139-9a5c-4567-8289-3c337e4adea2"
files = [f for f in os.listdir(brain_dir) if f.startswith("icon_deployer_source") and f.endswith(".png")]
if files:
    latest = sorted(files)[-1]
    convert_to_ico(os.path.join(brain_dir, latest), "shared/icon_deployer.ico")
