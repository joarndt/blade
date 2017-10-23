# The Illumminazibot

import time
import random
import datetime
import subprocess
import telepot
from telepot.loop import MessageLoop
from message import Command, MessageFactory
import time
from client import *
import email
import io

def handle(msg): 
    chat_id = msg['chat']['id']
    if 'text' in msg:
        command = msg['text']
        
        if debug: print msg
        if debug: print chat_id
        
        if debug: print 'Got command: %s' % command

        #writes command for current channelclients
        if chat_id == ts3 and command=='/status':
            com = Command(
                    'channelclientlist cid=874',
                )
            client.send_command(com)
        #unlisten from teamspeakchat
        elif chat_id == ts3 and command=='/stfu':
            listen = False
            bot.sendMessage(ts3,'stopped listening to TS3 Chat')
        #listen to teamspeakchat
        elif chat_id == ts3 and command=='/listen':
            listen = True
            bot.sendMessage(ts3,'started listening to TS3 Chat')
        #writes textmessage into teamspeakchat     
        elif chat_id == ts3:
            com  = "sendtextmessage targetmode=2 msg="
            txt = ''
            if 'username' in msg['from']:
                txt += msg['from']['username']
            elif 'first_name' in msg['from']:
                        txt += msg['from']['first_name']
            txt +=': '
            txt +=msg['text']
            txt = txt.replace(" ","\s")
            com += txt
            command = Command(
                    str(com),
                )
            client.send_command(command)

file = open('chats.txt')
ts3 = int(file.readline())
illumuhnazi = int(file.readline())
file.close

listen = True
debug = False
client = Client()
client.subscribe()

file = open('token.txt')
token = file.readline()
file.close

bot = telepot.Bot(token)
MessageLoop(bot, handle).run_as_thread()

print 'I am listening ...'

while 1:
    messages = client.get_messages()
    for message in messages:
        if message.command == 'notifytextmessage' and message['invokername']!='BIade' and listen:
            txt = message['invokername']
            txt+=':\n'
            txt+= message['msg']
            txt = txt.replace("[URL]","")
            txt = txt.replace("[/URL]","")
            bot.sendMessage(ts3,txt)
        elif message.is_response():
            clients = 'Currently Online:'
            for part in message.response:
                clients+='\n'
                clients+=part['client_nickname']
            clients+='\nlisten: '
            if listen:
                clients+='True'
            else :
                clients+='False'
            bot.sendMessage(ts3,clients)        

    time.sleep(1)