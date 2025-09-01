@echo off
title DnD Bot Controller

:: Name of your bot file
set "BOT_FILE=bot.py"

:: Unique window title for the bot terminal (used to kill the right cmd)
set "BOT_WINDOW_TITLE=DnD_Bot_Terminal"

:menu
cls
echo ================================
echo         DnD Bot Manager
echo ================================
echo.
echo [1] Start Bot
echo [2] Stop Bot
echo [3] Restart Bot
echo [4] Exit
echo.
set /p choice="Select an option: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" exit

goto menu

:start
echo Starting %BOT_FILE%...
start "DnD_Bot_Terminal" cmd /k "python %BOT_FILE%"
echo Bot started in a new terminal window. Press any key to return to menu.
pause >nul
goto menu

:stop
echo Stopping %BOT_FILE%...

:: Kill Python processes
taskkill /f /im python.exe >nul 2>&1

:: Kill the cmd window with the specific title
for /f "tokens=2 delims=," %%i in ('tasklist /v /fi "imagename eq cmd.exe" /fo csv ^| findstr "%BOT_WINDOW_TITLE%"') do (
    taskkill /f /pid %%i >nul 2>&1
)

echo Bot stopped and windows cleaned up. Press any key to return to menu.
pause >nul
goto menu

:restart
echo Restarting %BOT_FILE%...

:: Kill old bot
taskkill /f /im python.exe >nul 2>&1

:: Kill old terminal window by title
for /f "tokens=2 delims=," %%i in ('tasklist /v /fi "imagename eq cmd.exe" /fo csv ^| findstr "%BOT_WINDOW_TITLE%"') do (
    taskkill /f /pid %%i >nul 2>&1
)

timeout /t 1 >nul
start "DnD_Bot_Terminal" cmd /k "python %BOT_FILE%"
echo Bot restarted in a clean new window. Press any key to return to menu.
pause >nul
goto menu
