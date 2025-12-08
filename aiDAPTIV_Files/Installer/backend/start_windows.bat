@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: >>> START: CUSTOM PYTHON PATH CONFIGURATION <<<
SET "PROJECT_ROOT=%~dp0"
SET "PYTHON_EXE=%PROJECT_ROOT%\..\python\python.exe"

:: ----------------------------
:: User-configurable environment
:: ----------------------------


SET "WEBUI_AUTH=False"

:: OpenAI API
SET "OPENAI_API_BASE_URL=http://localhost:13141/v1"
SET "OPENAI_API_KEY=EMPTY"

:: Tool server
SET "TOOL_SERVER_CONNECTIONS=[{"type": "openapi", "url": "http://localhost:8000", "spec_type": "url", "spec": "", "path": "openapi.json", "auth_type": "none", "key": "", "config": {"enable": true}, "info": {"id": "", "name": "github-server", "description": "Github MCP Server"}}]"
:: >>> END: CUSTOM PYTHON PATH CONFIGURATION <<<
:: Get the directory of the current script
SET "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%" || exit /b

:: Add conditional Playwright browser installation
IF /I "%WEB_LOADER_ENGINE%" == "playwright" (
    IF "%PLAYWRIGHT_WS_URL%" == "" (
        echo Installing Playwright browsers...
        "%PYTHON_EXE%" -m playwright install chromium
        "%PYTHON_EXE%" -m playwright install-deps chromium
    )

    "%PYTHON_EXE%" -c "import nltk; nltk.download('punkt_tab')"
)

SET "KEY_FILE=.webui_secret_key"
IF NOT "%WEBUI_SECRET_KEY_FILE%" == "" (
    SET "KEY_FILE=%WEBUI_SECRET_KEY_FILE%"
)


SET PORT=8001
SET HOST=localhost

IF "%UVICORN_WORKERS%"=="" SET UVICORN_WORKERS=1

SET "CORS_ALLOW_ORIGIN=http://localhost:5173,http://localhost:8001"
:: Start the server in background
powershell -WindowStyle Hidden -Command ^
  "Start-Process '%PYTHON_EXE%' -ArgumentList '-m uvicorn open_webui.main:app --host %HOST% --port %PORT% --workers %UVICORN_WORKERS% --ws auto' -WindowStyle Hidden"

:: Wait a few seconds for server to be ready
timeout /t 30

:: Full paths for safety
SET "FLOW_SCRIPT=%PROJECT_ROOT%flow.py"

:: Run flow.py and redirect output
echo Executing flow.py...
"%PYTHON_EXE%" "%FLOW_SCRIPT%"

SET "FLOW_EXIT=%ERRORLEVEL%"

:: Check if flow.py failed
IF NOT "%FLOW_EXIT%"=="0" (
    echo.
    echo ===============================================
    echo  ERROR: flow.py failed with exit code %FLOW_EXIT%
    echo  The server did NOT start successfully.
    echo ===============================================
    pause
    exit /b %FLOW_EXIT%
)

REM ---------------------------------------------
REM 5) OPEN BROWSER AUTOMATICALLY
REM ---------------------------------------------
echo Opening browser...
start "" "http://localhost:%BACKEND_PORT%"

echo.
echo ===============================================
echo  All components are now running successfully!
echo ===============================================
pause