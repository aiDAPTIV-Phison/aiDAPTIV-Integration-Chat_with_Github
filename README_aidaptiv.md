# Installation of OpenWebUI + Github MCP with aiDAPTIV

## Pre-requisite 
1. You should have the aiDAPTIV server up and hosted on `http://localhost:8080/v1`.
2. You should log in to your GitHub account and obtain a personal access token [following this guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) or follow the guide specified in the below [section](#how-to-get-github-personal-access-token-pat).

## Setup
1. Navigate into the installer package.
2. Double click the `start_all.bat` script in the installer package.
3. It should have multiple command prompt terminal windows popping up.
4. Afterwards, wait for a few minutes for the application to initialize its states. 
5. In the "Backend" command prompt window, it should show "KV Cache Generated Successfully".
```
Waiting for 0 seconds, press a key to continue ...
Executing flow.py
KV Cache Generated Successfully!
```
If the installation is failed, then it would have message similar to this

```
API healthcheck ping failed, retrying in 15 seconds
API healthcheck ping failed, retrying in 15 seconds
API healthcheck ping failed, retrying in 15 seconds
API healthcheck ping failed, retrying in 15 seconds
API healthcheck ping failed, retrying in 15 seconds
The Open-WebUI backend cannot be connected. Terminating re-trying...
Connected URL: http://<HOST-GIVEN>:<PORT-GIVEN>/api/
```
6. If your installation is successful, open your browser (Google/Edge/etc.).
7. Type in `http://localhost:8001` to navigate to the application.
8. You should see a new chat being created called `Asking Github Repository (Example)`.
9. You may continue asking question from here or create a new chat to ask about another Github repository with accelerated inference speed.


## How to get Github Personal Access Token (PAT)

1. Click on your profile icon on the top right corner.
2. Go to `Setting`, you will be navigated to the setting page.
3. Then, find `Developer settings` and click on the button.
4. Expand the `Personal access tokens` menu, and click on the `Tokens (classic)`.
5. Click on the `Generate new token > Generate a new token (classic)`
6. Fill in your credentials details.
7. Type in your token name and check all the permission required (at least check the first item).
8. Click on `Generate token` button at the end of the page. 
9. You should be able to copy your token. 
10. Paste that into the installer command prompt windows when prompted a PAT.


## Notes
- If the execution of `flow.py` shows the following, it means that it found `Asking Github Repository (Example)` in the `open-webui`. So, it assumes that the KV Cache is already initialized. Thus, the installation is still success.

```
The KV Cache is already initialized, aborting...
```

- If the execution of `flow.py` shows installation failed (message below), then you may check if all the pre-requisites are fulfilled.

```
The Open-WebUI backend cannot be connected. Installation is failed. Terminating re-trying...\nConnected URL: http://{HOST}:{PORT}/api/
```
