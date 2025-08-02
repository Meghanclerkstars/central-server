import os
import sys
import shutil
import subprocess
import zipfile
from dotenv import load_dotenv

load_dotenv()

RCLONE_REMOTE = os.getenv("RCLONE_REMOTE")
RCLONE_DEST_PATH = os.getenv("RCLONE_DEST_PATH")

def zip_folder(folder_path):
    zip_path = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)
    return zip_path

def upload_to_drive(folder_path):
    folder_name = os.path.basename(folder_path)
    zip_path = zip_folder(folder_path)
    zip_name = os.path.basename(zip_path)
    drive_path = f"{RCLONE_REMOTE}:{RCLONE_DEST_PATH}/{zip_name}"

    try:
        print(f"☁️ Uploading {zip_path} → {drive_path}")
        subprocess.run(["rclone", "copyto", zip_path, drive_path], check=True)
        print("✅ Upload successful. Deleting local folder and zip...")
        shutil.rmtree(folder_path)
        os.remove(zip_path)
        print("🗑️ Cleaned up local data.")
    except subprocess.CalledProcessError:
        print("❌ Upload failed.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python3 upload_to_drive.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        sys.exit(1)

    upload_to_drive(folder_path)
