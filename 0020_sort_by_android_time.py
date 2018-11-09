import os
import csv
import time
import gc
import re
import copy
from collections import defaultdict
from fileinput import filename

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


FIRST_VALID_ANDROID_DATE = 1396571221202 # 2014 04 04 00 27 01
#MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 691200000 # 8 day
MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 604800000 # 7 day
#MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 2592000000 # 30 day
MIN_DIF_IN_ANDROID_AND_SERVER_TIME = 0
#MAX_DIF_IN_SERVERSAVE_AND_SERVER_TIME = 86400000 # 1 day
LAST_VALID_SERVER_DATE_FOR_FIRSTVERSION_OF_THE_DATA = 1417391999000 # 30 Nov 2014 23:59:59 GMT

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

def toString(originRow,record,numOfLinesPerUser):
  outStr=""+str(originRow)+";"
  for item in record:
    outStr+=item+";"
  outStr+=str(numOfLinesPerUser)
  return outStr

def toString(record):
  for item in record:
    outStr+=item+";"
  return outStr[:-1]

def denoteRecordID(line):
  return line[3]

#MAIN

lastTime = time.time()
lastTime = whatTheTime(lastTime)
#FILE_READING
path = INFILE_PATH
userV1 = defaultdict(dict)
timesV1 = []
userV2 = []
outList = []
numOfRecordAll = 0.0
numOfExaminedRecordAll = 0.0
numOfUser = 0.0
numberOfDeletedDuplicated = 0.0
#numberOfPotentialDuplicated = 0.0
for fileName in os.listdir(path):
  with open(''+path+fileName) as csvfile:
    stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
    i = 1
    for line in stunnerReader:
      appVersion = int(line[8])
      if appVersion >= VERSIONS_SINCE_VERSION_2:
        userV2.append(line)
      else :  
        timesV1.append((line[11],line[0]))
        userV1[line[0]]=line[1:]
    timesV1.sort()
    userV2.sort(key=denoteRecordID)
    numOfLinesPerUser=0
    numOfExaminedLinesPerUser=0
    if len(timesV1) > 0 :
      prevPrintedOriginRow = -1
      prevOriginRow = -1
      numOfChange = 0.0
      for atuple in timesV1:
        numOfExaminedLinesPerUser+=1
        if int(prevOriginRow) > -1 :
          if userV1[prevOriginRow] != userV1[atuple[1]] : 
            if userV1[prevOriginRow][10] == userV1[atuple[1]][10] :
              dif1=""
              dif2=""
              empty1=0
              empty2=0
              stopIndex=0
              equal = True  
              equalAtEveryPostion = True
              for j in range(7, len(userV1[atuple[1]])):
                comparable = True
                bothEmpty = False
                if userV1[prevOriginRow][j] == "" :
                  empty1+=1
                  comparable = False
                if userV1[atuple[1]][j] == "" :
                  if comparable == False :
                    bothEmpty = True
                    empty1-=1
                  else :
                    empty2+=1
                    comparable = False
                if userV1[prevOriginRow][j] != userV1[atuple[1]][j] :
                  equalAtEveryPostion = False  
                if comparable == True and userV1[prevOriginRow][j] != userV1[atuple[1]][j] :
                  dif1=userV1[prevOriginRow][j]
                  dif2=userV1[atuple[1]][j]
                  stopIndex=j
                  equal = False
                  break
              if equalAtEveryPostion == False :
                if equal == True :
                  if empty1 > empty2 :
                    prevOriginRow = atuple[1]
                  numberOfDeletedDuplicated+=1.0 
                else :
                  if userV1[prevOriginRow][35] != userV1[atuple[1]][35] and userV1[prevOriginRow][35] == "7":
                    if int(prevPrintedOriginRow) > -1 :
                      if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(prevOriginRow,userV1[prevOriginRow],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                    prevOriginRow = atuple[1]
                  elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] and userV1[atuple[1]][35] == "7":
                    if int(prevPrintedOriginRow) > -1 :
                      if int(userV1[prevPrintedOriginRow][0]) > int(userV1[atuple[1]][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(atuple[1],userV1[atuple[1]],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(atuple[1])
                    prevOriginRow = prevOriginRow
                  elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                    userV1[prevOriginRow][8] == "NA" and userV1[atuple[1]][8] != "NA": 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                    userV1[prevOriginRow][8] != "NA" and userV1[atuple[1]][8] == "NA": 
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                  userV1[prevOriginRow][8] == userV1[prevPrintedOriginRow][8] and userV1[atuple[1]][8] != userV1[prevPrintedOriginRow][8] :
                    if int(prevPrintedOriginRow) > -1 :
                      if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(prevOriginRow,userV1[prevOriginRow],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                    prevOriginRow = atuple[1]
                  elif userV1[prevOriginRow][8] != userV1[atuple[1]][8] and \
                  userV1[prevOriginRow][8] != userV1[prevPrintedOriginRow][8] and userV1[atuple[1]][8] == userV1[prevPrintedOriginRow][8] : 
                    if int(prevPrintedOriginRow) > -1 :
                      if int(userV1[prevPrintedOriginRow][0]) > int(userV1[atuple[1]][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(atuple[1],userV1[atuple[1]],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(atuple[1])
                    prevOriginRow = prevOriginRow
                  elif userV1[prevOriginRow][14] != userV1[atuple[1]][14] :
                    if userV1[atuple[1]][36] not in VERSIONS_STUN_SERVER_OK and userV1[atuple[1]][14] == "1" :
                      prevOriginRow = prevOriginRow 
                    elif userV1[prevOriginRow][36] not in VERSIONS_STUN_SERVER_OK and userV1[prevOriginRow] == "1" :
                      prevOriginRow = atuple[1]
                    elif userV1[atuple[1]][14] in OFFLINE_NAT_TYPES :
                      userV1[atuple[1]][14] = "-2"
                      prevOriginRow = atuple[1]
                    elif userV1[prevOriginRow][14] in OFFLINE_NAT_TYPES :
                      userV1[prevOriginRow][14] = "-2"
                      prevOriginRow = prevOriginRow 
                    elif (userV1[atuple[1]][14] in SYMMETRIC_NAT_TYPES and \
                         (userV1[prevOriginRow][14] in OPEN_NAT_TYPES or userV1[prevOriginRow][14] in RESTRICTED_NAT_TYPES or userV1[prevOriginRow][14] in PORTRESTRICTED_NAT_TYPES) ) or \
                        (userV1[atuple[1]][14] in PORTRESTRICTED_NAT_TYPES and (userV1[prevOriginRow][14] in OPEN_NAT_TYPES or userV1[prevOriginRow][14] in RESTRICTED_NAT_TYPES) ) or \
                        (userV1[atuple[1]][14] in RESTRICTED_NAT_TYPES and userV1[atuple[1]][14] in OPEN_NAT_TYPES) :
                      prevOriginRow = atuple[1]
                    else :  
                      prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0
                  elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] and \
                  userV1[atuple[1]][35] in CONNECTION_TRIGER and userV1[prevOriginRow][35] not in CONNECTION_TRIGER :
                    #if the rec == connection trigger and the prev wont  
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] and \
                  userV1[atuple[1]][35] not in CONNECTION_TRIGER and userV1[prevOriginRow][35] in CONNECTION_TRIGER :
                    #if the prev == connection trigger and the rec wont
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif getMobileNetworkTypeState(userV1[atuple[1]][30]) < getMobileNetworkTypeState(userV1[prevOriginRow][30]) :
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif getMobileNetworkTypeState(userV1[atuple[1]][30]) > getMobileNetworkTypeState(userV1[prevOriginRow][30]) :
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][9] != userV1[atuple[1]][9] and \
                    userV1[prevOriginRow][9] == "NA" and userV1[atupl[1]][9] != "NA": 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][9] != userV1[atuple[1]][9] and \
                    userV1[prevOriginRow][9] != "NA" and userV1[atuple[1]][9] == "NA": 
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0
                  elif userV1[prevOriginRow][11] != userV1[atuple[1]][11] and \
                    float(userV1[prevOriginRow][11]) == 0.0 and float(userV1[atuple[1]][11]) != 0.0 :
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][11] != userV1[atuple[1]][11] and \
                    float(userV1[prevOriginRow][11]) != 0.0 and float(userV1[atuple[1]][11]) == 0.0 :
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][12] != userV1[atuple[1]][12] and \
                    float(userV1[prevOriginRow][12]) == 0.0 and float(userV1[atuple[1]][12]) != 0.0 :
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][12] != userV1[atuple[1]][12] and \
                    float(userV1[prevOriginRow][12]) != 0.0 and float(userV1[atuple[1]][12]) == 0.0 :
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0
                  elif userV1[prevOriginRow][18] != userV1[atuple[1]][18] :
                    if (userV1[prevOriginRow][18] in BATTERY_PLUGGED_STATE and userV1[prevOriginRow][23] in BATTERY_STATUS_CHARGING) or \
                    (userV1[prevOriginRow][18] not in BATTERY_PLUGGED_STATE and userV1[prevOriginRow][23] not in BATTERY_STATUS_CHARGING) :
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated+=1.0
                    else :  
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated+=1.0
                  elif userV1[prevOriginRow][13] != userV1[atuple[1]][13] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0       
                  elif userV1[prevOriginRow][19] != userV1[atuple[1]][19] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0  
                  elif userV1[prevOriginRow][20] != userV1[atuple[1]][20] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][21] != userV1[atuple[1]][21] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0
                  elif userV1[prevOriginRow][24] != userV1[atuple[1]][24] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0
                  elif userV1[prevOriginRow][26] != userV1[atuple[1]][26] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0  
                  elif userV1[prevOriginRow][30] != userV1[atuple[1]][30] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0    
                  elif userV1[prevOriginRow][34] != userV1[atuple[1]][34] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif userV1[prevOriginRow][35] != userV1[atuple[1]][35] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0   
                  else :
                    print("isEqual:"+str(equal)+"E1:"+str(empty1)+"E2:"+str(empty2)+"DiffAtIndex:"+str(stopIndex)+"=>"+dif1+"!="+dif2+"========================================================================================================================")
                    print(userV1[atuple[1]])
                    print(userV1[prevOriginRow])
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
              else :
                prevOriginRow = atuple[1]
                numberOfDeletedDuplicated+=1.0       
            else :
              if int(prevPrintedOriginRow) > -1 :
                if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]) :
                #if int(userV1[prevPrintedOriginRow][0])+1 != int(userV1[prevOriginRow][0]) and int(userV1[prevPrintedOriginRow][0]) != int(userV1[prevOriginRow][0]) : #!TODO 
                  numOfChange += 1.0
              numOfLinesPerUser+=1
              file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
              file.write(''+toString(prevOriginRow,userV1[prevOriginRow],numOfLinesPerUser)+'\n')
              file.close()
              prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
              prevOriginRow = atuple[1]
          else:
            prevOriginRow = atuple[1]
            numberOfDeletedDuplicated+=1.0
        else :
          prevOriginRow = atuple[1] # first assignment    
      if int(prevOriginRow) > -1 :
        if int(prevPrintedOriginRow) > -1 :
          if int(userV1[prevPrintedOriginRow][0]) > int(userV1[prevOriginRow][0]) : #!TODO 
            numOfChange += 1.0
        numOfLinesPerUser+=1
        file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
        file.write(''+toString(prevOriginRow,userV1[prevOriginRow],numOfLinesPerUser)+'\n')
        file.close()
      
    if len(userV2) > 0 :
      for line in userV2 :
        file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
        file.write(''+toString(line)+'\n')
        file.close()
    userV1.clear()
    timesV1.clear()
    userV2.clear()
    numOfUser+=1
    numOfRecordAll+=numOfLinesPerUser
    numOfExaminedRecordAll+=numOfExaminedLinesPerUser
    if numOfUser%100==0 :
      n = gc.collect()
    if numOfLinesPerUser > 1 :
      outList.append((numOfChange/(numOfLinesPerUser-1),[fileName,numOfLinesPerUser,numOfChange]))
    else:
      outList.append((0.0,[fileName,numOfLinesPerUser,numOfChange]))
outList.sort(reverse=True)
file = open("000000000000000000000", "a+", encoding="utf-8")
for outLine in outList :
  file.write(''+str(outLine[1][0])+" "+str(outLine[1][1])+" "+str(outLine[1][2])+" "+str(outLine[0])+'\n')
file.close()
print("TotalNumberOfExaminedRecord: "+str(numOfExaminedRecordAll)+" NumberOfAppropriateRecord: "+str(numOfRecordAll)+" NumberOfDeletedDuplicated: "+str(numberOfDeletedDuplicated))#+" NumberOfPotentialDuplicated: "+str(numberOfPotentialDuplicated))
lastTime = whatTheTime(lastTime)
