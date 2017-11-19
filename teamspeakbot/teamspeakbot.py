# teamspeakbot
import time
import sys
import subprocess
import threading
from subprocess import call
import telepot
import telepot.api
import urllib3 
from telepot.loop import MessageLoop
from message import *
from client import *

class Teamspeakbot(object):

    #init 
    def __init__(self):

        #variable for listening to ts chat 
        self.listen = True

        #set debugmode
        if len(sys.argv)==1 and sys.argv[0] == "-debug":
            self.debug = True
        else:
            self.debug = False

        #indicates if ts is running
        self.ts_running = False

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

    #Telegram bot loop 
    def handle(self, msg): 

        #get chat id
        chat_id = msg['chat']['id']

        #checks for textmessage
        if 'text' in msg:

            command = msg['text']
            
            #debug output        
            if self.debug: print msg
            if self.debug: print chat_id
            if self.debug: print 'Got command: %s' % command


            #quitting teamspeak
            if chat_id == ts3 and command == '/quit':
                if ts_running:
                    self.tsStop(self.client)
                else:
                    self.writeTelegram('Not in Teamspeak')
            
            #joining teamspeak
            elif chat_id == ts3 and command == '/join':
                if self.ts_running:
                    self.writeTelegram('already in Teamspeak')
                else:
                    self.client = tsStart(auth)
                    self.client.subscribe()

            elif self.ts_running:

                #writes command for current channelclients
                if chat_id == ts3 and command=='/status':
                    com = Command(
                            'channelclientlist cid=' + channelid,
                        )
                    self.client.send_command(com)

                #unlisten from teamspeakchat
                elif chat_id == ts3 and command == '/stfu':
                    self.listen = False
                    self.bot.sendMessage(ts3,'stopped listening to TS3 Chat')

                #listen to teamspeakchat
                elif chat_id == ts3 and command == '/listen':
                    self.listen = True
                    self.writeTelegram("started listening to TS3 Chat")
                
                #builds textmessages and writes it into teamspeakchat     
                elif chat_id == ts3:
                    com  = "sendtextmessage targetmode=2 msg="
                    txt = ''
                    if 'username' in msg['from']:
                        txt += msg['from']['username']
                    elif 'first_name' in msg['from']:
                        txt += msg['from']['first_name']
                    txt +=': ' + msg['text']
                    txt = txt.replace(" ","\s")
                    com += txt
                    command = Command(
                            str(com),
                        )
                    self.client.send_command(command)
#           else:
#               writeTelegram('bot is not in Teamspeak')
    



    #starts Teamspeak
    def tsStart(self, auth):

        #some  output for Telegram
        self.writeTelegram('joining Teamspeak')

        #starts Teamspeak
        cmd = ["ts3"]
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        time.sleep(20)

        #initiate Clientquery connection
        client = Client(self.auth)
        client.subscribe()
        self.setTsRunning(True)
        self.sendWhoami(self.client)

        return client

    #stops Teamspeak
    def tsStop(self, client):
        
        #some output for Telegram
        self.writeTelegram('quitting Teamspeak')

        #close connection and quit Teamspeak
        self.setTsRunning(False)
        self.client.close()
        call(["killall","-SIGKILL" , "ts3client_linux_amd64"])
        call(["killall","-SIGKILL" , "ts3client_linux_x86"])
        time.sleep(60);

    #sends whoami command for verification
    def sendWhoami(self, client):
        com = Command('whoami')
        client.send_command(com)

    #sets ts_running variable
    def setTsRunning(self, tmp):
        self.ts_running = tmp

    #write message into Telegram chat
    def writeTelegram(self, string):
        self.bot.sendMessage(self.ts3, string)

    #thread for keeping the connection
    def __keepAliveThread():
        while True:
            self.bot.getMe()
            time.sleep(60)

    #function
    def keepAlive(self, ):
        t = threading.Thread(target = self.__keepAliveThread)
        t.daemon = True
        t.start()

    

def tsMessageLoop(self):
    #listen to teamspeakchat
    while 1:
        if self.ts_running:
            #get teamspeak clientquery messages
            messages = self.client.get_messages()
            for message in messages:
                if self.debug: print message

                #outputs teamspeakchat in telegram group
                if message.command == 'notifytextmessage' and message['invokerid']!=invokerid and self.listen:
                    txt = message['invokername'] + ':\n' + message['msg']
                    txt = txt.replace("[URL]","")
                    txt = txt.replace("[/URL]","")
                    self.bot.sendMessage(ts3,txt)

                #gets current userid
                elif message.is_response_to(Command('whoami')):
                    self.invokerid = message.__getitem__('clid')
                    self.channelid = message.__getitem__('cid')

                #status output for telegram group    
                elif message.is_response():

                    clients = 'Currently Online:'

                    if message.is_multipart_message():
                        for part in message.responses:
                            if 'client_nickname' in part.keys():
                                clients += '\n' + part.__getitem__('client_nickname')
                    else :
                        if 'client_nickname' in message.keys():
                            clients += '\n' + message.__getitem__('client_nickname')
                    clients+='\nlisten: '
                    if listen:
                        clients+='True'
                    else :
                        clients+='False'
                    self.writeTelegram(clients)
        time.sleep(1)
