import itertools
import time

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from processor import *

options = webdriver.ChromeOptions()
options.binary_location = "chrome/chrome.exe"
options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
driver.get('https://www.kongregate.com/games/0rava/mutilate-a-doll-2')
driver.execute_script("window.open('https://pandorabots.com/mitsuku/');")
driver.switch_to.window(driver.window_handles[1])
driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div/div/div[2]/div[2]/button').click()
ai = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/div/div/div/form/div[1]/input')
driver.switch_to.window(driver.window_handles[0])
input("Press enter once you have logged in.")

username = driver.find_element_by_xpath('/html/body/div[5]/div/div[2]/div/ul/li[1]/a/span[2]').get_attribute('innerHTML')
wait = WebDriverWait(driver, 999999)
chat = driver.find_element_by_xpath('/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div[1]/div[1]/div[5]/div[10]/div[2]/div/div[4]/div[1]/textarea')
chatroom = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div[1]/div[1]/div[5]/div[10]/div[1]/div[1]/span[1]'))).get_attribute('innerHTML')
print("Connected to", chatroom)
chat.send_keys(username, " has connected to ", chatroom + '!', ' Checkout the code here: https://github.com/cheffplayer/Mitsuku')
chat.send_keys(Keys.ENTER)

def botrun():
    while True:
        try:
            for c in itertools.count(1):
                driver.find_element_by_xpath('/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div[1]/div[1]/div[5]/div[10]/div[2]/div/div[3]/div['+str(c)+']/p/span[3]')
        except:
            chatuser = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div[1]/div[1]/div[5]/div[10]/div[2]/div/div[3]/div['+str(c)+']/p/span[2]/span'))).get_attribute('innerHTML').replace('<br>', ' ')[:250]

        #if else is to prevent bot from talking to itself
        if chatuser == username:
            pass
        else:
            listen = wait.until(ec.visibility_of_element_located((By.XPATH,'/html/body/div[6]/table/tbody/tr/td[2]/div/div[1]/div[2]/div/div/div/table/tbody/tr[2]/td[2]/div[1]/div[1]/div[5]/div[10]/div[2]/div/div[3]/div['+str(c)+']/p/span[3]'))).get_attribute('innerHTML').replace('<br>', ' ')[:250]
            print(chatuser + ':', listen)
            driver.switch_to.window(driver.window_handles[1])

            # inputs the listen variable into the bot
            ai.send_keys(listen)
            ai.send_keys(Keys.ENTER)
            time.sleep(.5)

            try:
                for b in itertools.count(3):
                    driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div/div/div/div[4]/div[2]/div/div['+str(b)+']/div/div/div')
            except:
                b = b - 1
            #checks to see if mitsuku gave a response; goes back to start of loop if not
            try:
                botresponse = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div/div/div/div[4]/div[2]/div/div['+str(b)+']/div/div/div').get_attribute('innerHTML').replace('<br>', ' ')[:250]
            except:
                pass

            #if else is to prevent bot from parroting other users
            if botresponse == listen:
                print("Chat output: ", botresponse)
                print()
                driver.switch_to.window(driver.window_handles[0])
            else:
                botresponse = mistakes(botresponse)

                print("Chat output: ", botresponse[0])
                driver.switch_to.window(driver.window_handles[0])

                #simulates time to read the chat message
                time.sleep(len(botresponse[0]) / 11)

                #delays the response based on response character length
                time.sleep(2 + len(botresponse[0]) / 10)

                #sends message to chat
                chat.send_keys(botresponse[0])
                chat.send_keys(Keys.ENTER)

                #sends a typo correction if one was made
                try:
                    time.sleep(2 + len(botresponse[1]) / 8)
                    print('Correction: ', botresponse[1])
                    chat.send_keys(botresponse[1])
                    chat.send_keys(Keys.ENTER)
                except:
                    pass

                print()
botrun()
