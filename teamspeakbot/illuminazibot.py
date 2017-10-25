# The Illumminazibot
import time
import subprocess
import telepot
from telepot.loop import MessageLoop
from message import *
from client import *



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
#variable for invokerid
invokerid = 0


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
client = Client(auth)
client.subscribe()

#start bot with bot_token
bot = telepot.Bot(token)
MessageLoop(bot, handle).run_as_thread()

#command to get current userid
whoami = Command(
    'whoami',
)
client.send_command(whoami)

print 'I am listening ...'

#listen to teamspeakchat
while 1:

    #get teamspeak clientquery messages
    messages = client.get_messages()
    for message in messages:

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

        #status output for telegram group    
        elif message.is_response():
            clients = 'Currently Online:'
            for part in message.responses:
                clients+='\n' + part['client_nickname']
            clients+='\nlisten: '
            if listen:
                clients+='True'
            else :
                clients+='False'
            bot.sendMessage(ts3,clients)  

    time.sleep(1)