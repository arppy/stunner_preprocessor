import os
import csv
import time
import re
import sys
from fileinput import filename

try:
  import simplejson as json
except ImportError:
  import json
import xml.etree.ElementTree as ET


V18_RELEASEDATE = 1526083200000 #18 (1.2.3) 12 May 2018 
INFILE_PATH = 'res/res_v2/'
OUTFILE_PATH = 'p2pOUT/'
allRecord = 0
allFiltered = 0
max_timestamp = 0;

def maxTimestamp(ts):
  global max_timestamp
  if ts > max_timestamp :
    max_timestamp = ts
def whatTheTime(lastTime):
  print("elapsed: ", time.time() - lastTime)
  return time.time()
def addNAToString(times):
  nas = ''
  for i in range(0, times) :
    nas += ';'
  return nas
def replaceProblematicChars(inputString):
  niceString = inputString.replace('\'', '')
  niceString = niceString.replace('">\', \'L:> M:AB@5==K5 2K7>2K','L:M:AB@5==K52K72K')
  niceString = niceString.replace('">|-|L:> M:AB@5==K5 2K7>2K','L:M:AB@5==K52K72K')
  niceString = niceString.replace('">, L:> M:AB@5==K5 2K7>2K','L:M:AB@5==K52K72K')
  niceString = niceString.replace('\x1f>8A: A\', \'C61K','x1f8AAC61K')
  niceString = niceString.replace('\x1f>8A: A|-|C61K','x1f8AAC61K')
  niceString = niceString.replace('\x1f>8A: A, C61K','x1f8AAC61K')
  niceString = niceString.replace('=\n', '=')
  niceString = niceString.replace('=\\n', '=')
  niceString = niceString.replace('=\\\n', '=')
  niceString = niceString.replace('=\\\\n', '=')
  niceString = niceString.replace('=\\\\\\\\n', '=')
  niceString = niceString.replace('\n', '')
  niceString = niceString.replace('\t', '')
  niceString = niceString.replace('"\\\\\\\\"Vamos Ecuador\\\\\\\\""', '"Vamos Ecuador"')
  niceString = niceString.replace('ZAIN IQ\\n', 'ZAIN IQ')
  niceString = niceString.replace('\\\\', '')
  niceString = niceString.replace('\\\\\\\\', '')  # inputString = r''+inputString
  niceString = niceString.replace('\\', '')
  niceString = niceString.replace('""O2 - UK""', '"O2-UK"')
  niceString = niceString.replace('""AT&T""', '"AT&T"')
  niceString = niceString.replace('""OrangeF""', '"OrangeF"')
  niceString = niceString.replace('""BIMcell""', '"BIMcell"')
  niceString = niceString.replace('""TaiwanMobile""', '"TaiwanMobile"')
  niceString = niceString.replace("/", "").replace("+", "").replace("=", "").replace("?", "").replace(" ", "")
  return niceString
def toBatteryDTOString(record):
  tostring = ''
  try :
    tostring += ';' + replaceProblematicChars(str(record["technology"]))  # $18
  except :
    tostring += ';'
  try :
    tostring += ';' + str(record["present"])  # $19
  except :
    tostring += ';'
  tostring += ';' + str(record["pluggedState"])  # $20
  tostring += ';' + str(record["voltage"])  # $21
  tostring += ';' + str(record["temperature"])  # $22
  tostring += ';' + str(record["percentage"])  # $23
  tostring += ';' + str(record["health"])  # $24
  tostring += ';' + str(record["chargingState"])  # $25
  return tostring
def toString(record):
  tostring = '' + str(record["sourceRow"]) # $1
  tostring += ';' + str(record["sender"])  # $2
  tostring += ';' + str(record["startConn"])  # $3
  tostring += ';' + str(record["completedConn"])  # $4
  tostring += ';' + str(record["channelOpen"])  # $5
  tostring += ';' + str(record["channelClosed"])  # $6
  tostring += ';' + str(record["createdAt"])  # $7
  tostring += ';' + str(record["selfID"])  # $8
  tostring += ';' + str(record["chosenID"])  # $9
  if record["publicIP"] is not None:
    tostring += ';' + replaceProblematicChars(record["publicIP"])  # $10
  else :
    tostring += addNAToString(1)
  if record["localIP"] is not None:
    tostring += ';' + replaceProblematicChars(record["localIP"])  # $11
  else :
    tostring += addNAToString(1)
  tostring += ';' + str(record["timeStamp"])  # $12
  maxTimestamp(record["timeStamp"])
  tostring += ';' + str(record["latitude"])  # $13
  tostring += ';' + str(record["longitude"])  # $14
  androidVersionString = str(record["androidVersion"])
  if androidVersionString :
    tostring += ';' + str(record["androidVersion"])  # $15
  else :
    tostring += ';'
  tostring += ';' + str(record["discoveryResultCode"])  # $16
  try :
    tostring += ';' + str(record["connectionMode"])  # $17
  except:
    tostring += ';'
  try :
    tostring += toBatteryDTOString(record["batteryDTO"])  # $18 -- $25
  except:
    tostring += addNAToString(8)
  if record["wifiDTO"] is not None:
    if record["wifiDTO"]["bandwidth"] is not None :
      tostring += ';' + replaceProblematicChars(str(record["wifiDTO"]["bandwidth"]))  # $26
      # tostring+= ';'+str(getWifiBandwidthState(record["wifiDTO"]["bandwidth"])) #$26
    else :
      tostring += ';'
    if record["wifiDTO"]["ssid"] is not None :
      tostring += ';' + replaceProblematicChars(str(record["wifiDTO"]["ssid"]))  # $27
    else :
      tostring += ';'
    if record["wifiDTO"]["rssi"] is not None :
      tostring += ';' + replaceProblematicChars(str(record["wifiDTO"]["rssi"]))  # $28
    else :
      tostring += ';'
    if record["wifiDTO"]["macAddress"] is not None :
      tostring += ';' + replaceProblematicChars(str(record["wifiDTO"]["macAddress"]))  # $29
    else :
      tostring += ';'
  else :
    tostring += addNAToString(4)
  if record["mobileDTO"] is not None:
    try :
      carrierString = replaceProblematicChars(record["mobileDTO"]["carrier"])
      if carrierString:
        tostring += ';' + carrierString  # $30
      else :
        tostring += ';'
    except UnicodeEncodeError:
      carrierString = replaceProblematicChars(record["mobileDTO"]["carrier"])
      if carrierString:
        tostring += ';' + carrierString  # $30
      else :
        tostring += ';'
    try:
        tostring += ';' + replaceProblematicChars(record["mobileDTO"]["simCountryIso"])  # $31
    except :
        tostring += ';'
    tostring += ';' + str(record["mobileDTO"]["networkType"])  # $32
    # tostring+= ';'+str(getMobileBandwidthState(record["mobileDTO"]["networkType"])) #$32
    tostring += ';' + str(record["mobileDTO"]["roaming"])  # $33
  else :
    tostring += addNAToString(4)
  if record["uptimeInfoDTO"] is not None:
    if "shutdownTimestamp" in record["uptimeInfoDTO"] :
      tostring += ';' + str(record["uptimeInfoDTO"]["shutdownTimestamp"])  # $34
    else :
      tostring += ';'
    if "turnOnStimestamp" in record["uptimeInfoDTO"] :
      tostring += ';' + str(record["uptimeInfoDTO"]["turnOnStimestamp"])  # $35
    else :
      tostring += ';'
    tostring += ';' + str(record["uptimeInfoDTO"]["uptime"])  # $36
  else :
    tostring += addNAToString(3)
  try:
    tostring += ';' + str(record["triggerCode"])  # $37
  except KeyError:
    tostring += ';'
  try:
    tostring += ';' + str(record["appVersion"])  # $38
  except KeyError:
    tostring += ';'
  try:
    tostring += ';' + str(record["timeZone"])  # $39
  except KeyError:
    tostring += ';'
  return tostring


print("JSON TO CSV START")
# MAIN
lastTime = time.time()
lastTime = whatTheTime(lastTime)
# FILE_READING
path = INFILE_PATH
files = os.listdir(path)
files.sort()
for fileName in files:
  counterPerFile = 0
  try:
    with open('' + path + fileName) as csvfile:
      next(csvfile)
      counterPerFile+=1      
      stunnerReader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for line in stunnerReader:
        counterPerFile+=2
        if not line[0] :
          allFiltered+=1
        else :  
          jsonStr = ""
          for i in range(9,len(line)) :
            splittedElement = line[i].split("\"\"")
            jsonStr += splittedElement[0]  
            for j in range(1,len(splittedElement)):
              jsonStr += "\""+splittedElement[j]  
            jsonStr += ","
          jsonStr = jsonStr[:-2] #remove last comma(,) and quote
          jsonStr = jsonStr[1:] #remove first quote  
          record = json.loads(jsonStr, strict=False)
          record["sourceFile"] = fileName
          record["sourceRow"] = counterPerFile
          record["selfID"] = line[0]
          record["chosenID"] = line[1]
          record["sender"] = line[2]
          record["startConn"] = line[3]
          record["completedConn"] = line[4]
          record["channelOpen"] = line[5]
          record["channelClosed"] = line[6]
          record["timeZone"] = line[7]
          record["createdAt"] = line[8]
          outstr = toString(record)
          allRecord+=1
          file = open('' + OUTFILE_PATH + line[0], "a+", encoding="utf-8")
          file.write('' + outstr + '\n')
          file.close()
  except IsADirectoryError as e :
    print("Warning: " + str(fileName) + " is a directory")
    print(str(e))    
lastTime = whatTheTime(lastTime)
print("JSON TO CSV END. ALL RECORD: "+str(allRecord)+" ALL FILTERED: "+str(allFiltered))      