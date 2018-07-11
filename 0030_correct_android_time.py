import os
import csv
import time
import gc
from collections import deque

BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

TIMEDIF_SAMESESSION = 3600000 # one hour

OUTFILE_PATH = 'out3/'
#INFILE_PATH = 'outErr/out/' #out2
#INFILE_PATH = 'out2/'
INFILE_PATH = 'out/'

def toString(record,androidSortedValidation) :
  outStr=""+record[0]
  for item in record[1:] :
    outStr+=";"+str(item)
  outStr+=";"+str(androidSortedValidation)  
  return outStr

def whatTheTime(lastTime):
  print("elapsed: ",time.time() - lastTime)
  return time.time()


def isThereAnyError(thisLine, prevLine) :
  if ( thisLine[22]  == "-2" and prevLine[22] == "-2" ) :
    return False 
  if ( thisLine[22]  != "" and prevLine[22] != "" ) :
    if ( thisLine[19] in BATTERY_PLUGGED_STATE and prevLine[19] in BATTERY_PLUGGED_STATE and
           thisLine[24] in BATTERY_STATUS_CHARGING and prevLine[24] in BATTERY_STATUS_CHARGING and
           int(thisLine[22]) >= int(prevLine[22])-1 ) :
      return False
    if ( thisLine[19] in BATTERY_UNPLUGGED_STATE and prevLine[19] in BATTERY_UNPLUGGED_STATE and
           thisLine[24] in BATTERY_STATUS_NOT_CHARGING and prevLine[24] in BATTERY_STATUS_NOT_CHARGING and
           int(thisLine[22]) <= int(prevLine[22])+1 ) :
      return False
  if ( prevLine[19] in BATTERY_UNPLUGGED_STATE and prevLine[24] in BATTERY_STATUS_NOT_CHARGING and
       thisLine[19] in BATTERY_PLUGGED_STATE and thisLine[24] in BATTERY_STATUS_CHARGING and 
       thisLine[36] == "3" ) :
    return False
  if ( prevLine[19] in BATTERY_PLUGGED_STATE and prevLine[24] in BATTERY_STATUS_CHARGING and 
       thisLine[19] in BATTERY_UNPLUGGED_STATE and thisLine[24] in BATTERY_STATUS_NOT_CHARGING and
       thisLine[36] == "4" ) :
    return False
  if ( thisLine[35] != "" and prevLine[35] != "" ) :
    if (int(thisLine[35]) != 0 and int(prevLine[35]) != 0 and
        abs((int(thisLine[11]) - int(prevLine[11])) - (int(thisLine[35]) - int(prevLine[35]))) < 1000 ) :
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
    for line in csv.reader(csvfile, delimiter=';', quotechar='|'):
      numOfAllRowPerThisUser+=1
      if prevLine :
        if int(line[11]) - int(prevLine[11]) > TIMEDIF_SAMESESSION or line[36] == "6":
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
            if int(line[1]) - int(prevLine[1]) == 1 or int(line[1]) - int(prevLine[1]) == 0 :
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
              if int(line[1]) - int(prevLine[1]) == 1 or int(line[1]) - int(prevLine[1]) == 0 :
                if int(line[11]) - int(lastQuestionable[11]) > TIMEDIF_SAMESESSION :
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

  