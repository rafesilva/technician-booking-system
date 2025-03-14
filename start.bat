@echo off
echo Starting Technician Booking System

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python to run this application.
    pause
    exit /b 1
)

python start.py

if %ERRORLEVEL% neq 0 (
    echo An error occurred while running the application.
    pause
) 