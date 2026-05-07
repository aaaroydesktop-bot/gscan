#!/usr/bin/env python3
"""
Gscan v6.0 - Ultra-Fast Async OSINT Tracker
Developed by: Anupom Roy
"""
import requests
import re
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

# ==================== BANNER & MENU ====================
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
    print(Fore.CYAN + "      Gscan v6.0 - Ultra-Fast Async OSINT Tracker")
    print(Fore.WHITE + "      Developed by: " + Fore.YELLOW + "Anupom Roy")
    print(Fore.WHITE + "      -------------------------------------------\n")

def show_disclaimer():
    print(Fore.RED + Style.BRIGHT + "\n[!] LEGAL DISCLAIMER")
    print(Fore.WHITE + "This tool is for educational and authorized security research only.")
    print(Fore.WHITE + "Do NOT use it for illegal activities. Respect privacy and laws.\n")

# ==================== EMAIL OSINT (unchanged but improved) ====================
def check_gravatar(email):
    print(Fore.YELLOW + "\n[*] Step 3: Checking Gravatar...")
    try:
        md5_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
        url = f"https://en.gravatar.com/{md5_hash}.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200 and 'entry' in res.json():
            profile = res.json()['entry'][0]
            print(Fore.GREEN + "[+] Gravatar Profile Found!")
            print(f"    Username: {profile.get('preferredUsername', 'N/A')}")
            print(f"    Display Name: {profile.get('displayName', 'N/A')}")
        else:
            print(Fore.RED + "[-] No public Gravatar profile found.")
    except:
        print(Fore.RED + "[-] Gravatar check failed.")

def check_data_breaches(email):
    print(Fore.YELLOW + "\n[*] Step 2: Checking Data Breaches...")
    try:
        url = f"https://api.xposedornot.com/v1/check-email/{email}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('breaches'):
                print(Fore.RED + Style.BRIGHT + "[!] WARNING: Email found in breaches!")
                for breach in data['breaches'][0]:
                    print(Fore.MAGENTA + f"  ☠️  {breach}")
            else:
                print(Fore.GREEN + "[+] No known breaches found.")
    except:
        print(Fore.RED + "[-] Breach check failed.")

def scan_email():
    email = input(Fore.GREEN + "\n[+] Enter Email: " + Fore.WHITE).strip()
    if "@" not in email or "." not in email:
        print(Fore.RED + "[!] Invalid email!")
        return
    print(Fore.YELLOW + f"\n[*] Target: {email}")
    print(Fore.YELLOW + "[*] Running Holehe (120+ platforms)...")
    try:
        subprocess.run(["holehe", email, "--only-used"], check=True)
    except FileNotFoundError:
        subprocess.run([sys.executable, "-m", "pip", "install", "holehe"], check=True)
        subprocess.run(["holehe", email, "--only-used"])
    check_data_breaches(email)
    check_gravatar(email)

# ==================== USERNAME OSINT - ASYNC VERSION ====================
# Clean unique list (~185 sites)
SITES = {
    "GitHub": "https://github.com/{u}",
    "GitLab": "https://gitlab.com/{u}",
    "BitBucket": "https://bitbucket.org/{u}/",
    "Reddit": "https://www.reddit.com/user/{u}",
    "Pinterest": "https://www.pinterest.com/{u}/",
    "Medium": "https://medium.com/@{u}",
    "Vimeo": "https://vimeo.com/{u}",
    "SoundCloud": "https://soundcloud.com/{u}",
    "Telegram": "https://t.me/{u}",
    "TikTok": "https://www.tiktok.com/@{u}",
    "Roblox": "https://www.roblox.com/user.aspx?username={u}",
    "Twitch": "https://www.twitch.tv/{u}",
    "Steam": "https://steamcommunity.com/id/{u}",
    "Patreon": "https://www.patreon.com/{u}",
    "Dev.to": "https://dev.to/{u}",
    "Linktree": "https://linktr.ee/{u}",
    "About.me": "https://about.me/{u}",
    "Flickr": "https://www.flickr.com/people/{u}/",
    "Behance": "https://www.behance.net/{u}",
    "Dribbble": "https://dribbble.com/{u}",
    "ArtStation": "https://www.artstation.com/{u}",
    "DeviantArt": "https://www.deviantart.com/{u}",
    "Chess.com": "https://www.chess.com/member/{u}",
    "Lichess": "https://lichess.org/@/{u}",
    "Wattpad": "https://www.wattpad.com/user/{u}",
    "Blogger": "https://{u}.blogspot.com",
    "WordPress": "https://{u}.wordpress.com",
    "HackerNews": "https://news.ycombinator.com/user?id={u}",
    "CodePen": "https://codepen.io/{u}",
    "LeetCode": "https://leetcode.com/{u}",
    "HackerRank": "https://www.hackerrank.com/{u}",
    "Codeforces": "https://codeforces.com/profile/{u}",
    "Pastebin": "https://pastebin.com/u/{u}",
    "Replit": "https://replit.com/@{u}",
    "ProductHunt": "https://www.producthunt.com/@{u}",
    "BuyMeACoffee": "https://www.buymeacoffee.com/{u}",
    "Ko-fi": "https://ko-fi.com/{u}",
    "Fiverr": "https://www.fiverr.com/{u}",
    "Last.fm": "https://www.last.fm/user/{u}",
    "Mixcloud": "https://www.mixcloud.com/{u}/",
    "DailyMotion": "https://www.dailymotion.com/{u}",
    "Giphy": "https://giphy.com/channel/{u}",
    "Tenor": "https://tenor.com/users/{u}",
    "Imgur": "https://imgur.com/user/{u}",
    "Unsplash": "https://unsplash.com/@{u}",
    "VSCO": "https://vsco.co/{u}",
    "Disqus": "https://disqus.com/by/{u}/",
    "Instructables": "https://www.instructables.com/member/{u}/",
    "Wikipedia": "https://en.wikipedia.org/wiki/User:{u}",
    "TryHackMe": "https://tryhackme.com/p/{u}",
    "HackTheBox": "https://app.hackthebox.com/users/{u}",
    "Keybase": "https://keybase.io/{u}",
    "HubPages": "https://hubpages.com/@{u}",
    "Kaggle": "https://www.kaggle.com/{u}",
    "Bandcamp": "https://bandcamp.com/{u}",
    "WeHeartIt": "https://weheartit.com/{u}",
    "Rumble": "https://rumble.com/user/{u}",
    "HackerOne": "https://hackerone.com/{u}",
    "Bugcrowd": "https://bugcrowd.com/{u}",
    "Freelancer": "https://www.freelancer.com/u/{u}",
    "DockerHub": "https://hub.docker.com/u/{u}",
    "NPM": "https://www.npmjs.com/~{u}",
    "PyPI": "https://pypi.org/user/{u}/",
    "Codecademy": "https://www.codecademy.com/profiles/{u}",
    "SourceForge": "https://sourceforge.net/u/{u}/profile/",
    "FreeCodeCamp": "https://www.freecodecamp.org/{u}",
    "VK": "https://vk.com/{u}",
    "OK.ru": "https://ok.ru/{u}",
    "Spotify": "https://open.spotify.com/user/{u}",
    "SlideShare": "https://www.slideshare.net/{u}",
    "Scribd": "https://www.scribd.com/{u}",
    "Badoo": "https://badoo.com/profile/{u}",
    "Gumroad": "https://{u}.gumroad.com/",
    "Canva": "https://www.canva.com/{u}",
    "Foursquare": "https://foursquare.com/{u}",
    "Letterboxd": "https://letterboxd.com/{u}/",
    "MyAnimeList": "https://myanimelist.net/profile/{u}",
    "OpenStreetMap": "https://www.openstreetmap.org/user/{u}",
    "Strava": "https://www.strava.com/athletes/{u}",
    "Trello": "https://trello.com/{u}",
    "Figma": "https://www.figma.com/@{u}",
    "Goodreads": "https://www.goodreads.com/user/show/{u}",
    "Kickstarter": "https://www.kickstarter.com/profile/{u}",
    "Notion": "https://{u}.notion.site",
    "Opensea": "https://opensea.io/{u}",
    "Substack": "https://{u}.substack.com",
    "Thingiverse": "https://www.thingiverse.com/{u}",
    "Trustpilot": "https://www.trustpilot.com/users/{u}",
    "Udemy": "https://www.udemy.com/user/{u}/",
    "Zomato": "https://www.zomato.com/{u}",
    "TripAdvisor": "https://www.tripadvisor.com/Profile/{u}",
    "Smule": "https://www.smule.com/{u}",
    "Speedrun": "https://www.speedrun.com/user/{u}",
    "Mastodon": "https://mastodon.social/@{u}",
    "AllTrails": "https://www.alltrails.com/members/{u}",
    "Ebay": "https://www.ebay.com/usr/{u}",
    "FaceIT": "https://www.faceit.com/en/players/{u}",
    "FortniteTracker": "https://fortnitetracker.com/profile/all/{u}",
    "Gitee": "https://gitee.com/{u}",
    "Hackaday": "https://hackaday.io/{u}",
    "Issuu": "https://issuu.com/{u}",
    "Itchio": "https://{u}.itch.io/",
    "LiveJournal": "https://{u}.livejournal.com/",
    "Lottiefiles": "https://lottiefiles.com/{u}",
    "MyFitnessPal": "https://www.myfitnesspal.com/profile/{u}",
    "Newgrounds": "https://{u}.newgrounds.com/",
    "Osu": "https://osu.ppy.sh/users/{u}",
    "Packagist": "https://packagist.org/packages/{u}/",
    "Pexels": "https://www.pexels.com/@{u}",
    "Pixabay": "https://pixabay.com/users/{u}/",
    "PlayStation": "https://my.playstation.com/profile/{u}",
    "PokemonShowdown": "https://pokemonshowdown.com/users/{u}",
    "ReverbNation": "https://www.reverbnation.com/{u}",
    "Sketchfab": "https://sketchfab.com/{u}",
    "TrueAchievements": "https://www.trueachievements.com/gamer/{u}",
    "UltimateGuitar": "https://www.ultimate-guitar.com/u/{u}",
    "Xbox": "https://account.xbox.com/en-us/profile?gamertag={u}",
    "HackerEarth": "https://www.hackerearth.com/@{u}",
    "TopCoder": "https://www.topcoder.com/members/{u}",
    "CodeChef": "https://www.codechef.com/users/{u}",
    "Upwork": "https://www.upwork.com/freelancers/~{u}",
    "500px": "https://500px.com/p/{u}",
    "Crunchyroll": "https://www.crunchyroll.com/user/{u}",
    "Tumblr": "https://{u}.tumblr.com/",
    "Ghostbin": "https://ghostbin.com/user/{u}",
    "JSFiddle": "https://jsfiddle.net/user/{u}/",
    "Glitch": "https://glitch.com/@{u}",
    "RubyGems": "https://rubygems.org/profiles/{u}",
    "GOG": "https://www.gog.com/u/{u}",
    "EpicGames": "https://store.epicgames.com/en-US/p/{u}",
    "ModDB": "https://www.moddb.com/members/{u}",
    "NexusMods": "https://www.nexusmods.com/users/{u}",
    "GameBanana": "https://gamebanana.com/members/{u}",
    "IGN": "https://www.ign.com/boards/members/{u}/",
    "Gamespot": "https://www.gamespot.com/profile/{u}/",
    "Polygon": "https://www.polygon.com/users/{u}",
}

async def check_site_async(session, site_name, url_template, username, headers):
    url = url_template.format(u=username)
    try:
        async with session.get(url, headers=headers, timeout=8) as response:
            if response.status == 200:
                text = await response.text()
                if "page not found" not in text.lower() and "doesn't exist" not in text.lower():
                    return f"{Fore.GREEN}[+] {site_name}: {Fore.WHITE}{url}"
    except:
        pass
    return None

async def scan_username_async():
    username = input(Fore.GREEN + "\n[+] Enter Username: " + Fore.WHITE).strip()
    if not username:
        print(Fore.RED + "[!] Username cannot be empty!")
        return

    print(Fore.YELLOW + f"\n[*] Scanning '{username}' across {len(SITES)} platforms (Async Mode)...")
    print(Fore.CYAN + "[*] Using asyncio + aiohttp for maximum speed\n")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found = []

    async with aiohttp.ClientSession() as session:
        tasks = [check_site_async(session, name, url, username, headers) for name, url in SITES.items()]
        results = await tqdm_asyncio.gather(*tasks, desc="Scanning", unit="site")

    found = [r for r in results if r]
    for r in found:
        print(r)

    print(Fore.GREEN + Style.BRIGHT + f"\n[=] Total Profiles Found: {len(found)}")

    # Export option
# Export option
    if found:
        save = input(Fore.YELLOW + "\n[?] Save results to JSON & CSV? (y/n): ").lower()
        if save == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gscan_{username}_{timestamp}"
            
            # ANSI কালার কোড রিমুভ করার ফাংশন
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            
            clean_found = []
            csv_data = []
            
            for line in found:
                clean_line = ansi_escape.sub('', line) # কালার মুছে ফেলবে
                clean_found.append(clean_line)
                
                parts = clean_line.split(": ", 1)
                if len(parts) == 2:
                    csv_data.append([parts[0].replace("[+] ", ""), parts[1]])

            # JSON
            with open(f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump({"username": username, "found_profiles": clean_found, "timestamp": timestamp}, f, indent=2, ensure_ascii=False)
            print(Fore.GREEN + f"[+] Saved: {filename}.json")

            # CSV
            with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Platform", "URL"])
                writer.writerows(csv_data)
            print(Fore.GREEN + f"[+] Saved: {filename}.csv")

# ==================== MAIN ====================
def main():
    show_disclaimer()
    while True:
        display_banner()
        print(Fore.WHITE + "1. 📧 Email OSINT (Holehe + Breaches + Gravatar)")
        print(Fore.MAGENTA + "2. 👤 Username OSINT (185+ Platforms - Async + Export)")
        print(Fore.WHITE + "3. 👨‍💻 About Developer")
        print(Fore.WHITE + "4. ❌ Exit\n")

        choice = input(Fore.GREEN + "Select option (1-4): " + Style.RESET_ALL).strip()

        if choice == "1":
            scan_email()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == "2":
            asyncio.run(scan_username_async())
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == "3":
            print(Fore.CYAN + "\nGscan v6.0 - Ultra-Fast Async OSINT Framework")
            print("Developer: Anupom Roy | GitHub: github.com/aaaroydesktop-bot")
            input(Fore.YELLOW + "\nPress Enter...")
        elif choice == "4":
            print(Fore.RED + "\n[!] Exiting Gscan v6.0... Happy Hunting!\n")
            sys.exit()
        else:
            print(Fore.RED + "[!] Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Interrupted by user. Exiting...\n")
        sys.exit()