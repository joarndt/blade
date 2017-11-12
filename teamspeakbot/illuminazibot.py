# The Illumminazibot
import time
import sys
import subprocess
from subprocess import call
import telepot
import telepot.api
import urllib3 
from telepot.loop import MessageLoop
from message import *
from client import *



#starts Teamspeak
def ts_start(auth):

    #some  output for Telegram
    write_telegram('joining Teamspeak')

    #starts Teamspeak
    cmd = ["ts3"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    time.sleep(20)

    #initiate Clientquery connection
    client = Client(auth)
    client.subscribe()
    set_ts_running(True)
    send_whoami(client)

    return client

#stops Teamspeak
def ts_stop(client):
    
    #some output for Telegram
    write_telegram('quitting Teamspeak')

    #close connection and quit Teamspeak
    set_ts_running(False)
    client.close()
    call(["killall","-SIGKILL" , "ts3client_linux_amd64"])
    call(["killall","-SIGKILL" , "ts3client_linux_x86"])
    time.sleep(60);

#sends whomai command for verification
def send_whoami(client):
    com = Command('whoami')
    client.send_command(com)

#sets ts_running variable
def set_ts_running(tmp):
    global ts_running
    ts_running = tmp

#write message into Telegram chat
def write_telegram(string):
    global bot
    bot.sendMessage(ts3, string)

#Telegram bot loop 
def handle(msg): 

    #get chat id
    chat_id = msg['chat']['id']

    #checks for textmessage
    if 'text' in msg:

        command = msg['text']
        
        #debug output        
        if debug: print msg
        if debug: print chat_id
        if debug: print 'Got command: %s' % command


        #quitting teamspeak
        if chat_id == ts3 and command == '/quit':
            global client

            if ts_running:
                ts_stop(client)
            else:
                write_telegram('Not in Teamspeak')
        
        #joining teamspeak
        elif chat_id == ts3 and command == '/join':
            global client

            if ts_running:
                write_telegram('already in Teamspeak')
            else:
                client = ts_start(auth)
                client.subscribe()

        elif ts_running:

            #writes command for current channelclients
            if chat_id == ts3 and command=='/status':
                com = Command(
                        'channelclientlist cid=' + channelid,
                    )
                client.send_command(com)

            #unlisten from teamspeakchat
            elif chat_id == ts3 and command == '/stfu':
                global listen
                listen = False
                bot.sendMessage(ts3,'stopped listening to TS3 Chat')

            #listen to teamspeakchat
            elif chat_id == ts3 and command == '/listen':
                global listen
                listen = True
                write_telegram("started listening to TS3 Chat")
            
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
                client.send_command(command)
#        else:
#            write_telegram('bot is not in Teamspeak')

#variable for listening to ts chat 
listen = True

#variable for debugmode
debug = False
if len(sys.argv)==1 and sys.argv[0] == "-debug":
    debug = True

ts_running = False
#variable for invokerid
invokerid = 0
channelid = 0


#read necessary data for bot
file = open('data.txt')

#bot token for interaction with Telegram
#had to remove the \n for use in function
token = str(file.readline()).replace("\n", "") 
#auth code for TeamspeakClientQuery
auth = file.readline()
#chat id for interaction with Teamspeak
ts3 = int(file.readline())

#end of reading
file.close

bot = telepot.Bot(token)    


#start bot with bot_token
bot = telepot.Bot(token)
MessageLoop(bot, handle).run_as_thread()

#start teamspeak client connection
client = ts_start(auth)

print 'I am listening ...'

#listen to teamspeakchat
while 1:
    if ts_running:
        #get teamspeak clientquery messages
        messages = client.get_messages()
        for message in messages:
            if debug: print message

            #outputs teamspeakchat in telegram group
            if message.command == 'notifytextmessage' and message['invokerid']!=invokerid and listen:
                txt = message['invokername'] + ':\n' + message['msg']
                txt = txt.replace("[URL]","")
                txt = txt.replace("[/URL]","")
                bot.sendMessage(ts3,txt)

            #gets current userid
            elif message.is_response_to(Command('whoami')):
                invokerid = message.__getitem__('clid')
                channelid = message.__getitem__('cid')

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
                write_telegram(clients)

    time.sleep(1)