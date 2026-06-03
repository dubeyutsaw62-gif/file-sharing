import os
import socket
import time
from flask import Flask, render_template_string, request, send_from_directory, jsonify

app = Flask(__name__)
BASE_STORAGE = 'network_vault'
os.makedirs(os.path.join(BASE_STORAGE, 'all'), exist_ok=True)

# List to keep track of devices that have visited
online_registry = {} 

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickShare Vault</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: sans-serif; }
        .vault-card { background: #1e293b; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .device-pill { cursor: pointer; border: 1px solid #334155; padding: 10px; border-radius: 8px; margin-bottom: 10px; transition: 0.2s; }
        .device-pill.active { background: #3b82f6; border-color: #60a5fa; }
        .file-box { background: #334155; padding: 10px; border-radius: 5px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 vault-card">
                <h3 class="text-center mb-4">🔐 Personal Vault</h3>
                <p class="small text-center text-secondary">Your IP: <span id="my-ip">{{ my_ip }}</span></p>

                <h6>1. Choose Target Device:</h6>
                <div id="device-list" class="mb-4">
                    <div class="device-pill active" onclick="setTarget('all')">📢 Broadcast to All</div>
                </div>

                <h6>2. Send File:</h6>
                <input type="file" id="fileInput" class="form-control mb-2 bg-dark text-white border-secondary">
                <button onclick="uploadFile()" class="btn btn-primary w-100 mb-4">Send to Target</button>

                <hr class="opacity-25">

                <h6>📩 Your Mailbox (Private to you)</h6>
                <div id="mailbox"></div>
            </div>
        </div>
    </div>

    <script>
        let selectedTarget = 'all';

        function setTarget(ip) {
            selectedTarget = ip;
            document.querySelectorAll('.device-pill').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
        }

        async function sync() {
            // Get Online Devices
            const devRes = await fetch('/get_devices');
            const devices = await devRes.json();
            const devDiv = document.getElementById('device-list');
            const myIp = document.getElementById('my-ip').innerText;
            
            // Rebuild device list but exclude self
            let html = `<div class="device-pill ${selectedTarget=='all'?'active':''}" onclick="setTarget('all')">📢 Broadcast to All</div>`;
            devices.forEach(ip => {
                if(ip !== myIp) {
                    html += `<div class="device-pill ${selectedTarget==ip?'active':''}" onclick="setTarget('${ip}')">📱 Device: ${ip}</div>`;
                }
            });
            devDiv.innerHTML = html;

            // Get My Mailbox
            const mailRes = await fetch('/get_my_files');
            const files = await mailRes.json();
            const mailDiv = document.getElementById('mailbox');
            mailDiv.innerHTML = files.length ? '' : '<p class="small text-secondary">No private files yet.</p>';
            files.forEach(f => {
                mailDiv.innerHTML += `<div class="file-box d-flex justify-content-between align-items-center">
                    <span>${f}</span>
                    <a href="/download/${f}" class="btn btn-sm btn-success">Download</a>
                </div>`;
            });
        }

        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files[0]) return alert("Select a file!");
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('target', selectedTarget);

            await fetch('/upload', { method: 'POST', body: formData });
            alert("Sent!");
            fileInput.value = '';
        }

        setInterval(sync, 3000);
        sync();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    # Register the user
    client_ip = request.remote_addr
    online_registry[client_ip] = time.time()
    return render_template_string(HTML_PAGE, my_ip=client_ip)

@app.route('/get_devices')
def get_devices():
    # Clean up old devices (older than 30s) and return list
    current_time = time.time()
    active = [ip for ip, t in online_registry.items() if current_time - t < 30]
    return jsonify(active)

@app.route('/get_my_files')
def get_my_files():
    client_ip = request.remote_addr
    all_files = []
    private_files = []
    
    # Path for 'all' folder
    all_path = os.path.join(BASE_STORAGE, 'all')
    if os.path.exists(all_path):
        all_files = os.listdir(all_path)
        
    # Path for private IP folder
    private_path = os.path.join(BASE_STORAGE, client_ip)
    if os.path.exists(private_path):
        private_files = os.listdir(private_path)
        
    return jsonify(list(set(all_files + private_files))) # set() removes duplicates
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    target = request.form.get('target', 'all')
    
    # Save to specific folder
    target_path = os.path.join(BASE_STORAGE, target)
    os.makedirs(target_path, exist_ok=True)
    file.save(os.path.join(target_path, file.filename))
    return "OK"

@app.route('/download/<filename>')
def download(filename):
    client_ip = request.remote_addr
    
    # 1. Search in your private IP folder
    private_path = os.path.join(BASE_STORAGE, client_ip)
    if os.path.exists(os.path.join(private_path, filename)):
        return send_from_directory(os.path.abspath(private_path), filename)
        
    # 2. Search in the 'all' (Broadcast) folder
    all_path = os.path.join(BASE_STORAGE, 'all')
    if os.path.exists(os.path.join(all_path, filename)):
        return send_from_directory(os.path.abspath(all_path), filename)
        
    # 3. Fallback: Search ALL subdirectories in the vault (Just in case)
    for root, dirs, files in os.walk(BASE_STORAGE):
        if filename in files:
            return send_from_directory(os.path.abspath(root), filename)

    return "File not found on server", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)