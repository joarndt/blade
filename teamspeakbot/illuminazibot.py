# The Illumminazibot
import time
import subprocess
from subprocess import call
import telepot
from telepot.loop import MessageLoop
from message import *
from client import *

def ts_start(auth):
    cmd = ["ts3"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    print 'joining Teamspeak'
    time.sleep(2)
    client = Client(auth)
    client.subscribe()
    set_ts_running(True)
    return client

def ts_stop(client):
    set_ts_running(False)
    client.close()
    call(["killall", "ts3client_linux_amd64"])

def send_whoami():
    com = Command(
        'whoami',
    )
    client.send_command(com)

def set_ts_running(tmp):
    global ts_running
    ts_running = tmp

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

        #writes command for current channelclients
        if chat_id == ts3 and command=='/status':
            com = Command(
                    'channelclientlist cid=' + channelid,
                )
            client.send_command(com)

        #unlisten from teamspeakchat
        elif chat_id == ts3 and command == '/stfu':
            listen = False
            bot.sendMessage(ts3,'stopped listening to TS3 Chat')

        #listen to teamspeakchat
        elif chat_id == ts3 and command == '/listen':
            listen = True
            bot.sendMessage(ts3,'started listening to TS3 Chat')
        
        #quitting teamspeak
        elif chat_id == ts3 and command == '/quit':
            global client
            ts_stop(client)
        
        #joining teamspeak
        elif chat_id == ts3 and command == '/join':
            global client
            client = ts_start(auth)
            client.subscribe()
            send_whoami()
        
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

#variable for listening to ts chat 
listen = True
#variable for debugmode
debug = False
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

#start teamspeak client connection
client = ts_start(auth)

#start bot with bot_token
bot = telepot.Bot(token)
MessageLoop(bot, handle).run_as_thread()

print 'I am listening ...'

whoami = Command(
        'whoami',
    )
client.send_command(whoami)

#listen to teamspeakchat
while 1:
    if ts_running:
        #get teamspeak clientquery messages
        messages = client.get_messages()
        for message in messages:
            if debug: print message
            print message

            #outputs teamspeakchat in telegram group
            if message.command == 'notifytextmessage' and message['invokerid']!=invokerid and listen:
                txt = message['invokername']
                txt+=':\n'
                txt+= message['msg']
                txt = txt.replace("[URL]","")
                txt = txt.replace("[/URL]","")
                bot.sendMessage(ts3,txt)

            #gets current userid
            elif message.is_response_to(whoami):
                invokerid = message.__getitem__('clid')
                channelid = message.__getitem__('cid')

            #status output for telegram group    
            elif message.is_response():
                clients = 'Currently Online:'
                if debug:  print message
                if 'client_nickname' in message.keys():
                    clients += '\n' + message.__getitem__('client_nickname')
                else :
                    for part in message.responses:
                        clients+='\n' + part['client_nickname']
                clients+='\nlisten: '
                if listen:
                    clients+='True'
                else :
                    clients+='False'
                bot.sendMessage(ts3,clients)  

    time.sleep(1)