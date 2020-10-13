# dumbs the sentence down to be more humanlike
import random

def mistakes(botresponse):
    global typocorrection, decide
    responselen = len(botresponse.split())
    lastword = botresponse.split()
    if lastword[responselen - 1][-1:] == ".":
        if lastword[responselen - 1][-2:] != "..":
            botresponse = botresponse[:-1]
    if botresponse[0:1] == ".":
        botresponse = botresponse[1:]
    if botresponse[0] != "I" and botresponse[0:2] != "OK":
        botresponse = botresponse[0].lower() + botresponse[1:]
    for i in range(2, len(botresponse)):
        if (botresponse[i:i + 2] == ". " or botresponse[i:i + 2] == "? ") and i < len(botresponse) - 2 and botresponse[
            i + 2] != "I":
            botresponse = botresponse[0:i + 2] + botresponse[i + 2].lower() + botresponse[i + 3:]

    # simulates typos and corrections
    punctuation = ',.?'
    outputsplit = botresponse.split()
    wordint = random.randint(0, len(outputsplit) - 1)
    typoword = (outputsplit[wordint]).strip(punctuation)

    if random.randint(1, 15) == 1:
        try:
            if len(typoword) > 3:
                decide = 1
                typoword2 = typoword[1:]
                botresponse = ' '.join([x.replace(typoword, typoword2, 1) for x in outputsplit])
        except:
            pass
    elif random.randint(1, 15) == 1:
        try:
            decide = 0
            commontypos = {
                'what': ['wat', 'wjat', 'waht', 'wgat'],
                'your': ['ur', 'yuor', '''you're'''],
                'then': ['tehn', 'thne']
            }
            commontypochoice = random.choice(list(commontypos))
            botresponse = ' '.join(
                [x.replace(commontypochoice, random.choice(commontypos[commontypochoice]), 1) for x in
                 outputsplit])
        except:
            pass
    else:
        decide = 0
    # writes a typo correction if one was made
    try:
        if decide == 1:
            typophrases = [' ', 'oops ', 'i meant ', 'meant to say ', 'sorry ']
            typocorrection = random.choice(typophrases) + typoword + '*'
            decide = 0
    except:
        pass
    #sends processed text to file
    return botresponse