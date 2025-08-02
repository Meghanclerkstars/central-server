import requests
import time
import json
import subprocess

CENTRAL_SERVER_URL = "https://central-server-zdrt.onrender.com/report"
DEVICE_NAME = "flirpi"

def get_public_url():
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:4040/api/tunnels"], capture_output=True, text=True)
        data = json.loads(result.stdout)
        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("❌ Failed to get tunnel:", e)
    return None

def report_to_server(url):
    try:
        payload = {"hostname": DEVICE_NAME, "url": url}  # <-- Changed "device_name" to "hostname"
        response = requests.post(CENTRAL_SERVER_URL, json=payload)
        print(f"✅ Reported to central: {response.status_code}")
    except Exception as e:
        print("❌ Failed to report:", e)

def main():
    print("⏳ Starting ngrok tunnel...")
    for i in range(10):  # Try for ~10 seconds
        url = get_public_url()
        if url:
            report_to_server(url)
            return
        else:
            print(f"⏳ Attempt {i+1}/10 - ngrok not ready")
            time.sleep(1)
    print("❌ No public URL found")

if __name__ == "__main__":
    main()
