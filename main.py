from _thread import start_new_thread
from difflib import SequenceMatcher
from re import search, findall
from time import sleep, strftime
from string import punctuation

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
        highlight_words = [cfg['username'].lower(), "bot", "robot", "chatbot"]
        for word in contents.split():
            removed_punctuation = word.translate(str.maketrans('', '', punctuation))
            removed_punctuation = removed_punctuation.lower()
            for check in highlight_words:
                if compare(check, removed_punctuation) > 0.58:
                    word = f'\033[{colors[2]}{word}\033[0{colors[i]}'
            contents_split += f"{word} "
        contents = "".join(contents_split)
        print(f"{strftime('[%I:%M %p]')} {username}{contents}\033[m")

    def status(self, i, *args):
        status_strings = [
            f"\n{cfg['username']} has connected\n",
            "Chat inactivity... (clearing memory)",
            "Connection dropped. Reconnecting...",
            f"""Reply is too similar to a previous message.
                Current: {args[0]}
                Previous: {args[1]}""",
            f"{args[0]} sent code {args[1]}."
        ]
        print(f"{strftime('[%I:%M %p]')} \u001B[1;34m{status_strings[i]}\u001B[m")
PrintMessage = PrintMessage()

def sendrequest(history):
    lines = [f"{cfg['chat_description']}\n\n"]
    for i in range(0, len(history), 2):
        lines.append(f"{history[i]}: {history[i + 1]}\n")
    lines.append(f"{cfg['username']}:")
    package = "".join(lines)
    request_data = {
        0: {
            "name": "api.eleuther.ai",
            "url": "https://api.eleuther.ai/completion",
            "json": {
                "context": package,
                "topP": 0.9,
                "temp": 0.9,
                "response_length": 40,
                "remove_input": True,
            }
        },
        1: {
            "name": "api-inference.huggingface.co",
            "url": "https://api-inference.huggingface.co/models/EleutherAI/gpt-j-6B",
            "json": {
                "inputs": package,
                "parameters": {
                    "use_cache": False,
                    "top_p": 0.9,
                    "temperature": 0.9,
                    "max_new_tokens": 40,
                    "return_full_text": False}
            }
        },
        2: {
            "name": "bellard.org",
            "url": "https://bellard.org/textsynth/api/v1/engines/gptj_6B/completions",
            "json": {
                "prompt": package,
                "temperature": 0.9,
                "top_k": 40,
                "top_p": 0.9,
                "seed": 0,
                "stream": False}
        }
    }
    for key, value in request_data.items():
        response = post(value["url"], json=value["json"])
        if response.status_code == 200:
            return parse(response)
        PrintMessage.status(4, value["name"], response.status_code)
    return None

def parse(response):
    cleaned_response = (f"""{cfg['username']}:{response.text.split('"')[1::2][1]}"""
                        .encode('ascii', errors="ignore")
                        .decode('unicode_escape', errors="ignore"))
    posts = findall(r'(.*?)\n', cleaned_response.replace("\n\n", "\n"))
    final_posts = []
    for post in enumerate(posts):
        username = post[1].split()[0][:-1].lower()
        message = ' '.join(post[1].split()[1:])
        if username != cfg['username'].lower():
            break
        final_posts += [message]
        if len(final_posts) > 1 and compare(final_posts[0], final_posts[1]) > 0.75:
            final_posts = [final_posts[0]]
    return final_posts

def on_message(wsapp, message):
    if "<message to" in message:
        username = findall('/([^"]*)"', message)[1]
        contents = search('<body>(.*)</body>', message).group(1)
        PrintMessage.chat(username, contents)
        if contents[:8] == ":sticker":
            contents = findall(r'e":"(.*?)"}', contents)[0]
        memory.extend([username, contents])
    elif "</stream:stream>" in message:
        PrintMessage.status(2, None, None)
        initialize()

def spam_test(previous, current, replying_to):
    previous.extend(replying_to)
    for x in enumerate(current):
        for y in enumerate(previous):
            if compare(x[1], y[1]) < 0.75:
                continue
            PrintMessage.status(3, x[1], y[1])
            return False
    return True

def read_chat():
    global thread_running
    thread_running = 1
    i = 0
    try:
        previous_responses = [""]
        while True:
            current_message = len(memory)
            while current_message == len(memory):
                i += 1
                sleep(1)
                if i % 60 == 0:
                    ping(wsapp)
                if i == cfg['inactivity_minutes'] * 60 and not memory:
                    del memory[:len(memory) - 2]
                    PrintMessage.status(1, None, None)
            i = 0

            if memory[-2] != cfg['username']:
                while True:
                    current_responses = sendrequest(memory)
                    if current_responses is None:
                        sleep(5)
                        continue
                    break
                if spam_test(previous_responses, current_responses, memory[-1]):
                    previous_responses = current_responses
                    for respond in enumerate(current_responses):
                        chatsend(wsapp, cfg, respond[1])
                        sleep(2 + len(respond[1]) / 10)
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
    PrintMessage.status(0, None, None)

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
