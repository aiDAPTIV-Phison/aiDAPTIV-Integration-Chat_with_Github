@echo off
echo Stopping Open WebUI, MCP server, and backend...

:: Stop OpenWebUI Backend (uvicorn server)
taskkill /IM python.exe /F >nul 2>&1

:: Kill MCP Github server
taskkill /IM github-mcp-server.exe /F >nul 2>&1

echo Done.
