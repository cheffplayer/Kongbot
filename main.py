from threading import Thread
from difflib import SequenceMatcher
from re import search, findall
from time import sleep, strftime, mktime
from string import punctuation
from json import dumps, loads
from base64 import b64decode
from datetime import datetime

from requests import Session
from websocket import WebSocketApp

from messages import ping, chatsend, connect
from setup import generate_config

session = Session()

while True:
    try:
        import config

        cfg = {
            "username": config.chat_username,
            "token": config.auth_token,
            "sig": config.user_vars_sig,
            "vars": config.user_vars,
            "extra": config.extra_vars,
            "cookie": config.cookie,
            "spam_detection": config.spam_detection,
            "inactivity_minutes": config.inactivity_minutes,
            "chat_description": config.chat_description
        }
    except:
        print("No config file detected. Please enter your Kongregate account details...")
        generate_config()
        continue
    break

class GPT:
    processing = False

    def __init__(self, chat_input):
        self.chat_input = chat_input
        self.packaged_input = self.package(chat_input)
        self.apis = {
            0: {
                "name": "api.eleuther.ai",
                "url": "https://api.eleuther.ai/completion",
                "header": None,
                "json": {
                    "context": self.packaged_input,
                    "topP": 0.9,
                    "temp": 0.9,
                    "response_length": 40,
                    "remove_input": True,
                }
            },
            1: {
                "name": "api-inference.huggingface.co",
                "url": "https://api-inference.huggingface.co/models/EleutherAI/gpt-j-6B",
                "header": None,
                "json": {
                    "inputs": self.packaged_input,
                    "parameters": {
                        "use_cache": False,
                        "top_p": 0.9,
                        "temperature": 0.9,
                        "max_new_tokens": 40,
                        "return_full_text": False}
                }
            },
            2: {
                "name": "api.textsynth.com",
                "url": "https://api.textsynth.com/v1/engines/gptj_6B/completions",
                "header": {"Authorization": "Bearer 842a11464f81fc8be43ac76fb36426d2"},
                "json": {
                    "prompt": self.packaged_input,
                    "temperature": 0.9,
                    "top_k": 40,
                    "top_p": 0.9,
                    "max_tokens": 40,
                    "stream": False,
                    "stop": None}
            }
        }

    def package(self, history):
        self.processing = True
        lines = [f"{cfg['chat_description']}\n\n"]
        for message in enumerate(history):
            lines.append(f"{message[1]}\n")
        lines.append(f"{cfg['username']}:")
        return "".join(lines)

    def send_to_api(self):
        for key, value in self.apis.items():
            try:
                response = session.post(value["url"], headers=value["header"], json=value["json"], timeout=20)
                if response.status_code == 200:
                    return response.text
            except:
                PrintMessage.status(3, value["name"], None)

    def process_response(self, response):
        text_keys = ["generated_text", "text"]
        response = loads(response)
        if type(response) is list:
            response = response[0]
        cleaned_response = f"{cfg['username']}:{[response[key] for key in text_keys if key in response][0]}"
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
        self.processing = False
        return final_posts

    def spam_test(self, replies):
        history = [
            message.partition(' ')[2]
            for message in reversed(self.chat_input[:cfg['spam_detection']])
        ]
        for x in replies:
            for y in history:
                if compare(x, y) > 0.75:
                    PrintMessage.status(2, x, y)
                    return False
        return True


class BotMemory:
    memory = {}
    silenced = (False, 0)

    def __init__(self, username, message):
        if username == cfg["username"]:
            return
        if username not in list(self.memory.keys()):
            profile = {
                f"{username}": {
                    "muted": False,
                    "posts": 0,
                    "last_post_time": 0,
                    "inactive": False,
                    "history": {}
                }
            }
            self.memory.update(profile)
        self.user = self.memory[username]
        self.username = username
        if not self.is_muted():
            profile_page = session.get(f"https://www.kongregate.com/accounts/{username}", cookies=cfg["cookie"])
            if "has muted you" in profile_page.text:
                self.mute()
                PrintMessage.status(5, username, None)
            self.user["posts"] += 1
            self.post_id = f"post_{self.user['posts']}"
            self.user["history"][self.post_id] = {"message": message, "reply": None}
            self.user["last_post_time"] = int(strftime("%s"))
            self.user["inactive"] = False
        else:
            self.user["inactive"] = True
            self.user["posts"] = 0
            self.user["history"] = {}

    def parse_history(self):
        constructed = []
        for value in self.user["history"].items():
            constructed.append(f"{self.username}: {value[1]['message']}")
            if value[1]['reply']:
                replies = [f"{cfg['username']}: {reply}" for reply in value[1]['reply']]
                constructed.extend(replies)
        return constructed

    def reply(self, reply):
        self.user["history"][self.post_id]["reply"] = reply

    def mute(self):
        self.user["muted"] = True

    def is_muted(self):
        return self.user["muted"]


class PrintMessage:

    @staticmethod
    def chat(username, contents, bot):
        #blue, white, highlight, faint
        colors = [';36m', ';97m', '46;97m', ';90m']
        if username == cfg['username']:
            i = 0
        elif bot.is_muted():
            i = 3
        else:
            i = 1
        username = f'\033[1{colors[i]}{username}: \033[0{colors[i]}'
        contents_split = []
        highlight_words = [cfg['username'].lower(), "bot", "robot", "chatbot", "mute", "report"]
        for word in contents.split():
            normalized = word.translate(str.maketrans('', '', punctuation))
            normalized = normalized.lower()
            for check in highlight_words:
                if compare(check, normalized) > 0.75:
                    word = f'\033[{colors[2]}{word}\033[0{colors[i]}'
            contents_split += f"{word} "
        contents = "".join(contents_split)
        print(f"{strftime('[%I:%M %p]')} {username}{contents}\033[m")

    @staticmethod
    def status(i, *args):
        status_strings = [
            f"{cfg['username']} has connected\n",
            "Connection dropped. Reconnecting...",
            f"""Reply is too similar to a previous message.
                Current: {args[0]}
                Previous: {args[1]}""",
            f"{args[0]} took too long to respond.",
            f"{cfg['username']} is banned.",
            f"{args[0]} has muted you.",
            f"Clearing memory for {args[0]} (inactivity).",
            f"{cfg['username']} got silenced for {args[0]} minutes.",
            f"{cfg['username']} is no longer silenced."
        ]
        print(f"{strftime('[%I:%M %p]')} \u001B[1;34m{status_strings[i]}\u001B[m")

PrintMessage = PrintMessage()

def compare(string1, string2):
    return SequenceMatcher(a=string1, b=string2).ratio()

def on_message(wsapp, message):
    if (
        BotMemory.silenced[0] is True
        and int((BotMemory.silenced[1] - int(strftime("%s"))) / 60) < 0
    ):
        BotMemory.silenced = (False, 0)
        PrintMessage.status(8, None, None)

    for key, value in BotMemory.memory.items():
        if (
            value["inactive"] is False
            and (int(strftime("%s")) - value["last_post_time"]) / 60 > cfg["inactivity_minutes"]
        ):
            PrintMessage.status(6, key, None)
            BotMemory.memory[key]["inactive"] = True
            BotMemory.memory[key]["history"] = {}
            BotMemory.memory[key]["posts"] = 0

    if "<message to" in message:  # chat message
        ping(wsapp)
        username = findall('/([^"]*)"', message)[1]
        contents = search('<body>(.*)</body>', message).group(1)
        if contents[:8] == ":sticker":
            contents = findall(r'e":"(.*?)"}', contents)[0]
        bot = BotMemory(username, contents)
        PrintMessage.chat(username, contents, bot)
        chat = bot.parse_history()
        if (
            username != cfg['username']
            and bot.is_muted() is False
            and GPT.processing is False
            and BotMemory.silenced[0] is False
        ):
            GPT.processing = True
            Thread(target=read_chat, args=(chat, bot), daemon=True).start()
    elif "admin@of1.kongregate.com/server" in message:  # silenced
        encoded_time = search('<msg opcode="silenced">(.*)</msg>', message).group(1)
        decoded_time = loads(str(b64decode(encoded_time), "utf-8"))
        reformated_time = datetime.strptime(decoded_time['scheduled_end'], "%d %b %Y %H:%M:%S %z")
        struct_time = reformated_time.timetuple()
        silenced_until = int(mktime(struct_time))
        BotMemory.silenced = (True, silenced_until)
        PrintMessage.status(7, int((silenced_until - int(strftime("%s"))) / 60), None)
    elif "</stream:stream>" in message:  # disconnected
        PrintMessage.status(1, None, None)
        initialize()
    elif "<not-authorized" in message:  # banned
        PrintMessage.status(4, None, None)
        wsapp.close()

def read_chat(chat, bot):
    with open('memory.json', 'w') as memory:
        gpt = GPT(chat)
        while True:
            response = gpt.send_to_api()
            if response is None:
                continue
            bot_replies = gpt.process_response(response)
            if gpt.spam_test(bot_replies) is True:
                break
        for message in bot_replies:
            bot.reply(bot_replies)
            sleep(2 + len(message) / 10)
            chatsend(wsapp, cfg, message)
        memory.write(dumps(BotMemory.memory, indent=4))
    memory.close()
    GPT.processing = False

def on_open(wsapp):
    connect(wsapp, cfg)
    PrintMessage.status(0, None, None)

def initialize():
    wsapp.close()
    wsapp.run_forever()


wsapp = WebSocketApp("wss://chat-proxy.kongregate.com/?sid=c10a854d-9e88-42e7-acd6-4f64a894a318&svid=747c5705-f640-48f2-9be0-03f0d6d3fe51&wsr=false&wss=false&ca=0&wc=0&bc=0&tc=0&sr=0&ss=0&pb=true",
                     on_message=on_message,
                     on_open=on_open)
initialize()
