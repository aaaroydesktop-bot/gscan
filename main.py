#!/usr/bin/env python
import os
import sys
import subprocess
import requests
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
    print(Fore.CYAN + "      Advanced Email OSINT Tracker v2.0 (Ultra)")
    print(Fore.WHITE + "      Developed by: " + Fore.YELLOW + "Anupom Roy")
    print(Fore.WHITE + "      -----------------------------------------\n")

def check_data_breaches(email):
    print(Fore.YELLOW + "\n[*] Step 2: Checking Data Breach Databases (Deep Web Leaks)...")
    try:
        # XposedOrNot ফ্রি API ব্যবহার করা হচ্ছে
        url = f"https://api.xposedornot.com/v1/check-email/{email}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'breaches' in data and data['breaches']:
                print(Fore.RED + Style.BRIGHT + "\n[!] WARNING: Email found in Data Breaches!")
                print(Fore.WHITE + "This email was registered on the following sites which got hacked:\n")
                for breach in data['breaches'][0]:
                    print(Fore.MAGENTA + f" ☠️  {breach}")
            else:
                print(Fore.GREEN + "\n[+] No data breaches found for this email.")
        elif response.status_code == 404:
            print(Fore.GREEN + "\n[+] No data breaches found. Email is safe from known leaks.")
        else:
            print(Fore.RED + "\n[-] Could not reach Data Breach API. Status:", response.status_code)
    except Exception as e:
        print(Fore.RED + "\n[-] Data Breach scan failed. Check your internet connection.")

def scan_email():
    print(Fore.GREEN + "[+] Enter the Email address you want to track:")
    email = input(Fore.WHITE + " ❯❯❯ ").strip()

    if "@" not in email or "." not in email:
        print(Fore.RED + "\n[!] Invalid Email Address! Please try again.")
        return

    print(Fore.YELLOW + f"\n[*] Target Target: {email}")
    print(Fore.YELLOW + "[*] Step 1: Checking 120+ Active Platforms via Holehe...\n")
    
    try:
        subprocess.run(["holehe", email, "--only-used"])
    except FileNotFoundError:
        print(Fore.RED + "\n[!] 'holehe' not found. Running installation...")
        os.system("pip install holehe")
        subprocess.run(["holehe", email, "--only-used"])
        
    # Step 2: Data breach check
    check_data_breaches(email)

def about_dev():
    print(Fore.CYAN + "\n--- About Gscan Ultra ---")
    print(Fore.WHITE + "Gscan is an advanced OSINT tool combining live account")
    print(Fore.WHITE + "enumeration (120+ sites) with Deep Web Data Breach records")
    print(Fore.WHITE + "to provide maximum possible accuracy for email tracking.")
    print(Fore.GREEN + "\nDeveloper: " + Fore.YELLOW + "Anupom Roy")
    print(Fore.GREEN + "Role     : " + Fore.WHITE + "Software & Mobile App Developer")
    print(Fore.GREEN + "GitHub   : " + Fore.WHITE + "github.com/aaaroydesktop-bot")
    print(Fore.MAGENTA + "\nKeep your data safe and hack ethically!")

def main():
    while True:
        display_banner()
        print(Fore.WHITE + "1. 🔍 Start Deep Email Tracking")
        print(Fore.WHITE + "2. 👨‍💻 About Developer")
        print(Fore.WHITE + "3. ❌ Exit\n")
        
        choice = input(Fore.GREEN + "Select an option (1/2/3): " + Style.RESET_ALL)
        
        if choice == '1':
            scan_email()
            input(Fore.YELLOW + "\nPress Enter to return to menu...")
        elif choice == '2':
            about_dev()
            input(Fore.YELLOW + "\nPress Enter to return to menu...")
        elif choice == '3':
            print(Fore.RED + "\n[!] Exiting Gscan... Good bye Anupom!")
            sys.exit()
        else:
            print(Fore.RED + "\n[!] Invalid choice! Try again.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Interrupted! Exiting...")
        sys.exit()