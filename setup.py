import requests
import json
import base64


def generate_config():
    username = input("Username: ")
    password = input("Password: ")
    with open("config.py", "w") as f:
        information = '''
"""
! Do not edit the general account data, or you will be unable to connect to chat !

### Bot settings ###
--chat_length
How many chat messages to remember before clearing the memory. The eleuther.ai API has a limit to how much
text can be sent to it per request, so do not set this value too high.

--inactivity_minutes
How many minutes of chat inactivity to wait before clearing the memory.

--chat_description
This gives context to the bot about what it is looking at. Tweaking it will make it might give better results.

"""
'''

        session = requests.Session()
        url = f'utf8=%E2%9C%93&authenticity_token=yMPnJJN9Pcgr6zcq4fmZ5LH3SWgrvimD4X%2BMnIk%2FH8X5dr4I9ohwsaa1zsE1vY8dYDvzHogimJ0BRZRbbViYAQ%3D%3D&from_welcome_box=true&username={username}&password={password}&remember_me=true'
        session.post("https://www.kongregate.com/session", data=url)
        data = session.get("http://www.kongregate.com/accounts/status?game_id=287709")
        accountdata = json.loads(data.text)
        token = str(base64.b64encode((f'{accountdata["chat_username"].lower()}@of1.kongregate.com\u0000'
                                      f'{accountdata["chat_username"].lower()}\u0000''{'f'\"k\":\"'
                                      f'{accountdata["chat_password"]}\"''}').encode("utf-8")), "utf-8")

        a = "\&quot;"
        configuration = f'''

### General account data ###
chat_username = '{accountdata["chat_username"]}'
user_vars_sig = '{accountdata["user_chat_hash"]['user_vars_sig']}'
user_vars = '{str(accountdata["user_chat_hash"]['user_vars']).replace('"', a)}'
extra_vars = '{(str(accountdata["user_chat_hash"]['extra_vars'])[:-1]+"'}").replace("'", "&quot;").replace(" ", "&quot;")}'
auth_token = '{token}'

### Bot settings ###
chat_length = 6
inactivity_minutes = 5
chat_description = '{accountdata["chat_username"]} is a roleplayer.'

'''

        f.write(information + configuration)