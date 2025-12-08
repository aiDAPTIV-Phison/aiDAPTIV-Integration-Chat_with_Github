# aiDAPTIV Chat With Github (OpenWebUI + Github MCP) User Guide 
## Overview 
This guide explains how to install and use OpenWebUI, GitHub MCP, and aiDAPTIV together — including how to see KV Cache reuse effects during application startup.
You will learn how to set up the environment, build & reuse KV Cache, use GitHub MCP tools, and troubleshoot common issues.

## Chapter 1: Installation and Setting
### Installation Steps
#### Prerequisites
1. You should have the aiDAPTIV server up and hosted on `http://localhost:13141/v1`.
2. You should log in to your GitHub account and obtain a personal access token [following this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) or follow the guide specified in the below [section](#how-to-get-github-personal-access-token-pat).

#### How to get Github Personal Access Token (PAT)

1. Click on your profile icon on the top right corner.
2. Go to `Setting`, you will be navigated to the setting page.
3. Then, find `Developer settings` and click on the button.
4. Expand the `Personal access tokens` menu, and click on the `Tokens (classic)`.
5. Click on the `Generate new token > Generate a new token (classic)`
6. Fill in your credentials details.
7. Type in your token name and check all the permission required (at least check the first item).
8. Click on `Generate token` button at the end of the page. 
9. You should be able to copy your token. 
10. Paste that into the installer command prompt windows when prompted for a PAT.


#### Setup
1. Navigate to the installer package directory.
2. Double-click the `start_all.bat` script in the installer package.
3. It should have 1 terminal window popping up requesting your Github PAT. 
   - Enter your PAT when prompted 
   - If you have previously provided a PAT, an `.env` file will be used automatically, and you will not be prompted again during future launches.


## Chapter 2: How to Use?
### Usage Workflow
1. **Initial Setup**
   - Wait for the application to finish initializing its components(OpenWebUI backend and Github MCP server). Once initialization completes, your browser will automatically open the `Chat With GitHub` interface.
   - If the setup is successful, a new chat titled `Asking Github Repository (Example)` will appear automatically.
   - You may continue asking question in this chat or create a new one to ask about another Github repository with accelerated inference speed (via KV Cache reuse).
   - If you want to ask questions, you must **enable the Github tool use** before starting inference:
     - At the center of your page, you will see a chat box. Near the left bottom corner of the chat box, you can locate an icon beside "+", click on the button (Integrations)
     - Click on `Tools >`.
     - Toggle ON the `github-mcp-server` tool so that the Agent can acess Github Repository details.
   - To terminate or stop the application, double-click the `stop_all.bat` script in your installer directory. 

2. **Basic Operation**
- **Search repositories**
  - Use example GitHub repositories (or your own) to query repository details through the MCP integrations.
- **Repository Management**
  - Depending on the permission granted in your PAT, you can explore additional GitHub MCP features such as: 
    - Creating repositories
    - Creating pull requests
    - Pushing and pulling content
    - Other GitHub automation features

## Chapter 3: Troubleshooting
### Issue 1: No Github tool available 
- **Symptoms**
    - No Github tool available in the chat box
    - **Cause**: Github PAT was expired/ incorrect
-  **Solution**
   -  Obtain a new Github PAT [following this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) or follow the guide specified in the above [section](#how-to-get-github-personal-access-token-pat)

