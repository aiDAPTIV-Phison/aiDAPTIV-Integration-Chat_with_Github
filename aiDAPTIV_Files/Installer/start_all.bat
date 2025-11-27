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

SET "FLOW_FLAG=%PROJECT_ROOT%backend\flow_done.flag"


echo ===============================================
echo   Open WebUI Launcher
echo ===============================================
echo.

REM ---------------------------------------------
REM 1) PROMPT USER FOR GITHUB TOKEN
REM ---------------------------------------------
echo Please enter your GitHub Personal Access Token:
set /p GITHUB_TOKEN=Token: 

if "%GITHUB_TOKEN%"=="" (
    echo ERROR: Token cannot be empty.
    pause
    exit /b
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
START "MCP Server" "%MCP_PATH%"
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
START "Backend Server" "%BACKEND_PATH%"

echo Backend is running!
echo.
