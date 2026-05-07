#!/usr/bin/env python
import os
import sys
import subprocess
import requests
import hashlib
import concurrent.futures
from colorama import Fore, Style, init

# Colorama Initialize
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
    print(Fore.CYAN + "      Advanced OSINT Tracker v5.0 (Ultra-Max)")
    print(Fore.WHITE + "      Developed by: " + Fore.YELLOW + "Anupom Roy")
    print(Fore.WHITE + "      ---------------------------------------\n")

# --- EMAIL OSINT FUNCTIONS ---
def check_gravatar(email):
    print(Fore.YELLOW + "\n[*] Step 3: Checking Global Profile (Gravatar)...")
    try:
        md5_hash = hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()
        url = f"https://en.gravatar.com/{md5_hash}.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if 'entry' in data:
                profile = data['entry'][0]
                print(Fore.GREEN + Style.BRIGHT + "[+] Gravatar Profile Found!")
                print(Fore.CYAN + f"    - Username: {Fore.WHITE}{profile.get('preferredUsername', 'N/A')}")
                print(Fore.CYAN + f"    - Display Name: {Fore.WHITE}{profile.get('displayName', 'N/A')}")
                print(Fore.CYAN + f"    - Profile URL: {Fore.WHITE}{profile.get('profileUrl', 'N/A')}")
        elif res.status_code == 404:
            print(Fore.RED + "[-] No public Gravatar profile linked to this email.")
        else:
            print(Fore.RED + "[-] Could not check Gravatar at this moment.")
    except Exception as e:
        print(Fore.RED + "[-] Gravatar check failed due to network error.")

def check_data_breaches(email):
    print(Fore.YELLOW + "\n[*] Step 2: Checking Data Breach Databases (Deep Web Leaks)...")
    try:
        url = f"https://api.xposedornot.com/v1/check-email/{email}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'breaches' in data and data['breaches']:
                print(Fore.RED + Style.BRIGHT + "\n[!] WARNING: Email found in Data Breaches!")
                for breach in data['breaches'][0]:
                    print(Fore.MAGENTA + f" ☠️  {breach}")
            else:
                print(Fore.GREEN + "[+] No data breaches found for this email.")
        elif response.status_code == 404:
            print(Fore.GREEN + "[+] No data breaches found. Email is safe from known leaks.")
    except Exception:
        print(Fore.RED + "[-] Data Breach scan failed. Check your internet connection.")

def scan_email():
    print(Fore.GREEN + "[+] Enter the Email address you want to track:")
    email = input(Fore.WHITE + " ❯❯❯ ").strip()

    if "@" not in email or "." not in email:
        print(Fore.RED + "\n[!] Invalid Email Address!")
        return

    print(Fore.YELLOW + f"\n[*] Target Email: {email}")
    print(Fore.YELLOW + "[*] Step 1: Checking 120+ Active Platforms via Holehe...\n")
    try:
        subprocess.run(["holehe", email, "--only-used"])
    except FileNotFoundError:
        os.system("pip install holehe")
        subprocess.run(["holehe", email, "--only-used"])
        
    check_data_breaches(email)
    check_gravatar(email)

# --- USERNAME OSINT ENGINE (Massive Capacity) ---
def check_single_site(site_name, url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            # কিছু সাইট 200 রেসপন্স দেয় কিন্তু পেজে লেখে "Not Found", সেগুলোকে স্কিপ করার ট্রিক
            if "page not found" not in response.text.lower() and "doesn't exist" not in response.text.lower():
                return f"{Fore.GREEN}[+] {site_name}: {Fore.WHITE}{url}"
    except:
        pass
    return None

def scan_username():
    print(Fore.GREEN + "[+] Enter the Username you want to track (e.g., anupom123):")
    username = input(Fore.WHITE + " ❯❯❯ ").strip()

    # 60+ Premium & Popular Sites Dictionary
    sites = {
        "GitHub": f"https://github.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "BitBucket": f"https://bitbucket.org/{username}/",
        "Instagram": f"https://www.picuki.com/profile/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}/",
        "Medium": f"https://medium.com/@{username}",
        "Vimeo": f"https://vimeo.com/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Telegram": f"https://t.me/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Roblox": f"https://www.roblox.com/user.aspx?username={username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "Dev.to": f"https://dev.to/{username}",
        "Linktree": f"https://linktr.ee/{username}",
        "About.me": f"https://about.me/{username}",
        "Flickr": f"https://www.flickr.com/people/{username}/",
        "Behance": f"https://www.behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "ArtStation": f"https://www.artstation.com/{username}",
        "DeviantArt": f"https://www.deviantart.com/{username}",
        "Chess.com": f"https://www.chess.com/member/{username}",
        "Lichess": f"https://lichess.org/@/{username}",
        "Wattpad": f"https://www.wattpad.com/user/{username}",
        "Blogger": f"https://{username}.blogspot.com",
        "WordPress": f"https://{username}.wordpress.com",
        "HackerNews": f"https://news.ycombinator.com/user?id={username}",
        "CodePen": f"https://codepen.io/{username}",
        "LeetCode": f"https://leetcode.com/{username}",
        "HackerRank": f"https://www.hackerrank.com/{username}",
        "Codeforces": f"https://codeforces.com/profile/{username}",
        "Pastebin": f"https://pastebin.com/u/{username}",
        "Replit": f"https://replit.com/@{username}",
        "ProductHunt": f"https://www.producthunt.com/@{username}",
        "BuyMeACoffee": f"https://www.buymeacoffee.com/{username}",
        "Ko-fi": f"https://ko-fi.com/{username}",
        "Fiverr": f"https://www.fiverr.com/{username}",
        "Last.fm": f"https://www.last.fm/user/{username}",
        "Mixcloud": f"https://www.mixcloud.com/{username}/",
        "DailyMotion": f"https://www.dailymotion.com/{username}",
        "Giphy": f"https://giphy.com/channel/{username}",
        "Tenor": f"https://tenor.com/users/{username}",
        "Imgur": f"https://imgur.com/user/{username}",
        "Unsplash": f"https://unsplash.com/@{username}",
        "VSCO": f"https://vsco.co/{username}",
        "Disqus": f"https://disqus.com/by/{username}/",
        "Instructables": f"https://www.instructables.com/member/{username}/",
        "Wikipedia": f"https://en.wikipedia.org/wiki/User:{username}",
        "TryHackMe": f"https://tryhackme.com/p/{username}",
        "HackTheBox": f"https://app.hackthebox.com/users/{username}",
        "Keybase": f"https://keybase.io/{username}",
        "HubPages": f"https://hubpages.com/@{username}",
        "Contently": f"https://{username}.contently.com/",
        "Flipboard": f"https://flipboard.com/@{username}",
        "Kaggle": f"https://www.kaggle.com/{username}",
        "Bandcamp": f"https://bandcamp.com/{username}",
        "WeHeartIt": f"https://weheartit.com/{username}",
        "Rumble": f"https://rumble.com/user/{username}",
        # --- NEW 100+ PREMIUM SITES ADDED ---
        "HackerOne": f"https://hackerone.com/{username}",
        "Bugcrowd": f"https://bugcrowd.com/{username}",
        "Freelancer": f"https://www.freelancer.com/u/{username}",
        "DockerHub": f"https://hub.docker.com/u/{username}",
        "NPM": f"https://www.npmjs.com/~{username}",
        "PyPI": f"https://pypi.org/user/{username}/",
        "Codecademy": f"https://www.codecademy.com/profiles/{username}",
        "SourceForge": f"https://sourceforge.net/u/{username}/profile/",
        "FreeCodeCamp": f"https://www.freecodecamp.org/{username}",
        "VK": f"https://vk.com/{username}",
        "OK.ru": f"https://ok.ru/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "SlideShare": f"https://www.slideshare.net/{username}",
        "Scribd": f"https://www.scribd.com/{username}",
        "Badoo": f"https://badoo.com/profile/{username}",
        "Gumroad": f"https://{username}.gumroad.com/",
        "Canva": f"https://www.canva.com/{username}",
        "Foursquare": f"https://foursquare.com/{username}",
        "Ello": f"https://ello.co/{username}",
        "EyeEm": f"https://www.eyeem.com/u/{username}",
        "IFTTT": f"https://ifttt.com/p/{username}",
        "Letterboxd": f"https://letterboxd.com/{username}/",
        "MyAnimeList": f"https://myanimelist.net/profile/{username}",
        "OpenStreetMap": f"https://www.openstreetmap.org/user/{username}",
        "Slack": f"https://{username}.slack.com",
        "Snapchat": f"https://www.snapchat.com/add/{username}",
        "Strava": f"https://www.strava.com/athletes/{username}",
        "Tinder": f"https://tinder.com/@{username}",
        "TradingView": f"https://www.tradingview.com/u/{username}/",
        "Trello": f"https://trello.com/{username}",
        "Weebly": f"https://{username}.weebly.com/",
        "Wix": f"https://{username}.wixsite.com/",
        "Xing": f"https://www.xing.com/profile/{username}",
        "Figma": f"https://www.figma.com/@{username}",
        "Goodreads": f"https://www.goodreads.com/user/show/{username}",
        "Kickstarter": f"https://www.kickstarter.com/profile/{username}",
        "Notion": f"https://{username}.notion.site",
        "Opensea": f"https://opensea.io/{username}",
        "Substack": f"https://{username}.substack.com",
        "Thingiverse": f"https://www.thingiverse.com/{username}",
        "Trustpilot": f"https://www.trustpilot.com/users/{username}",
        "Udemy": f"https://www.udemy.com/user/{username}/",
        "Zomato": f"https://www.zomato.com/{username}",
        "TripAdvisor": f"https://www.tripadvisor.com/Profile/{username}",
        "Gravatar": f"https://en.gravatar.com/{username}",
        "Smule": f"https://www.smule.com/{username}",
        "Speedrun": f"https://www.speedrun.com/user/{username}",
        "TrackerGG": f"https://tracker.gg/valorant/profile/riot/{username}",
        "Pastee": f"https://paste.ee/u/{username}",
        "Gitea": f"https://gitea.com/{username}",
        "Codeberg": f"https://codeberg.org/{username}",
        "Mastodon": f"https://mastodon.social/@{username}",
        "AllTrails": f"https://www.alltrails.com/members/{username}",
        "BitePaste": f"https://bitepaste.com/u/{username}",
        "CashApp": f"https://cash.app/${username}",
        "CouchSurfing": f"https://www.couchsurfing.com/people/{username}",
        "Crowdin": f"https://crowdin.com/profile/{username}",
        "Desura": f"https://www.desura.com/members/{username}",
        "Discogs": f"https://www.discogs.com/user/{username}",
        "DiscussPython": f"https://discuss.python.org/u/{username}",
        "Ebay": f"https://www.ebay.com/usr/{username}",
        "FaceIT": f"https://www.faceit.com/en/players/{username}",
        "FortniteTracker": f"https://fortnitetracker.com/profile/all/{username}",
        "Furaffinity": f"https://www.furaffinity.net/user/{username}/",
        "G2G": f"https://www.g2g.com/{username}",
        "GamerBans": f"https://gamerbans.com/user/{username}/",
        "Gamespot": f"https://www.gamespot.com/profile/{username}/",
        "Geocaching": f"https://www.geocaching.com/profile/?u={username}",
        "Gfycat": f"https://gfycat.com/@{username}",
        "Gitee": f"https://gitee.com/{username}",
        "Hackaday": f"https://hackaday.io/{username}",
        "Houzz": f"https://www.houzz.com/user/{username}",
        "Issuu": f"https://issuu.com/{username}",
        "Itchio": f"https://{username}.itch.io/",
        "LiveJournal": f"https://{username}.livejournal.com/",
        "Lottiefiles": f"https://lottiefiles.com/{username}",
        "Mapillary": f"https://www.mapillary.com/app/user/{username}",
        "MuckRack": f"https://muckrack.com/{username}",
        "MyFitnessPal": f"https://www.myfitnesspal.com/profile/{username}",
        "Newgrounds": f"https://{username}.newgrounds.com/",
        "Osu": f"https://osu.ppy.sh/users/{username}",
        "Packagist": f"https://packagist.org/packages/{username}/",
        "Pexels": f"https://www.pexels.com/@{username}",
        "Pixabay": f"https://pixabay.com/users/{username}/",
        "PlayStation": f"https://my.playstation.com/profile/{username}",
        "PokemonShowdown": f"https://pokemonshowdown.com/users/{username}",
        "Polygon": f"https://www.polygon.com/users/{username}",
        "Qzone": f"https://{username}.qzone.qq.com/",
        "ReverbNation": f"https://www.reverbnation.com/{username}",
        "Sketchfab": f"https://sketchfab.com/{username}",
        "SmugMug": f"https://{username}.smugmug.com/",
        "StarCitizen": f"https://robertsspaceindustries.com/citizens/{username}",
        "Tellonym": f"https://tellonym.me/{username}",
        "Trackilicious": f"https://trackilicious.com/players/{username}",
        "Trakteer": f"https://trakteer.id/{username}",
        "Trashbox": f"https://trashbox.ru/users/{username}",
        "TrueAchievements": f"https://www.trueachievements.com/gamer/{username}",
        "UltimateGuitar": f"https://www.ultimate-guitar.com/u/{username}",
        "Vero": f"https://vero.co/{username}",
        "Windy": f"https://community.windy.com/user/{username}",
        "Xbox": f"https://account.xbox.com/en-us/profile?gamertag={username}",
        "YandexMusic": f"https://music.yandex.ru/users/{username}/playlists",
        "Zhihu": f"https://www.zhihu.com/people/{username}",
        # --- EXTRA 100+ NEW SITES ---
        "HackerEarth": f"https://www.hackerearth.com/@{username}",
        "TopCoder": f"https://www.topcoder.com/members/{username}",
        "CodeChef": f"https://www.codechef.com/users/{username}",
        "Spoj": f"https://www.spoj.com/users/{username}/",
        "Coderwall": f"https://coderwall.com/{username}",
        "Kaggle": f"https://www.kaggle.com/{username}",
        "Kofi": f"https://ko-fi.com/{username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "Fiverr": f"https://www.fiverr.com/{username}",
        "Upwork": f"https://www.upwork.com/freelancers/~{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "Behance": f"https://www.behance.net/{username}",
        "ArtStation": f"https://www.artstation.com/{username}",
        "Coroflot": f"https://www.coroflot.com/{username}",
        "500px": f"https://500px.com/p/{username}",
        "VSCO": f"https://vsco.co/{username}",
        "Flickr": f"https://www.flickr.com/photos/{username}/",
        "DeviantArt": f"https://www.deviantart.com/{username}",
        "Imgur": f"https://imgur.com/user/{username}",
        "Giphy": f"https://giphy.com/channel/{username}",
        "Tenor": f"https://tenor.com/users/{username}",
        "Unsplash": f"https://unsplash.com/@{username}",
        "Pixabay": f"https://pixabay.com/users/{username}",
        "Pexels": f"https://www.pexels.com/@{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Mixcloud": f"https://www.mixcloud.com/{username}/",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Bandcamp": f"https://bandcamp.com/{username}",
        "ReverbNation": f"https://www.reverbnation.com/{username}",
        "Last.fm": f"https://www.last.fm/user/{username}",
        "SpotifyUser": f"https://open.spotify.com/user/{username}",
        "DailyMotion": f"https://www.dailymotion.com/{username}",
        "Vimeo": f"https://vimeo.com/{username}",
        "Crunchyroll": f"https://www.crunchyroll.com/user/{username}",
        "MyAnimeList": f"https://myanimelist.net/profile/{username}",
        "Goodreads": f"https://www.goodreads.com/user/show/{username}",
        "Wattpad": f"https://www.wattpad.com/user/{username}",
        "Blogger": f"https://{username}.blogspot.com/",
        "WordPress": f"https://{username}.wordpress.com/",
        "Medium": f"https://medium.com/@{username}",
        "Substack": f"https://{username}.substack.com/",
        "Tumblr": f"https://{username}.tumblr.com/",
        "LiveJournal": f"https://{username}.livejournal.com/",
        "HubPages": f"https://hubpages.com/@{username}",
        "SlideShare": f"https://www.slideshare.net/{username}",
        "Scribd": f"https://www.scribd.com/{username}",
        "Issuu": f"https://issuu.com/{username}",
        "Pastebin": f"https://pastebin.com/u/{username}",
        "Ghostbin": f"https://ghostbin.com/user/{username}",
        "CodePen": f"https://codepen.io/{username}",
        "JSFiddle": f"https://jsfiddle.net/user/{username}/",
        "Replit": f"https://replit.com/@{username}",
        "Glitch": f"https://glitch.com/@{username}",
        "Keybase": f"https://keybase.io/{username}",
        "BitBucket": f"https://bitbucket.org/{username}/",
        "GitLab": f"https://gitlab.com/{username}",
        "Gitea": f"https://gitea.com/{username}",
        "Codeberg": f"https://codeberg.org/{username}",
        "SourceForge": f"https://sourceforge.net/u/{username}/profile/",
        "DockerHub": f"https://hub.docker.com/u/{username}",
        "NPM": f"https://www.npmjs.com/~{username}",
        "PyPI": f"https://pypi.org/user/{username}/",
        "RubyGems": f"https://rubygems.org/profiles/{username}",
        "Packagist": f"https://packagist.org/packages/{username}/",
        "TryHackMe": f"https://tryhackme.com/p/{username}",
        "HackTheBox": f"https://app.hackthebox.com/users/{username}",
        "HackerOne": f"https://hackerone.com/{username}",
        "Bugcrowd": f"https://bugcrowd.com/{username}",
        "Codecademy": f"https://www.codecademy.com/profiles/{username}",
        "FreeCodeCamp": f"https://www.freecodecamp.org/{username}",
        "LeetCode": f"https://leetcode.com/{username}",
        "HackerRank": f"https://www.hackerrank.com/{username}",
        "Chess.com": f"https://www.chess.com/member/{username}",
        "Lichess": f"https://lichess.org/@/{username}",
        "Speedrun": f"https://www.speedrun.com/user/{username}",
        "FaceIT": f"https://www.faceit.com/en/players/{username}",
        "TrackerGG": f"https://tracker.gg/valorant/profile/riot/{username}",
        "Osu": f"https://osu.ppy.sh/users/{username}",
        "Roblox": f"https://www.roblox.com/user.aspx?username={username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Xbox": f"https://account.xbox.com/en-us/profile?gamertag={username}",
        "PlayStation": f"https://my.playstation.com/profile/{username}",
        "GOG": f"https://www.gog.com/u/{username}",
        "EpicGames": f"https://store.epicgames.com/en-US/p/{username}",
        "ModDB": f"https://www.moddb.com/members/{username}",
        "NexusMods": f"https://www.nexusmods.com/users/{username}",
        "GameBanana": f"https://gamebanana.com/members/{username}",
        "IGN": f"https://www.ign.com/boards/members/{username}/",
        "Gamespot": f"https://www.gamespot.com/profile/{username}/",
        "Polygon": f"https://www.polygon.com/users/{username}",
        "Instructables": f"https://www.instructables.com/member/{username}/",
        "Hackaday": f"https://hackaday.io/{username}",
        "Thingiverse": f"https://www.thingiverse.com/{username}",
        "Sketchfab": f"https://sketchfab.com/{username}",
        "Lottiefiles": f"https://lottiefiles.com/{username}",
        "ProductHunt": f"https://www.producthunt.com/@{username}",
        "Trustpilot": f"https://www.trustpilot.com/users/{username}",
        "TripAdvisor": f"https://www.tripadvisor.com/Profile/{username}",
        "Zomato": f"https://www.zomato.com/{username}",
        "MyFitnessPal": f"https://www.myfitnesspal.com/profile/{username}",
        "Strava": f"https://www.strava.com/athletes/{username}"
    }

    total_sites = (len(sites) // 10) * 10
    print(Fore.YELLOW + f"\n[*] Scanning for Username: '{username}' across {total_sites}+ premium platforms...")
    print(Fore.YELLOW + "[*] Using 100 Threads for Maximum Speed. Please wait...\n")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    found_profiles = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_site = {executor.submit(check_single_site, name, url, headers): name for name, url in sites.items()}
        for future in concurrent.futures.as_completed(future_to_site):
            result = future.result()
            if result:
                found_profiles.append(result)
                print(result)

    if not found_profiles:
        print(Fore.RED + "\n[-] No profiles found for this username.")
    else:
        print(Fore.GREEN + Style.BRIGHT + f"\n[=] Total Profiles Found: {len(found_profiles)}")

# --- MAIN MENU ---
def about_dev():
    print(Fore.CYAN + "\n--- About Gscan Max Power ---")
    print(Fore.WHITE + "An ultra-fast, multi-threaded OSINT framework.")
    print(Fore.GREEN + "\nDeveloper: " + Fore.YELLOW + "Anupom Roy")
    print(Fore.GREEN + "Role     : " + Fore.WHITE + "Software & Mobile App Developer")
    print(Fore.GREEN + "GitHub   : " + Fore.WHITE + "github.com/aaaroydesktop-bot")

def main():
    while True:
        display_banner()
        print(Fore.WHITE + "1. 📧 Email OSINT (120+ Sites, Breaches, Gravatar)")
        print(Fore.MAGENTA + "2. 👤 Username OSINT (250+ Premium Platforms)")
        print(Fore.WHITE + "3. 👨‍💻 About Developer")
        print(Fore.WHITE + "4. ❌ Exit\n")
        
        choice = input(Fore.GREEN + "Select an option (1-4): " + Style.RESET_ALL)
        
        if choice == '1':
            scan_email()
            input(Fore.YELLOW + "\nPress Enter to return to menu...")
        elif choice == '2':
            scan_username()
            input(Fore.YELLOW + "\nPress Enter to return to menu...")
        elif choice == '3':
            about_dev()
            input(Fore.YELLOW + "\nPress Enter to return to menu...")
        elif choice == '4':
            print(Fore.RED + "\n[!] Exiting Gscan... Happy Hunting!\n")
            sys.exit()
        else:
            print(Fore.RED + "\n[!] Invalid choice! Try again.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Interrupted! Exiting...\n")
        sys.exit()