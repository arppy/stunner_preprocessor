import os
import csv
import time
import gc
import sys
import re
import copy
from collections import defaultdict
from fileinput import filename
import multiprocessing
import datetime


OUTFILE_PATH = 'out2/'
INFILE_PATH = 'out/'

#TRIGER_PRIORITY_LIST = ["9","8","1","7","6","3","4","2","5","1","-1"]

OFFLINE_NAT_TYPES = set(['-2', '-1', '1'])
SYMMETRIC_NAT_TYPES = set(['2', '6'])
RESTRICTED_NAT_TYPES =  set(['4'])
PORTRESTRICTED_NAT_TYPES =  set(['4'])
OPEN_NAT_TYPES = set(['0', '3'])

CONNECTION_TRIGER = set(['1', '7', '8'])
SYSTEM_TRIGER = set(['6', '10', '14', '16', '19'])
BATTERY_TRIGER = set(['2', '3', '4'])
OTHER_TRIGER = set(['-1', '0', '5', '9', '11', '13', '15', '17', '18'])

BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

VERSIONS_SINCE_STUN_SERVER_OK = 14
VERSIONS_SINCE_VERSION_2 = 20

DEVELOPMENT_VERSIONS = set([19])

NAT_AND_WEBRTC_FIELDS = set([24,25,26,27,28,29,30,31,32,33])
FIELDS_FOR_EQUALS = [2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52]
HASHED_FIELDS = set([2,12,13])

FIRST_VALID_ANDROID_DATE = 1396571221202 # 2014 04 04 00 27 01
#MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 691200000 # 8 day
MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 604800000 # 7 day
#MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 2592000000 # 30 day
MIN_DIF_IN_ANDROID_AND_SERVER_TIME = 0
#MAX_DIF_IN_SERVERSAVE_AND_SERVER_TIME = 86400000 # 1 day
LAST_VALID_SERVER_DATE_FOR_FIRSTVERSION_OF_THE_DATA = 1417391999000 # 30 Nov 2014 23:59:59 GMT

if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] is not None and str.isnumeric(sys.argv[1]):
  NUMBER_OF_CORES = int(sys.argv[1])
else :
  NUMBER_OF_CORES = 1

TO_PUBLIC = False
if len(sys.argv) > 2 and sys.argv[2] and sys.argv[2] is not None and sys.argv[2] == "toPublic":
  TO_PUBLIC = True

def getMobileNetworkTypeState(networkTypeR):  #slow: 0 ; fast: 1;
  networkTypeStr = str(networkTypeR)
  if networkTypeStr == "UNKNOWN" or networkTypeStr == "NA" or \
  networkTypeStr == "CDMA" or networkTypeStr == "IS-95" or networkTypeStr == "IS95" or \
  networkTypeStr == "iDen" or \
  networkTypeStr == "GPRS" or \
  networkTypeStr == "EDGE" or \
  networkTypeStr == "1xRTT" :
    return 0
  elif networkTypeStr == "EVDO_0" or networkTypeStr == "EV-DO Rel.0" or networkTypeStr == "EV-DORel.0" or \
       networkTypeStr == "EVDO_A" or networkTypeStr == "EV-DO Rev.A" or networkTypeStr == "EV-DORev.A" or \
       networkTypeStr == "eHRPD" or \
       networkTypeStr == "EVDO_B" or networkTypeStr == "EV-DO Rev.B" or networkTypeStr == "EV-DORev.B" or \
       networkTypeStr == "UMTS" or \
       networkTypeStr == "HSPA" or networkTypeStr == "HSDPA" or networkTypeStr == "HSUPA" or networkTypeStr == "HSPDA" or \
       networkTypeStr == "HSPA+" or \
       networkTypeStr == "LTE" : 
    return 1
  else :
    if networkTypeR != "" :
      print(networkTypeStr)
    return 0

def whatTheTime(lastTime):
  print("elapsed: ",time.time() - lastTime)
  return time.time()

def toStringV1(originRow,record,numOfLinesPerUser):
  outStr=""+str(originRow)+";"
  for item in record:
    outStr+=item+";"
  outStr+=str(numOfLinesPerUser)
  return outStr

def toStringV2(record):
  outStr=""
  for item in record:
    outStr+=item+";"
  return outStr[:-1]

def denoteRecordID(line):
  return int(line[3])

def denoteTimestamp(line):
  return int(line[4])

def denoteServerOrder(line):
  return int(line[53])

def isNatAndWebRtcdiscovery(line):
  if(line[27] and line[30] and line[31]) :
    return True
  return False

def sortAndDuplicateFiltering(fileList, outSufix):
  lastTime = time.time()
  lastTime = whatTheTime(lastTime)
  # FILE_READING
  user = []
  outUser = []
  outList = []
  prevline = []
  numOfRecordAll = 0.0
  numOfExaminedRecordAll = 0.0
  numOfUser = 0.0
  numberOfDeletedDuplicated = 0.0
  jMax = 0
  # numberOfPotentialDuplicated = 0.0
  for fileName in fileList:
    with open(''+INFILE_PATH+fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      for line in stunnerReader:
        user.append(line)
      user.sort(key=denoteTimestamp)
      for line in user :
        if len(prevline) > 0 :
          equals = True
          lineHasMore = True
          prevLineHasMore = True
          for j in FIELDS_FOR_EQUALS :
            if line[j] == "" and prevline[j] != "" :
              lineHasMore = False
            elif line[j] != "" and prevline[j] == "" :
              prevLineHasMore = False
            elif line[j] != prevline[j] :
              equals = False
              if jMax<j :
                jMax=j
              break;
            if lineHasMore == False and prevLineHasMore == False :
              equals = False
              if jMax < j:
                jMax = j
              break;
          if equals == True :
            numberOfDeletedDuplicated+=1.0
            if lineHasMore == True :
              prevline = line
          else :
            outUser.append(prevline)
            prevline = line
        else :
          prevline = line
      outUser.append(prevline)
      if TO_PUBLIC == True :
        outUser.sort(key=denoteServerOrder)
      prevTempDate = ""
      file = open('' + OUTFILE_PATH + str(outSufix) + '/' + fileName+'.'+prevTempDate, "a+", encoding="utf-8")
      for line in outUser :
        if str(line[0]) != "1391385600000" and  str(line[0]) != "1409529600000" and str(line[0]) != "1412121600000":
          serverTimestamp = int(line[0])/1000
        else :
          serverTimestamp = int(line[1])/1000
        tempDate = str(datetime.datetime.fromtimestamp(serverTimestamp).strftime('%Y-%m'))
        if tempDate != prevTempDate :
          file.close()
          file = open('' + OUTFILE_PATH + str(outSufix) + '/' + fileName+'.'+tempDate, "a+", encoding="utf-8")
        file.write('' + toStringV2(line) + '\n')
        prevTempDate = tempDate
      file.close()
      numOfUser+=1
      numOfRecordAll+=len(outUser)
      numOfExaminedRecordAll+=len(user)
      user.clear()
      outUser.clear()
      prevline.clear()
      if numOfUser%100==0 :
        n = gc.collect()
  print("TotalNumberOfExaminedRecord: " + str(numOfExaminedRecordAll) + " NumberOfAppropriateRecord: " + str(numOfRecordAll) + " NumberOfDeletedDuplicated: " + str(numberOfDeletedDuplicated), jMax)
  lastTime = whatTheTime(lastTime)

#MAIN
fileList = {}
for core in range(NUMBER_OF_CORES) :
  fileList[core] = []
# FILE_READING
files = os.listdir(INFILE_PATH)
files.sort()
THREAD_FILE_NUMBER_BLOCK_SIZE = int(len(files)/NUMBER_OF_CORES)
fi=0
core = 0
print(str(os.path.getsize(INFILE_PATH)),os.stat(INFILE_PATH))
sumOfSize = 0
for fileName in files:
  sumOfSize+=os.path.getsize(INFILE_PATH+'/'+fileName)
THREAD_FILE_SIZE_BLOCK_SIZE = int(sumOfSize/NUMBER_OF_CORES)
#print(str(0),sumOfSize,str(THREAD_FILE_SIZE_BLOCK_SIZE),str(NUMBER_OF_CORES*THREAD_FILE_SIZE_BLOCK_SIZE))
for fileName in files:
  #searchObj = re.search(r'^[0-9]{6}_2014[0-9]{4}-[0-9]{4}\.csv$', fileName)
  fileList[core].append(fileName)
  fi+=os.path.getsize(INFILE_PATH+'/'+fileName)
  if fi / THREAD_FILE_SIZE_BLOCK_SIZE > 1 and core != NUMBER_OF_CORES-1:
    sumOfSize -= fi
    core += 1
    THREAD_FILE_SIZE_BLOCK_SIZE = int(sumOfSize / (NUMBER_OF_CORES-core))
    #print(fi, sumOfSize, str(THREAD_FILE_SIZE_BLOCK_SIZE), str(NUMBER_OF_CORES-core))
    fi = 0
#print(fi, sumOfSize, str(THREAD_FILE_SIZE_BLOCK_SIZE), str(NUMBER_OF_CORES-core))
processes = []
for core in range(NUMBER_OF_CORES) :
  processes.append(multiprocessing.Process(target=sortAndDuplicateFiltering, args=(fileList[core], core)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()