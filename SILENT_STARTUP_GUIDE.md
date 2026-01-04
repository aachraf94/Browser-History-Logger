# Silent Startup Guide - Browser History Logger

## Files for Silent Execution

1. **start_silent.bat** - Silent launcher (no window)
2. **start_history_tracker_silent.vbs** - VBScript that runs Python hidden
3. **start_history_tracker.bat** - Original launcher (shows window)

## Quick Test

Double-click `start_silent.bat` - nothing should appear on screen, but the script will be running in the background.

To verify it's running:

- Open Task Manager (Ctrl+Shift+Esc)
- Look for `python.exe` process

## Add to Windows Startup

### Method 1: Startup Folder (Recommended)

1. Press `Win + R`
2. Type: `shell:startup`
3. Press Enter
4. Copy `start_silent.bat` into the opened folder
5. Restart your computer to test

### Method 2: Task Scheduler (More Control)

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task"
3. Name: `Browser History Logger`
4. Trigger: `When I log on`
5. Action: `Start a program`
6. Program: `C:\path\to\start_silent.bat` (use full path)
7. Finish and test by restarting

## Stopping the Silent Script

Since it runs hidden, to stop it:

### Option 1: Task Manager

1. Open Task Manager (Ctrl+Shift+Esc)
2. Find `python.exe`
3. Right-click → End Task

### Option 2: Command Line

```bash
taskkill /F /IM python.exe
```

### Option 3: PowerShell

```powershell
Get-Process python | Stop-Process -Force
```

## Checking if it's Running

```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

Or in Task Manager, look for `python.exe` process.

## Log Output (Optional)

If you want to see logs while running silently, modify `start_history_tracker_silent.vbs` to redirect output to a log file.

## Important Notes

- The script runs completely hidden - no window, no console
- It will continue running until you stop it or restart the computer
- Check the `browsing_history.db` file to verify it's collecting data
- Use `python browser_history_logger.py view` to see collected history

## Troubleshooting

If the silent script doesn't work:

1. **Test the regular version first:**

   ```
   start_history_tracker.bat
   ```

2. **Check Python is in PATH:**

   ```
   python --version
   ```

3. **Check virtual environment exists:**
   Look for `venv` folder in the directory

4. **Run VBScript directly:**

   ```
   wscript start_history_tracker_silent.vbs
   ```

5. **Enable logging (edit the VBScript):**
   Add before the last line:
   ```vbscript
   pythonCmd = pythonCmd & " > """ & ScriptDir & "\output.log"" 2>&1"
   ```
