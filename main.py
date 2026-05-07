# Gscan v10.2 Final (Safe Educational Edition)


#!/usr/bin/env python3
"""
Gscan v10.2 Final
Safe Async OSINT Framework
Educational / Authorized Security Research Only

Features:
- Async username scanning
- SQLite cache with expiration
- JSON + CSV export
- Rate limiting
- Retry/backoff
- Site validators
- Safe subprocess usage
- Better error handling
- Termux/Linux compatible
"""

import os
import sys
import csv
import json
import asyncio
import random
import subprocess
from datetime import datetime, timedelta

import aiohttp
import aiofiles
import aiosqlite
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm_asyncio

# ================= INIT =================
init(autoreset=True)

# ================= CONFIG =================
MAX_CONCURRENT = 8
TIMEOUT = 12
CACHE_DB = "gscan_cache.db"
CACHE_EXPIRE_HOURS = 24

sem = asyncio.Semaphore(MAX_CONCURRENT)

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"
]

# ================= SITE DATABASE =================
SITES = {
    "GitHub": "https://github.com/{u}",
    "GitLab": "https://gitlab.com/{u}",
    "Reddit": "https://www.reddit.com/user/{u}",
    "Medium": "https://medium.com/@{u}",
    "Dev.to": "https://dev.to/{u}",
    "CodePen": "https://codepen.io/{u}",
    "Replit": "https://replit.com/@{u}",
    "Pinterest": "https://www.pinterest.com/{u}/",
    "Twitch": "https://www.twitch.tv/{u}",
    "Steam": "https://steamcommunity.com/id/{u}",
    "Chess.com": "https://www.chess.com/member/{u}",
    "Lichess": "https://lichess.org/@/{u}",
    "LeetCode": "https://leetcode.com/{u}",
    "HackerRank": "https://www.hackerrank.com/{u}",
    "Codeforces": "https://codeforces.com/profile/{u}",
    "Kaggle": "https://www.kaggle.com/{u}",
    "DockerHub": "https://hub.docker.com/u/{u}",
    "Behance": "https://www.behance.net/{u}",
    "Dribbble": "https://dribbble.com/{u}",
    "ArtStation": "https://www.artstation.com/{u}",
    "TryHackMe": "https://tryhackme.com/p/{u}",
    "HackTheBox": "https://app.hackthebox.com/users/{u}",
    "Letterboxd": "https://letterboxd.com/{u}/",
    "MyAnimeList": "https://myanimelist.net/profile/{u}",
}

# ================= VALIDATORS =================
NEGATIVE_PATTERNS = {
    "GitHub": ["not found"],
    "Reddit": ["nobody on reddit", "page not found"],
    "Medium": ["404"],
}

SITE_VALIDATORS = {
    "GitHub": lambda text: "repositories" in text.lower(),
    "Reddit": lambda text: "karma" in text.lower(),
    "Steam": lambda text: "games" in text.lower(),
    "LeetCode": lambda text: "ranking" in text.lower(),
}

# ================= SQLITE =================
async def init_db():
    async with aiosqlite.connect(CACHE_DB) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                username TEXT PRIMARY KEY,
                result TEXT,
                timestamp TEXT
            )
            """
        )
        await db.commit()


async def get_cache(username):
    async with aiosqlite.connect(CACHE_DB) as db:
        cur = await db.execute(
            "SELECT result, timestamp FROM scans WHERE username = ?",
            (username,)
        )

        row = await cur.fetchone()

        if not row:
            return None

        result, timestamp = row

        try:
            saved_time = datetime.fromisoformat(timestamp)
        except ValueError:
            return None

        if datetime.now() - saved_time > timedelta(hours=CACHE_EXPIRE_HOURS):
            return None

        return json.loads(result)


async def save_cache(username, result):
    async with aiosqlite.connect(CACHE_DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO scans VALUES (?, ?, ?)",
            (
                username,
                json.dumps(result),
                datetime.now().isoformat()
            )
        )
        await db.commit()

# ================= PARSER =================
def parse_profile(text, site_name, username):
    soup = BeautifulSoup(text, "lxml")

    result = {
        "exists": False,
        "confidence": 0,
        "signals": []
    }

    # Negative fingerprints
    if site_name in NEGATIVE_PATTERNS:
        if any(x in text.lower() for x in NEGATIVE_PATTERNS[site_name]):
            return result

    # OG title
    og = soup.find("meta", property="og:title")
    if og:
        content = og.get("content", "")
        if username.lower() in content.lower():
            result["confidence"] += 25
            result["signals"].append("og:title")

    # HTML title
    if soup.title and username.lower() in soup.title.text.lower():
        result["confidence"] += 20
        result["signals"].append("title")

    # Site validator
    validator = SITE_VALIDATORS.get(site_name)

    if validator:
        try:
            if validator(text):
                result["confidence"] += 35
                result["signals"].append("validator")
        except Exception:
            pass

    if result["confidence"] >= 40:
        result["exists"] = True

    return result

# ================= REQUEST =================
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5)
)
async def fetch(session, url, headers):
    async with session.get(
        url,
        headers=headers,
        timeout=TIMEOUT,
        allow_redirects=True
    ) as response:

        text = await response.text(errors="ignore")

        return response, text

# ================= CHECKER =================
async def check_site(session, site_name, url_template, username):
    async with sem:
        await asyncio.sleep(0.2)

        url = url_template.format(u=username)

        headers = {
            "User-Agent": random.choice(UA_LIST)
        }

        try:
            response, text = await fetch(session, url, headers)

            if response.status == 404:
                return None

            parsed = parse_profile(text, site_name, username)

            if parsed["exists"]:
                return {
                    "site": site_name,
                    "url": str(response.url),
                    "confidence": parsed["confidence"],
                    "signals": parsed["signals"]
                }

        except aiohttp.ClientError:
            return None

        except asyncio.TimeoutError:
            return None

        except Exception:
            return None

    return None

# ================= EXPORT =================
async def export_results(username, results):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_file = f"gscan_{username}_{ts}.json"
    csv_file = f"gscan_{username}_{ts}.csv"

    # JSON
    async with aiofiles.open(json_file, "w", encoding="utf-8") as f:
        await f.write(json.dumps(results, indent=2))

    # CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "site",
            "url",
            "confidence"
        ])

        for r in results:
            writer.writerow([
                r["site"],
                r["url"],
                r["confidence"]
            ])

    print(Fore.GREEN + f"[+] Saved: {json_file}")
    print(Fore.GREEN + f"[+] Saved: {csv_file}")

# ================= USERNAME SCAN =================
async def scan_username():
    username = input(Fore.GREEN + "\n[+] Username: ").strip()

    if not username:
        print(Fore.RED + "[!] Empty username")
        return

    await init_db()

    cached = await get_cache(username)

    if cached:
        print(Fore.CYAN + "[*] Loaded from cache\n")

        for item in cached:
            print(
                Fore.GREEN +
                f"[+] {item['site']}: {item['url']} ({item['confidence']}%)"
            )

        return

    print(
        Fore.YELLOW +
        f"\n[*] Scanning {len(SITES)} public platforms...\n"
    )

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            check_site(session, site, url, username)
            for site, url in SITES.items()
        ]

        results = await tqdm_asyncio.gather(
            *tasks,
            desc="Scanning",
            unit="site"
        )

    found = [r for r in results if r]

    for item in found:
        print(
            Fore.GREEN +
            f"[+] {item['site']}: {item['url']} | Confidence: {item['confidence']}%"
        )

    print(Fore.CYAN + f"\n[=] Total Found: {len(found)}")

    await save_cache(username, found)

    if found:
        choice = input(
            Fore.YELLOW + "\n[?] Export JSON + CSV? (y/n): "
        ).lower()

        if choice == "y":
            await export_results(username, found)

# ================= EMAIL =================
def email_osint():
    print(Fore.YELLOW + "\n[*] Public email footprint checks only")

    email = input(Fore.GREEN + "[+] Email: ").strip()

    if "@" not in email:
        print(Fore.RED + "[!] Invalid email")
        return

    print(Fore.CYAN + f"[*] Running Holehe for: {email}\n")

    try:
        subprocess.run(
            ["holehe", email],
            check=True
        )

    except FileNotFoundError:
        print(Fore.RED + "[!] Holehe not installed")

    except subprocess.CalledProcessError:
        print(Fore.RED + "[!] Holehe execution failed")

# ================= UI =================
def banner():
    os.system("clear" if os.name == "posix" else "cls")

    print(Fore.MAGENTA + Style.BRIGHT + r"""
   ____ ____   ____    _    _   _
  / ___/ ___| / ___|  / \  | \ | |
 | |  _\___ \| |     / _ \ |  \| |
 | |_| |___) | |___ / ___ \| |\  |
  \____|____/ \____/_/   \_\_| \_|
    """)

    print(Fore.CYAN + "     Gscan v10.2 Final - Safe OSINT Framework")
    print(Fore.WHITE + "     Educational & Authorized Use Only\n")

# ================= MAIN =================
def main():
    while True:
        banner()

        print("1. Username OSINT")
        print("2. Email OSINT")
        print("3. Exit\n")

        choice = input(Fore.GREEN + "Select: ").strip()

        if choice == "1":
            asyncio.run(scan_username())
            input(Fore.YELLOW + "\nPress Enter...")

        elif choice == "2":
            email_osint()
            input(Fore.YELLOW + "\nPress Enter...")

        elif choice == "3":
            print(Fore.RED + "\n[!] Exiting...\n")
            sys.exit()

        else:
            print(Fore.RED + "[!] Invalid choice")

# ================= ENTRY =================
if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Interrupted\n")
        sys.exit()
