# Watch Tower
Simple Python Script for Tracking Bug Bounty Programs.

This script collects data from this [Repository](https://github.com/Osb0rn3/bugbounty-targets) This script collects data from this repository and sends us a notification if it changes.

Types Of Notification Supported: 
- New Program.
- Change Program From RDP To VDP. 
- Change Program From VDP To RDP. 
- New Targets.
- Add Target Into The Scope.
- Delete Target From Scope. 



## Install
1. Download or clone this GitHub repo
```
git clone https://github.com/omidxrz/Watch-Tower
```
2. Install requirements with:
```
pip3 install -r requirements.txt
```
3. Run Postgres With Docker 
```
docker-compose up -d 
```
4. Change Webhook
```
Discord:
  - 'Weboohk1'
  - 'Webhook2'
```
- You Can Add Multi Tokens
5. Run First time With InActive Mode.(It does not send notifications)
```
# inActive Mode
python3 main.py inactive 
# Run Active Mode
python3 main.py  
```
- if you see this error **pg_config executable not found.** then try this :
```
apt install libpq-dev
```


### Crontab 
1. Give permission to Script
```
chmod +x main.py
```
2. Set Crontab For Run Script Every 15M 
```
*/15 * * * * /usr/bin/python3 /PATH_SCRIPT/main.py
```
