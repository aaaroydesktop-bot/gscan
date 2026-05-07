#!/usr/bin/env python3
"""
Gscan v6.1 - Ultra-Fast Async OSINT Tracker (Improved Detection)
Developed by: Anupom Roy
"""

import os
import sys
import asyncio
import aiohttp
import json
import csv
import hashlib
import subprocess
from datetime import datetime
from colorama import Fore, Style, init
from tqdm.asyncio import tqdm_asyncio

init(autoreset=True)

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_banner():
    clear_screen()
    print(Fore.MAGENTA + Style.BRIGHT + r"""
     ____ ____   ____    _    _   _ 
    / ___/ ___| / ___|  / \  | \ | |
    | |  _\___ \| |     / _ \ |  \| |
    | |_| |___) | |___ / ___ \| |\  |
     \____|____/ \____/_/   \_\_| \_|
    """)
    print(Fore.CYAN + "      Gscan v6.1 - Ultra-Fast Async OSINT Tracker")
    print(Fore.WHITE + "      Developed by: " + Fore.YELLOW + "Anupom Roy")
    print(Fore.WHITE + "      -------------------------------------------\n")

def show_disclaimer():
    print(Fore.RED + Style.BRIGHT + "\n[!] LEGAL DISCLAIMER")
    print(Fore.WHITE + "This tool is for educational & authorized use only.\n")

# ==================== EMAIL OSINT ====================
def check_gravatar(email):
    print(Fore.YELLOW + "\n[*] Checking Gravatar...")
    try:
        md5 = hashlib.md5(email.lower().strip().encode()).hexdigest()
        url = f"https://en.gravatar.com/{md5}.json"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=6)
        if res.status_code == 200 and 'entry' in res.json():
            print(Fore.GREEN + "[+] Gravatar profile found!")
        else:
            print(Fore.RED + "[-] No Gravatar profile.")
    except:
        print(Fore.RED + "[-] Gravatar check failed.")

def check_data_breaches(email):
    print(Fore.YELLOW + "\n[*] Checking Data Breaches...")
    try:
        res = requests.get(f"https://api.xposedornot.com/v1/check-email/{email}", timeout=10)
        if res.status_code == 200 and res.json().get('breaches'):
            print(Fore.RED + "[!] Email found in data breaches!")
        else:
            print(Fore.GREEN + "[+] No known breaches.")
    except:
        print(Fore.RED + "[-] Breach check failed.")

def scan_email():
    email = input(Fore.GREEN + "\n[+] Enter Email: " + Fore.WHITE).strip()
    if "@" not in email:
        print(Fore.RED + "[!] Invalid email!")
        return
    print(Fore.YELLOW + f"\n[*] Target: {email}")
    try:
        subprocess.run(["holehe", email, "--only-used"], check=True)
    except FileNotFoundError:
        subprocess.run([sys.executable, "-m", "pip", "install", "holehe"])
        subprocess.run(["holehe", email, "--only-used"])
    check_data_breaches(email)
    check_gravatar(email)

# ==================== IMPROVED USERNAME OSINT ====================
SITES = { ... }  # (আগের মতোই 185+ ইউনিক সাইট রাখা হয়েছে)

NOT_FOUND_KEYWORDS = [
    "user not found", "profile not found", "doesn't exist", "no such user",
    "page not found", "404", "sorry, we couldn't find", "this account doesn't exist",
    "user does not exist", "account not found", "we couldn't find that user",
    "user profile not found", "invalid username", "user doesn't exist"
]

async def check_site_async(session, site_name, url_template, username, headers):
    url = url_template.format(u=username)
    try:
        async with session.get(url, headers=headers, timeout=8) as resp:
            # Step 1: 404 হলে সরাসরি বাদ
            if resp.status == 404:
                return None

            text = await resp.text()
            text_lower = text.lower()

            # Step 2: Not Found কীওয়ার্ড চেক
            if any(kw in text_lower for kw in NOT_FOUND_KEYWORDS):
                return None

            # Step 3: যদি উপরের কোনোটাই না হয়, তাহলে Registered ধরা হবে
            return f"{Fore.GREEN}[+] {site_name}: {Fore.WHITE}{url}"
    except:
        return None

async def scan_username_async():
    username = input(Fore.GREEN + "\n[+] Enter Username: " + Fore.WHITE).strip()
    if not username:
        print(Fore.RED + "[!] Username cannot be empty!")
        return

    print(Fore.YELLOW + f"\n[*] Scanning '{username}' across {len(SITES)} platforms (Improved Detection)...\n")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found = []

    async with aiohttp.ClientSession() as session:
        tasks = [check_site_async(session, name, url, username, headers) 
                 for name, url in SITES.items()]
        results = await tqdm_asyncio.gather(*tasks, desc="Scanning", unit="site")

    found = [r for r in results if r]
    for r in found:
        print(r)

    print(Fore.GREEN + Style.BRIGHT + f"\n[=] Total Profiles Found: {len(found)} / {len(SITES)}")

    # Export
    if found:
        save = input(Fore.YELLOW + "\n[?] Save to JSON + CSV? (y/n): ").lower()
        if save == 'y':
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"gscan_{username}_{ts}"
            with open(f"{fname}.json", "w", encoding="utf-8") as f:
                json.dump({"username": username, "found": found, "time": ts}, f, indent=2)
            with open(f"{fname}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Platform", "URL"])
                for line in found:
                    parts = line.split(": ", 1)
                    if len(parts) == 2:
                        writer.writerow([parts[0].replace("[+] ", ""), parts[1]])
            print(Fore.GREEN + f"[+] Saved: {fname}.json & {fname}.csv")

# ==================== MAIN ====================
def main():
    show_disclaimer()
    while True:
        display_banner()
        print(Fore.WHITE + "1. 📧 Email OSINT")
        print(Fore.MAGENTA + "2. 👤 Username OSINT (Improved Accuracy)")
        print(Fore.WHITE + "3. 👨‍💻 About")
        print(Fore.WHITE + "4. ❌ Exit\n")
        choice = input(Fore.GREEN + "Select (1-4): " + Style.RESET_ALL).strip()

        if choice == "1":
            scan_email()
            input(Fore.YELLOW + "\nPress Enter...")
        elif choice == "2":
            asyncio.run(scan_username_async())
            input(Fore.YELLOW + "\nPress Enter...")
        elif choice == "3":
            print("Gscan v6.1 by Anupom Roy")
            input(Fore.YELLOW + "\nPress Enter...")
        elif choice == "4":
            print(Fore.RED + "\n[!] Exiting...\n")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Exiting...\n")