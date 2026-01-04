# Browser History Logger

**Non-Intrusive Browser Monitoring System**

A lightweight, proxy-free solution for monitoring browser history across multiple browsers without affecting internet speed or performance.

---

## 🎯 Features

### Core Functionality

- ✅ **No Proxy Required** - Direct history file access
- ✅ **Zero Internet Impact** - No speed reduction or connection interference
- ✅ **Multi-Browser Support** - Chrome, Edge, Brave, Firefox
- ✅ **Automatic Monitoring** - Checks every 5 minutes
- ✅ **Smart Deduplication** - Prevents duplicate entries
- ✅ **Works Live** - Monitors even when browsers are running
- ✅ **SQLite Database** - Efficient local storage
- ✅ **Privacy Friendly** - All data stored locally

### Supported Browsers

| Browser         | Status       |
| --------------- | ------------ |
| Google Chrome   | ✅ Supported |
| Microsoft Edge  | ✅ Supported |
| Brave Browser   | ✅ Supported |
| Mozilla Firefox | ✅ Supported |

---

## 📁 Files

- **`browser_history_logger.py`** - Main monitoring script
- **`start_history_tracker.bat`** - Easy launcher (double-click to start)
- **`browsing_history.db`** - SQLite database (auto-created)

---

## 🚀 Quick Start

### Method 1: Double-Click Launch

Simply double-click **`start_history_tracker.bat`** to begin monitoring.

### Method 2: Command Line

```bash
python browser_history_logger.py
```

The script will:

1. Create the database if it doesn't exist
2. Detect all supported browsers
3. Start monitoring every 5 minutes
4. Display real-time collection status

---

## 📊 Available Commands

### Start Monitoring

```bash
python browser_history_logger.py
```

Runs continuous monitoring (checks every 5 minutes)

### View Recent History

```bash
# View last 50 entries
python browser_history_logger.py view

# View last 100 entries
python browser_history_logger.py view 100
```

Shows recent browsing history with timestamps, browser, title, and URLs

### Daily Report

```bash
python browser_history_logger.py report
```

Generates today's activity report including:

- Top visited sites today
- Browser usage breakdown
- Total visits per domain

### Top Sites

```bash
# Top sites from last 7 days
python browser_history_logger.py top

# Top sites from last 30 days
python browser_history_logger.py top 30
```

Displays most visited websites with visit counts

### Search for Website

```bash
# Search for specific website
python browser_history_logger.py search youtube

# Search with multiple words
python browser_history_logger.py search "social media"
```

Searches both URLs and page titles, shows up to 100 matches

### Overall Summary

```bash
python browser_history_logger.py summary
```

Complete statistics overview:

- Total history entries and unique URLs
- Browser usage breakdown with percentages
- Top 10 all-time most visited websites
- Most active day
- Full date range of tracked history

### Help

```bash
python browser_history_logger.py help
```

Displays all available commands with examples

---

## 💾 Database Structure

### Tables

#### `browsing_history`

Stores all browser history entries

- `timestamp` - When the page was visited
- `url` - Full URL
- `title` - Page title
- `visit_count` - Number of visits
- `browser` - Browser name (Chrome, Edge, etc.)
- `last_visit_time` - Last visit timestamp

#### `daily_summary`

Aggregated daily statistics

- `date` - Date of activity
- `domain` - Website domain
- `visit_count` - Total visits
- `browser` - Browser used

---

## 🔧 How It Works

1. **History File Detection**

   - Locates browser history files in standard Windows directories
   - Supports multiple browser profiles

2. **Safe File Access**

   - Creates temporary copies of history files
   - Works even when browsers are actively running
   - Uses PowerShell fallback for locked files

3. **Smart Data Collection**

   - Tracks last processed entry per browser
   - Only collects new entries to avoid duplicates
   - Converts browser timestamps to readable format

4. **Continuous Monitoring**
   - Runs in background checking every 5 minutes
   - Minimal CPU and memory usage
   - Press Ctrl+C to stop

---

## ⚙️ Requirements

- **Operating System:** Windows
- **Python:** 3.6 or higher
- **Dependencies:** None (uses built-in libraries only)
  - `sqlite3` - Database management
  - `os`, `shutil` - File operations
  - `time`, `datetime` - Scheduling and timestamps
  - `pathlib` - Path handling

---

## 📈 Example Usage Workflow

```bash
# 1. Start monitoring in background
start start_history_tracker.bat

# 2. Let it collect data for a while...

# 3. View what's been collected
python browser_history_logger.py view

# 4. Check today's activity
python browser_history_logger.py report

# 5. Search for specific sites
python browser_history_logger.py search facebook

# 6. Get overall statistics
python browser_history_logger.py summary

# 7. Find top sites over last month
python browser_history_logger.py top 30
```

---

## 🆚 Comparison with Version 1

| Feature           | Version 1 (Proxy)       | Version 2 (Direct)    |
| ----------------- | ----------------------- | --------------------- |
| Internet Speed    | ❌ Reduced              | ✅ No impact          |
| Setup Complexity  | ❌ High (proxy + certs) | ✅ Simple (just run)  |
| Browser Support   | Limited                 | ✅ All major browsers |
| Real-time Capture | ✅ Yes                  | 5-minute intervals    |
| SSL Certificate   | ❌ Required             | ✅ Not needed         |
| Reliability       | Medium                  | ✅ High               |
| User Detection    | Low                     | ✅ Undetectable       |

---

## 🛡️ Privacy & Security

- ✅ All data stored **locally** in SQLite database
- ✅ No external connections or cloud sync
- ✅ No network interception
- ✅ Works offline
- ✅ Can be password-protected (database encryption available)

---

## 🐛 Troubleshooting

### "Could not access browser history"

- Browser might be running - this is normal, script will retry next cycle
- Some browsers use different profile paths - check browser profile location

### No data appearing

- Wait at least 5 minutes for first collection cycle
- Ensure browsers have been used and have history
- Check if browser history is enabled (not cleared automatically)

### Database errors

- Delete `browsing_history.db` to reset and start fresh
- Ensure write permissions in script directory

---

## 📝 Notes

- History collection happens every **5 minutes** by default
- Change interval by editing `run_continuous(interval_seconds=300)` in code
- Works best when left running in background
- Low resource usage (< 50MB RAM, negligible CPU)
- Database file size: ~1MB per 10,000 entries

---

## 🎓 Advanced Tips

**Schedule at Windows Startup:**

1. Press `Win + R`
2. Type `shell:startup`
3. Create shortcut to `start_history_tracker.bat` in that folder

**Run as Windows Service:**
Use `install_service.py` from parent directory (if available)

**Export Data:**
Database is standard SQLite - use any SQLite viewer or export to CSV/Excel

---

## 📞 Support

For issues or questions, check the help command:

```bash
python browser_history_logger.py help
```

---

**Version 2.0** - Updated January 2026  
_Non-intrusive browser monitoring without proxy interference_
