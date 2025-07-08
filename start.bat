@echo off
:: Set UTF-8 encoding (doesn't fix emoji issue entirely, but helpful)
chcp 65001 >nul
title HawkBot - No Sleep Mode

:: Keep system awake using PowerShell (minimizes CPU, avoids sleep)
start powershell -WindowStyle Hidden -Command "while ($true) {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{SCROLLLOCK}'); Start-Sleep -Seconds 60}"

:: Navigate to bot directory
cd /d "C:\Users\hithe\OneDrive\Desktop\HAWK_JULY"

:: OPTIONAL: Activate virtual environment (uncomment if you use venv)
:: call venv\Scripts\activate.bat

:: Start the bot using safe UTF-8-compatible call (if emoji is removed or handled in Python)
python main.py

:: Pause to keep CMD open after execution
pause
