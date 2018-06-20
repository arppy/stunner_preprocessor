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
SYSTEM_TRIGER = set(['6', '9'])
BATTERY_AND_OTHER_TRIGER = set(['-1', '0', '2', '3', '4', '5'])

BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

VERSIONS_STUN_SERVER_OK = set(['14'])

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

#MAIN

lastTime = time.time()
lastTime = whatTheTime(lastTime)
#FILE_READING
path = INFILE_PATH
user = defaultdict(dict)
times = []
outList = []
numOfRecordAll = 0.0
numOfExaminedRecordAll = 0.0
numOfUser = 0.0
numberOfDeletedDuplicated = 0.0
#numberOfPotentialDuplicated = 0.0
for fileName in os.listdir(path):
  with open(''+path+fileName) as csvfile:
    stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
    for line in stunnerReader:
      times.append((line[11],line[0]))
      user[line[0]]=line[1:]
    times.sort()
    numOfLinesPerUser=0
    numOfExaminedLinesPerUser=0
    if len(times) > 0 :
      prevPrintedOriginRow = -1
      prevOriginRow = -1
      numOfChange = 0.0
      for atuple in times:
        numOfExaminedLinesPerUser+=1
        if int(prevOriginRow) > -1 :
          if user[prevOriginRow] != user[atuple[1]] : 
            if user[prevOriginRow][10] == user[atuple[1]][10] :
              dif1=""
              dif2=""
              empty1=0
              empty2=0
              stopIndex=0
              equal = True  
              equalAtEveryPostion = True
              for j in range(7, len(user[atuple[1]])):
                comparable = True
                bothEmpty = False
                if user[prevOriginRow][j] == "" :
                  empty1+=1
                  comparable = False
                if user[atuple[1]][j] == "" :
                  if comparable == False :
                    bothEmpty = True
                    empty1-=1
                  else :
                    empty2+=1
                    comparable = False
                if user[prevOriginRow][j] != user[atuple[1]][j] :
                  equalAtEveryPostion = False  
                if comparable == True and user[prevOriginRow][j] != user[atuple[1]][j] :
                  dif1=user[prevOriginRow][j]
                  dif2=user[atuple[1]][j]
                  stopIndex=j
                  equal = False
                  break
              if equalAtEveryPostion == False :
                if equal == True :
                  if empty1 > empty2 :
                    prevOriginRow = atuple[1]
                  numberOfDeletedDuplicated+=1.0 
                else :
                  if user[prevOriginRow][35] != user[atuple[1]][35] and user[prevOriginRow][35] == "7":
                    if int(prevPrintedOriginRow) > -1 :
                      if int(user[prevPrintedOriginRow][0]) > int(user[prevOriginRow][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(prevOriginRow,user[prevOriginRow],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                    prevOriginRow = atuple[1]
                  elif user[prevOriginRow][35] != user[atuple[1]][35] and user[atuple[1]][35] == "7":
                    if int(prevPrintedOriginRow) > -1 :
                      if int(user[prevPrintedOriginRow][0]) > int(user[atuple[1]][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(atuple[1],user[atuple[1]],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(atuple[1])
                    prevOriginRow = prevOriginRow
                  elif user[prevOriginRow][8] != user[atuple[1]][8] and \
                    user[prevOriginRow][8] == "NA" and user[atuple[1]][8] != "NA": 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][8] != user[atuple[1]][8] and \
                    user[prevOriginRow][8] != "NA" and user[atuple[1]][8] == "NA": 
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][8] != user[atuple[1]][8] and \
                  user[prevOriginRow][8] == user[prevPrintedOriginRow][8] and user[atuple[1]][8] != user[prevPrintedOriginRow][8] :
                    if int(prevPrintedOriginRow) > -1 :
                      if int(user[prevPrintedOriginRow][0]) > int(user[prevOriginRow][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(prevOriginRow,user[prevOriginRow],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(prevOriginRow)
                    prevOriginRow = atuple[1]
                  elif user[prevOriginRow][8] != user[atuple[1]][8] and \
                  user[prevOriginRow][8] != user[prevPrintedOriginRow][8] and user[atuple[1]][8] == user[prevPrintedOriginRow][8] : 
                    if int(prevPrintedOriginRow) > -1 :
                      if int(user[prevPrintedOriginRow][0]) > int(user[atuple[1]][0]) : 
                        numOfChange += 1.0
                    numOfLinesPerUser+=1
                    file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
                    file.write(''+toString(atuple[1],user[atuple[1]],numOfLinesPerUser)+'\n')
                    file.close()
                    prevPrintedOriginRow = copy.deepcopy(atuple[1])
                    prevOriginRow = prevOriginRow
                  elif user[prevOriginRow][14] != user[atuple[1]][14] :
                    if user[atuple[1]][36] not in VERSIONS_STUN_SERVER_OK and user[atuple[1]][14] == "1" :
                      prevOriginRow = prevOriginRow 
                    elif user[prevOriginRow][36] not in VERSIONS_STUN_SERVER_OK and user[prevOriginRow] == "1" :
                      prevOriginRow = atuple[1]
                    elif user[atuple[1]][14] in OFFLINE_NAT_TYPES :
                      user[atuple[1]][14] = "-2"
                      prevOriginRow = atuple[1]
                    elif user[prevOriginRow][14] in OFFLINE_NAT_TYPES :
                      user[prevOriginRow][14] = "-2"
                      prevOriginRow = prevOriginRow 
                    elif (user[atuple[1]][14] in SYMMETRIC_NAT_TYPES and \
                         (user[prevOriginRow][14] in OPEN_NAT_TYPES or user[prevOriginRow][14] in RESTRICTED_NAT_TYPES or user[prevOriginRow][14] in PORTRESTRICTED_NAT_TYPES) ) or \
                        (user[atuple[1]][14] in PORTRESTRICTED_NAT_TYPES and (user[prevOriginRow][14] in OPEN_NAT_TYPES or user[prevOriginRow][14] in RESTRICTED_NAT_TYPES) ) or \
                        (user[atuple[1]][14] in RESTRICTED_NAT_TYPES and user[atuple[1]][14] in OPEN_NAT_TYPES) :
                      prevOriginRow = atuple[1]
                    else :  
                      prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0
                  elif user[prevOriginRow][35] != user[atuple[1]][35] and \
                  user[atuple[1]][35] in CONNECTION_TRIGER and user[prevOriginRow][35] not in CONNECTION_TRIGER :
                    #if the rec == connection trigger and the prev wont  
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][35] != user[atuple[1]][35] and \
                  user[atuple[1]][35] not in CONNECTION_TRIGER and user[prevOriginRow][35] in CONNECTION_TRIGER :
                    #if the prev == connection trigger and the rec wont
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif getMobileNetworkTypeState(user[atuple[1]][30]) < getMobileNetworkTypeState(user[prevOriginRow][30]) :
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif getMobileNetworkTypeState(user[atuple[1]][30]) > getMobileNetworkTypeState(user[prevOriginRow][30]) :
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][9] != user[atuple[1]][9] and \
                    user[prevOriginRow][9] == "NA" and user[atupl[1]][9] != "NA": 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][9] != user[atuple[1]][9] and \
                    user[prevOriginRow][9] != "NA" and user[atuple[1]][9] == "NA": 
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0
                  elif user[prevOriginRow][11] != user[atuple[1]][11] and \
                    float(user[prevOriginRow][11]) == 0.0 and float(user[atuple[1]][11]) != 0.0 :
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][11] != user[atuple[1]][11] and \
                    float(user[prevOriginRow][11]) != 0.0 and float(user[atuple[1]][11]) == 0.0 :
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][12] != user[atuple[1]][12] and \
                    float(user[prevOriginRow][12]) == 0.0 and float(user[atuple[1]][12]) != 0.0 :
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][12] != user[atuple[1]][12] and \
                    float(user[prevOriginRow][12]) != 0.0 and float(user[atuple[1]][12]) == 0.0 :
                    prevOriginRow = prevOriginRow
                    numberOfDeletedDuplicated+=1.0
                  elif user[prevOriginRow][18] != user[atuple[1]][18] :
                    if (user[prevOriginRow][18] in BATTERY_PLUGGED_STATE and user[prevOriginRow][23] in BATTERY_STATUS_CHARGING) or \
                    (user[prevOriginRow][18] not in BATTERY_PLUGGED_STATE and user[prevOriginRow][23] not in BATTERY_STATUS_CHARGING) :
                      prevOriginRow = prevOriginRow
                      numberOfDeletedDuplicated+=1.0
                    else :  
                      prevOriginRow = atuple[1]
                      numberOfDeletedDuplicated+=1.0
                  elif user[prevOriginRow][13] != user[atuple[1]][13] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0       
                  elif user[prevOriginRow][19] != user[atuple[1]][19] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0  
                  elif user[prevOriginRow][20] != user[atuple[1]][20] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][21] != user[atuple[1]][21] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0
                  elif user[prevOriginRow][24] != user[atuple[1]][24] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0
                  elif user[prevOriginRow][26] != user[atuple[1]][26] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0  
                  elif user[prevOriginRow][30] != user[atuple[1]][30] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0    
                  elif user[prevOriginRow][34] != user[atuple[1]][34] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
                  elif user[prevOriginRow][35] != user[atuple[1]][35] : 
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0   
                  else :
                    print("isEqual:"+str(equal)+"E1:"+str(empty1)+"E2:"+str(empty2)+"DiffAtIndex:"+str(stopIndex)+"=>"+dif1+"!="+dif2+"========================================================================================================================")
                    print(user[atuple[1]])
                    print(user[prevOriginRow])
                    prevOriginRow = atuple[1]
                    numberOfDeletedDuplicated+=1.0 
              else :
                prevOriginRow = atuple[1]
                numberOfDeletedDuplicated+=1.0       
            else :
              if int(prevPrintedOriginRow) > -1 :
                if int(user[prevPrintedOriginRow][0]) > int(user[prevOriginRow][0]) :
                #if int(user[prevPrintedOriginRow][0])+1 != int(user[prevOriginRow][0]) and int(user[prevPrintedOriginRow][0]) != int(user[prevOriginRow][0]) : #!TODO 
                  numOfChange += 1.0
              numOfLinesPerUser+=1
              file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
              file.write(''+toString(prevOriginRow,user[prevOriginRow],numOfLinesPerUser)+'\n')
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
          if int(user[prevPrintedOriginRow][0]) > int(user[prevOriginRow][0]) : #!TODO 
            numOfChange += 1.0
        numOfLinesPerUser+=1
        file = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
        file.write(''+toString(prevOriginRow,user[prevOriginRow],numOfLinesPerUser)+'\n')
        file.close()
      user.clear()
      times.clear()
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
