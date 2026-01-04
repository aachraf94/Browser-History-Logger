"""
Browser History Logger - Non-Intrusive Monitoring
Reads browser history files every 5 minutes without affecting internet speed
Supports: Chrome, Edge, Brave, Firefox
No proxy required - Direct history file access
"""

import sqlite3
import os
import shutil
import time
from datetime import datetime
from pathlib import Path


class BrowserHistoryLogger:
    def __init__(self, db_name="browsing_history.db"):
        self.db_name = db_name
        self.setup_database()
        self.last_ids = {}  # Track last seen IDs per browser to avoid duplicates
        print("✓ Browser History Logger initialized")
        print(f"✓ Database: {self.db_name}")
    
    def setup_database(self):
        """Create SQLite database for storing browsing history"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browsing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                visit_count INTEGER DEFAULT 1,
                browser TEXT NOT NULL,
                last_visit_time TEXT,
                UNIQUE(url, timestamp, browser)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                domain TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                browser TEXT,
                UNIQUE(date, domain, browser)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON browsing_history(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON browsing_history(url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_browser ON browsing_history(browser)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_summary(date)')
        
        conn.commit()
        conn.close()
    
    def get_browser_paths(self):
        """Get paths to browser history files"""
        localappdata = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')
        
        browsers = {
            'Chrome': os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'History'),
            'Edge': os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'History'),
            'Brave': os.path.join(localappdata, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'History'),
        }
        
        # Firefox requires finding the profile folder
        firefox_base = os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')
        if os.path.exists(firefox_base):
            for profile in os.listdir(firefox_base):
                if 'default' in profile.lower():
                    firefox_path = os.path.join(firefox_base, profile, 'places.sqlite')
                    if os.path.exists(firefox_path):
                        browsers['Firefox'] = firefox_path
                        break
        
        return browsers
    
    def copy_locked_file(self, source_path):
        """Copy a file that might be locked by browser"""
        temp_path = source_path + '.tmp'
        try:
            # Try direct copy first
            shutil.copy2(source_path, temp_path)
            return temp_path
        except Exception as e:
            # If file is locked, try alternative method
            try:
                import subprocess
                # Use PowerShell to copy even if file is in use
                cmd = f'Copy-Item -Path "{source_path}" -Destination "{temp_path}" -Force'
                subprocess.run(['powershell', '-Command', cmd], check=True, capture_output=True)
                return temp_path
            except:
                return None
    
    def extract_domain(self, url):
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def read_chromium_history(self, history_path, browser_name):
        """Read history from Chromium-based browsers (Chrome, Edge, Brave)"""
        if not os.path.exists(history_path):
            return []
        
        temp_path = self.copy_locked_file(history_path)
        if not temp_path:
            print(f"⚠️ Could not access {browser_name} history (browser may be open)")
            return []
        
        entries = []
        try:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            # Get last ID we processed for this browser
            last_id = self.last_ids.get(browser_name, 0)
            
            # Chromium stores time as microseconds since 1601-01-01
            cursor.execute('''
                SELECT id, url, title, visit_count, last_visit_time
                FROM urls
                WHERE id > ?
                ORDER BY id
            ''', (last_id,))
            
            for row in cursor.fetchall():
                row_id, url, title, visit_count, last_visit_time = row
                
                # Convert Chrome timestamp (microseconds since 1601-01-01) to datetime
                try:
                    # Chrome epoch starts at 1601-01-01
                    chrome_epoch = datetime(1601, 1, 1)
                    visit_time = chrome_epoch.timestamp() + (last_visit_time / 1000000)
                    timestamp = datetime.fromtimestamp(visit_time).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                entries.append({
                    'id': row_id,
                    'url': url,
                    'title': title or 'No Title',
                    'visit_count': visit_count,
                    'timestamp': timestamp,
                    'browser': browser_name
                })
                
                # Update last seen ID
                self.last_ids[browser_name] = max(self.last_ids.get(browser_name, 0), row_id)
            
            conn.close()
        except Exception as e:
            print(f"✗ Error reading {browser_name} history: {e}")
        finally:
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
        
        return entries
    
    def read_firefox_history(self, history_path):
        """Read history from Firefox"""
        if not os.path.exists(history_path):
            return []
        
        temp_path = self.copy_locked_file(history_path)
        if not temp_path:
            print(f"⚠️ Could not access Firefox history (browser may be open)")
            return []
        
        entries = []
        try:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            last_id = self.last_ids.get('Firefox', 0)
            
            cursor.execute('''
                SELECT moz_places.id, url, title, visit_count, last_visit_date
                FROM moz_places
                WHERE moz_places.id > ?
                ORDER BY moz_places.id
            ''', (last_id,))
            
            for row in cursor.fetchall():
                row_id, url, title, visit_count, last_visit_date = row
                
                # Firefox stores time as microseconds since Unix epoch
                try:
                    visit_time = last_visit_date / 1000000  # Convert to seconds
                    timestamp = datetime.fromtimestamp(visit_time).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                entries.append({
                    'id': row_id,
                    'url': url,
                    'title': title or 'No Title',
                    'visit_count': visit_count,
                    'timestamp': timestamp,
                    'browser': 'Firefox'
                })
                
                self.last_ids['Firefox'] = max(self.last_ids.get('Firefox', 0), row_id)
            
            conn.close()
        except Exception as e:
            print(f"✗ Error reading Firefox history: {e}")
        finally:
            try:
                os.remove(temp_path)
            except:
                pass
        
        return entries
    
    def save_entries(self, entries):
        """Save history entries to database (avoiding duplicates)"""
        if not entries:
            return 0
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        saved = 0
        
        for entry in entries:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO browsing_history 
                    (timestamp, url, title, visit_count, browser, last_visit_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    entry['timestamp'],
                    entry['url'],
                    entry['title'],
                    entry['visit_count'],
                    entry['browser'],
                    entry['timestamp']
                ))
                
                if cursor.rowcount > 0:
                    saved += 1
                    
                    # Update daily summary
                    domain = self.extract_domain(entry['url'])
                    today = datetime.now().strftime('%Y-%m-%d')
                    
                    cursor.execute('''
                        INSERT INTO daily_summary (date, domain, visit_count, browser)
                        VALUES (?, ?, 1, ?)
                        ON CONFLICT(date, domain, browser) 
                        DO UPDATE SET visit_count = visit_count + 1
                    ''', (today, domain, entry['browser']))
            
            except Exception as e:
                print(f"✗ Error saving entry: {e}")
        
        conn.commit()
        conn.close()
        
        return saved
    
    def collect_all_histories(self):
        """Collect history from all browsers"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collecting browser histories...")
        
        browser_paths = self.get_browser_paths()
        total_new = 0
        
        for browser_name, history_path in browser_paths.items():
            try:
                if browser_name == 'Firefox':
                    entries = self.read_firefox_history(history_path)
                else:
                    entries = self.read_chromium_history(history_path, browser_name)
                
                if entries:
                    saved = self.save_entries(entries)
                    total_new += saved
                    if saved > 0:
                        print(f"✓ {browser_name}: {saved} new entries")
                    else:
                        print(f"  {browser_name}: No new entries")
                else:
                    print(f"  {browser_name}: No history found")
                    
            except Exception as e:
                print(f"✗ Error processing {browser_name}: {e}")
        
        if total_new > 0:
            print(f"✓ Total new entries saved: {total_new}")
        else:
            print("  No new browsing activity detected")
        
        return total_new
    
    def run_continuous(self, interval_seconds=300):
        """Run continuous monitoring every N seconds (default 5 minutes)"""
        print("=" * 80)
        print("🕵️  Browser History Logger - Non-Intrusive Monitoring")
        print("=" * 80)
        print(f"\n✓ Monitoring browsers: Chrome, Edge, Brave, Firefox")
        print(f"✓ Check interval: {interval_seconds} seconds ({interval_seconds//60} minutes)")
        print(f"✓ Database: {self.db_name}")
        print(f"✓ No proxy required - Direct history access")
        print(f"✓ No internet speed impact")
        print("\n📊 Commands:")
        print("   python browser_history_logger.py view           - View recent history")
        print("   python browser_history_logger.py report         - Daily report")
        print("   python browser_history_logger.py top            - Top visited sites")
        print("   python browser_history_logger.py search <term>  - Search for website")
        print("   python browser_history_logger.py summary        - Overall statistics")
        print("\nPress Ctrl+C to stop monitoring\n")
        print("=" * 80)
        
        try:
            while True:
                self.collect_all_histories()
                print(f"\n⏳ Next check in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped")


def view_history(db_name="browsing_history.db", limit=50):
    """View recent browsing history"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT timestamp, browser, title, url
            FROM browsing_history
            ORDER BY timestamp DESC
            LIMIT {limit}
        ''')
        
        rows = cursor.fetchall()
        
        print("\n" + "=" * 120)
        print(f"Recent Browsing History (Last {limit} entries)")
        print("=" * 120)
        
        for timestamp, browser, title, url in rows:
            print(f"\n[{timestamp}] [{browser}]")
            print(f"  Title: {title}")
            print(f"  URL: {url}")
        
        cursor.execute('SELECT COUNT(*) FROM browsing_history')
        total = cursor.fetchone()[0]
        
        print("\n" + "=" * 120)
        print(f"📊 Total entries in database: {total}")
        print("=" * 120)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def daily_report(db_name="browsing_history.db"):
    """Generate daily browsing report"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        print("\n" + "=" * 80)
        print(f"📅 Daily Browsing Report - {today}")
        print("=" * 80)
        
        cursor.execute('''
            SELECT domain, SUM(visit_count) as total_visits, browser
            FROM daily_summary
            WHERE date = ?
            GROUP BY domain, browser
            ORDER BY total_visits DESC
            LIMIT 20
        ''', (today,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n🔝 Top Sites Visited Today:")
            for domain, visits, browser in results:
                print(f"  {domain} - {visits} visits [{browser}]")
        else:
            print("\n  No browsing activity recorded today")
        
        # Browser breakdown
        cursor.execute('''
            SELECT browser, SUM(visit_count) as total
            FROM daily_summary
            WHERE date = ?
            GROUP BY browser
            ORDER BY total DESC
        ''', (today,))
        
        browser_stats = cursor.fetchall()
        
        if browser_stats:
            print(f"\n📊 Browser Usage Today:")
            for browser, visits in browser_stats:
                print(f"  {browser}: {visits} visits")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def top_sites(db_name="browsing_history.db", days=7):
    """Show top visited sites"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print(f"\n🔝 Top Visited Sites (Last {days} Days)")
        print("=" * 80)
        
        cursor.execute(f'''
            SELECT domain, SUM(visit_count) as total_visits
            FROM daily_summary
            WHERE date >= date('now', '-{days} days')
            GROUP BY domain
            ORDER BY total_visits DESC
            LIMIT 30
        ''', ())
        
        results = cursor.fetchall()
        
        if results:
            for i, (domain, visits) in enumerate(results, 1):
                print(f"{i:2}. {domain} - {visits} visits")
        else:
            print("  No data available")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def search_website(search_term, db_name="browsing_history.db"):
    """Search for a specific website in history"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print(f"\n🔍 Search Results for: '{search_term}'")
        print("=" * 120)
        
        cursor.execute('''
            SELECT timestamp, browser, title, url
            FROM browsing_history
            WHERE url LIKE ? OR title LIKE ?
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"\nFound {len(rows)} results:\n")
            for timestamp, browser, title, url in rows:
                print(f"[{timestamp}] [{browser}]")
                print(f"  Title: {title}")
                print(f"  URL: {url}")
                print()
        else:
            print(f"\n  No results found for '{search_term}'")
        
        print("=" * 120)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def overall_summary(db_name="browsing_history.db"):
    """Show overall browsing statistics"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print("\n" + "=" * 80)
        print("📊 Overall Browsing Summary")
        print("=" * 80)
        
        # Total entries
        cursor.execute('SELECT COUNT(*) FROM browsing_history')
        total_entries = cursor.fetchone()[0]
        
        # Date range
        cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM browsing_history')
        date_range = cursor.fetchone()
        
        # Unique domains
        cursor.execute('SELECT COUNT(DISTINCT url) FROM browsing_history')
        unique_urls = cursor.fetchone()[0]
        
        # Browser breakdown
        cursor.execute('''
            SELECT browser, COUNT(*) as count
            FROM browsing_history
            GROUP BY browser
            ORDER BY count DESC
        ''')
        browser_stats = cursor.fetchall()
        
        # Top 10 all-time domains
        cursor.execute('''
            SELECT domain, SUM(visit_count) as total_visits
            FROM daily_summary
            GROUP BY domain
            ORDER BY total_visits DESC
            LIMIT 10
        ''')
        top_domains = cursor.fetchall()
        
        # Most active day
        cursor.execute('''
            SELECT date, SUM(visit_count) as total
            FROM daily_summary
            GROUP BY date
            ORDER BY total DESC
            LIMIT 1
        ''')
        most_active = cursor.fetchone()
        
        print(f"\n📈 Statistics:")
        print(f"   Total History Entries: {total_entries:,}")
        print(f"   Unique URLs: {unique_urls:,}")
        
        if date_range[0] and date_range[1]:
            print(f"   Date Range: {date_range[0][:10]} to {date_range[1][:10]}")
        
        if browser_stats:
            print(f"\n🌐 Browser Usage:")
            total_browser_entries = sum(count for _, count in browser_stats)
            for browser, count in browser_stats:
                percentage = (count / total_browser_entries * 100) if total_browser_entries > 0 else 0
                print(f"   {browser}: {count:,} entries ({percentage:.1f}%)")
        
        if top_domains:
            print(f"\n🔝 Top 10 All-Time Websites:")
            for i, (domain, visits) in enumerate(top_domains, 1):
                print(f"   {i:2}. {domain} - {visits:,} visits")
        
        if most_active:
            print(f"\n📅 Most Active Day:")
            print(f"   {most_active[0]} - {most_active[1]:,} visits")
        
        print("\n" + "=" * 80)
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "view":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            view_history(limit=limit)
        elif command == "report":
            daily_report()
        elif command == "top":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            top_sites(days=days)
        elif command == "search":
            if len(sys.argv) > 2:
                search_term = sys.argv[2]
                search_website(search_term)
            else:
                print("Usage: python browser_history_logger.py search <website>")
                print("Example: python browser_history_logger.py search youtube")
        elif command == "summary":
            overall_summary()
        elif command == "help":
            print("""
Browser History Logger - Commands

Usage:
  python browser_history_logger.py              - Start continuous monitoring
  python browser_history_logger.py view         - View recent history (default: 50)
  python browser_history_logger.py view 100     - View recent history (specify limit)
  python browser_history_logger.py report       - Generate daily report
  python browser_history_logger.py top          - Show top sites (last 7 days)
  python browser_history_logger.py top 30       - Show top sites (specify days)
  python browser_history_logger.py search <term> - Search for website/keyword
  python browser_history_logger.py summary      - Show overall statistics
  python browser_history_logger.py help         - Show this help

Examples:
  python browser_history_logger.py search youtube
  python browser_history_logger.py search facebook
  python browser_history_logger.py search "video games"

Features:
  ✓ No proxy required
  ✓ No internet speed impact
  ✓ Monitors: Chrome, Edge, Brave, Firefox
  ✓ Checks every 5 minutes
  ✓ Automatic deduplication
  ✓ Works even when browsers are open
            """)
        else:
            print(f"Unknown command: {command}")
            print("Use 'python browser_history_logger.py help' for usage")
    else:
        # Start continuous monitoring
        logger = BrowserHistoryLogger()
        logger.run_continuous(interval_seconds=300)  # 5 minutes
