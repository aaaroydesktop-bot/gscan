#!/bin/bash

GREEN="\e[1;32m"
BLUE="\e[1;34m"
YELLOW="\e[1;33m"
RESET="\e[0m"

clear
echo -e "${BLUE}================================================${RESET}"
echo -e "${GREEN}      Gscan v9.2 - Enterprise Setup${RESET}"
echo -e "${BLUE}================================================${RESET}\n"

echo -e "${YELLOW}[*] Updating system packages...${RESET}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[*] Installing Core Dependencies (Python, Git, libxml)...${RESET}"
pkg install python git libxml2 libxslt -y

echo -e "${YELLOW}[*] Installing Python Modules... (This may take a minute)${RESET}"
pip install --upgrade pip
pip install aiohttp aiosqlite aiofiles colorama tqdm beautifulsoup4 lxml tenacity holehe playwright playwright-stealth

echo -e "${YELLOW}[*] Setting up execution permissions...${RESET}"
chmod +x main.py
cp main.py $PREFIX/bin/gscan
chmod +x $PREFIX/bin/gscan

echo -e "\n${GREEN}✅ Installation Complete!${RESET}"
echo -e "${GREEN}🎉 Type '${BLUE}gscan${GREEN}' anywhere in your terminal to start the tool.${RESET}\n"