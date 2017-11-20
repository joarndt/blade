# -*- coding: iso-8859-1 -*-
# teamspeakbot
from datetime import datetime
import time
import argparse
import subprocess
import threading
from subprocess import call
import telepot
from telepot.loop import MessageLoop
from message import *
from client import *

class Teamspeakbot(object):

    #init 
    def __init__(self):

        

        #set debugmode
        #self.debug = sys.argv[0] == "-debug" or sys.argv[0] == "-d"
        #print self.debug, sys.argv[1]
        self.debug = True

        #parser = argparse.ArgumentParser(description='Process some integers.')
        #parser.add_argument("-foo", ..., required=True)
        #parser.parse_args()

        #variable for listening to ts chat 
        self.listen = True

        #indicates if ts is running
        self.tsRunning = False

        ######################
        ### Ts Chat Format ###
        ######################
        self.userFormat = "[b]"
        self.userColor ={
            (106066030, "[color=#00aa00]", "Blade"),      #Blade
            (128494099, "[color=#1C85FF]", "Oracle"),     #Oracle         
            (443210169, "[color=#caa047]", "Imperial"),   #Imperial
            (389880533, "[color=#BD5866]", "NiSs4n"),     #NiSs4n
            (111111111, "[color=#287065]", "Velo"),       #Velo todo
        }
        self.chatFormat = "[/b][color=grey]"





        #empty clientlist
        self.tsClients = []

        #set default ids
        self.invokerid = "0"
        self.channelid = "0"

        #read necessary data for bot
        file = open('data.txt')

        #bot token for interaction with Telegram
        #had to remove the \n for use in function
        self.token = str(file.readline()).replace("\n", "") 
        #auth code for TeamspeakClientQuery
        self.auth = file.readline()
        #chat id for interaction with Teamspeak
        self.ts3 = int(file.readline())

        #end of reading
        file.close

        #start bot with bot_token
        self.bot = telepot.Bot(self.token)
        MessageLoop(self.bot, self.handle).run_as_thread()
        self.keepAlive()

        #start teamspeak client connection
        self.client = self.tsStart(self.auth)

        print 'I am listening ...'

        self.tsMessageLoop(self.ts3)

    #Telegram bot loop 
    def handle(self, msg): 

        #get chat id
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']        

        #checks for textmessage
        if 'text' in msg:

            command = msg['text'].split('@')[0]
            
            #debug output        
            if self.debug: print msg
            if self.debug: print chat_id
            if self.debug: print 'Got command: %s' % command


            #quitting teamspeak
            if chat_id == self.ts3 and command == '/quit':
                self.tsQuit(self.client)
            
            #joining teamspeak
            elif chat_id == self.ts3 and command == '/join':
                if self.tsRunning:
                    self.writeTelegram('already in Teamspeak')
                else:
                    self.client = self.tsStart(self.auth)
                    self.client.subscribe()

            elif self.tsRunning:

                #writes command for current channelclients
                if chat_id == self.ts3 and command=='/status':
                    self.sendStatus(self.client, self.channelid)

                #unlisten from teamspeakchat
                elif chat_id == self.ts3 and command == '/stfu':
                    self.listen = False
                    self.writeTelegram('stopped listening to TS3 Chat')

                #listen to teamspeakchat
                elif chat_id == self.ts3 and command == '/listen':
                    self.listen = True
                    self.writeTelegram("started listening to TS3 Chat")
                
                #builds textmessages and writes it into teamspeakchat     
                elif chat_id == self.ts3:
                    self.writeTeamspeak(
                        self.userFormat 
                        + self.getUsername(msg) 
                        + ': ' 
                        + self.chatFormat 
                        + msg['text']
                    )

#           else:
#               writeTelegram('bot is not in Teamspeak')
    



    #starts Teamspeak
    def tsStart(self, auth):

        #some  output for Telegram
        self.writeTelegram('joining Teamspeak')

        #starts Teamspeak
        process = subprocess.Popen(["ts3"],stdout = subprocess.PIPE)
        time.sleep(20)

        #initiate Clientquery connection
        client = Client(self.auth)
        client.subscribe()

        self.setTsRunning(True)
        self.sendWhoami(client)

        return client

    #stops Teamspeak
    def tsStop(self, client):
        
        #some output for Telegram
        self.writeTelegram('quitting Teamspeak')

        #close connection and quit Teamspeak
        self.setTsRunning(False)
        client.close()
        call(["killall","-SIGKILL" , "ts3client_linux_amd64"])
        call(["killall","-SIGKILL" , "ts3client_linux_x86"])
        time.sleep(60);

    #sends whoami command for verification
    def sendWhoami(self, client):
        client.send_command(Command('whoami'))

    def sendStatus(self, client, channelid):
        client.send_command(Command('channelclientlist cid=' + channelid))

    def tsQuit(self, client):
        if self.tsRunning:
            self.tsStop(client)
        else:
            self.writeTelegram('Not in Teamspeak')

    #sets tsRunning variable
    def setTsRunning(self, tmp):
        self.tsRunning = tmp

    #write message into Telegram chat
    def writeTelegram(self, string):
        self.bot.sendMessage(self.ts3, string)

    def writeTeamspeak(self, string):
        message  = "sendtextmessage targetmode=2 msg=" + string.replace(" ","\s")
        self.client.send_command(Command(message.encode('utf-8')))

    #thread for keeping the connection
    def __keepAliveThread(self):
        while True:
            self.bot.getMe()
            x=datetime.today()
            print x
            if self.tsClients.__len__() == 1 and self.tsClients[0][0] == self.invokerid and self.tsRunning:
                self.writeTelegram("auto quit")
                self.tsQuit(self.client)
            time.sleep(60)

    #function
    def keepAlive(self):
        t = threading.Thread(target = self.__keepAliveThread)
        t.daemon = True
        t.start()

    #gets username from msg 
    def getUsername(self, msg):
        #if known then colorize it and make default name
        if 'id' in msg['from']:
            for part in self.userColor:
                if part[0] == msg['from']:
                    return part[1] + part[2]
        elif 'username' in msg['from']: 
            return msg['from']['username']           
        elif 'first_name' in msg['from']: 
            return msg['from']['first_name']
        return "no username found"


    def tsMessageLoop(self, ts3):
        #listen to teamspeakchat
        while 1:
            if self.tsRunning:
                #get teamspeak clientquery messages
                messages = self.client.get_messages()
                for message in messages:
                    if self.debug: print message

                    #outputs teamspeakchat in telegram group
                    if message.command == 'notifytextmessage' and message['invokerid']!=self.invokerid and self.listen:

                        #build message for Telegram
                        msg = (message['invokername'] + ':\n' + message['msg']).replace("[URL]","").replace("[/URL]","")

                        self.writeTelegram(msg)

                    #Teamspeakuser joined 
                    elif message.command == "notifycliententerview" and message['ctid'] == self.channelid:
                        
                        if 'client_nickname' in message.keys() and 'clid' in message.keys():
                            self.tsClients.append((message['clid'], message['client_nickname']))
                            self.writeTelegram(message['client_nickname'] + " joined Teamspeak")

                    #Teamspeakuser left            
                    elif message.command == "notifyclientleftview" and message['cfid'] == self.channelid:

                        if 'clid' in message.keys():
                            for part in self.tsClients:
                                if part[0] == message['clid']:
                                    self.writeTelegram(part[1] + " left Teamspeak")
                                    self.tsClients.remove(part)

                            
                    #gets current userid
                    elif message.is_response_to(Command('whoami')):
                        self.invokerid = message.__getitem__('clid')
                        self.channelid = message.__getitem__('cid')
                        self.sendStatus(self.client, self.channelid)

                    #status output for telegram group    
                    elif message.is_response():
                        self.tsClients = []
                        #build message for status 
                        msg = 'Currently Online:'
                        for part in message.responses:
                            if 'client_nickname' in part.keys() and 'clid' in part.keys():
                                self.tsClients.append((part.__getitem__('clid'), part.__getitem__('client_nickname')))
                                msg += '\n' + part.__getitem__('client_nickname')
                        msg += '\nlisten: ' + str(self.listen)

                        self.writeTelegram(msg)
            time.sleep(1)

#start Teamspeakbot
Teamspeakbot()
