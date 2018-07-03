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
from collections import defaultdict

V14_RELEASEDATE = 1493078400000 #14 (1.1.4) 25 Apr 2017 14:37
V13_RELEASEDATE = 1426464000000 #13 (1.1.3) 2015. márc. 16.
V12_RELEASEDATE = 1421625600000 #12 (1.1.2) 2015. jan. 19.
V11_RELEASEDATE = 1412812800000 #11 (1.1.1) 2014. okt. 9.
V10_RELEASEDATE = 1412294400000 #10 (1.1.0) 2014. okt. 3.
V9_RELEASEDATE = 1398643200000 #  9 (1.0.9) 2014. ápr. 28.
V8_RELEASEDATE = 1397088000000 #  8 (1.0.8) 2014. ápr. 10.
V7_RELEASEDATE = 1396137600000 #  7 (1.0.7) 2014. márc. 30.
V6_RELEASEDATE = 1395964800000 #  6 (1.0.6) 2014. márc. 28.
V5_RELEASEDATE = 1395792000000 #  5 (1.0.5) 2014. márc. 26.
V4_RELEASEDATE = 1394755200000 #  4 (1.0.4) 2014. márc. 14.
V3_RELEASEDATE = 1390262400000 #  3 (1.0.3) 2014. jan. 21.
V2_RELEASEDATE = 1388966400000 #  2 (1.0.1) 2014. jan. 6.
V1_RELEASEDATE = 1387497600000 #  1 (1.0.0) 2013. dec. 20.

FIRST_VALID_ANDROID_DATE = 1396571221202  # 2014 04 04 00 27 01
# MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 691200000 # 8 day
MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 604800000  # 7 day
# MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 2592000000 # 30 day
MIN_DIF_IN_ANDROID_AND_SERVER_TIME = 0
MAX_DIF_IN_SERVERSAVE_AND_SERVER_TIME = 3600000  # 1 hour
LAST_VALID_SERVER_DATE_FOR_FIRSTVERSION_OF_THE_DATA = 1417391999000  # 30 Nov 2014 23:59:59 GMT

BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

INFILE_PATH = 'res/'
OUTFILE_PATH = 'out/'
LAST_FAIL_APP_VERSION = 13
STUNNER_APP_ID = 'hu.uszeged.inf.wlab.stunner'

max_timestamp = 0;
allRecord = 0
allFiltered = 0
counter = 0
differentServerTimePerUser = defaultdict(dict);
rowPerUser = defaultdict(dict);
previousValidUploadDate = defaultdict(dict);
platform = STUNNER_APP_ID


def maxTimestamp(ts):
  global max_timestamp
  if ts > max_timestamp :
    max_timestamp = ts


def isEmptyFields(record) :
  global allFiltered, errorPerUser
  if not "batteryDTO" in record:
    print(record)
    return True
  if record["batteryDTO"] is None:
    allFiltered += 1
    # return True
  return False


def determineUnkownValue(record):
  '''if record["connectionMode"] == -1 :
    record["discoveryResultCode"] = 9 '''
  try:
    if ((record["batteryDTO"]["pluggedState"] == -1) and (record["batteryDTO"]["chargingState"] in BATTERY_STATUS_NOT_CHARGING)) :
      record["batteryDTO"]["pluggedState"] = 0
  except:
    try:
      record["batteryDTO"]["pluggedState"] = -1
    except:
      record["batteryDTO"] = {}
      record["batteryDTO"]["pluggedState"] = -1
  if not "uptimeInfoDTO" in record:
    record["uptimeInfoDTO"] = {}
    record["uptimeInfoDTO"]["uptime"] = ""
  return record


def getWifiBandwidthState(bdw):
  if bdw is None :
    return 0
  bandwidth = int(bdw.replace(" Mbps", ""))
  if(bandwidth > 40) :
    return 3
  elif (bandwidth <= 40 and bandwidth > 5) :
    return 2
  elif (bandwidth <= 5 and bandwidth > 0) :
    return 1
  else :
    return 0

def getTimeZoneTimeGeonames(latitude, longitude) :
  requestString = 'http://ws.geonames.org/timezone?lat=' + str(latitude) + '&lng=' + str(longitude) + '&username=arphead'
  data = json.dumps([1, 2, 3])
  req = urllib2.Request(requestString, data, {'Content-Type': 'application/json'})
  f = urllib2.urlopen(req)
  response = f.read()
  f.close()
  root = ET.fromstring(response)
  for offset in root.iter('dstOffset'):
    return int(float(offset.text))


def addNAToString(times):
  nas = ''
  for i in range(0, times) :
    nas += ';'
  return nas


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
  tostring = '' + str(rowPerUser[record["deviceHash"]]) # $1
  tostring += ';' + str(differentServerTimePerUser[record["deviceHash"]])  # $2
  tostring += ';' + str(record["fileCreationDate"])  # $3
  tostring += ';' + str(record["previousValidUploadDate"])  # $4
  tostring += ';' + str(record["sourceFile"])  # $5
  tostring += ';' + str(record["sourceRow"])  # $6
  tostring += ';' + str(record["serverSideUploadDate"])  # $7
  tostring += ';' + str(record["deviceHash"])  # $8
  tostring += ';' + str(record["platform"])  # $9
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


def whatTheTime(lastTime):
  print("elapsed: ", time.time() - lastTime)
  return time.time()


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
  baseNameString = os.path.basename(fileName).split(".")
  try :
    fileCreationDate = int(baseNameString[0]) * 60 * 60 * 1000
  except :
    fileCreationDate = -1
  try:
    with open('' + path + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      i = 0;
      for line in stunnerReader:
        originLen = len(line)
        originLine = line
        line = "|-|".join(line)
        line = replaceProblematicChars(line)
        line = line.split("|-|")
        #if(originLen != len(line)) :
          #print(originLine)
          #print(line)
        for record in line:
          #record = replaceProblematicChars(record)  
          if i == 0 :
            try:
              serverSideUploadDate = int(record)
            except :
              serverSideUploadDate = -1
          if i == 1 :
            userName = str(record)
            if not previousValidUploadDate[userName]:
              previousValidUploadDate[userName] = 0
            if not differentServerTimePerUser[userName] :
              differentServerTimePerUser[userName] = 0
            if not rowPerUser[userName] :
              rowPerUser[userName] = 0
          if i >= 2 :
            if re.match('^hu', record) is not None:
              platform = str(record)
            else :
              #record = record.decode('utf-8', errors='ignore').encode('utf-8', errors='ignore')
              #record = record.decode('ascii',errors='ignore')
              #record = record.decode('iso-8859-1',errors='ignore')
              try:
                record = json.loads(record, strict=False)
                if not type(record) == type({}) :
                  raise ValueError
                allRecord += 1
                record = determineUnkownValue(record)
                record["sourceFile"] = fileName
                record["sourceRow"] = counterPerFile
                record["fileCreationDate"] = fileCreationDate
                record["serverSideUploadDate"] = serverSideUploadDate
                record["previousValidUploadDate"] = previousValidUploadDate[userName]
                record["deviceHash"] = userName
                record["platform"] = platform
                try:
                  difInServerAndAndroidTime = int(record["serverSideUploadDate"]) - int(record["timeStamp"])
                  try:
                    appVersion = int(record["appVersion"]);
                  except:
                    appVersion = 1;    
                  if difInServerAndAndroidTime >= MIN_DIF_IN_ANDROID_AND_SERVER_TIME and \
                     ( (appVersion == 1 and V1_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 2 and V2_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 3 and V3_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 4 and V4_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 5 and V5_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 6 and V6_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 7 and V7_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 8 and V8_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 9 and V9_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 10 and V10_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 11 and V11_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 12 and V12_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 13 and V13_RELEASEDATE < int(record["timeStamp"])) or \
                       (appVersion == 14 and V14_RELEASEDATE < int(record["timeStamp"])) ) :
                    rowPerUser[userName] +=1
                    if previousValidUploadDate[userName] != serverSideUploadDate :
                      differentServerTimePerUser[userName] += 1
                      previousValidUploadDate[userName] = serverSideUploadDate
                      record["previousValidUploadDate"] = previousValidUploadDate[userName]
                    outstr = toString(record)  
                    file = open('' + OUTFILE_PATH + userName, "a+", encoding="utf-8")
                    file.write('' + outstr + '\n')
                    file.close()
                    # print(previousValidUploadDate[userName], serverSideUploadDate)
                  else :
                    allFiltered += 1
                  # print('Too OLD version of JSON!',allFiltered/allRecord, userName, line)
                except :
                  allFiltered += 1
                  print('Missing Record! ',str(fileName), str(allFiltered / allRecord), str(userName), str(record), str(line))  
              except ValueError:  
                if i>=4 :
                  allFiltered += 1
                  print('Not a JSON! ',str(fileName), str(allFiltered / allRecord), str(userName), str(record), str(line))
          i += 1;
        if i >= 3 :
          i = 0
          counter += 1
          counterPerFile += 1
          if counter % 100000 == 0:
            print(counter)
            sys.stdout.flush()
  except IsADirectoryError :
      print("Warning: " + str(fileName) + " is a directory")
lastTime = whatTheTime(lastTime)
print("JSON TO CSV END. ALL RECORD: "+str(allRecord)+" ALL FILTERED: "+str(allFiltered))

