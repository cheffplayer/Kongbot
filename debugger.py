#lets you manually send inputs through the processor
from processor import *

while True:
    botresponse = input('Input: ')
    mistakes(botresponse)
    file = open('botresponse.txt', 'r')
    filelist = file.read().split('\n')
    print(filelist)
