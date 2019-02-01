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

versionReleasDate = {}
versionReleasDate[25] = 1545004800000 #25 
versionReleasDate[24] = 1548115200000 #24 (2.0.4) 22 Jan 2019 
versionReleasDate[23] = 1545004800000 #23 (2.0.3) 17 Dec 2018 lastDisconnect is the same on any Android version. so it does not mean the exactly time when a device goes offline in newer Android version. double P2P offer is possible
versionReleasDate[22] = 1543190400000 #22 (2.0.2) 26 Nov 2018 Lack of offline start record on 24 or greater Android version. 
versionReleasDate[21] = 1540944002000 #21 (2.0.1) 31 Okt 2018 
versionReleasDate[20] = 1540771202000 #20 (2.0.0) 29 Okt 2018 
versionReleasDate[19] = 1540771201000 #19 (1.2.4) 29 Okt 2018 has never released, development version
versionReleasDate[18] = 1526083200000 #18 (1.2.3) 12 May 2018 P2P crash
versionReleasDate[17] = 1524441600000 #17 (1.2.2) 23 Apr 2018 P2P crash
versionReleasDate[16] = 1524268800000 #16 (1.2.1) 21 Apr 2018 P2P crash
versionReleasDate[15] = 1524009600000 #15 (1.2.0) 18 Apr 2018 P2P crash
versionReleasDate[14] = 1493078400000 #14 (1.1.4) 25 Apr 2017 14:37
versionReleasDate[13] = 1426464000000 #13 (1.1.3) 2015. márc. 16.
versionReleasDate[12] = 1421625600000 #12 (1.1.2) 2015. jan. 19.
versionReleasDate[11] = 1412812800000 #11 (1.1.1) 2014. okt. 9.
versionReleasDate[10] = 1412294400000 #10 (1.1.0) 2014. okt. 3.
versionReleasDate[9] = 1398643200000 #  9 (1.0.9) 2014. ápr. 28. first ok
versionReleasDate[8] = 1397088000000 #  8 (1.0.8) 2014. ápr. 10.
versionReleasDate[7] = 1396137600000 #  7 (1.0.7) 2014. márc. 30.
versionReleasDate[6] = 1395964800000 #  6 (1.0.6) 2014. márc. 28.
versionReleasDate[5] = 1395792000000 #  5 (1.0.5) 2014. márc. 26.
versionReleasDate[4] = 1394755200000 #  4 (1.0.4) 2014. márc. 14.
versionReleasDate[3] = 1390262400000 #  3 (1.0.3) 2014. jan. 21.
versionReleasDate[2] = 1388966400000 #  2 (1.0.1) 2014. jan. 6.
versionReleasDate[1] = 1387497600000 #  1 (1.0.0) 2013. dec. 20. no continuous measure

#MYMACADRESS = "kQbJyfSx3g1CAjMVXG9rWbUribixMm17dOd72kx0jKk=\n"
MYMACADRESS = "kQbJyfSx3g1CAjMVXG9rWbUribixMm17dOd72kx0jKk\u003d"
FIRST_VALID_ANDROID_DATE = 1396571221202  # 2014 04 04 00 27 01
# MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 691200000 # 8 day
MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 604800000  # 7 day
# MAX_DIF_IN_ANDROID_AND_SERVER_TIME = 2592000000 # 30 day
MIN_DIF_IN_ANDROID_AND_SERVER_TIME = 0
MAX_DIF_IN_SERVERSAVE_AND_SERVER_TIME = 3600000  # 1 hour
LAST_VALID_SERVER_DATE_FOR_FIRSTVERSION_OF_THE_DATA = 1417391999000  # 30 Nov 2014 23:59:59 GMT

DEVELOPMENT_VERSIONS = set([19])
NOT_USED_TRIGGER_CODES = set([-1,15,17])
BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

INFILE_PATH = 'res/res_v1/'
OUTFILE_PATH = 'out/'
LAST_FAIL_APP_VERSION = 13
VERSION_TWO_SINCE = 20
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


def toStringV2(record):
  tostring = '' + str(record["fileCreationDate"])  # $1
  tostring += ';' + replaceNullNA(str(record["serverSideUploadDate"]))  # $2
  tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["androidID"])))) # $3
  tostring += ';' + str(record["recordID"])  # $4
  tostring += ';' + replaceNullNA(str(record["timeStamp"]))  # $5
  maxTimestamp(record["timeStamp"])
  tostring += ';' + str(record["timeZoneUTCOffset"])  # $6
  tostring += ';' + str(record["triggerCode"])  # $7
  tostring += ';' + str(record["androidVersion"])  # $8
  tostring += ';' + str(record["appVersion"])  # $9
  tostring += ';' + str(record["connectionMode"])  # $10
  tostring += ';' + str(record["networkInfo"])  # $11
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["localIP"])))  # $12
  tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["wifiDTO"]["macAddress"]))))  # $13
  tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["wifiDTO"]["ssid"]))))  # $14
  tostring += ';' + str(record["wifiDTO"]["state"])  # $15
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["wifiDTO"]["bandwidth"])))  # $16
  tostring += ';' + str(record["wifiDTO"]["rssi"])  # $17
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["carrier"])))  # $18
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["networkType"])))  # $19
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["networkCountryIso"])))  # $20
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["simCountryIso"])))  # $21
  tostring += ';' + str(record["mobileDTO"]["roaming"])  # $22
  tostring += ';' + str(record["mobileDTO"]["phoneType"])  # $23
  tostring += ';' + str(record["mobileDTO"]["airplane"])  # $24
  tostring += ';' + str(record["natResultsDTO"]["discoveryResult"])  # $25
  tostring += ';' + str(record["natResultsDTO"]["exitStatus"])  # $26
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["natResultsDTO"]["publicIP"])))  # $27
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["natResultsDTO"]["STUNserver"])))  # $28
  tostring += ';' + replaceNullNA(str(record["natResultsDTO"]["lastDiscovery"]))  # $29
  tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["connectionStart"]))  # $30
  tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["connectionEnd"]))  # $31
  tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["channelOpen"]))  # $32
  tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["channelClosed"]))  # $33
  tostring += ';' + str(record["webRTCResultsDTO"]["exitStatus"])  # $34
  tostring += ';' + replaceNullNA(str(record["lastDisconnect"]))  # $35
  tostring += ';' + str(record["batteryDTO"]["chargingState"])  # $36
  tostring += ';' + str(record["batteryDTO"]["pluggedState"])  # $37
  tostring += ';' + str(record["batteryDTO"]["percentage"])  # $38
  tostring += ';' + str(record["batteryDTO"]["health"])  # $39
  tostring += ';' + str(record["batteryDTO"]["present"])  # $40
  tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["batteryDTO"]["technology"])))  # $41
  tostring += ';' + str(record["batteryDTO"]["temperature"])  # $42
  tostring += ';' + str(record["batteryDTO"]["voltage"])  # $43
  tostring += ';' + replaceNullNA(str(record["uptimeInfoDTO"]["turnOnTimestamp"]))  # $44
  tostring += ';' + replaceNullNA(str(record["uptimeInfoDTO"]["shutDownTimestamp"]))  # $45
  tostring += ';' + str(record["uptimeInfoDTO"]["uptime"])  # $46
  tostring += ';' + replaceNullNA(str(record["latitude"]))  # $47
  tostring += ';' + replaceNullNA(str(record["longitude"]))  # $48
  tostring += ';' + replaceNullNA(str(record["locationCaptureTimestamp"]))  # $49
  return tostring

def toStringV1(record):
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

def removeLastCharsFromString(inputHashedString):
  return inputHashedString[:-10]

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

def replaceNullNA(inputString):
  if inputString == "N/A" or inputString == "NA" or inputString == "null" or inputString == "0" or inputString == "0L" or inputString == "0.0":
    return ''
  else: 
    return inputString

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
                  if(int(record["serverSideUploadDate"]) == 0  or int(record["serverSideUploadDate"]) == -1 ) :
                    difInServerAndAndroidTime = 0
                  else :
                    difInServerAndAndroidTime = int(record["serverSideUploadDate"]) - int(record["timeStamp"])
                  try:
                    appVersion = int(record["appVersion"]);
                  except:
                    appVersion = 1
                  try:
                    triggerCode = int(record["triggerCode"])
                  except:
                    triggerCode = -1 
                  if difInServerAndAndroidTime >= MIN_DIF_IN_ANDROID_AND_SERVER_TIME and \
                    versionReleasDate[appVersion] <= int(record["timeStamp"]) :
                    rowPerUser[userName] +=1
                    if previousValidUploadDate[userName] != serverSideUploadDate :
                      differentServerTimePerUser[userName] += 1
                      previousValidUploadDate[userName] = serverSideUploadDate
                      record["previousValidUploadDate"] = previousValidUploadDate[userName]
                    if appVersion >= VERSION_TWO_SINCE :
                      outstr = toStringV2(record)
                    else :    
                      outstr = toStringV1(record)  
                    file = open('' + OUTFILE_PATH + userName , "a+", encoding="utf-8")
                    file.write('' + outstr + '\n')
                    file.close()
                    # print(previousValidUploadDate[userName], serverSideUploadDate)
                  else :
                    allFiltered += 1
                    #print('Too OLD version of JSON!',fileName,str(appVersion),record["timeStamp"],\
                    #      str(difInServerAndAndroidTime >= MIN_DIF_IN_ANDROID_AND_SERVER_TIME),str(difInServerAndAndroidTime),str(record["serverSideUploadDate"]))
                except Exception as e :
                  allFiltered += 1
                  print('Missing Record! ',str(fileName), str(userName), str(appVersion), str(line),type(e), e, e.args )  
              except ValueError:  
                if i>=4 :
                  allFiltered += 1
                  print('Not a JSON! ',str(fileName), str(appVersion), str(userName), str(record), str(line))
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

