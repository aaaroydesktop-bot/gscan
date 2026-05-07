#!/bin/bash

GREEN="\e[1;32m"
BLUE="\e[1;34m"
RESET="\e[0m"

echo -e "${BLUE}[*] Gscan - Installing Environment...${RESET}"
pkg update -y && pkg upgrade -y
pkg install python git -y

echo -e "${BLUE}[*] Installing dependencies...${RESET}"
pip install -r requirements.txt

echo -e "${BLUE}[*] Configuring global command...${RESET}"
chmod +x main.py
cp main.py $PREFIX/bin/gscan
chmod +x $PREFIX/bin/gscan

echo -e "${GREEN}✅ Gscan installed successfully!${RESET}"
echo -e "${GREEN}🎉 Type '${BLUE}gscan${GREEN}' anywhere to start the tool.${RESET}"