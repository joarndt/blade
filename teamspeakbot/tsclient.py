
import subprocess
import threading
from subprocess import call
import time
from message import *
from client import *

# Tsclient controll script and Query handling


class Tsclient(object):

    def __init__(self, bot, groupId, auth, debug=False):

        # empty clientlist
        self.debug = debug
        self.tsClients = dict()
        self.auth = auth
        self.bot = bot
        self.groupId = groupId

        # variable for listening to ts chat
        self.listen = True

        # indicates if ts is running
        self.tsRunning = False

        # set default ids
        self.invokerid = "0"
        self.channelid = "0"

        self.messageThread = threading.Thread(target=self.tsMessageLoop)
        self.messageThread.daemon = True
        self.messageThread.start()

    # listen to Teamspeakchat
    def tsMessageLoop(self):
        while 1:
            if self.tsRunning:

                # get teamspeak clientquery messages
                messages = self.client.get_messages()
                for message in messages:
                    if self.debug: print message

                    # outputs teamspeakchat in telegram group
                    if message.command == 'notifytextmessage' and message['invokerid'] != self.invokerid and self.listen:
                        msg = (message['invokername'] + ':\n' + message['msg']).replace("[URL]","").replace("[/URL]","")
                        self.writeTelegram(msg)

                    # Teamspeakuser joined 
                    elif message.command == "notifycliententerview" and message['ctid'] == self.channelid:
                        if 'client_nickname' in message.keys() and 'clid' in message.keys():
                            self.tsClients[message['clid']] = message['client_nickname']
                            self.writeTelegram(message['client_nickname'] + " joined Teamspeak")

                    # Teamspeakuser left            
                    elif message.command == "notifyclientleftview" and message['cfid'] == self.channelid:
                        if 'clid' in message.keys():
                            if message['clid'] in self.tsClients:
                                self.writeTelegram(self.tsClients[message['clid']] + " left Teamspeak")
                                del self.tsClients[message['clid']]
                            else:
                                self.writeTelegram("BIade ffs fix me")

                    # gets current userid
                    elif message.is_response_to(Command('whoami')):
                        self.invokerid = message['clid']
                        self.channelid = message['cid']
                        self.sendStatus()

                    # status output for telegram group    
                    elif message.is_response():
                        # reset tsClients list
                        del self.tsClients
                        self.tsClients = dict()
                        # build message for status and appends these Clients to list
                        msg = 'Currently Online:'
                        for part in message.responses:
                            if 'client_nickname' in part.keys() and 'clid' in part.keys():
                                self.tsClients[part['clid']] = part['client_nickname']
                                msg += '\n' + part['client_nickname']
                        msg += '\nlisten: ' + str(self.listen)

                        self.writeTelegram(msg)
            time.sleep(1)

    # starts Teamspeak
    def tsStart(self):

        # if Teamspeak is already running
        if self.tsRunning:
            self.writeTelegram("already in Teamspeak")
            

        # some  output for Telegram
        self.writeTelegram("joining Teamspeak")

        # starts Teamspeak
        subprocess.Popen(["ts3"], stdout=subprocess.PIPE)
        time.sleep(20)

        # initiate Clientquery connection
        client = Client(self.auth)
        client.subscribe()
        self.client = client

        # set boolean
        self.setTsRunning(True)
        self.setListen(True)
        self.sendWhoami()

        

    # stops Teamspeak
    def tsStop(self):

        if not self.tsRunning:
            self.writeTelegram("not in Teamspeak")
            return

        # some output for Telegram
        self.writeTelegram("quitting Teamspeak")

        # close connection and quit Teamspeak
        self.setTsRunning(False)
        self.client.close()
        call(["killall","-SIGKILL" , "ts3client_linux_amd64"])
        call(["killall","-SIGKILL" , "ts3client_linux_x86"])
        time.sleep(60);

    # quits Teamspeak
    def tsQuit(self):
        if self.tsRunning:
            self.tsStop()
        else:
            self.writeTelegram('Not in Teamspeak')

    def autoQuit(self):
        if self.tsClients.__len__() == 1 and self.invokerid in self.tsClients and self.tsRunning:
            self.tsQuit()

    # sends whoami command for verification
    def sendWhoami(self):
        self.client.send_command(Command('whoami'))

    # send status message for channel_id
    def sendStatus(self):
        self.client.send_command(Command('channelclientlist cid=' + self.channelid))

    # returns tsRunning variable
    def getTsRunning(self):
        return self.tsRunning

    # sets tsRunning variable
    def setTsRunning(self, tmp):
        self.tsRunning = tmp

    # sets listen variable
    def setListen(self, tmp):
    	self.tsListen = tmp

    # write message into Teamspeak chat
    def writeTeamspeak(self, string):
        message = "sendtextmessage targetmode=2 msg=" + string.replace(" ", "\s")
        self.client.send_command(Command(message.encode('utf-8')))

    def writeTelegram(self, string):
        self.bot.sendMessage(self.groupId, string)
