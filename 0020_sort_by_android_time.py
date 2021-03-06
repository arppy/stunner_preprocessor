import os
import csv
import time
import gc
import re
import sys
import copy
from collections import defaultdict
from fileinput import filename
import multiprocessing


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
  return int(line[4])

def isNatAndWebRtcdiscovery(line):
  if(line[27] and line[30] and line[31]) :
    return True
  return False

def sortAndDuplicateFiltering(fileList) :
  userV1 = defaultdict(dict)
  timesV1 = []
  userV2 = []
  numOfRecordAll = 0.0
  numOfExaminedRecordAll = 0.0
  numOfUser = 0.0
  numberOfDeletedDuplicated = 0.0
  for fileName in fileList:
    with open('' + INFILE_PATH + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      i = 1
      for line in stunnerReader:
        try:
          appVersion = int(line[8])
        except:
          appVersion = VERSIONS_SINCE_VERSION_2 - 1
        if appVersion >= VERSIONS_SINCE_VERSION_2:
          userV2.append(line)
        else:
          timesV1.append((line[11], line[0]))
          userV1[line[0]] = line[1:]
      timesV1.sort()
      userV2.sort(key=denoteRecordID)
      numOfLinesPerUser = 0
      numOfExaminedLinesPerUser = 0
      numOfChange = 0.0
      prevPrintedOriginRow = -1
      prevOriginRow = -1
      if len(timesV1) > 0:
        for atuple in timesV1:
          numOfExaminedLinesPerUser += 1
          if int(prevOriginRow) > -1:
            if userV1[prevOriginRow] != userV1[atuple[1]]:
              if userV1[prevOriginRow][10] == userV1[atuple[1]][10]:
                dif1 = ""
                dif2 = ""
                empty1 = 0
                empty2 = 0
                stopIndex = 0
                equal = True
                equalAtEveryPostion = True
                for j in range(7, len(userV1[atuple[1]])):
                  comparable = True
                  bothEmpty = False
                  if userV1[prevOriginRow][j] == "":
                    empty1 += 1
                    comparable = False
                  if userV1[atuple[1]][j] == "":
                    if comparable == False:
                      bothEmpty = True
                      empty1 -= 1
                    else:
                      empty2 += 1
                      comparable = False
                  if userV1[prevOriginRow][j] != userV1[atuple[1]][j]:
                    equalAtEveryPostion = False
                  if comparable == True and userV1[prevOriginRow][j] != userV1[atuple[1]][j]:
                    dif1 = userV1[prevOriginRow][j]
                    dif2 = userV1[atuple[1]][j]
                    stopIndex = j
                    equal = False
                    break
                if equalAtEveryPostion == False:
                  if equal == True:
                    if empty1 > empty2:
                      prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated += 1.0
                  else:
                    if userV1[prevOriginRow][35] != userV1[atuple[1]][35] and userV1[prevOriginRow][35] == "7":
                      if int(prevPrintedOriginRow) > -1:
                        if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]):
                          numOfChange += 1.0
                      numOfLinesPerUser += 1
                      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
                      file.write('' + toStringV1(prevOriginRow, userV1[prevOriginRow], numOfLinesPerUser) + '\n')
                      file.close()
                      prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                      prevOriginRow = atuple[1]
                    elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] and userV1[atuple[1]][35] == "7":
                      if int(prevPrintedOriginRow) > -1:
                        if int(userV1[prevPrintedOriginRow][0]) > int(userV1[atuple[1]][0]):
                          numOfChange += 1.0
                      numOfLinesPerUser += 1
                      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
                      file.write('' + toStringV1(atuple[1], userV1[atuple[1]], numOfLinesPerUser) + '\n')
                      file.close()
                      prevPrintedOriginRow = copy.deepcopy(atuple[1])
                      prevOriginRow = prevOriginRow
                    elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                        userV1[prevOriginRow][8] == "NA" and userV1[atuple[1]][8] != "NA":
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                        userV1[prevOriginRow][8] != "NA" and userV1[atuple[1]][8] == "NA":
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                        userV1[prevOriginRow][8] == userV1[prevPrintedOriginRow][8] and userV1[atuple[1]][8] != \
                        userV1[prevPrintedOriginRow][8]:
                      if int(prevPrintedOriginRow) > -1:
                        if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]):
                          numOfChange += 1.0
                      numOfLinesPerUser += 1
                      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
                      file.write('' + toStringV1(prevOriginRow, userV1[prevOriginRow], numOfLinesPerUser) + '\n')
                      file.close()
                      prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                      prevOriginRow = atuple[1]
                    elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                        userV1[prevOriginRow][8] != userV1[prevPrintedOriginRow][8] and userV1[atuple[1]][8] == \
                        userV1[prevPrintedOriginRow][8]:
                      if int(prevPrintedOriginRow) > -1:
                        if int(userV1[prevPrintedOriginRow][0]) > int(userV1[atuple[1]][0]):
                          numOfChange += 1.0
                      numOfLinesPerUser += 1
                      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
                      file.write('' + toStringV1(atuple[1], userV1[atuple[1]], numOfLinesPerUser) + '\n')
                      file.close()
                      prevPrintedOriginRow = copy.deepcopy(atuple[1])
                      prevOriginRow = prevOriginRow
                    elif userV1[prevOriginRow][14] != userV1[atuple[1]][14]:
                      if userV1[atuple[1]][36] and int(userV1[atuple[1]][36]) >= VERSIONS_SINCE_STUN_SERVER_OK and \
                          userV1[atuple[1]][14] == "1":
                        prevOriginRow = prevOriginRow
                      elif userV1[prevOriginRow][36] and int(
                          userV1[prevOriginRow][36]) >= VERSIONS_SINCE_STUN_SERVER_OK and userV1[prevOriginRow] == "1":
                        prevOriginRow = atuple[1]
                      elif userV1[atuple[1]][14] in OFFLINE_NAT_TYPES:
                        userV1[atuple[1]][14] = "-2"
                        prevOriginRow = atuple[1]
                      elif userV1[prevOriginRow][14] in OFFLINE_NAT_TYPES:
                        userV1[prevOriginRow][14] = "-2"
                        prevOriginRow = prevOriginRow
                      elif (userV1[atuple[1]][14] in SYMMETRIC_NAT_TYPES and \
                            (userV1[prevOriginRow][14] in OPEN_NAT_TYPES or userV1[prevOriginRow][
                              14] in RESTRICTED_NAT_TYPES or userV1[prevOriginRow][14] in PORTRESTRICTED_NAT_TYPES)) or \
                          (userV1[atuple[1]][14] in PORTRESTRICTED_NAT_TYPES and (
                              userV1[prevOriginRow][14] in OPEN_NAT_TYPES or userV1[prevOriginRow][
                            14] in RESTRICTED_NAT_TYPES)) or \
                          (userV1[atuple[1]][14] in RESTRICTED_NAT_TYPES and userV1[atuple[1]][14] in OPEN_NAT_TYPES):
                        prevOriginRow = atuple[1]
                      else:
                        prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] and \
                        userV1[atuple[1]][35] in CONNECTION_TRIGER and userV1[prevOriginRow][
                      35] not in CONNECTION_TRIGER:
                      # if the rec == connection trigger and the prev wont
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] and \
                        userV1[atuple[1]][35] not in CONNECTION_TRIGER and userV1[prevOriginRow][
                      35] in CONNECTION_TRIGER:
                      # if the prev == connection trigger and the rec wont
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif getMobileNetworkTypeState(userV1[atuple[1]][30]) < getMobileNetworkTypeState(
                        userV1[prevOriginRow][30]):
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif getMobileNetworkTypeState(userV1[atuple[1]][30]) > getMobileNetworkTypeState(
                        userV1[prevOriginRow][30]):
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][9] != userV1[atuple[1]][9] and \
                        userV1[prevOriginRow][9] == "NA" and userV1[atuple[1]][9] != "NA":
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][9] != userV1[atuple[1]][9] and \
                        userV1[prevOriginRow][9] != "NA" and userV1[atuple[1]][9] == "NA":
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][11] != userV1[atuple[1]][11] and \
                        float(userV1[prevOriginRow][11]) == 0.0 and float(userV1[atuple[1]][11]) != 0.0:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][11] != userV1[atuple[1]][11] and \
                        float(userV1[prevOriginRow][11]) != 0.0 and float(userV1[atuple[1]][11]) == 0.0:
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][12] != userV1[atuple[1]][12] and \
                        float(userV1[prevOriginRow][12]) == 0.0 and float(userV1[atuple[1]][12]) != 0.0:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][12] != userV1[atuple[1]][12] and \
                        float(userV1[prevOriginRow][12]) != 0.0 and float(userV1[atuple[1]][12]) == 0.0:
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][18] != userV1[atuple[1]][18]:
                      if (userV1[prevOriginRow][18] in BATTERY_PLUGGED_STATE and userV1[prevOriginRow][
                        23] in BATTERY_STATUS_CHARGING) or \
                          (userV1[prevOriginRow][18] not in BATTERY_PLUGGED_STATE and userV1[prevOriginRow][
                            23] not in BATTERY_STATUS_CHARGING):
                        prevOriginRow = prevOriginRow
                        numberOfDeletedDuplicated += 1.0
                      else:
                        prevOriginRow = atuple[1]
                        numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][13] != userV1[atuple[1]][13]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][19] != userV1[atuple[1]][19]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][20] != userV1[atuple[1]][20]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][21] != userV1[atuple[1]][21]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][24] != userV1[atuple[1]][24]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][26] != userV1[atuple[1]][26]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][30] != userV1[atuple[1]][30]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][34] != userV1[atuple[1]][34]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    elif userV1[prevOriginRow][35] != userV1[atuple[1]][35]:
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                    else:
                      print("isEqual:" + str(equal) + "E1:" + str(empty1) + "E2:" + str(empty2) + "DiffAtIndex:" + str(
                        stopIndex) + "=>" + dif1 + "!=" + dif2 + "========================================================================================================================")
                      print(userV1[atuple[1]])
                      print(userV1[prevOriginRow])
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated += 1.0
                else:
                  prevOriginRow = atuple[1]
                  numberOfDeletedDuplicated += 1.0
              else:
                if int(prevPrintedOriginRow) > -1:
                  if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]):
                    # if int(userV1[prevPrintedOriginRow][0])+1 != int(userV1[prevOriginRow][0]) and int(userV1[prevPrintedOriginRow][0]) != int(userV1[prevOriginRow][0]) : #!TODO
                    numOfChange += 1.0
                numOfLinesPerUser += 1
                file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
                file.write('' + toStringV1(prevOriginRow, userV1[prevOriginRow], numOfLinesPerUser) + '\n')
                file.close()
                prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                prevOriginRow = atuple[1]
            else:
              prevOriginRow = atuple[1]
              numberOfDeletedDuplicated += 1.0
          else:
            prevOriginRow = atuple[1]  # first assignment
        if int(prevOriginRow) > -1:
          if int(prevPrintedOriginRow) > -1:
            if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]):  # !TODO
              numOfChange += 1.0
          numOfLinesPerUser += 1
          file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
          file.write('' + toStringV1(prevOriginRow, userV1[prevOriginRow], numOfLinesPerUser) + '\n')
          file.close()

      if len(userV2) > 0:
        prevline = []
        file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
        for line in userV2:
          numOfExaminedLinesPerUser += 1
          isPrintPrevLine = True
          isDropThisLine = False
          if len(prevline) > 0 and line[3] == prevline[3]:
            isPrintPrevLine = False
            for j in range(2, len(prevline)):
              if j in NAT_AND_WEBRTC_FIELDS or j in HASHED_FIELDS:
                continue
              if line[j] != prevline[j]:
                isPrintPrevLine = True
                print(fileName, str(j), '----------')
                print(toStringV2(prevline))
                print(toStringV2(line))
                break
            if not isPrintPrevLine and isNatAndWebRtcdiscovery(prevline) and not isNatAndWebRtcdiscovery(line):
              isDropThisLine = True
          if len(prevline) > 0 and isPrintPrevLine:
            file.write('' + toStringV2(prevline) + '\n')
            numOfLinesPerUser += 1
          else:
            numberOfDeletedDuplicated += 1
          if not isDropThisLine:
            prevline = line;
        file.write('' + toStringV2(prevline) + '\n')
        file.close()
        numOfLinesPerUser += 1
      userV1.clear()
      timesV1.clear()
      userV2.clear()
      numOfUser += 1
      numOfRecordAll += numOfLinesPerUser
      numOfExaminedRecordAll += numOfExaminedLinesPerUser
      if numOfUser % 100 == 0:
        n = gc.collect()


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
  processes.append(multiprocessing.Process(target=sortAndDuplicateFiltering, args=(fileList[core],)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()