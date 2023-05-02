#!/usr/bin/python3
import yaml, os, psycopg2, requests, sys
from discord_webhook import DiscordWebhook, DiscordEmbed

# https://twitter.com/omidxrz

# TODO
# Add Telegram Notification



# Read Config 
def Config():
    ConfigFile = os.path.dirname(os.path.abspath(__file__)) + '/config.yaml'
    if not os.path.exists(ConfigFile):
        print('[-] Error: ConfigNotFound.')
        sys.exit()

    with open(ConfigFile, "r") as _:
        try:
            config = yaml.safe_load(_)
        except Exception as err:
            print(f'[-] Error: {err}')
        return config
config = Config()


# Database Function
def database():
    try:
        conn = psycopg2.connect(
            host=config['Database'][0],
            port=config['Database'][1],
            database=config['Database'][2],
            user=config['Database'][3],
            password=config['Database'][4])
    except Exception as err:
        print("[-] I am unable to connect to the database :(") 
        print(f'[-] Error: {err}')
        return
    return conn


def CreateTables():
    conn = database()
    query = conn.cursor()
    conn.autocommit = True 
    
    try:
        query.execute("CREATE TABLE Programs (id serial PRIMARY KEY, name VARCHAR(255), platform VARCHAR(255), submission VARCHAR(255), bounty BOOLEAN NOT NULL);")
        query.execute("CREATE TABLE targets ( id serial PRIMARY KEY, name VARCHAR(10000), type VARCHAR(255), scope BOOLEAN NOT NULL, program_id INTEGER);")
        query.execute("alter table targets add constraint fk_target foreign key (program_id) REFERENCES programs (id);")

    except Exception as err:
        print(f"[+] Info: {err}",end='')
        return
    query.close()
    print("[+] Tables Created.")

# Send To Discord Function 
def discord(title, description):

    # print(Name)
    channels = config['Discord']
    for Channel in channels:
        webhook = DiscordWebhook(
            url= Channel,
            rate_limit_retry=True)
        embed = DiscordEmbed(
            title=title,
            description=description,
            color='65535')
        webhook.add_embed(embed)
        response = webhook.execute()


def ChcekPrograms(Name, Submission, Platform, Bounty):
    conn = database()
    select_query = conn.cursor()
    try:
        select_query.execute("SELECT * FROM Programs WHERE name=%s AND platform=%s;", (Name, Platform,))
    except Exception as err:
        if 'psycopg2.errors.UndefinedTable:' in err:
            CreateTables()
        print(f"Error: {err}")
        return 
    
    # Insert to Database
    # ChangeTitle = ""
    fetch = select_query.fetchone()
    if fetch == None:
        try:
            insert_query = conn.cursor()
            insert_query.execute("INSERT INTO Programs(name,platform,submission,bounty)VALUES(%s, %s, %s, %s) returning id ;", (Name, Platform, Submission, Bounty))
            conn.commit() 
            id = insert_query.fetchone()[0]
            insert_query.close()
            ChangeTitle = f"[+] New Program"
            description = f'**Program: **{Name}\n**Submission: **{Submission}\n**Bounty: **{Bounty}\n**Platform:** {Platform}\n'
            discord(title=ChangeTitle ,description=description)
            print(f"[+] {ChangeTitle}: {Name}")
        except Exception as err:
            print(f"Error: {err}");return

    else:
        if (fetch[4] == False and Bounty == True):
            ChangeTitle = "[+] Change Program From VDP To BBP"
            description = f'**Program: **{Name}\n**Submission: **{Submission}\n**Bounty: **{Bounty}\n**Platform:** {Platform}\n'
            discord(title=ChangeTitle ,description=description)
            print(f"[+] {ChangeTitle}: {Name}")
        elif (fetch[4] == True and Bounty == False):
            ChangeTitle = "[-] Change Program From BBP To VDP"
            description = f'**Program: **{Name}\n**Submission: **{Submission}\n**Bounty: **{Bounty}\n**Platform:** {Platform}\n'
            discord(title=ChangeTitle ,description=description)
            print(f"[+] {ChangeTitle}: {Name}")
        update_query = conn.cursor()
        try:
            update_query.execute("UPDATE Programs SET bounty = %s WHERE id = %s;", (Bounty, fetch[0]))
            conn.commit()
            id = fetch[0]
            update_query.close()
            
        except Exception as err:
            print(f"Error: {err}");return
    return id

def CheckTargets(Title, Type, Scope, PK):
    # print(Title)
    conn = database()
    select_query = conn.cursor()

    # Check Target Exist OR !Exist.
    try:
        select_query.execute("SELECT * FROM Targets WHERE name=%s AND type=%s AND program_id=%s;", (Title, Type, PK))
    except Exception as err:
        print(f"Error: {err}")
        return 
    
    fetch = select_query.fetchone()
    if fetch == None:
        # print(Title, Type, Scope, PK)
        # If Exist 
        try:
            # Add into Database
            insert_query = conn.cursor()
            insert_query.execute("INSERT INTO targets(name, type, scope, program_id)VALUES(%s, %s, %s, %s) returning id ;", (Title, Type, Scope, PK))
            conn.commit() 
            # id = insert_query.fetchone()[0]
            insert_query.close()

            # Get Program Name & Submission

            getProgram = conn.cursor()
            getProgram.execute("SELECT * FROM Programs WHERE id=%s ;", (PK,))
            ProgramsDetails = getProgram.fetchone()
            conn.commit()
            getProgram.close()
            ChangeTitle = "[+] New Target"
            description = f'**Target: **{Title}\n**Type: **{Type}\n**Scope: **{Scope}\n**Bounty:** {ProgramsDetails[4]}\n**Platform:** {ProgramsDetails[2]}\n**Program:** {ProgramsDetails[3]}'

            # Send To Discord
            discord(title=ChangeTitle ,description=description)
            
            print(f"[+] {ChangeTitle}: {Title}")
        except Exception as err:
            print(f"Error: {err}")
            return
    else:
        # !Exist
        try:
            getProgram = conn.cursor()
            getProgram.execute("SELECT * FROM Programs WHERE id=%s ;", (fetch[4],))
            ProgramsDetail = getProgram.fetchone()
            getProgram.close()
        except Exception as err :
            print(f"Error: {err}")

        if (fetch[3] == True and Scope == False):
            ChangeTitle = "[-] Target is out of Scope Now."
            description = f'**Target: **{Title}\n**Type: **{Type}\n**Scope: **{Scope}\n**Bounty:** {ProgramsDetail[4]}\n**Platform:** {ProgramsDetail[2]}\n**Program:** {ProgramsDetail[3]}'
            discord(title=ChangeTitle ,description=description)
            print(f"[+] {ChangeTitle}: {Title}")
        
        elif (fetch[3] == False and Scope == True):
            ChangeTitle = "[+] Target is in Scope Now."
            description = f'**Target: **{Title}\n**Type: **{Type}\n**Scope: **{Scope}\n**Bounty:** {ProgramsDetail[4]}\n**Platform:** {ProgramsDetail[2]}\n**Program:** {ProgramsDetail[3]}'
            discord(title=ChangeTitle ,description=description)
            print(f"[+] {ChangeTitle}: {Title}")
        # Update Target Changes.
        try:
            update_query = conn.cursor()
            update_query.execute("UPDATE targets SET scope = %s WHERE id = %s;", (Scope, fetch[0]))
            conn.commit()
            update_query.close()
        except Exception as err:
            print(f"Error: {err}");return
        
        
def bugcrowd():

    BugcrowdURL = 'https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/bugcrowd.json'
    Response = requests.request('GET', BugcrowdURL)
    try:
        Response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return

    for Program in Response.json():
        Name = Program['name']
        Submission = f"https://bugcrowd.com{Program['report_path']}"
        Platform = 'bugcrowd'
        try:
            if Program["min_rewards"]:
                Bounty = True
        except:
            Bounty = False

        PK = ChcekPrograms(Name, Submission, Platform, Bounty)

        try:
            targets = Program["target_groups"]
            for target in targets:

                if target["in_scope"] == True:
                    for asset in target["targets"]:
                        target_name = asset["name"]
                        type = asset["category"]
                        scope = True
                        CheckTargets(target_name, type, scope, PK)
                        # return

                elif target["in_scope"] == False:

                    for asset in target["targets"]:
                        target_name = asset["name"]
                        type = asset["category"]
                        scope = False
                        CheckTargets(target_name, type, scope, PK)
                        # return
        except Exception as err:
            print(err)
    print('[+] Bugcrowd Programs Updated. ✅')


def hackerone():
    HackeroneURL = "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/hackerone.json"
    Response = requests.request('GET', HackeroneURL)
    # Hackerone = Response.json()
    # write_to_file("hackerone_data.json", hackerOne.text)
    for program in Response.json():
        handle = program['attributes']['handle']
        Name = program['attributes']['name']
        Submission = f'https://hackerone.com/{handle}'
        SubmissionState = program['attributes']['submission_state']
        Platform = 'hackerone'
        if SubmissionState == 'paused':
            BugBounty = False
        else:
            BugBounty = program['attributes']['offers_bounties']
        if Name == 'Agoric':
            BugBounty = True
        else:
            BugBounty = BugBounty
        # print(Name, Submission, Platform, BugBounty)
        PK = ChcekPrograms(Name, Submission, Platform, BugBounty)
        for target in program['relationships']['structured_scopes']['data']:
            Title = target['attributes']['asset_identifier']
            type = target['attributes']['asset_type']
            if target['attributes']['eligible_for_bounty'] == True and target['attributes']['eligible_for_submission'] == True:
                Scope = True
            else:
                Scope = False
            CheckTargets(Title, type, Scope, PK)
    print('Hackerone Programs Updated. ✅')


# def telegram(data):
    # Pass

def main():
    # Connect To The Database & Create Tables
    database()
    CreateTables()
    
    
    # Start Parse Bugcrowd
    bugcrowd()
    # Start Parse Hackerone
    hackerone()
    # # Start Parse Intigriti

if __name__=="__main__":
    main()