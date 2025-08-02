import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEST_BASE = os.path.expanduser("~/flir_sim/input_images")

def find_flir_mount():
    media_root = "/media/pi"
    for mount in os.listdir(media_root):
        flir_path = os.path.join(media_root, mount, "DCIM", "100_FLIR")
        if os.path.isdir(flir_path):
            return flir_path
    return None

def copy_images(src_folder, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    copied = 0
    for file in os.listdir(src_folder):
        if file.lower().endswith(".jpg"):
            src_path = os.path.join(src_folder, file)
            dest_path = os.path.join(dest_folder, file)
            shutil.copy2(src_path, dest_path)
            print(f"📷 Copied: {file}")
            copied += 1
    return copied

def main():
    flir_folder = find_flir_mount()
    if not flir_folder:
        print("❌ FLIR camera not found. Please ensure it's connected and mounted.")
        return

    print("🔍 FLIR camera found at:", flir_folder)

    timestamp = datetime.now().strftime("site_%Y-%m-%d_%a_%H%M")
    dest_folder = os.path.join(DEST_BASE, timestamp)
    copied_count = copy_images(flir_folder, dest_folder)

    if copied_count:
        print(f"✅ {copied_count} image(s) copied to {dest_folder}")
    else:
        print("⚠️ No images found to copy.")

if __name__ == "__main__":
    main()
