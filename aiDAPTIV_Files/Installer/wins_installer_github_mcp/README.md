# Github-MCP-Server Setup

## Go Installation
If you have not already installed Go, download it here
`https://go.dev/doc/install`

## Windows Installer Packaging

- Clone the Github Repository of `github-mcp-server` using the following command

```bash
git clone https://github.com/github/github-mcp-server.git
```

- Build a Windows Executable with the following command

```bash
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o github-mcp-server.exe ./cmd/github-mcp-server
```

## Obtain the Github Personal Access Token
- Log in to your GitHub account and create a Personal Access Token (PAT) by following the guide (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## Run the MCP Server
- Navigate to the directory where your `github-mcp-server.exe` is stored
```bash
cd mcp-server-pkg
```

- Set the environment variables (GitHub Personal Access Token and the toolsets you want)
```bash
set GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_TOKEN
set GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security,experiments
```

- Run the MCP server through MCPO
```bash
uvx mcpo --port 8000 -- github-mcp-server.exe stdio
```
