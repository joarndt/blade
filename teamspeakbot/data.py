import pickle

# class that contains necessary data for the Teamspeakbot
# it reads and saves necessary data in files
class Data(object):

    def __init__(self):

        # create or read Bot Data
        try:
            self.botData = self.readBotData()
        except (OSError, IOError, EOFError) as e:
            self.botData = dict()
            self.writeBotData()

        # create or read user Info
        try:
            self.userInfo = self.readUserInfo()
        except (OSError, IOError, EOFError) as e:
            self.userInfo = dict()
            self.writeUserInfo()

        if 'token' not in self.botData:
            tmp = raw_input("please enter Telegram Bot Token:").replace("\n", "").replace(" ","")
            self.botData['token'] = tmp

        if 'auth' not in self.botData:
            tmp = raw_input("please enter ClientQuery API Key:").replace("\n", "").replace(" ","")
            self.botData['auth'] = tmp

        if 'chatId' not in self.botData:
            print "please write in Telegram to get the chat which should be used"

    def __enter__(self, *args, **kwargs):
        return Data(*args, **kwargs)

    # read and write with pickle for data
    def readUserInfo(self):
        with open("clientInfo.pkl", "rb") as file:
            return pickle.load(file)

    def writeUserInfo(self):
        with open("clientInfo.pkl", "wb") as file:
            pickle.dump(self.userInfo, file)

    def readBotData(self):
        with open("data.pkl", "rb") as file:
            return pickle.load(file)

    def writeBotData(self):
        with open("data.pkl", "wb") as file:
            return pickle.dump(self.botData, file)

    def isUser(self, id):
    	return id in self.userInfo

    # getter and setter for data
    def getUserInfo(self):
        return self.userInfo

    def setUsername(self, id, username):
    	self.userInfo[id] = (self.userInfo[id][0] if id in self.userInfo else "[color=#aaaaaa]", username)
    	self.writeUserInfo()

    def setUsercolor(self, id, usercolor, username):
    	# checks if its a valid hex RGB code
        if len(usercolor) == 6:
            for part in usercolor:
                number= ord(part)
                if (number < 48 or number > 57) and (number < 97 or number > 102):
                    self.writeTelegram("its not a valid Hex RGB code")
                    return False

        self.userInfo[id]= ("[color=#" + usercolor + "]", username)
        self.writeUserInfo()
        return True

    def getUsercolor(self, id):
    	return self.userInfo[id][0]

    def getUsername(self, id):
    	return self.userInfo[id][1]

    def getBotData(self):
        return self.botData

    def getToken(self):
    	return self.botData['token']

    def getAuth(self):
    	return self.botData['auth']

    def getChatId(self):
    	return self.botData['chatId'] if 'chatId' in self.botData else "0"

    def setChatId(self, id):
    	self.botData['chatId'] = id
    	self.writeBotData()