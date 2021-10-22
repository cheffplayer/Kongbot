from _thread import start_new_thread
from difflib import SequenceMatcher
from random import randint
from re import search, findall
from time import sleep, strftime

from requests import post
from websocket import WebSocketApp

from setup import generate_config

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
            "inactivity_minutes": config.inactivity_minutes
        }
    except:
        print("No config file detected. Please enter your Kongregate account details...")
        generate_config()
        continue
    break

def timestamp():
    return strftime("[%I:%M %p] ")

def chatsend(send):
    wsapp.send(f"<message to='287709-ngu-idle-1@conference.of1.kongregate.com' from='{cfg['username'].lower()}@of1.kongregate.com/xiff' type='groupchat' id='02826d44-fc2d-4ddf-885d-339c6e1709ea' xmlns='jabber:client'><body>{str(send)}</body><x xmlns='jabber:x:event'><composing/></x></message>")

def ping():
    wsapp.send("<iq type='get' id='32a9b0a3-1d77-4b12-8965-fc809bdb340f:ping' xmlns='jabber:client'><ping xmlns='urn:xmpp:ping'/></iq>")

def compare(string1, string2):
    return SequenceMatcher(a=string1, b=string2).ratio()

def sendrequest(history):
    lines = ["This is a chatroom conversation\n"]
    for i in range(0, len(history), 2):
        lines.append(f"{timestamp()}{history[i]}: {history[i + 1]}\n")
    lines.append(f"{timestamp()}{cfg['username']}:")
    package = ("".join(lines))
    while True:
        try:
            r = post("https://api.eleuther.ai/completion", json={
                "context": package,
                "topP": 0.9,
                "temp": 1.5,
                "response_length": 40,
                "remove_input": True}, )
            response = search(r':"(.*?)\\', r.text).group(1).strip()
            cont1 = findall(r'] (.*?):', r.text)[0]
            cont2 = findall(r': (.*?)\\', r.text)[0]
            return response, cont1, cont2
        except: continue

def connect():
    wsapp.send("<open xmlns='urn:ietf:params:xml:ns:xmpp-framing' to='of1.kongregate.com' version='1.0'/>")
    wsapp.send(f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{cfg['token']}</auth>")
    wsapp.send("<iq type='set' id='_bind_auth_2' xmlns='jabber:client'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>xiff</resource></bind></iq>")
    wsapp.send("<iq type='set' id='_session_auth_2' xmlns='jabber:client'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>")
    wsapp.send("<presence xmlns='jabber:client'><show>chat</show></presence>")
    wsapp.send(f"<presence from='{cfg['username'].lower()}@of1.kongregate.com/xiff' to='287709-ngu-idle-1@conference.of1.kongregate.com/{cfg['username']}' xmlns='jabber:client'><x xmlns='http://jabber.org/protocol/muc'><history seconds='60'/></x><status>[&quot;{cfg['sig']}&quot;,&quot;{cfg['vars']}&quot;,{cfg['extra']}]</status></presence>")


history = []
responses = ["0"]
def on_message(wsapp, message):
    #print(message)
    if "<message to" in message:
        username = findall('/([^"]*)"', message)[1]
        contents = search('<body>(.*)</body>', message).group(1)
        if username != cfg['username']:
            print(timestamp() + '\033[1;37m' + username + '\033[0;0m' + ": " + contents)
        else:
            print(timestamp() + '\033[1;36m' + username + '\033[0;36m' + ": " + contents + '\033[0;0m')
        if contents[0:8] == ":sticker": contents = "sticker"
        history.append(username)
        history.append(contents)
    elif "</stream:stream>" in message: print(f"\n{timestamp()}\u001B[1;34mConnection dropped\u001B[0;0m\n")

def run(*args):
    i = 0
    i2 = 0
    while True:
        length = len(history)
        sleep(1)
        if len(history) == length:
            i2 += 1
            if i2 == cfg['inactivity_minutes'] * 60:
                history.clear()
                print(f"{timestamp()}\u001B[1;34mChat inactivity... (clearing memory)\u001B[0;0m")
        else: i2 = 0
        if len(history) > cfg['chat_length']: history.clear()
        if len(history) >= 2 and history[-2] != cfg['username']:
            response, cont1, cont2 = sendrequest(history)
            responses.append(response)
            if compare(responses[-1], history[-1]) > 0.8: continue
            elif compare(responses[-1], responses[-2]) > 0.8: continue
            elif responses[-1] == "": continue
            else:
                chatsend(responses[-1])
                if (cont1 == cfg['username'] and
                    randint(0, 1) == 1 and
                    compare(responses[-1], cont2) < 0.8): chatsend(cont2)
        i += 1
        if i == 30:
            ping()
            i = 0

def on_open(wsapp):
    connect()
    print(f"\n{timestamp()}\u001B[1;34m{cfg['username']} has connected\n\u001B[0;0m")
    start_new_thread(run, ())

wsapp = WebSocketApp("wss://chat-proxy.kongregate.com/?sid=c10a854d-9e88-42e7-acd6-4f64a894a318&svid=747c5705-f640-48f2-9be0-03f0d6d3fe51&wsr=false&wss=false&ca=0&wc=0&bc=0&tc=0&sr=0&ss=0&pb=true",
                     on_message=on_message,
                     on_open=on_open)
wsapp.run_forever()
