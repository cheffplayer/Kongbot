
# Kongbot

## Kongregate chatbot

This script opens up a connection with Kongregate's chat websocket and uses various GPT-J-6B APIs to automatically generate responses to chat messages. Avoid running it on accounts that you care about, because they risk getting banned if people report you for being a chatbot.
jerome_a2 is the bot in this example:
![image](example.png)

## <u>Main features</u>

 - Tries to avoid repeating itself, and others.
 - Automatically ignores users that mute the bot.
 - If a moderator silences the bot, then it will wait until it is unsilenced.
 - Portable configuration file. This lets you bypass IP bans if you generate it on another network.
 - Forgets conversations after a certain amount of time. This prevents the bot from continuing a conversation that ended a long time ago.

## <u>Resources</u>

[EleutherAI](https://6b.eleuther.ai/ "EleutherAI")\
[Hugging Face](https://huggingface.co/EleutherAI/gpt-j-6B "Hugging Face")\
[TextSynth](https://textsynth.com/playground.html "TextSynth")

## <u>Usage</u>

```shell
pip3 install websocket-client
git clone https://github.com/cheffplayer/Kongbot.git
cd Kongbot/
python3 main.py
```

You will be prompted to for your Kongregate account details when you first run the script, but it will automatically log you in after that. If you want to change the account that the script uses, then just delete `config.py` and rerun `main.py`
The best way to tweak the way that the bot responds to messages is to edit the `chat_description` setting in `config.py`.

