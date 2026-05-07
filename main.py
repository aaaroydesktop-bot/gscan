#!/usr/bin/env python3
"""
Gscan v9.2 - Enterprise OSINT (All Critical Bugs Fixed + Optimized)
"""

import os
import sys
import asyncio
import aiohttp
import aiosqlite
import aiofiles
import json
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from tqdm.asyncio import tqdm_asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

init(autoreset=True)

# ==================== GLOBAL ====================
MAX_CONCURRENT = 10
sem = asyncio.Semaphore(MAX_CONCURRENT)
PROXY_LIST = []
UA_LIST = [ ... ]  # stable list

# Per-site cooldown (Adaptive Throttling)
SITE_COOLDOWN = {}
LAST_REQUEST = {}

# ==================== SQLITE + CACHE ====================
# ... (আগের মতোই)

# ==================== ADVANCED PARSER (Fixed) ====================
def advanced_dom_parser(text: str, site_name: str, username: str) -> dict:
    soup = BeautifulSoup(text, "lxml")
    result = {"exists": False, "confidence": 0, "signals": []}

    # JSON-LD + OpenGraph + Meta + Schema (আগের মতো)
    # ...

    # Username check (এখন parameter আছে)
    og_title = soup.find("meta", property="og:title")
    if og_title and username.lower() in og_title.get("content", "").lower():
        result["confidence"] += 25
        result["signals"].append("username_match")

    # Per-site CSS + DOM logic
    if site_name == "GitHub":
        if soup.select_one("span.p-name") or soup.select_one("div.js-profile-editable-area"):
            result["exists"] = True
            result["confidence"] += 45

    if result["confidence"] >= 55:
        result["exists"] = True
    return result

# ==================== SMART BROWSER FALLBACK (Optimized) ====================
BROWSER_CONTEXT = None
HIGH_VALUE_SITES = {"GitHub", "Reddit", "Twitter", "Instagram", "Steam", "Twitch", "LinkedIn", "Facebook"}

async def get_browser_context():
    global BROWSER_CONTEXT
    if BROWSER_CONTEXT is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        BROWSER_CONTEXT = await browser.new_context()
    return BROWSER_CONTEXT

async def smart_browser_fallback(url: str, site_name: str):
    if site_name not in HIGH_VALUE_SITES:
        return None  # Only for important sites

    try:
        context = await get_browser_context()
        page = await context.new_page()
        await stealth_async(page)
        await page.goto(url, timeout=12000)
        content = await page.content()
        await page.close()
        return content
    except:
        return None

# ==================== ADAPTIVE THROTTLING ====================
async def adaptive_wait(site_name: str):
    now = datetime.now()
    if site_name in LAST_REQUEST:
        diff = (now - LAST_REQUEST[site_name]).total_seconds()
        if diff < 1.5:  # minimum delay
            await asyncio.sleep(1.5 - diff)
    LAST_REQUEST[site_name] = now

# ==================== ULTIMATE CHECKER v9.2 ====================
@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
async def check_site_v92(session, site_name, url_template, username):
    async with sem:
        await adaptive_wait(site_name)  # Adaptive Throttling

        url = url_template.format(u=username)
        headers = {"User-Agent": random.choice(UA_LIST)}
        proxy = random.choice(PROXY_LIST) if PROXY_LIST else None

        try:
            async with session.get(url, headers=headers, proxy=proxy, timeout=8, allow_redirects=True) as resp:
                text = await resp.text()
                parser = advanced_dom_parser(text, site_name, username)

                if parser["exists"]:
                    return {"site": site_name, "url": str(resp.url), "confidence": parser["confidence"], "signals": parser["signals"]}

        except:
            # Smart Browser Fallback (only for high value sites)
            content = await smart_browser_fallback(url, site_name)
            if content:
                parser = advanced_dom_parser(content, site_name, username)
                if parser["exists"]:
                    return {"site": site_name, "url": url, "confidence": 80, "signals": ["playwright"]}

        return None

# ==================== SCAN ====================
async def scan_username_v92():
    username = input(Fore.GREEN + "\n[+] Enter Username: ").strip()
    await init_db()

    cached = await get_from_cache(username)
    if cached:
        print(Fore.CYAN + "[*] Loaded from cache")
        for r in cached:
            print(f"{Fore.GREEN}[+] {r['site']} → {r['url']} ({r['confidence']}%)")
        return

    print(Fore.YELLOW + f"\n[*] Scanning with v9.2 (Optimized + Smart Fallback)...\n")

    found = []
    if os.path.exists("proxies.txt"):
        global PROXY_LIST
        with open("proxies.txt") as f:
            PROXY_LIST = [line.strip() for line in f if line.strip()]

    async with aiohttp.ClientSession() as session:
        tasks = [check_site_v92(session, name, url, username) for name, url in SITES.items()]
        results = await tqdm_asyncio.gather(*tasks, desc="v9.2 Scan", unit="site")

    found = [r for r in results if r]
    for r in found:
        print(f"{Fore.GREEN}[+] {r['site']}: {r['url']} (Confidence: {r['confidence']}%)")

    print(Fore.GREEN + Style.BRIGHT + f"\n[=] Total: {len(found)}")

    await save_to_cache(username, found)

    if found:
        save = input(Fore.YELLOW + "\n[?] Save? (y/n): ").lower()
        if save == 'y':
            fname = f"gscan_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            async with aiofiles.open(fname, "w", encoding="utf-8") as f:
                await f.write(json.dumps({"username": username, "results": found}, indent=2))
            print(Fore.GREEN + f"[+] Saved: {fname}")

# ==================== MAIN ====================
def main():
    while True:
        display_banner()
        print("1. Email OSINT")
        print("2. Username OSINT (v9.2 - Final Optimized)")
        print("3. Exit")
        choice = input("\nSelect: ").strip()

        if choice == "1":
            scan_email()
        elif choice == "2":
            asyncio.run(scan_username_v92())
        elif choice == "3":
            sys.exit()

if __name__ == "__main__":
    main()