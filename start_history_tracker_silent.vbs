Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
ScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
WshShell.CurrentDirectory = ScriptDir

' Check if virtual environment exists and build command
Dim pythonCmd
If CreateObject("Scripting.FileSystemObject").FolderExists(ScriptDir & "\venv\Scripts") Then
    ' Use virtual environment
    pythonCmd = """" & ScriptDir & "\venv\Scripts\python.exe"" """ & ScriptDir & "\browser_history_logger.py"""
ElseIf CreateObject("Scripting.FileSystemObject").FolderExists(ScriptDir & "\..\venv\Scripts") Then
    ' Use parent directory virtual environment
    pythonCmd = """" & ScriptDir & "\..\venv\Scripts\python.exe"" """ & ScriptDir & "\browser_history_logger.py"""
Else
    ' Use system Python
    pythonCmd = "python """ & ScriptDir & "\browser_history_logger.py"""
End If

' Run the command hidden (0 = hidden window, False = don't wait for it to complete)
WshShell.Run pythonCmd, 0, False
