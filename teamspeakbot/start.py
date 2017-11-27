from bot import *
from data import *
import argparse
import logger
import time

# set debugmode
# self.debug = sys.argv[0] == "-debug" or sys.argv[0] == "-d"
# print self.debug, sys.argv[1]

# parser = argparse.ArgumentParser(description='Process some integers.')
# parser.add_argument("-foo", ..., required=True)
# parser.parse_args()

data = Data()
Bot(data)

while 1:
    time.sleep(1)
