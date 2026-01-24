#!/usr/bin/env python3
"""
=============== WEBSITE SCRAPER TOOL ===============
Professional Web Resource Extractor
Linux & Termux Compatible
Author: Abhishek
Version: 2.0
====================================================
"""

import os
import sys
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
import argparse
import concurrent.futures
import hashlib
import ssl
import socket
import random
from urllib.parse import urljoin, urlparse, urlunparse
import json
import logging
from datetime import datetime
import mimetypes
import threading
from queue import Queue
import signal

# Disable SSL warnings for Termux compatibility
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# SSL context for secure connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class WebsiteScraper:
    def __init__(self, target_url, output_dir=None, depth=2, delay=1, max_threads=5):
        """
        Initialize the Website Scraper
        
        Args:
            target_url: Website URL to scrape
            output_dir: Output directory path
            depth: Scraping depth (default: 2)
            delay: Delay between requests in seconds
            max_threads: Maximum concurrent threads
        """
        self.target_url = self.normalize_url(target_url)
        self.domain = urlparse(self.target_url).netloc
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = Path(f"scraped_{self.domain}_{timestamp}")
        
        self.depth = depth
        self.delay = delay
        self.max_threads = max_threads
        
        # Data structures
        self.visited_urls = set()
        self.resource_queue = Queue()
        self.failed_urls = []
        self.successful_downloads = []
        
        # Session configuration
        self.session = self.create_session()
        
        # Directory structure
        self.setup_directories()
        
        # Statistics
        self.stats = {
            'html_pages': 0,
            'css_files': 0,
            'js_files': 0,
            'images': 0,
            'fonts': 0,
            'other': 0,
            'start_time': time.time()
        }
        
        # User agents rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        ]
        
        # Setup logging
        self.setup_logging()
        
        # Signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def normalize_url(self, url):
        """Ensure URL has proper scheme"""
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url
    
    def create_session(self):
        """Create and configure HTTP session"""
        session = requests.Session()
        session.verify = False
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def setup_directories(self):
        """Create directory structure for scraped content"""
        directories = [
            self.output_dir,
            self.output_dir / 'html',
            self.output_dir / 'css',
            self.output_dir / 'js',
            self.output_dir / 'images',
            self.output_dir / 'fonts',
            self.output_dir / 'media',
            self.output_dir / 'metadata',
            self.output_dir / 'logs'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging system"""
        log_file = self.output_dir / 'logs' / 'scraper.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C interrupt"""
        self.logger.info("\n[!] Interrupt received. Saving progress...")
        self.save_progress()
        sys.exit(0)
    
    def get_safe_filename(self, url, resource_type='html'):
        """Generate safe filename from URL"""
        parsed_url = urlparse(url)
        
        # Remove scheme and domain
        path = parsed_url.path
        if not path or path == '/':
            filename = 'index'
        else:
            # Clean path for filename
            filename = path.strip('/').replace('/', '_')
            filename = re.sub(r'[^\w\-_.]', '_', filename)
        
        # Add query hash if present
        if parsed_url.query:
            query_hash = hashlib.md5(parsed_url.query.encode()).hexdigest()[:8]
            filename = f"{filename}_{query_hash}"
        
        # Determine extension
        if resource_type == 'css':
            ext = '.css'
        elif resource_type == 'js':
            ext = '.js'
        elif resource_type == 'image':
            ext = self.get_file_extension(url)
        elif resource_type == 'font':
            ext = self.get_file_extension(url)
        else:
            ext = '.html'
        
        # Add extension if not present
        if not filename.endswith(ext):
            filename += ext
        
        return filename[:200]  # Limit filename length
    
    def get_file_extension(self, url):
        """Get file extension from URL or content type"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Common extensions mapping
        extensions = {
            '.css': '.css',
            '.js': '.js',
            '.jpg': '.jpg', '.jpeg': '.jpg',
            '.png': '.png',
            '.gif': '.gif',
            '.svg': '.svg',
            '.webp': '.webp',
            '.woff': '.woff', '.woff2': '.woff2',
            '.ttf': '.ttf', '.otf': '.otf',
            '.ico': '.ico'
        }
        
        for ext in extensions:
            if path.endswith(ext):
                return extensions[ext]
        
        return '.bin'  # Default extension
    
    def download_resource(self, url, resource_type):
        """Download a single resource"""
        try:
            # Rate limiting
            time.sleep(self.delay)
            
            # Randomize user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            
            # Send request
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Determine save path
            filename = self.get_safe_filename(url, resource_type)
            
            if resource_type == 'html':
                save_path = self.output_dir / 'html' / filename
                # Process HTML for internal resources
                content = self.process_html_content(response.content, url, filename)
            elif resource_type == 'css':
                save_path = self.output_dir / 'css' / filename
                content = response.content
                # Process CSS for background images
                content = self.process_css_content(content, url)
            elif resource_type == 'js':
                save_path = self.output_dir / 'js' / filename
                content = response.content
            elif resource_type == 'image':
                save_path = self.output_dir / 'images' / filename
                content = response.content
            elif resource_type == 'font':
                save_path = self.output_dir / 'fonts' / filename
                content = response.content
            else:
                save_path = self.output_dir / 'media' / filename
                content = response.content
            
            # Save file
            with open(save_path, 'wb') as f:
                f.write(content)
            
            # Update statistics
            self.stats[f'{resource_type}s'] = self.stats.get(f'{resource_type}s', 0) + 1
            self.successful_downloads.append(url)
            
            self.logger.info(f"[+] Downloaded: {resource_type.upper()} - {filename}")
            
            # Save metadata
            self.save_metadata(url, save_path, resource_type, response.headers)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[-] Failed: {url} - {str(e)}")
            self.failed_urls.append({'url': url, 'error': str(e)})
            return False
    
    def process_html_content(self, content, base_url, filename):
        """Process HTML content to update resource URLs"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Update all links
            self.update_resource_links(soup, base_url, 'link', 'href', ['stylesheet'])
            self.update_resource_links(soup, base_url, 'script', 'src')
            self.update_resource_links(soup, base_url, 'img', 'src')
            self.update_resource_links(soup, base_url, 'source', 'src')
            self.update_resource_links(soup, base_url, 'audio', 'src')
            self.update_resource_links(soup, base_url, 'video', 'src')
            
            # Update inline styles
            for tag in soup.find_all(style=True):
                updated_style = self.update_css_urls(tag['style'], base_url)
                tag['style'] = updated_style
            
            # Extract additional links
            self.extract_links(soup, base_url)
            
            # Convert to string with proper formatting
            return soup.prettify().encode('utf-8')
            
        except Exception as e:
            self.logger.error(f"HTML processing error: {str(e)}")
            return content
    
    def update_resource_links(self, soup, base_url, tag_name, attr_name, rel_values=None):
        """Update resource links in HTML"""
        tags = soup.find_all(tag_name, **{attr_name: True})
        
        for tag in tags:
            if rel_values and tag.get('rel') and tag.get('rel')[0] not in rel_values:
                continue
                
            original_url = tag[attr_name]
            absolute_url = urljoin(base_url, original_url)
            
            # Check if it's a resource we should download
            if self.is_external_resource(absolute_url):
                continue
            
            # Determine resource type
            resource_type = self.get_resource_type(absolute_url)
            
            if resource_type:
                # Add to download queue
                if absolute_url not in self.visited_urls:
                    self.resource_queue.put((absolute_url, resource_type))
                    self.visited_urls.add(absolute_url)
                
                # Update URL to local path
                filename = self.get_safe_filename(absolute_url, resource_type)
                local_path = f"../{resource_type}s/{filename}"
                tag[attr_name] = local_path
    
    def update_css_urls(self, css_content, base_url):
        """Update URLs in CSS content"""
        # Find all url() declarations
        pattern = r'url\([\'"]?([^\'")]+)[\'"]?\)'
        
        def replace_url(match):
            original_url = match.group(1)
            
            # Skip data URIs
            if original_url.startswith('data:'):
                return match.group(0)
            
            absolute_url = urljoin(base_url, original_url)
            
            # Check if it's a resource we should download
            if self.is_external_resource(absolute_url):
                return match.group(0)
            
            resource_type = self.get_resource_type(absolute_url)
            
            if resource_type in ['image', 'font']:
                if absolute_url not in self.visited_urls:
                    self.resource_queue.put((absolute_url, resource_type))
                    self.visited_urls.add(absolute_url)
                
                filename = self.get_safe_filename(absolute_url, resource_type)
                return f'url("../{resource_type}s/{filename}")'
            
            return match.group(0)
        
        return re.sub(pattern, replace_url, css_content)
    
    def process_css_content(self, content, base_url):
        """Process CSS content"""
        try:
            css_text = content.decode('utf-8', errors='ignore')
            updated_css = self.update_css_urls(css_text, base_url)
            return updated_css.encode('utf-8')
        except:
            return content
    
    def extract_links(self, soup, base_url):
        """Extract all links from HTML"""
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Only follow internal links within depth limit
            if (self.is_internal_url(absolute_url) and 
                absolute_url not in self.visited_urls and
                self.get_url_depth(absolute_url) <= self.depth):
                
                self.resource_queue.put((absolute_url, 'html'))
                self.visited_urls.add(absolute_url)
    
    def get_resource_type(self, url):
        """Determine resource type from URL"""
        url_lower = url.lower()
        
        if url_lower.endswith('.css') or 'stylesheet' in url:
            return 'css'
        elif url_lower.endswith('.js'):
            return 'js'
        elif any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
            return 'image'
        elif any(url_lower.endswith(ext) for ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']):
            return 'font'
        elif url_lower.endswith('.html') or url_lower.endswith('.htm'):
            return 'html'
        
        # Try to determine from content type
        try:
            response = self.session.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/css' in content_type:
                return 'css'
            elif 'javascript' in content_type or 'application/javascript' in content_type:
                return 'js'
            elif 'text/html' in content_type:
                return 'html'
            elif 'image/' in content_type:
                return 'image'
            elif 'font/' in content_type or 'application/font' in content_type:
                return 'font'
        except:
            pass
        
        return None
    
    def is_internal_url(self, url):
        """Check if URL is internal to the target domain"""
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.domain or not parsed_url.netloc
    
    def is_external_resource(self, url):
        """Check if resource is external"""
        return not self.is_internal_url(url)
    
    def get_url_depth(self, url):
        """Calculate URL depth from base URL"""
        base_path = urlparse(self.target_url).path
        url_path = urlparse(url).path
        
        if base_path == '/':
            base_depth = 0
        else:
            base_depth = len(base_path.strip('/').split('/'))
        
        if url_path == '/':
            url_depth = 0
        else:
            url_depth = len(url_path.strip('/').split('/'))
        
        return url_depth - base_depth
    
    def save_metadata(self, url, filepath, resource_type, headers):
        """Save metadata about downloaded resource"""
        metadata_file = self.output_dir / 'metadata' / 'downloads.json'
        
        metadata = {
            'url': url,
            'filepath': str(filepath),
            'resource_type': resource_type,
            'size': filepath.stat().st_size if filepath.exists() else 0,
            'downloaded_at': datetime.now().isoformat(),
            'headers': dict(headers)
        }
        
        # Load existing metadata
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Add new metadata
        data.append(metadata)
        
        # Save updated metadata
        with open(metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_progress(self):
        """Save scraping progress"""
        progress_file = self.output_dir / 'logs' / 'progress.json'
        
        progress_data = {
            'target_url': self.target_url,
            'total_visited': len(self.visited_urls),
            'successful_downloads': len(self.successful_downloads),
            'failed_urls': self.failed_urls,
            'statistics': self.stats,
            'completed_at': datetime.now().isoformat()
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    def print_banner(self):
        """Print tool banner"""
        banner = """
        ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
        ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
        ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝
        ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
        ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
        ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
        
        ========== WEBSITE SCRAPER TOOL v2.0 ==========
        Author: Abhishek
        Target: %s
        Output: %s
        ===============================================
        """ % (self.target_url, self.output_dir)
        
        print(banner)
    
    def print_stats(self):
        """Print scraping statistics"""
        elapsed_time = time.time() - self.stats['start_time']
        
        stats_text = """
        ============== SCRAPING COMPLETE ==============
        Target Website: %s
        Output Directory: %s
        
        =============== STATISTICS ================
        HTML Pages: %d
        CSS Files: %d
        JavaScript Files: %d
        Images: %d
        Fonts: %d
        Other Resources: %d
        -------------------------------------------
        Total Downloaded: %d
        Failed Downloads: %d
        
        =============== TIME & INFO ===============
        Start Time: %s
        Elapsed Time: %.2f seconds
        ===========================================
        
        [!] All resources saved to: %s
        [!] Logs available in: %s/logs/
        [!] Metadata in: %s/metadata/
        """ % (
            self.target_url,
            self.output_dir,
            self.stats.get('html_pages', 0),
            self.stats.get('css_files', 0),
            self.stats.get('js_files', 0),
            self.stats.get('images', 0),
            self.stats.get('fonts', 0),
            self.stats.get('other', 0),
            len(self.successful_downloads),
            len(self.failed_urls),
            datetime.fromtimestamp(self.stats['start_time']).strftime('%Y-%m-%d %H:%M:%S'),
            elapsed_time,
            self.output_dir,
            self.output_dir,
            self.output_dir
        )
        
        print(stats_text)
    
    def run(self):
        """Main scraping execution"""
        self.print_banner()
        
        print("[*] Starting website scraper...")
        print(f"[*] Target: {self.target_url}")
        print(f"[*] Depth: {self.depth}")
        print(f"[*] Threads: {self.max_threads}")
        print(f"[*] Output directory: {self.output_dir}")
        print("-" * 50)
        
        # Start with main URL
        self.resource_queue.put((self.target_url, 'html'))
        self.visited_urls.add(self.target_url)
        
        # Worker function for threads
        def worker():
            while not self.resource_queue.empty():
                try:
                    url, resource_type = self.resource_queue.get_nowait()
                    self.download_resource(url, resource_type)
                    self.resource_queue.task_done()
                except Exception as e:
                    continue
        
        # Create thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for _ in range(min(self.max_threads, self.resource_queue.qsize())):
                future = executor.submit(worker)
                futures.append(future)
            
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
        
        # Save final progress
        self.save_progress()
        
        # Print statistics
        self.print_stats()
        
        # Generate summary report
        self.generate_report()

    def generate_report(self):
        """Generate detailed report"""
        report_file = self.output_dir / 'scraping_report.txt'
        
        report_content = f"""
        ======= WEBSITE SCRAPING REPORT =======
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Target: {self.target_url}
        Domain: {self.domain}
        
        ======= DIRECTORY STRUCTURE =======
        {self.output_dir}/
            ├── html/      # HTML pages
            ├── css/       # Stylesheets
            ├── js/        # JavaScript files
            ├── images/    # Images
            ├── fonts/     # Font files
            ├── media/     # Other media
            ├── metadata/  # Download metadata
            └── logs/      # Log files
        
        ======= DOWNLOAD SUMMARY =======
        Total URLs Attempted: {len(self.visited_urls)}
        Successful Downloads: {len(self.successful_downloads)}
        Failed Downloads: {len(self.failed_urls)}
        Success Rate: {(len(self.successful_downloads)/len(self.visited_urls)*100):.1f}%
        
        ======= RESOURCE BREAKDOWN =======
        HTML Pages: {self.stats.get('html_pages', 0)}
        CSS Files: {self.stats.get('css_files', 0)}
        JavaScript Files: {self.stats.get('js_files', 0)}
        Images: {self.stats.get('images', 0)}
        Fonts: {self.stats.get('fonts', 0)}
        Other Resources: {self.stats.get('other', 0)}
        
        ======= FAILED DOWNLOADS =======
        """
        
        for failed in self.failed_urls[:10]:  # Show first 10 failures
            report_content += f"\nURL: {failed['url']}"
            report_content += f"\nError: {failed['error']}\n"
        
        if len(self.failed_urls) > 10:
            report_content += f"\n... and {len(self.failed_urls) - 10} more failures."
        
        report_content += f"""
        
        ======= IMPORTANT NOTES =======
        1. All resource paths have been updated to local references
        2. Open html/index.html to view the scraped website locally
        3. Check logs/scraper.log for detailed process information
        4. Review metadata/downloads.json for download details
        
        ======= NEXT STEPS =======
        1. Test the scraped website locally
        2. Check for any broken links or missing resources
        3. Modify content as needed for offline use
        4. Compress the output directory for sharing
        
        ======= TOOL INFORMATION =======
        Website Scraper Tool v2.0
        Author: Abhishek
        Compatible with: Linux, Termux, Windows (with Python)
        """
        
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        print(f"[+] Detailed report saved to: {report_file}")


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Professional Website Scraper - Downloads complete websites for offline use',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com -o my_website -d 3
  %(prog)s https://example.com -t 10 --delay 0.5
  
Note: Use responsibly and respect robots.txt and website terms of service.
        """
    )
    
    parser.add_argument('url', help='Website URL to scrape')
    parser.add_argument('-o', '--output', default=None, help='Output directory name')
    parser.add_argument('-d', '--depth', type=int, default=2, help='Scraping depth (default: 2)')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Maximum threads (default: 5)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("[!] Please provide a valid URL with http:// or https://")
        print(f"[*] Trying with https://{args.url}")
        args.url = 'https://' + args.url
    
    try:
        # Create scraper instance
        scraper = WebsiteScraper(
            target_url=args.url,
            output_dir=args.output,
            depth=args.depth,
            delay=args.delay,
            max_threads=args.threads
        )
        
        # Run scraper
        scraper.run()
        
    except KeyboardInterrupt:
        print("\n[!] Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
