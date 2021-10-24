from _thread import start_new_thread
from difflib import SequenceMatcher
from re import search, findall
from time import sleep, strftime

from requests import post
from websocket import WebSocketApp

from messages import ping, chatsend, connect
from setup import generate_config

thread_running = 0
memory = []

while True:
    try:
        import config
        cfg = {
            "username": config.chat_username,
            "token": config.auth_token,
            "sig": config.user_vars_sig,
            "vars": config.user_vars,
            "extra": config.extra_vars,
            "chat_length": config.chat_length,
            "inactivity_minutes": config.inactivity_minutes,
            "chat_description": config.chat_description
        }
    except:
        print("No config file detected. Please enter your Kongregate account details...")
        generate_config()
        continue
    break

def timestamp():
    return strftime("[%I:%M %p] ")

def compare(string1, string2):
    return SequenceMatcher(a=string1, b=string2).ratio()

class PrintMessage:
    @staticmethod
    def chat(username, contents):
        #blue, white, highlight
        colors = [';36m', ';97m', '46;97m']
        i = 0 if username == cfg['username'] else 1
        username = f'\033[1{colors[i]}{username}: \033[0{colors[i]}'
        contents_split = contents.split()
        for i2 in range(len(contents_split)):
            if compare(contents_split[i2].lower(), cfg['username'].lower()) > 0.58\
                    or contents_split[i2].lower() == "bot":
                    contents_split[i2] = f'\033[{colors[2]}{contents_split[i2]}\033[0{colors[i]}'
        contents = " ".join(contents_split)
        print(timestamp() + username + contents + '\033[m')

    status_strings = [
        f"{cfg['username']} has connected",
        "Chat inactivity... (clearing memory)",
        "Connection dropped. Reconnecting..."
    ]

    def status(self, i):
        print(f"\n{timestamp()}\u001B[1;34m{self.status_strings[i]}\n\u001B[m")
PrintMessage = PrintMessage()

def sendrequest(history):
    lines = [f"{cfg['chat_description']}\n\n"]
    for i in range(0, len(history), 2): lines.append(f"{history[i]}: {history[i + 1]}\n")
    lines.append(f"{cfg['username']}:")
    package = "".join(lines)
    response = post("https://api.eleuther.ai/completion", json={
        "context": package,
        "topP": 0.9,
        "temp": 1.5,
        "response_length": 40,
        "remove_input": True}, )
    if response.status_code == 200:
        return parse(response.text.encode('ascii', errors="ignore").decode('unicode_escape'))

def parse(r):
    first_response = findall(r'":"(.*?)\n', r)[0].strip()
    usernames = findall(r'\n(.*?):', r)
    messages = findall(r': (.*?)\n', r)
    for i in range(len(usernames)):
        if usernames[i] != cfg['username']:
            messages = messages[:i]
            messages.insert(0, first_response)
            break
    if messages:
        try:
            if compare(messages[0], messages[1]) > 0.8: messages = messages[0]
        except: pass
        return messages

def on_message(wsapp, message):
    #print(message)
    if "<message to" in message:
        username = findall('/([^"]*)"', message)[1]
        contents = search('<body>(.*)</body>', message).group(1)
        PrintMessage.chat(username, contents)
        if contents[0:8] == ":sticker": contents = findall(r'e":"(.*?)"}', contents)[0]
        memory.extend([username, contents])
    elif "</stream:stream>" in message: PrintMessage.status(2); initialize()

def read_chat():
    global thread_running
    thread_running = 1
    i = 0
    try:
        previous_response = ''
        while True:
            current_message = len(memory)
            while current_message == len(memory):
                i += 1
                sleep(1)
                if i % 60 == 0: ping(wsapp)
                if i == cfg['inactivity_minutes'] * 60 and not memory:
                    del memory[:len(memory)-2]
                    PrintMessage.status(1)
            i = 0

            if memory[-2] != cfg['username']:
                while True:
                    responses = sendrequest(memory)
                    if responses is None:
                        sleep(5)
                        continue
                    break
                if (compare(responses[0], memory[-1]) < 0.8 and
                    compare(previous_response, responses[-1]) < 0.8):
                    for i2 in range(len(responses)): chatsend(wsapp, cfg, responses[i2]); sleep(1)
                    previous_response = responses[-1]
                    if len(memory) > cfg['chat_length']: del memory[:len(memory)-2]
    except Exception as error:
        # debugging purposes
        print(f"{type(error).__name__} at line {error.__traceback__.tb_lineno}: {error}")
        #print("responses: ", responses)
        #print("memory: ", memory)
        thread_running = 0
        initialize()

def on_open(wsapp):
    connect(wsapp, cfg)
    PrintMessage.status(0)

def initialize():
    global thread_running
    if thread_running == 0: start_new_thread(read_chat, ())
    wsapp.close()
    wsapp.run_forever()

wsapp = WebSocketApp("wss://chat-proxy.kongregate.com/?sid=c10a854d-9e88-42e7-acd6-4f64a894a318&svid=747c5705-f640-48f2-9be0-03f0d6d3fe51&wsr=false&wss=false&ca=0&wc=0&bc=0&tc=0&sr=0&ss=0&pb=true",
                     on_message=on_message,
                     on_open=on_open)
initialize()