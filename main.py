#!/usr/bin/env python3
"""
Gscan v11.0 Professional (Safe Educational Edition)
Advanced Async OSINT Framework with Dynamic Validation & Regex Security.
Author: Anupom (Senior Python Security Engineer)
"""

import os
import sys
import json
import asyncio
import random
import subprocess
import re
import csv
import shutil
import importlib.util
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# ================= 1. DEPENDENCY CHECKER =================
REQUIRED_PACKAGES = {
    "aiohttp": "aiohttp",
    "aiosqlite": "aiosqlite",
    "aiofiles": "aiofiles",
    "bs4": "beautifulsoup4",
    "tenacity": "tenacity",
    "tqdm": "tqdm",
    "colorama": "colorama",
    "rich": "rich"
}

def check_dependencies() -> None:
    """Checks for missing dependencies and offers auto-install."""
    missing = []
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        if importlib.util.find_spec(module_name) is None:
            missing.append(pip_name)
    
    if not shutil.which("holehe"):
        missing.append("holehe")

    if missing:
        print("\033[91m[!] Missing required dependencies:\033[0m")
        for pkg in missing:
            print(f"  - {pkg}")
        
        choice = input("\033[93m[?] Do you want to auto-install them now? (y/n): \033[0m").strip().lower()
        if choice == 'y':
            print("\033[96m[*] Installing missing packages...\033[0m")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
                print("\033[92m[+] Dependencies installed successfully! Restarting...\033[0m")
                os.execv(sys.executable, ['python'] + sys.argv)
            except subprocess.CalledProcessError:
                print("\033[91m[!] Failed to install dependencies. Please run: pip install -r requirements.txt\033[0m")
                sys.exit(1)
        else:
            print("\033[91m[!] Cannot run without required dependencies. Exiting.\033[0m")
            sys.exit(1)

# Run dependency check before third-party imports
check_dependencies()

# ================= 2. THIRD-PARTY IMPORTS =================
import aiohttp
import aiofiles
import aiosqlite
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm.asyncio import tqdm_asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# ================= 3. SYSTEM CONFIGURATION =================
init(autoreset=True)
console = Console()

MAX_CONCURRENT = 8
TIMEOUT = 12
CACHE_DB = "gscan_cache.db"
VALIDATORS_FILE = "validators.json"
CACHE_EXPIRE_HOURS = 24

sem = asyncio.Semaphore(MAX_CONCURRENT)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"
]

# ================= 4. DYNAMIC VALIDATOR SYSTEM =================
DEFAULT_SITES = {
    "GitHub": {
        "url": "https://github.com/{u}",
        "negative_patterns": ["not found"],
        "positive_keywords": ["repositories", "overview"]
    },
    "GitLab": {
        "url": "https://gitlab.com/{u}",
        "negative_patterns": ["sign in"],
        "positive_keywords": ["activity", "projects"]
    },
    "Reddit": {
        "url": "https://www.reddit.com/user/{u}",
        "negative_patterns": ["nobody on reddit", "page not found"],
        "positive_keywords": ["karma"]
    },
    "Medium": {
        "url": "https://medium.com/@{u}",
        "negative_patterns": ["404"],
        "positive_keywords": ["followers", "about"]
    },
    "Steam": {
        "url": "https://steamcommunity.com/id/{u}",
        "negative_patterns": ["specified profile could not be found"],
        "positive_keywords": ["games", "badges"]
    },
    "LeetCode": {
        "url": "https://leetcode.com/{u}",
        "negative_patterns": ["not found"],
        "positive_keywords": ["ranking", "submissions"]
    }
}

def save_default_validators() -> None:
    """Creates a default validators.json if missing."""
    try:
        with open(VALIDATORS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SITES, f, indent=4)
    except Exception as e:
        console.print(f"[red][!] Error saving default validators: {e}[/red]")

def load_validators() -> Dict[str, Any]:
    """Loads validators from JSON with hot-reload capability."""
    if not os.path.exists(VALIDATORS_FILE):
        save_default_validators()
        return DEFAULT_SITES
    try:
        with open(VALIDATORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        console.print("[yellow][!] Invalid JSON format in validators.json. Using defaults.[/yellow]")
        return DEFAULT_SITES

# ================= 5. SECURITY & UTILS =================
def is_valid_email(email: str) -> bool:
    """Professional Regex based Email Validation."""
    return bool(EMAIL_REGEX.match(email))

async def init_db() -> None:
    """Initializes SQLite database for caching."""
    async with aiosqlite.connect(CACHE_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                username TEXT PRIMARY KEY,
                result TEXT,
                timestamp TEXT
            )
        """)
        await db.commit()

async def get_cache(username: str) -> Optional[List[Dict]]:
    async with aiosqlite.connect(CACHE_DB) as db:
        cur = await db.execute("SELECT result, timestamp FROM scans WHERE username = ?", (username,))
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

async def save_cache(username: str, result: List[Dict]) -> None:
    async with aiosqlite.connect(CACHE_DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO scans VALUES (?, ?, ?)",
            (username, json.dumps(result), datetime.now().isoformat())
        )
        await db.commit()

# ================= 6. CORE LOGIC =================
def parse_profile(text: str, site_data: Dict, username: str) -> Dict[str, Any]:
    """Dynamically parses profile based on JSON rules."""
    soup = BeautifulSoup(text, "lxml")
    text_lower = text.lower()
    
    result = {"exists": False, "confidence": 0, "signals": []}

    # 1. Negative Patterns Check
    for neg in site_data.get("negative_patterns", []):
        if neg.lower() in text_lower:
            return result

    # 2. OG Title Validation
    og = soup.find("meta", property="og:title")
    if og:
        content = og.get("content", "")
        if username.lower() in content.lower():
            result["confidence"] += 25
            result["signals"].append("og:title")

    # 3. HTML Title Validation
    if soup.title and username.lower() in soup.title.text.lower():
        result["confidence"] += 20
        result["signals"].append("title")

    # 4. Positive Keyword Validator Check
    for pos in site_data.get("positive_keywords", []):
        if pos.lower() in text_lower:
            result["confidence"] += 35
            result["signals"].append("positive_keyword")
            break

    if result["confidence"] >= 40:
        result["exists"] = True

    return result

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def fetch(session: aiohttp.ClientSession, url: str, headers: Dict[str, str]) -> Tuple[aiohttp.ClientResponse, str]:
    async with session.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True) as response:
        text = await response.text(errors="ignore")
        return response, text

async def check_site(session: aiohttp.ClientSession, site_name: str, site_data: Dict, username: str) -> Optional[Dict]:
    async with sem:
        await asyncio.sleep(0.2)
        url = site_data.get("url", "").format(u=username)
        headers = {"User-Agent": random.choice(UA_LIST)}

        try:
            response, text = await fetch(session, url, headers)
            if response.status in [404, 403, 401]:
                return None

            parsed = parse_profile(text, site_data, username)

            if parsed["exists"]:
                return {
                    "site": site_name,
                    "url": str(response.url),
                    "confidence": parsed["confidence"],
                    "signals": parsed["signals"]
                }
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
        except Exception as e:
            return None
    return None

async def export_results(username: str, results: List[Dict]) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"gscan_{username}_{ts}.json"
    csv_file = f"gscan_{username}_{ts}.csv"

    # Save JSON Async
    async with aiofiles.open(json_file, "w", encoding="utf-8") as f:
        await f.write(json.dumps(results, indent=2))

    # Save CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Site", "URL", "Confidence"])
        for r in results:
            writer.writerow([r["site"], r["url"], r["confidence"]])

    console.print(f"[bold green][+] Results successfully exported to:[/bold green]\n - {json_file}\n - {csv_file}")

# ================= 7. MODULES =================
async def scan_username() -> None:
    console.print("\n[bold cyan]──> Username OSINT Scan[/bold cyan]")
    username = input(Fore.GREEN + "[+] Enter Target Username: ").strip()

    if not username or not username.isalnum():
        console.print("[bold red][!] Invalid username. Use alphanumeric characters only.[/bold red]")
        return

    await init_db()
    cached = await get_cache(username)
    validators = load_validators()

    if cached:
        console.print("[bold yellow][*] Match found in local database (Cache):[/bold yellow]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Site", style="cyan")
        table.add_column("URL", style="green")
        table.add_column("Confidence", justify="right")
        
        for item in cached:
            table.add_row(item['site'], item['url'], f"{item['confidence']}%")
        console.print(table)
        return

    console.print(f"[bold yellow]\n[*] Initializing asynchronous scan over {len(validators)} platforms...\n[/bold yellow]")
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_site(session, site, data, username) for site, data in validators.items()]
        results = await tqdm_asyncio.gather(*tasks, desc="[cyan]Scanning Target", unit="site")

    found = [r for r in results if r]
    
    if found:
        table = Table(title="Scan Results", show_header=True, header_style="bold magenta")
        table.add_column("Site", style="cyan")
        table.add_column("Profile URL", style="green")
        table.add_column("Confidence", justify="right", style="yellow")

        for item in found:
            table.add_row(item['site'], item['url'], f"{item['confidence']}%")
        
        console.print(table)
        console.print(f"[bold cyan][=] Total Profiles Identified: {len(found)}[/bold cyan]")
        await save_cache(username, found)

        choice = input(Fore.YELLOW + "\n[?] Do you want to export results (JSON + CSV)? (y/n): ").strip().lower()
        if choice == "y":
            await export_results(username, found)
    else:
        console.print("[bold red][!] No active profiles found for the given username.[/bold red]")

def email_osint() -> None:
    console.print("\n[bold cyan]──> Email Address OSINT Scan[/bold cyan]")
    email = input(Fore.GREEN + "[+] Enter Target Email: ").strip()

    # Dynamic secure validation before execution
    if not is_valid_email(email):
        console.print("[bold red][!] Invalid or malformed email address rejected for safety.[/bold red]")
        return

    console.print(f"[bold yellow][*] Executing Holehe Framework securely for: {email}[/bold yellow]\n")

    try:
        # Safe execution without shell=True to prevent injection attacks
        subprocess.run(["holehe", email], check=True, text=True)
    except FileNotFoundError:
        console.print("[bold red][!] Holehe CLI is not installed. Run: pip install holehe[/bold red]")
    except subprocess.CalledProcessError:
        console.print("[bold red][!] Holehe execution encountered an error.[/bold red]")
    except Exception as e:
        console.print(f"[bold red][!] Unexpected OSINT Error: {str(e)}[/bold red]")

# ================= 8. CLI UI / ABOUT =================
def show_about() -> None:
    about_text = """
[bold cyan]Developer:[/bold cyan] Anupom (Senior Python Security Engineer)
[bold cyan]GitHub:[/bold cyan]    https://github.com/YourUsername
[bold cyan]Version:[/bold cyan]   v11.0 Professional
[bold cyan]Features:[/bold cyan]  Async Scaling, Regex Security, Dynamic Json Validations, SQLite Caching

[bold red]LEGAL DISCLAIMER:[/bold red]
This framework is strictly for authorized penetration testing and educational purposes. 
The developer holds no responsibility for any misuse.
    """
    console.print(Panel(about_text, title="[bold magenta]About Gscan[/bold magenta]", border_style="cyan"))
    input(Fore.YELLOW + "\nPress Enter to return to menu...")

def banner() -> None:
    os.system("clear" if os.name == "posix" else "cls")
    banner_art = r"""
[bold magenta]
    ____                       _   _   _  ___  
   / ___|___  ___ __ _ _ __   | | | | / |/ _ \ 
  | |  _/ __|/ __/ _` | '_ \  | | | | | | | | |
  | |_| \__ \ (_| (_| | | | | | |_| | | | |_| |
   \____|___/\___\__,_|_| |_|  \___/  |_|\___/ 
[/bold magenta]
    """
    console.print(banner_art)
    console.print("[bold cyan]      Professional OSINT Framework - Safe & Modular[/bold cyan]")
    console.print("[bold yellow]      Developed by: Anupom[/bold yellow]")
    console.print("[bold green]      Use Responsibly. Authorized Research Only.[/bold green]\n")

# ================= 9. MAIN LOOP =================
async def main_async() -> None:
    while True:
        banner()
        console.print("[1] Username OSINT (Async & Cached)")
        console.print("[2] Email OSINT (Regex Secured)")
        console.print("[3] About Developer & Tool")
        console.print("[4] Exit\n")

        choice = input(Fore.GREEN + "Select Option [1-4]: ").strip()

        if choice == "1":
            await scan_username()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == "2":
            email_osint()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == "3":
            show_about()
        elif choice == "4":
            console.print("\n[bold red][!] Gracefully shutting down... Goodbye![/bold red]\n")
            break
        else:
            console.print("[bold red][!] Invalid Selection. Try again.[/bold red]")
            await asyncio.sleep(1)

def main() -> None:
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main_async())
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Operation Interrupted by User (Ctrl+C). Exiting safely...[/bold red]\n")
        sys.exit(0)

# ================= ENTRY =================
if __name__ == "__main__":
    main()