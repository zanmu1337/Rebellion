import subprocess
import os
import sys
import time
import json
import requests
from colorama import init, Fore, Style

init()

MITMDUMP = r"C:\Users\iexagq\AppData\Roaming\Python\Python314\Scripts\mitmdump.exe"
PORT = 8082

def check_webhook_silently():
    webhook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webhook.json")
    if not os.path.exists(webhook_path):
        return False, "webhook.json introuvable"
        
    with open(webhook_path, "r", encoding="utf-8") as f:
        WEBHOOKS = json.load(f)
        
    webhook_url = WEBHOOKS.get("results_webhook", "x")
    if not webhook_url or webhook_url == "x":
        return False, "Webhook non configuré"
        
    try:
        r = requests.get(webhook_url, timeout=5)
        if r.status_code == 200:
            return True, "Valide"
        else:
            return False, f"Code HTTP {r.status_code}"
    except Exception:
        return False, "Erreur de connexion"

def check_bot_token_silently():
    webhook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webhook.json")
    if not os.path.exists(webhook_path):
        return False, "webhook.json introuvable"
        
    with open(webhook_path, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
        
    token = CONFIG.get("bot_token", "x")
    
    if not token or token == "x":
        return False, "Token non configuré"
        
    try:
        headers = {"Authorization": f"Bot {token}"}
        r = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        if r.status_code == 200:
            return True, "Token valide"
        elif r.status_code == 401:
            return False, "Token invalide"
        else:
            return False, f"Code HTTP {r.status_code}"
    except Exception:
        return False, "Erreur de connexion"

if __name__ == "__main__":
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules", "mitm_script.py")
    bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules", "bot.py")
    
    bot_proc = subprocess.Popen(
        [sys.executable, bot_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    mitm_proc = subprocess.Popen(
        f'"{MITMDUMP}" -s "{script_path}" --listen-port {PORT} --ssl-insecure',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(3)
        
    wb_ok, wb_msg = check_webhook_silently()
    if wb_ok:
        print(f"{Fore.GREEN}[+] webhook - connected ({wb_msg}){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[!] webhook - disconnected ({wb_msg}){Style.RESET_ALL}")
        
    bot_ok, bot_msg = check_bot_token_silently()
    if bot_ok:
        print(f"{Fore.GREEN}[+] bot - connected ({bot_msg}){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[!] bot - disconnected ({bot_msg}){Style.RESET_ALL}")
        
    print(f"{Fore.GREEN}[+] mitm - connected (port {PORT}){Style.RESET_ALL}")
    
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Arrêt des processus...{Style.RESET_ALL}")
        bot_proc.terminate()
        mitm_proc.terminate()
        print(f"{Fore.RED}[+] Services - disconnected{Style.RESET_ALL}")