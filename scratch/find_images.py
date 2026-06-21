import glob
import os

images = glob.glob("**/*.png", recursive=True) + glob.glob("**/*.jpg", recursive=True) + glob.glob("**/*.jpeg", recursive=True)
for img in images:
    if 'node_modules' not in img and '.venv' not in img:
        print(f"File: {img}, Size: {os.path.getsize(img)} bytes")
