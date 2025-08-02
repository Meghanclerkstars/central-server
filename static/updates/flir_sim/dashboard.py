from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

INPUT_DIR = os.path.expanduser("~/flir_sim/input_images")
STATUS_FILE = os.path.expanduser("~/flir_sim/upload_status.json")

def list_folders():
    if not os.path.exists(INPUT_DIR):
        return []
    return sorted([
        f for f in os.listdir(INPUT_DIR)
        if os.path.isdir(os.path.join(INPUT_DIR, f))
    ], reverse=True)

def get_status():
    if not os.path.exists(STATUS_FILE):
        return {"status": "Idle", "folder": "N/A", "timestamp": "N/A"}
    with open(STATUS_FILE, "r") as f:
        return json.load(f)

@app.route("/", methods=["GET"])
def index():
    folders = list_folders()
    status = get_status()
    return render_template("index.html", folders=folders, status=status)

@app.route("/folder/<folder>/notes", methods=["GET", "POST"])
def folder_notes(folder):
    folder_path = os.path.join(INPUT_DIR, folder)
    notes_file = os.path.join(folder_path, "notes.txt")
    if request.method == "POST":
        client_name = request.form.get("client_name", "").strip()
        surveyor_name = request.form.get("surveyor_name", "").strip()
        notes = request.form.get("notes", "").strip()
        full_notes = f"Client Name: {client_name}\nSurveyor Name: {surveyor_name}\n---\n{notes}"
        with open(notes_file, "w") as f:
            f.write(full_notes)
        return redirect(url_for("index"))
    else:
        notes = ""
        if os.path.exists(notes_file):
            with open(notes_file, "r") as f:
                notes = f.read()
        return render_template("notes.html", folder=folder, notes=notes)

@app.route("/folder/<folder>/rename_folder", methods=["GET", "POST"])
def rename_folder(folder):
    folder_path = os.path.join(INPUT_DIR, folder)
    if request.method == "POST":
        user_input = request.form.get("new_folder_name", "").strip()

        if not user_input:
            return "Folder name cannot be empty", 400

        parts = folder.split('_')
        timestamp_suffix = '_'.join(parts[-4:]) if len(parts) >= 5 else datetime.now().strftime("%Y-%m-%d_%a_%H%M")

        new_folder = f"{user_input}_{timestamp_suffix}"
        new_folder_path = os.path.join(INPUT_DIR, new_folder)

        if not os.path.exists(new_folder_path):
            os.rename(folder_path, new_folder_path)

        return redirect(url_for("index"))
    return render_template("rename_folder.html", folder_name=folder)

@app.route("/upload_api/<folder>", methods=["POST"])
def upload_folder_api(folder):
    folder_path = os.path.join(INPUT_DIR, folder)

    status = {
        "status": "Uploading...",
        "folder": folder,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f)

    try:
        subprocess.run([
            "python3",
            os.path.expanduser("~/flir_sim/upload_to_drive.py"),
            folder_path
        ], check=True)

        status["status"] = "Uploaded"
        status["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f)
        return jsonify({"success": True})

    except subprocess.CalledProcessError:
        print("❌ Upload failed.")
        status["status"] = "Upload Failed ❌"
        status["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f)
        return jsonify({"success": False})

@app.route("/scan", methods=["POST"])
def scan_camera():
    try:
        result = subprocess.run(
            ["python3", os.path.expanduser("~/flir_sim/main.py")],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ FLIR Scan Success:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ FLIR Scan Failed:\n", e.stderr)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


