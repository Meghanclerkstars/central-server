from flask import Flask, request, jsonify, render_template_string, redirect
from datetime import datetime

app = Flask(__name__)

# In-memory store: hostname -> {url, last_seen}
active_pis = {}

@app.route("/report", methods=["POST"])
def report():
    data = request.get_json()
    if not data or "hostname" not in data or "url" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    hostname = data["hostname"]
    public_url = data["url"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    active_pis[hostname] = {
        "url": public_url,
        "last_seen": timestamp
    }

    print(f"✅ Pi reported: {hostname} → {public_url} @ {timestamp}")
    return jsonify({"message": "Reported"}), 200

@app.route("/pis", methods=["GET"])
def get_pis():
    return jsonify(active_pis)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connected Pis</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px 15px; border: 1px solid #ccc; text-align: left; }
            th { background-color: #eee; }
        </style>
    </head>
    <body>
        <h1>Connected Raspberry Pi Devices</h1>
        <table id="pi-table">
            <thead>
                <tr><th>Device</th><th>URL</th><th>Last Seen</th></tr>
            </thead>
            <tbody id="table-body">
                <!-- Filled dynamically -->
            </tbody>
        </table>
        <p style="font-size: 12px; color: #888;">Auto-refreshes every 10 seconds.</p>

        <script>
            async function fetchPis() {
                const response = await fetch('/pis');
                const data = await response.json();
                const tbody = document.getElementById('table-body');
                tbody.innerHTML = '';

                const keys = Object.keys(data);
                if (keys.length === 0) {
                    const row = document.createElement('tr');
                    const cell = document.createElement('td');
                    cell.colSpan = 3;
                    cell.textContent = 'No devices connected.';
                    row.appendChild(cell);
                    tbody.appendChild(row);
                    return;
                }

                for (const [hostname, info] of Object.entries(data)) {
                    const row = document.createElement('tr');

                    const nameCell = document.createElement('td');
                    nameCell.textContent = hostname;

                    const urlCell = document.createElement('td');
                    const link = document.createElement('a');
                    link.href = info.url;
                    link.target = "_blank";
                    link.textContent = info.url;
                    urlCell.appendChild(link);

                    const timeCell = document.createElement('td');
                    timeCell.textContent = info.last_seen;

                    row.appendChild(nameCell);
                    row.appendChild(urlCell);
                    row.appendChild(timeCell);

                    tbody.appendChild(row);
                }
            }

            fetchPis();
            setInterval(fetchPis, 10000);  // every 10 seconds
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route("/")
def home():
    return redirect("/dashboard")

from flask import send_from_directory

@app.route("/updates/flir_sim_update.zip")
def serve_update():
    return send_from_directory("static/updates", "flir_sim_update.zip")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
