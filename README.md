# 🌐 Web Scraper - Complete Website Downloader
A professional website scraping tool that downloads complete websites including HTML, CSS, JavaScript, images, and fonts for offline viewing. Perfect for web developers, security researchers, and digital archivists.

## ✨ Features

- **Complete Website Download**: Downloads all HTML, CSS, JS, images, and fonts
- **Local Path Rewriting**: Updates all resource paths for offline viewing
- **Multi-threaded**: Fast concurrent downloads with configurable threads
- **Depth Control**: Specify how many levels deep to scrape
- **Rate Limiting**: Configurable delays between requests
- **Metadata Logging**: Detailed JSON logs of all downloads
- **Progress Tracking**: Resume capability and progress saving
- **Cross-Platform**: Works on Linux, Termux, and other Unix-like systems
- **Professional Output**: Organized directory structure with reports

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Installation
```bash
# Clone the repositor
git clone https://github.com/abhiexploits/Web-scraper.gi
cd Web-scrap
# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x scraper.py
```

Dependencies

Only three packages required:

```bash
pip install requests beautifulsoup4 lxml
```

## 🚀 Quick Start

Basic Usage

```bash
# Scrape a website (default settings)
python scraper.py https://example.com
```

Advanced Usage

```bash
# Custom output directory
python scraper.py https://example.com -o my_website

# Increase scraping depth and threads
python scraper.py https://example.com -d 3 -t 10

# Add delay between requests
python scraper.py https://example.com --delay 0.5

# Verbose output
python scraper.py https://example.com -v
```

## ⚙️ Command Line Options

Option Description Default
url Target website URL (required) -
-o, --output Custom output directory name scraped_website_{timestamp}
-d, --depth Scraping depth (how many levels to follow) 2
-t, --threads Maximum concurrent download threads 5
--delay Delay between requests in seconds 1.0
-v, --verbose Enable verbose output False

## 📁 Output Structure

```
scraped_website_20240124_153045/
├── html/                 # All HTML pages
│   ├── index.html        # Main page
│   ├── about.html        # Other pages
│   └── contact.html
├── css/                  # Stylesheets
│   ├── style.css
│   ├── bootstrap.min.css
│   └── font-awesome.css
├── js/                   # JavaScript files
│   ├── main.js
│   ├── jquery.min.js
│   └── analytics.js
├── images/               # Images
│   ├── logo.png
│   ├── banner.jpg
│   └── icons/
├── fonts/                # Web fonts
│   ├── roboto.woff2
│   └── fontawesome.woff
├── media/                # Other media files
├── metadata/             # Download metadata
│   └── downloads.json    # Complete download log
└── logs/                 # Log files
    ├── scraper.log       # Detailed process log
    ├── progress.json     # Progress tracking
    └── scraping_report.txt
```

## 📋 Usage Examples

Example 1: Basic Website Download

```bash
python scraper.py https://example.com
```

Downloads the complete website to scraped_example.com_20240124_153045/

Example 2: Custom Directory with Depth 3

```bash
python scraper.py https://example.com -o my_backup -d 3
```

Downloads 3 levels deep into my_backup/ directory

Example 3: Fast Download with 10 Threads

```bash
python scraper.py https://example.com -t 10 --delay 0.2
```

Uses 10 concurrent threads with minimal delay

Example 4: Scrape for Offline Viewing

```bash
python scraper.py https://docs.python.org -o python_docs -d 2
```

Perfect for creating offline documentation

## 🛠️ Technical Details

How It Works

1. Initial Request: Downloads the main HTML page
2. Resource Extraction: Parses HTML for CSS, JS, images, and links
3. Path Rewriting: Converts absolute URLs to local relative paths
4. Recursive Download: Follows internal links up to specified depth
5. Concurrent Processing: Downloads multiple resources simultaneously
6. Metadata Logging: Records all downloads for verification

Features for Developers

· Modular Design: Easy to extend and customize
· Error Handling: Comprehensive error recovery and logging
· Session Management: Persistent HTTP sessions with retry logic
· Content Processing: Intelligent MIME type detection
· File Management: Safe filename generation from URLs

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

Development Setup

```bash
# Clone and setup
git clone https://github.com/abhiexploits/Web-scraper.git
cd Web-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

## ⚠️ Important Notes

Legal Considerations

· Only scrape websites you own or have permission to download
· Respect robots.txt files and website terms of service
· Do not use for malicious purposes or to violate copyright

Rate Limiting

· Use the --delay parameter to avoid overwhelming servers
· Consider the website's bandwidth and resources
· Be respectful of smaller websites

Limitations

· JavaScript-heavy SPAs may not render correctly offline
· Dynamic content loaded via AJAX won't be captured
· Some resources may be blocked by CORS policies

## 🔧 Troubleshooting

Common Issues

1. SSL Certificate Errors (Termux)

```bash
pkg install openssl-tool
pip install --upgrade certifi
```

1. Permission Denied

```bash
chmod +x scraper.py
```

1. Python Not Found

```bash
# Termux
pkg install python

# Ubuntu/Debian
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

1. Missing Dependencies

```bash
pip install --upgrade requests beautifulsoup4 lxml
```

Debug Mode

```bash
# Enable verbose logging
python scraper.py https://example.com -v

# Check log files
cat scraped_website/logs/scraper.log
```

## 📊 Performance Tips

1. Adjust Threads: Use -t option based on your network speed
2. Optimize Depth: Start with depth 1, then increase as needed
3. Use Delay: For large sites, use --delay to avoid bans
4. Monitor Memory: Large sites may require significant disk space
## 🙏 Acknowledgments

· Built with Python's powerful standard library
· Inspired by web archiving and digital preservation tools
· Thanks to all contributors and users

## 📞 Support

For issues, questions, or suggestions:

1. Check the Issues page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 📈 Future Enhancements

· Support for sitemap.xml parsing
· Browser automation integration
· Cloud storage integration
· GUI interface
· Docker containerization
· API endpoint for automation

---

Created with ❤️ by Abhishek
