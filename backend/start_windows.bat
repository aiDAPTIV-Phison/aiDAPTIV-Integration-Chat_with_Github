@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: >>> START: CUSTOM PYTHON PATH CONFIGURATION <<<
SET "PROJECT_ROOT=%~dp0"
echo "My proj root :%PROJECT_ROOT%"
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
SET "WEBUI_SECRET_KEY=%WEBUI_SECRET_KEY%"
SET "WEBUI_JWT_SECRET_KEY=%WEBUI_JWT_SECRET_KEY%"

:: Check if WEBUI_SECRET_KEY and WEBUI_JWT_SECRET_KEY are not set
IF "%WEBUI_SECRET_KEY% %WEBUI_JWT_SECRET_KEY%" == " " (
    echo Loading WEBUI_SECRET_KEY from file, not provided as an environment variable.

    IF NOT EXIST "%KEY_FILE%" (
        echo Generating WEBUI_SECRET_KEY
        :: Generate a random value to use as a WEBUI_SECRET_KEY in case the user didn't provide one
        SET /p WEBUI_SECRET_KEY=<nul
        FOR /L %%i IN (1,1,12) DO SET /p WEBUI_SECRET_KEY=<!random!>>%KEY_FILE%
        echo WEBUI_SECRET_KEY generated
    )

    echo Loading WEBUI_SECRET_KEY from %KEY_FILE%
    SET /p WEBUI_SECRET_KEY=<%KEY_FILE%
)

:: Execute uvicorn
SET "WEBUI_SECRET_KEY=%WEBUI_SECRET_KEY%"
IF "%UVICORN_WORKERS%"=="" SET UVICORN_WORKERS=1

SET "CORS_ALLOW_ORIGIN=http://localhost:5173,http://localhost:8001"
::"%PYTHON_EXE%" -m uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --forwarded-allow-ips '*' --workers %UVICORN_WORKERS% --ws auto
:: Start the server in background
echo "Host: %HOST%"
echo "Port: %PORT%"
start "" "%PYTHON_EXE%" -m uvicorn open_webui.main:app --host "%HOST%" --port "%PORT%" --workers %UVICORN_WORKERS% --ws auto

:: Wait a few seconds for server to be ready
timeout /t 15

:: Run flow.py script
echo Executing flow.py
"%PYTHON_EXE%" flow.py
