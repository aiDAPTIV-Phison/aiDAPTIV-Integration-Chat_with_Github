@echo off
cd /d "%~dp0"

SET "PYTHON_EXE=%~dp0..\python\python.exe"
SET "GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security,experiments"

:: Load .env file if it exists
if exist "..\.env" (
    for /f "usebackq tokens=1,2 delims== " %%A in ("..\.env") do (
        set %%A=%%B
    )
)

"%PYTHON_EXE%" -c "import mcpo; mcpo.main()" --port 8000 -- "%~dp0github-mcp-server.exe" stdio
