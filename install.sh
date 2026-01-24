#!/bin/bash
# Website Scraper Installation Script
# Linux aur Termux ke liye

echo "========================================="
echo "Website Scraper Installation"
echo "Author: Abhishek"
echo "========================================="

# Check Python version
echo "[*] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Installing..."
    
    # For Termux
    if [ -d "/data/data/com.termux" ]; then
        pkg install python -y
    # For Ubuntu/Debian
    elif [ -f "/etc/debian_version" ]; then
        sudo apt update && sudo apt install python3 python3-pip -y
    # For CentOS/RHEL
    elif [ -f "/etc/redhat-release" ]; then
        sudo yum install python3 python3-pip -y
    # For Arch Linux
    elif [ -f "/etc/arch-release" ]; then
        sudo pacman -S python python-pip
    else
        echo "[!] Please install Python3 manually"
        exit 1
    fi
fi

echo "[+] Python3 is installed"

# Install required packages
echo "[*] Installing required Python packages..."
pip3 install requests beautifulsoup4 lxml

# Make scraper executable
echo "[*] Setting up the scraper..."
chmod +x scraper.py

echo "========================================="
echo "[+] Installation completed successfully!"
echo "========================================="
echo ""
echo "Usage:"
echo "  ./scraper.py https://example.com"
echo "  ./scraper.py https://example.com -o my_site -d 3"
echo ""
echo "Options:"
echo "  -o OUTPUT    Output directory name"
echo "  -d DEPTH     Scraping depth (default: 2)"
echo "  -t THREADS   Number of threads (default: 5)"
echo "  --delay SEC  Delay between requests"
echo "  -v           Verbose output"
echo ""
echo "Examples:"
echo "  ./scraper.py https://example.com"
echo "  ./scraper.py https://example.com -o mywebsite -d 3 -t 10"
echo "========================================="
