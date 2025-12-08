@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM Determine root folder (aiDAPTIV-Integration-Chat_with_Github)
SET "PROJECT_ROOT=%~dp0\"
SET "ENV_FILE=%PROJECT_ROOT%.env"

REM MCP folder
SET "MCP_PATH=%PROJECT_ROOT%wins_installer_github_mcp\run_mcp.bat"
ECHO "%MCP_PATH%"

REM Backend server
SET "BACKEND_PATH=%PROJECT_ROOT%backend\start_windows.bat"

REM ==== MCP port ====
SET "MCP_PORT=8000"

REM ==== Backend port ====
SET "BACKEND_PORT=8001"

REM Python executable
SET "PYTHON_EXE=%PROJECT_ROOT%python\python.exe"

echo ===============================================
echo   Open WebUI Launcher
echo ===============================================
echo.

REM ---------------------------------------------
REM 1) LOAD EXISTING PAT FROM .env IF AVAILABLE
REM ---------------------------------------------
set "GITHUB_TOKEN="

if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
        if /i "%%A"=="GITHUB_PERSONAL_ACCESS_TOKEN" (
            set "GITHUB_TOKEN=%%B"
        )
    )
)

REM ---------------------------------------------
REM 2) PROMPT USER IF PAT IS MISSING OR EMPTY
REM ---------------------------------------------
:ASK_PAT
REM Prompt user for token if it's empty
if "%GITHUB_TOKEN%"=="" (
    set /p GITHUB_TOKEN=Please enter your GitHub Personal Access Token: 
)

REM Check if empty
if "%GITHUB_TOKEN%"=="" (
    echo ERROR: Token cannot be empty.
    echo.
    goto ASK_PAT
)


REM ---------------------------------------------
REM 3) VALIDATE PAT USING PYTHON
REM ---------------------------------------------
"%PYTHON_EXE%" -c "import os, requests; token=os.environ.get('GITHUB_TOKEN') or '%GITHUB_TOKEN%'; r=requests.get('https://api.github.com/user', headers={'Authorization':f'token {token}'}); exit(0 if r.status_code==200 else 1)"


IF ERRORLEVEL 1 (
    echo GitHub token is invalid. Please try again.
    set "GITHUB_TOKEN="
    goto ASK_PAT
)


REM ---------------------------------------------
REM 2) WRITE .env FILE FOR MCP SERVER
REM ---------------------------------------------
echo Writing .env file to:
echo    %ENV_FILE%
echo.

(
    echo GITHUB_PERSONAL_ACCESS_TOKEN=%GITHUB_TOKEN%
    echo GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security,experiments
) > "%ENV_FILE%"

echo .env file updated successfully!
echo.

REM ---------------------------------------------
REM 3) START MCP SERVER
REM ---------------------------------------------
echo Starting MCP Server...
start "" /b /min "%MCP_PATH%" >nul 2>&1

echo Waiting for MCP to start on port %MCP_PORT% ...

:WAIT_FOR_MCP
timeout /t 1 >nul
netstat -ano | find ":%MCP_PORT% " >nul
IF ERRORLEVEL 1 goto WAIT_FOR_MCP

echo MCP is running!
echo.

REM ---------------------------------------------
REM 4) START BACKEND SERVER
REM ---------------------------------------------
echo Starting Backend Server...
start "" /b /min "%BACKEND_PATH%" >nul 2>&1

echo Backend is running!
echo.
