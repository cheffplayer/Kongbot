import itertools
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

ffprofile = webdriver.FirefoxProfile()
adblockfile = r"D:\Downloads\Trading\Program\trading\adblock_plus-3.8.4-an+fx.xpi"
driver = webdriver.Firefox(ffprofile)
driver.install_addon(adblockfile)
driver.get("http://blank.org/")
driver.switch_to.window(driver.window_handles[0])
time.sleep(1)
driver.get('http://www.kongregate.com/games/UnknownGuardian/game-development-room-gdr?acomplete=gdr')
driver.switch_to.window(driver.window_handles[1])
driver.get('https://www.pandorabots.com/mitsuku/')
time.sleep(1)
driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div[2]/button').click()
ai = driver.find_element_by_xpath('/html/body/div[1]/div/div/div/form/div[1]/input')
time.sleep(3)
driver.switch_to.window(driver.window_handles[0])
input("Press enter once you have logged in.")

username = driver.find_element_by_xpath('/html/body/div[5]/div/div[2]/div/ul/li[1]/a/span[2]').get_attribute('innerHTML')

wait = WebDriverWait(driver, 999999)
chat = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/div[1]/div[6]/div[10]/div[2]/div[2]/div[4]/textarea')))
chatroom = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/div[1]/div[6]/div[10]/div[1]/div[1]/span[1]'))).get_attribute('innerHTML')
print("Connected to", chatroom)
chat.send_keys('https://github.com/cheffplayer/Mitsuku')
chat.send_keys(Keys.ENTER)

def botrun():
    while True:
        global c, chatuser
        try:
            for c in itertools.count(1):
                driver.find_element_by_xpath('/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/div[1]/div[6]/div[10]/div[2]/div[2]/div[3]/div[' + str(c) + ']/p/span[2]/span')
        except:
            chatuser = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/div[1]/div[6]/div[10]/div[2]/div[2]/div[3]/div[' + str(c) + ']/p/span[2]/span'))).get_attribute('innerHTML').replace('<br>', ' ')[:250]

        #if else is to prevent bot from talking to itself
        if chatuser == username:
            pass
        else:
            listen = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div/div[1]/div[6]/div[10]/div[2]/div[2]/div[3]/div[' + str(c) + ']/p/span[3]'))).get_attribute(
                'innerHTML').replace('<br>', ' ')[:250]
            print(chatuser + ':', listen)
            driver.switch_to.window(driver.window_handles[1])

            # inputs the listen variable into the bot
            ai.send_keys(listen)
            ai.send_keys(Keys.ENTER)
            time.sleep(.5)

            global b
            try:
                for b in itertools.count(3):
                    driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[4]/div[2]/div/div[' + str(b) + ']/div/div/div')
            except:
                b = b - 1
            #checks to see if the bot responded. if it didnt, then it recalibrates and outputs a preprogramed response
            try:
                botresponse = driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[4]/div[2]/div/div[' + str(b) + ']/div/div/div').get_attribute('innerHTML').replace('<br>', ' ')[:250]
            except:
                ai.send_keys("|")
                ai.send_keys(Keys.ENTER)
                botresponse = random.choice(['k', 'ok', 'what?', 'wat', 'sorry?', 'ok then'])

            #if else is to prevent bot from parroting other users
            if botresponse == listen:
                print("Chat output: ", botresponse)
                print()
                driver.switch_to.window(driver.window_handles[0])
            else:
                #removes a period if there is less than 2 of them at the end of the message
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
                    if (botresponse[i:i + 2] == ". " or botresponse[i:i + 2] == "? ") and i < len(botresponse) - 2 and botresponse[i + 2] != "I":
                        botresponse = botresponse[0:i + 2] + botresponse[i + 2].lower() + botresponse[i + 3:]
                print("Chat output: ", botresponse)
                driver.switch_to.window(driver.window_handles[0])

                #delays the response based on character length
                delayseconds = 2 + len(botresponse) / 8
                time.sleep(delayseconds)

                #sends message to chat
                chat.send_keys(botresponse)
                chat.send_keys(Keys.ENTER)
                print()


botrun()
