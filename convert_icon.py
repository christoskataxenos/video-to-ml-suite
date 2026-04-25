from PIL import Image
import os

def convert_to_ico(png_path, ico_path):
    print(f"Converting {png_path} to {ico_path}...")
    img = Image.open(png_path)
    # Define resolutions for standard Windows icons
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, sizes=icon_sizes)
    print("Done!")

if __name__ == "__main__":
    # Path to the generated image from previous tool output
    # I will replace this with the actual path in the next step or use it as a command
    pass
