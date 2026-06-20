# QuickShare Vault 
> A lightweight, cross-platform, P2P local file-sharing system built over the TCP/IP stack.

**QuickShare Vault** is a local area network (LAN) utility that transforms your computer into a private, high-speed file-sharing hub. It allows multiple cross-platform client devices (Android, iOS, Windows, Mac) to securely transmit and receive files via a standard web browser without using cellular data, an internet connection, or third-party cloud architectures.

---

##  System Architecture & Logic Flow

The application implements a localized **Client-Server Architecture** running entirely inside your private network subnet. 


```

```
                   [ Wi-Fi Router / LAN Switch ]
                                │
       ┌────────────────────────┴────────────────────────┐
       ▼                                                 ▼
 [ Host PC ]                                    [ Client Devices ]

```

(Runs Flask Backend)                            (Phones/Laptops/Tablets)

* Maps Network Vault                            - Runs Browser Interface
* Resolves Network IP                           - Periodic AJAX Polling (3s)
* Filters Storage by IP                         - Directed File Transfers

```

1. **Local Socket Resolution:** On startup, the system uses low-level socket APIs (`socket.SOCK_DGRAM`) to bind a dummy outbound port. This allows the OS network stack to identify the actual active interface IP assigned by the local router (e.g., `192.168.x.x`), evading loopback constraints (`127.0.0.1`).
2. **Asynchronous Polling Engine (Heartbeat):** The client-side UI uses JavaScript `setInterval` to send non-blocking asynchronous HTTP requests every 3 seconds to backend endpoints (`/get_devices` and `/get_my_files`). The server updates a thread-safe dictionary memory pool to determine which nodes are currently active on the subnet.
3. **Network Isolation (Source-IP Mailboxes):** Privacy is enforced at the network layer. When a client performs an operation, the server extracts its hardware-assigned IP signature using `request.remote_addr`. 
   * **Broadcast Mode:** Files uploaded to the public path `network_vault/all/` are visible to all authenticated router endpoints.
   * **Targeted Mode:** Files uploaded to a specific node are isolated in a custom folder (e.g., `network_vault/10.226.49.173/`). Client machines can only fetch index lists matching their own packet source IP, ensuring data confidentiality.

---

##  OSI Model & Protocol Layer Mapping

This project serves as a functional demonstration of structural data encapsulation across the standard **OSI/ISO Reference Model Layers**:

* **Layer 7 (Application Layer - HTTP):** Manages user interaction and request-response patterns. File metadata, UI listings, and actions are structured using HTTP `GET` (data pulling) and HTTP `POST` (multi-part payload uploads) verbs.
* **Layer 4 (Transport Layer - TCP):** Guarantees data integrity. Because binary chunks must arrive cleanly, the system utilizes TCP streams to handle segment ordering, sliding window flow control, packet acknowledgment, and automatic re-transmission over noisy wireless mediums.
* **Layer 3 (Network Layer - IP):** Handles logical layout configuration. It routes data packets accurately from the host interface down to destination endpoints across the local subnet using the IPv4 addressing format.

---

##  Key Features

* **Zero External Overhead:** Works offline. Files bypass the ISP infrastructure, moving natively via Wi-Fi airwaves at the router's maximum hardware threshold.
* **Live Speed Computation:** Tracks real-time throughput metrics (MB/s) directly within the `XMLHttpRequest` upload lifecycle by tracking byte displacement against delta-time intervals.
* **Zero Configuration UI:** Completely decoupled client runtime. No apps, packages, or configurations needed—recipients just hit a URL link.

---

##  Setup & Technical Prerequisites

### Dependencies
Ensure you have Python 3.x and the Flask web framework installed:
```bash
pip install flask

```

### File Layout

```text
├── share_ui.py       # Main Application Code (Python + Embedded HTML/JS UI)
└── network_vault/    # Root Storage Core (Generated on initial boot)
    ├── all/          # Public Shared Directory
    └── [Client_IP]/  # Dynamically generated isolated private mailboxes

```

### Installation & Run

1. Run the application as an administrator to ensure complete network binding:
```bash
python share_ui.py

```


2. Note the localized execution string emitted on the terminal:
```text
* Running on [http://192.168.](http://192.168.)X.X:5000

```


3. Open your mobile or target client browser, enter the given endpoint, and start transferring files safely within your local environment.
