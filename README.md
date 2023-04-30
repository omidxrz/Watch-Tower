# Watch Tower
Simple Python Script for Tracking Bug Bounty Programs.

## Install
1. Download or clone this GitHub repo
```
git clone 
```
2. Install requirements with:
```
pip3 install requirements.txt
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
5. Run Main Script 
```
python3 main.py 
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
