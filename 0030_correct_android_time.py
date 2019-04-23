import os
import csv
import time
import gc
from collections import deque

BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

TIMEDIF_SAMESESSION = { 1:1000*60*60,2:1000*60*24.9999 } # {1:one hour,2:24.9999 minute

VERSIONS_SINCE_VERSION_2 = 20

POS_OREDER_BY_SERVERSIDE_TIMESTAMP = { 1: 1}
POS_ANDROID_TIMESTAMP = {1: 11}
POS_BATTERY_PERCENTAGE = {1: 22}
POS_BATTERY_PLUGGED_STATE = {1: 19}
POS_BATTERY_STATUS_CHARGING = {1: 24}
POS_TRIGGER_EVENT = {1: 36}
POS_UPTIME = {1: 35}

OUTFILE_PATH = 'out3/'
#INFILE_PATH = 'outErr/out/' #out2
INFILE_PATH = 'out2/'
#INFILE_PATH = 'out/'

def toString(record,androidSortedValidation) :
  outStr=""+record[0]
  for item in record[1:] :
    outStr+=";"+str(item)
  if androidSortedValidation :
    outStr+=";"+str(androidSortedValidation)  
  return outStr

def whatTheTime(lastTime):
  print("elapsed: ",time.time() - lastTime)
  return time.time()


def isThereAnyError(thisLine, prevLine) :
  if ( thisLine[POS_BATTERY_PERCENTAGE[1]]  == "-2" and prevLine[POS_BATTERY_PERCENTAGE[1]] == "-2" ) :
    return False 
  if ( thisLine[POS_BATTERY_PERCENTAGE[1]]  != "" and prevLine[POS_BATTERY_PERCENTAGE[1]] != "" ) :
    if ( (thisLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_PLUGGED_STATE or thisLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_CHARGING) and
         (prevLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_PLUGGED_STATE or prevLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_CHARGING) and
           int(thisLine[POS_BATTERY_PERCENTAGE[1]]) >= int(prevLine[POS_BATTERY_PERCENTAGE[1]])-1 ) :
      return False
    if ( thisLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_UNPLUGGED_STATE and prevLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_UNPLUGGED_STATE and
           thisLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_NOT_CHARGING and prevLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_NOT_CHARGING and
           int(thisLine[POS_BATTERY_PERCENTAGE[1]]) <= int(prevLine[POS_BATTERY_PERCENTAGE[1]])+1 ) :
      return False
  if ( prevLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_UNPLUGGED_STATE and prevLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_NOT_CHARGING and
     ( thisLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_PLUGGED_STATE or thisLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_CHARGING ) and
       thisLine[POS_TRIGGER_EVENT[1]] == "3" ) :
    return False
  if ( (prevLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_PLUGGED_STATE or prevLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_CHARGING) and
       thisLine[POS_BATTERY_PLUGGED_STATE[1]] in BATTERY_UNPLUGGED_STATE and thisLine[POS_BATTERY_STATUS_CHARGING[1]] in BATTERY_STATUS_NOT_CHARGING and
       thisLine[POS_TRIGGER_EVENT[1]] == "4" ) :
    return False
  if ( thisLine[POS_UPTIME[1]] != "" and prevLine[POS_UPTIME[1]] != "" ) :
    if (int(thisLine[POS_UPTIME[1]]) != 0 and int(prevLine[POS_UPTIME[1]]) != 0 and
        abs((int(thisLine[POS_ANDROID_TIMESTAMP[1]]) - int(prevLine[POS_ANDROID_TIMESTAMP[1]])) - (int(thisLine[POS_UPTIME[1]]) - int(prevLine[POS_UPTIME[1]]))) < 1000 ) :
      return False 
  return True
  
  

#MAIN
lastTime = time.time()
lastTime = whatTheTime(lastTime)
#FILE_READING
path = INFILE_PATH
outList = []
numOfUserAll = 0
numOfRowAll = 0
numOfPrintedAll = 0
numOfDeletedAll = 0
numOfQuestionableAll = 0
for fileName in os.listdir(path):
  numOfAllRowPerThisUser=0
  numOfPrinted = 0
  numOfDeleted = 0
  numOfQuestionable = 0
  printCandidateLines = deque([])
  isQuestionable = False
  isError = False
  prevLine = []
  lastQuestionable = []
  outFile = open(''+OUTFILE_PATH+fileName, "a+", encoding="utf-8")
  outFileRemove = open(''+OUTFILE_PATH+fileName+"REMOVED", "a+", encoding="utf-8")
  with open(''+path+fileName) as csvfile:
    lines = list(csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE, strict=True))
    prevAppVersion = -1
    for line in lines: 
      numOfAllRowPerThisUser+=1
      try : 
        appVersion = int(line[8])
      except :
        appVersion = VERSIONS_SINCE_VERSION_2-1
      if prevAppVersion==-1 :
        prevAppVersion=appVersion
      print(prevLine)
      if appVersion >= VERSIONS_SINCE_VERSION_2:
        if prevAppVersion < VERSIONS_SINCE_VERSION_2 :
          if prevLine : # prevline form prev version => close everything and print
            if isError == True :
              printLine = printCandidateLines.popleft()
              outFile.write(''+toString(printLine,-1)+'\n')
              numOfPrinted+=1
              while printCandidateLines :
                printLine = printCandidateLines.popleft()
                outFileRemove.write(''+toString(printLine,-2)+'\n')
                numOfDeleted+=1
              outFileRemove.write(''+toString(prevLine,-2)+'\n')
              numOfDeleted+=1
            else :
              while printCandidateLines :
                printLine = printCandidateLines.popleft()
                outFile.write(''+toString(printLine,1)+'\n')
                numOfPrinted+=1
                if lastQuestionable == printLine :
                  break
                else :
                  numOfQuestionable+=1
              while printCandidateLines :
                printLine = printCandidateLines.popleft()
                outFile.write(''+toString(printLine,1)+'\n')
                numOfPrinted+=1
              outFile.write(''+toString(prevLine,1)+'\n')
              numOfPrinted+=1
            isQuestionable = False
            isError = False
            lastQuestionable = []
            prevLine = []
        outFile.write('' + toString(line, "") + '\n')
      else :
        if prevLine :
          if int(line[POS_ANDROID_TIMESTAMP[1]]) - int(prevLine[POS_ANDROID_TIMESTAMP[1]]) > TIMEDIF_SAMESESSION or line[POS_TRIGGER_EVENT[1]] == "6":
            if isError == True :
              printLine = printCandidateLines.popleft()
              outFile.write(''+toString(printLine,-1)+'\n')
              numOfPrinted+=1
              while printCandidateLines :
                printLine = printCandidateLines.popleft()
                outFileRemove.write(''+toString(printLine,-2)+'\n')
                numOfDeleted+=1
              outFileRemove.write(''+toString(prevLine,-2)+'\n')
              numOfDeleted+=1    
            else :  
              while printCandidateLines :
                printLine = printCandidateLines.popleft()
                outFile.write(''+toString(printLine,1)+'\n')
                numOfPrinted+=1
                if lastQuestionable == printLine :
                  break
                else :
                  numOfQuestionable+=1
              while printCandidateLines :
                printLine = printCandidateLines.popleft()
                outFile.write(''+toString(printLine,1)+'\n')
                numOfPrinted+=1    
              outFile.write(''+toString(prevLine,1)+'\n')
              numOfPrinted+=1
            isQuestionable = False
            isError = False
            lastQuestionable = []
          else :  
            isErrorNow = isThereAnyError(line, prevLine)  
            if isQuestionable == False :
              if int(line[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) - int(prevLine[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) == 1 \
               or int(line[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) - int(prevLine[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) == 0 :
                outFile.write(''+toString(prevLine,2)+'\n')      
                numOfPrinted+=1
              else :
                isQuestionable = True;
                lastQuestionable = line
                printCandidateLines.append(prevLine)
                if isErrorNow == True :
                  isError = True 
            else:
              printCandidateLines.append(prevLine)
              if isErrorNow == True :
                isError = True
                lastQuestionable = line
              else :  
                if int(line[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) - int(prevLine[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) == 1 \
                 or int(line[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) - int(prevLine[POS_OREDER_BY_SERVERSIDE_TIMESTAMP[1]]) == 0 :
                  if int(line[POS_ANDROID_TIMESTAMP[1]]) - int(lastQuestionable[POS_ANDROID_TIMESTAMP[1]]) > TIMEDIF_SAMESESSION :
                    if isError == False :
                      while printCandidateLines :
                        printLine = printCandidateLines.popleft()
                        outFile.write(''+toString(printLine,1)+'\n')
                        numOfPrinted+=1
                        if lastQuestionable == printLine :
                          break
                        else :
                          numOfQuestionable+=1
                      while printCandidateLines :
                        printLine = printCandidateLines.popleft()
                        outFile.write(''+toString(printLine,1)+'\n')
                        numOfPrinted+=1    
                    else:
                      printLine = printCandidateLines.popleft()
                      outFile.write(''+toString(printLine,-1)+'\n')
                      numOfPrinted+=1
                      while printCandidateLines :
                        printLine = printCandidateLines.popleft()
                        if printLine == lastQuestionable :
                          outFile.write(''+toString(printLine,1)+'\n')
                          numOfPrinted+=1
                          break
                        outFileRemove.write(''+toString(printLine,-2)+'\n')
                        numOfDeleted+=1
                      while printCandidateLines :
                        printLine = printCandidateLines.popleft()
                        outFile.write(''+toString(printLine,1)+'\n')
                        numOfPrinted+=1
                    isQuestionable = False
                    isError = False
                    lastQuestionable = []
                else :
                  isQuestionable = True;
                  lastQuestionable = prevLine
        prevLine = line
      prevAppVersion = appVersion
    if appVersion < VERSIONS_SINCE_VERSION_2:
      if isQuestionable == True :
        printCandidateLines.append(prevLine)
        if isError == True :
          printLine = printCandidateLines.popleft()
          outFile.write(''+toString(printLine,-1)+'\n')
          numOfPrinted+=1
          while printCandidateLines :
            printLine = printCandidateLines.popleft()
            outFileRemove.write(''+toString(printLine,-2)+'\n')
            numOfDeleted+=1
        else :
          while printCandidateLines :
            printLine = printCandidateLines.popleft()
            outFile.write(''+toString(printLine,1)+'\n')
            numOfPrinted+=1
            if lastQuestionable == printLine :
              break
            else :
              numOfQuestionable+=1
          while printCandidateLines :
            printLine = printCandidateLines.popleft()
            outFile.write(''+toString(printLine,1)+'\n')
            numOfPrinted+=1
          #numOfPrinted+=1
      else :
        outFile.write(''+toString(prevLine,2)+'\n')
        numOfPrinted+=1
      prevLine = []
      lastQuestionable = []
      isQuestionable = False
      isError = False
  printCandidateLines.clear()
  outFile.close()
  outFileRemove.close()
  outList.append((numOfDeleted/numOfAllRowPerThisUser,[fileName,numOfAllRowPerThisUser,numOfPrinted+numOfDeleted,numOfPrinted,numOfDeleted,numOfQuestionable]))
  numOfUserAll += 1
  numOfRowAll += numOfAllRowPerThisUser
  numOfPrintedAll += numOfPrinted
  numOfDeletedAll += numOfDeleted
  numOfQuestionableAll += numOfQuestionable
  if numOfUserAll%100==0 :
    n = gc.collect()
outList.sort(reverse=True)
file = open("000000000000000000001", "a+", encoding="utf-8")
for outLine in outList :
  file.write(''+str(outLine[1][0])+" "+str(outLine[1][1])+" "+str(outLine[1][2])+" "+str(outLine[1][3])+" "+str(outLine[1][4])+" "+str(outLine[1][5])+" "+str(outLine[0])+'\n')
file.close()
print("TotalNumberOfExaminedRecord: "+str(numOfRowAll)+
      " NumberOfAppropriateRecord: "+str(numOfPrintedAll)+
      " NumberOfDeleted: "+str(numOfDeletedAll)+
      " NumberOfOKQuestionable: "+str(numOfQuestionableAll) )
lastTime = whatTheTime(lastTime)

  