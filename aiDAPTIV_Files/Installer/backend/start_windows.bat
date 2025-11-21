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
SET "OPENAI_API_BASE_URL=http://localhost:8080/v1"
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
::"%PYTHON_EXE%" -m uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips '*' --workers %UVICORN_WORKERS% --ws auto
:: Start the server in background
start "" "%PYTHON_EXE%" -m uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --workers %UVICORN_WORKERS% --ws auto

:: Wait a few seconds for server to be ready
timeout /t 25

:: Run flow.py script
echo Executing flow.py
"%PYTHON_EXE%" flow.py
