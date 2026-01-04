@echo off
REM Silent Browser History Logger Launcher
REM Runs without showing any window - Perfect for Windows Startup

REM Change to script directory
cd /d "%~dp0"

REM Launch using VBScript (runs hidden)
wscript.exe "%~dp0start_history_tracker_silent.vbs"
