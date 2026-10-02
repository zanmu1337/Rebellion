## 🔥 What is Rebellion?

**Rebellion** is an automated JavaScript secret-hunting tool built on top of **mitmproxy**.

Once Rebellion is running, simply route your browser traffic through the proxy using **FoxyProxy**, a system proxy, or any other proxy-switching tool.

From there, you can browse **any authorized website normally**.

Rebellion automatically:

```text
Browser
   │
   │ HTTP / HTTPS traffic
   ▼
mitmproxy
   │
   ├── Detect JavaScript responses
   │
   ▼
Download JS files
   │
   ├── Analyze each file
   │
   ▼
Extract potential secrets
   │
   ├── Send findings to webhook
   │
   ▼
Process the next URL
```

No need to manually collect JavaScript URLs or download files yourself.

---

## ✨ Features

* 🌐 **Automatic JavaScript discovery**
* 📥 **Automatically downloads every detected JS file**
* 🔎 **Scans JavaScript for potentially exposed secrets**
* ⚡ **Processes multiple URLs/files automatically**
* 🔗 **Webhook integration for findings**
* 🧩 **Works transparently through mitmproxy**
* 🦊 Compatible with **FoxyProxy** and other proxy-switching tools
* ♾️ **No fixed URL limit** — every JavaScript resource encountered by the proxy can be processed

---

## 🚀 How it works

### 1. Start Rebellion

Launch the mitmproxy instance with Rebellion:

```bash
python rebellion.py
```

Rebellion is now attached to the proxy and ready to inspect traffic.

---

### 2. Switch your browser to the proxy

Use **FoxyProxy**, your browser's proxy settings, or any equivalent tool to route traffic through the mitmproxy instance.

Once enabled, you don't need to interact with Rebellion manually.

---

### 3. Browse normally

Open an authorized website and navigate normally.

Every time the browser loads a JavaScript resource, Rebellion automatically detects it.

All detected JavaScript files are automatically collected.

---

### 4. JavaScript files are downloaded

Instead of requiring you to manually gather URLs, Rebellion retrieves the JavaScript content directly from the intercepted traffic.

```text
JS URL detected
      ↓
Content retrieved
      ↓
File processed
      ↓
Secret analysis
```

This also means dynamically loaded JavaScript files can be handled as they appear during normal browsing.

---

### 5. Secrets are analyzed automatically

Each JavaScript file is passed through the secret-detection pipeline.

Rebellion looks for potentially exposed sensitive values such as credentials, API keys, tokens, and other secret-like patterns.

Detected results can then be forwarded to the configured webhook.

```text
JavaScript
    ↓
Secret Scanner
    ↓
Potential Finding
    ↓
Webhook
```

---

## 🔗 Webhook

When a potential secret is detected, Rebellion can send the result directly to your configured webhook.

This makes it possible to monitor findings without constantly watching the proxy output.

```text
┌──────────────┐
│ JavaScript   │
│   Response   │
└──────┬───────┘
       ↓
┌──────────────┐
│  Rebellion   │
│    Scanner   │
└──────┬───────┘
       ↓
┌──────────────┐
│   Finding    │
└──────┬───────┘
       ↓
┌──────────────┐
│   Webhook    │
└──────────────┘
```

---

## ♾️ Unlimited URL Processing

Rebellion isn't designed around scanning a single JavaScript URL at a time.

It operates directly on the traffic flowing through the proxy.

So if a page loads:

```text
app.js
vendor.js
runtime.js
chunk-1.js
chunk-2.js
chunk-3.js
...
chunk-500.js
```

Rebellion can process each JavaScript resource as it is encountered.

The same applies while navigating through multiple pages:

```text
Page 1 → JS files
Page 2 → JS files
Page 3 → JS files
Page 4 → JS files
...
```

You simply keep browsing — Rebellion keeps processing the JavaScript traffic it sees.

---

## 📦 Installation

### Clone the repository

```bash
git clone https://github.com/zanmu1337/Rebellion.git
cd Rebellion
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install mitmproxy

```bash
pip install mitmproxy
```

---

## 🔐 Configure mitmproxy

Start mitmproxy:

```bash
mitmproxy
```

Configure your browser or application to use the mitmproxy host and port.

Then visit:

```text
http://mitm.it
```

Install and trust the appropriate mitmproxy certificate so HTTPS traffic can be inspected.

---

## ⚡ Start Rebellion

Run:

```bash
python rebellion.py
```

Then enable your proxy in **FoxyProxy** (or your preferred proxy manager) and start browsing.

That's it.

**Browse → JavaScript gets captured → files get analyzed → findings get sent to the webhook.**

---

## 🧠 The idea

Rebellion is built around a simple principle:

> **Don't manually hunt for JavaScript. Let the traffic find it for you.**

Instead of:

```text
Find URLs
   ↓
Download JS
   ↓
Save files
   ↓
Run scanner
   ↓
Review results
```

Rebellion turns it into:

```text
             Browse
                ↓
           Proxy traffic
                ↓
        Detect JS resources
                ↓
          Analyze files
                ↓
       Extract potential secrets
                ↓
          Send to webhook
```

---

## ⚠️ Disclaimer

Rebellion is intended for **authorized security testing, research, and defensive purposes**.

Only use it against websites, applications, and infrastructure that you **own or have explicit permission to test**.

Do not use Rebellion to access, collect, or exfiltrate secrets from systems without authorization.
