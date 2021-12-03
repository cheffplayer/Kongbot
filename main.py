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

def compare(string1, string2):
    return SequenceMatcher(a=string1, b=string2).ratio()

class PrintMessage:
    @staticmethod
    def chat(username, contents):
        #blue, white, highlight
        colors = [';36m', ';97m', '46;97m']
        i = 0 if username == cfg['username'] else 1
        username = f'\033[1{colors[i]}{username}: \033[0{colors[i]}'
        contents_split = []
        for i2, word in enumerate(contents.split()):
            if (compare(word.lower(), cfg['username'].lower()) > 0.58
                    or word.lower() == "bot"):
                word = f'\033[{colors[2]}{word}\033[0{colors[i]}'
            contents_split += f"{word} "
        contents = "".join(contents_split)
        print(f"{strftime('[%I:%M %p]')} {username}{contents}\033[m")

    status_strings = [
        f"{cfg['username']} has connected",
        "Chat inactivity... (clearing memory)",
        "Connection dropped. Reconnecting..."
    ]

    def status(self, i):
        print(f"\n{strftime('[%I:%M %p]')} \u001B[1;34m{self.status_strings[i]}\n\u001B[m")
PrintMessage = PrintMessage()

def sendrequest(history):
    lines = [f"{cfg['chat_description']}\n\n"]
    for i in range(0, len(history), 2):
        lines.append(f"{history[i]}: {history[i + 1]}\n")
    lines.append(f"{cfg['username']}:")
    package = "".join(lines)
    response = post("https://api.eleuther.ai/completion", json={
        "context": package,
        "topP": 0.9,
        "temp": 0.7,
        "response_length": 40,
        "remove_input": True}, )
    if response.status_code != 200:
        return None
    return parse(f"{cfg['username']}:{response.text[20:][:-3]}"
                 .encode('ascii', errors="ignore")
                 .decode('unicode_escape'))

def parse(r):
    posts = findall(r'(.*?)\n', r.replace("\n\n", "\n"))
    final_posts = []
    for post in enumerate(posts):
        username = post[1].split()[0][:-1].lower()
        message = ' '.join(post[1].split()[1:])
        if username != cfg['username'].lower():
            break
        final_posts += [message]
        if len(final_posts) > 1 and compare(final_posts[0], final_posts[1]) > 0.80:
            final_posts = [final_posts[0]]
    return final_posts

def on_message(wsapp, message):
    if "<message to" in message:
        username = findall('/([^"]*)"', message)[1]
        contents = search('<body>(.*)</body>', message).group(1)
        PrintMessage.chat(username, contents)
        if contents[0:8] == ":sticker":
            contents = findall(r'e":"(.*?)"}', contents)[0]
        memory.extend([username, contents])
    elif "</stream:stream>" in message:
        PrintMessage.status(2)
        initialize()

def read_chat():
    global thread_running
    thread_running = 1
    i = 0
    try:
        while True:
            current_message = len(memory)
            while current_message == len(memory):
                i += 1
                sleep(1)
                if i % 60 == 0:
                    ping(wsapp)
                if i == cfg['inactivity_minutes'] * 60 and not memory:
                    del memory[:len(memory) - 2]
                    PrintMessage.status(1)
            i = 0

            if memory[-2] != cfg['username']:
                while True:
                    responses = sendrequest(memory)
                    if responses is None:
                        sleep(5)
                        continue
                    break
                if compare(memory[-1], responses[0]) < 0.8:
                    for response in enumerate(responses):
                        chatsend(wsapp, cfg, response[1])
                        sleep(1)
                    if len(memory) > cfg['chat_length']:
                        del memory[:len(memory) - 2]
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
    if thread_running == 0:
        start_new_thread(read_chat, ())
    wsapp.close()
    wsapp.run_forever()

wsapp = WebSocketApp("wss://chat-proxy.kongregate.com/?sid=c10a854d-9e88-42e7-acd6-4f64a894a318&svid=747c5705-f640-48f2-9be0-03f0d6d3fe51&wsr=false&wss=false&ca=0&wc=0&bc=0&tc=0&sr=0&ss=0&pb=true",
                     on_message=on_message,
                     on_open=on_open)
initialize()
