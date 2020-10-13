#lets you manually send inputs through the processor
from processor import *

while True:
    botresponse = input('Input: ')
    print(mistakes(botresponse))
