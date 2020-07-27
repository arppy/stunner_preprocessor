import os
import csv
import time
import re
import sys
import geoip2.database
from geoip2.errors import AddressNotFoundError
from fileinput import filename
import multiprocessing

try:
    import simplejson as json
except ImportError:
    import json
import xml.etree.ElementTree as ET
from collections import defaultdict

versionReleasDate = {}
versionReleasDate[25] = 1545004800000 #25 
versionReleasDate[24] = 1548115200000 #24 (2.0.4) 22 Jan 2019 lastDisconnect dont work
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
MAX_DIF_IN_ANDROID_AND_FILE_TIME = 1000*60*60*2  # 2 hour
LAST_VALID_SERVER_DATE_FOR_FIRSTVERSION_OF_THE_DATA = 1417391999000  # 30 Nov 2014 23:59:59 GMT

DEVELOPMENT_VERSIONS = set([19])
NOT_USED_TRIGGER_CODES = set([-1,15,17])
BATTERY_PLUGGED_STATE = set(['1', '2', '4'])
BATTERY_UNPLUGGED_STATE = set(['0', '-1'])
BATTERY_STATUS_CHARGING = set(['2', '5'])
BATTERY_STATUS_NOT_CHARGING = set(['1', '3', '4',])

INFILE_PATH = 'res/res_v1b/'
GEOLITE_CITY_READER = geoip2.database.Reader('res/geolite/GeoLite2-City.mmdb')
GEOLITE_ASN_READER = geoip2.database.Reader('res/geolite/GeoLite2-ASN.mmdb')
OUTFILE_PATH = 'out/'
LAST_FAIL_APP_VERSION = 13
VERSION_TWO_SINCE = 20
STUNNER_APP_ID = 'hu.uszeged.inf.wlab.stunner'
if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] is not None and str.isnumeric(sys.argv[1]):
  NUMBER_OF_CORES = int(sys.argv[1])
else :
  NUMBER_OF_CORES = 1

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
  if "androidID" in record :
    tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["androidID"])))) # $3
  else :
    tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["deviceHash"]))))  # $3
  if "recordID" in record :
    tostring += ';' + str(record["recordID"])  # $4
  else :
    tostring += addNAToString(1)
  if "timeStamp" in record :
    tostring += ';' + replaceNullNA(str(record["timeStamp"]))  # $5
  elif "date" in record :
    tostring += ';' + replaceNullNA(str(record["date"]))  # $5
  else:
    tostring += addNAToString(1)
  if "timeZoneUTCOffset" in record :
    tostring += ';' + str(record["timeZoneUTCOffset"])  # $6
  elif "timeZone" in record :
    tostring += ';' + str(record["timeZone"])  # $6
  else:
    tostring += addNAToString(1)
  if "triggerCode" in record :
    tostring += ';' + str(record["triggerCode"])  # $7
  else:
    tostring += addNAToString(1)
  if "androidVersion" in record:
    tostring += ';' + str(record["androidVersion"])  # $8
  else:
    tostring += addNAToString(1)
  if "appVersion" in record:
    tostring += ';' + str(record["appVersion"])  # $9
  else:
    tostring += addNAToString(1)
  if "connectionMode" in record:
    tostring += ';' + str(record["connectionMode"])  # $10
  else:
    tostring += addNAToString(1)
  if "networkInfo" in record:
    tostring += ';' + str(record["networkInfo"])  # $11
  else:
    tostring += addNAToString(1)
  if "localIP" in record and record["localIP"] is not None:
    tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["localIP"])))  # $12
  else :
    tostring += addNAToString(1)
  if "wifiDTO" in record and record["wifiDTO"] is not None:
    if "macAddress" in record["wifiDTO"] and record["wifiDTO"]["macAddress"] is not None :
      tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["wifiDTO"]["macAddress"]))))  # $13
    else :
      tostring += addNAToString(1)
    if "ssid" in record["wifiDTO"] and record["wifiDTO"]["ssid"] is not None :
      tostring += ';' + replaceNullNA(replaceProblematicChars(removeLastCharsFromString(str(record["wifiDTO"]["ssid"]))))  # $14
    else :
      tostring += addNAToString(1)
    if "state" in record["wifiDTO"] and record["wifiDTO"]["state"] is not None :
      tostring += ';' + str(record["wifiDTO"]["state"])  # $15
    else :
      tostring += addNAToString(1)
    if "bandwidth" in record["wifiDTO"] and record["wifiDTO"]["bandwidth"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["wifiDTO"]["bandwidth"])))  # $16
    else:
      tostring += addNAToString(1)
    if "rssi" in record["wifiDTO"] and record["wifiDTO"]["rssi"] is not None:
      tostring += ';' + str(record["wifiDTO"]["rssi"])  # $17
    else:
      tostring += addNAToString(1)
  elif "wifiInfo" in record and record["wifiInfo"] is not None:
    tostring += addNAToString(1)  # 13
    if "ssid" in record["wifiInfo"] and record["wifiInfo"]["ssid"] is not None:
      tostring += ';' + replaceNullNA(
        replaceProblematicChars(removeLastCharsFromString(str(record["wifiInfo"]["ssid"]))))  # $14
    else:
      tostring += addNAToString(1)
    tostring += addNAToString(1)  # 15
    if "bandwidth" in record["wifiInfo"] and record["wifiInfo"]["bandwidth"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["wifiInfo"]["bandwidth"])))  # $16
    else:
      tostring += addNAToString(1)
    tostring += addNAToString(1)  # 17
  else:
    tostring += addNAToString(5)
  if "mobileDTO" in record and record["mobileDTO"] is not None:
    if "carrier" in record["mobileDTO"] and record["mobileDTO"]["carrier"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["carrier"])))  # $18
    else:
      tostring += addNAToString(1)
    if "networkType" in record["mobileDTO"] and record["mobileDTO"]["networkType"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["networkType"])))  # $19
    else:
      tostring += addNAToString(1)
    if "networkCountryIso" in record["mobileDTO"] and record["mobileDTO"]["networkCountryIso"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["networkCountryIso"])))  # $20
    else:
      tostring += addNAToString(1)
    if "simCountryIso" in record["mobileDTO"] and record["mobileDTO"]["simCountryIso"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileDTO"]["simCountryIso"])))  # $21
    else:
      tostring += addNAToString(1)
    if "roaming" in record["mobileDTO"] and record["mobileDTO"]["roaming"] is not None:
      tostring += ';' + str(record["mobileDTO"]["roaming"])  # $22
    else:
      tostring += addNAToString(1)
    if "phoneType" in record["mobileDTO"] and record["mobileDTO"]["phoneType"] is not None:
      tostring += ';' + str(record["mobileDTO"]["phoneType"])  # $23
    else:
      tostring += addNAToString(1)
    if "airplane" in record["mobileDTO"] and record["mobileDTO"]["airplane"] is not None:
      tostring += ';' + str(record["mobileDTO"]["airplane"])  # $24
    else:
      tostring += addNAToString(1)
  elif "mobileNetInfo" in record and record["mobileNetInfo"] is not None:
    if "carrier" in record["mobileNetInfo"] and record["mobileNetInfo"]["carrier"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileNetInfo"]["carrier"])))  # $18
    else:
      tostring += addNAToString(1)
    if "netType" in record["mobileNetInfo"] and record["mobileNetInfo"]["netType"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["mobileNetInfo"]["netType"])))  # $19
    else:
      tostring += addNAToString(1)
    tostring += addNAToString(2) # 20 21
    if "isRoaming" in record["mobileNetInfo"] and record["mobileNetInfo"]["isRoaming"] is not None:
      tostring += ';' + str(record["mobileNetInfo"]["isRoaming"])  # $22
    else :
      tostring += addNAToString(1)
    tostring += addNAToString(2)  # 23 24
  else :
    tostring += addNAToString(7)
  ipstring = "NA"
  if "natResultsDTO" in record and record["natResultsDTO"] is not None:
    if "discoveryResult" in record["natResultsDTO"] and record["natResultsDTO"]["discoveryResult"] is not None :
      discoveryResult = record["natResultsDTO"]["discoveryResult"]
    else :
      discoveryResult = record["natResultsDTO"]["discoveryResultCode"]
    if "exitStatus" in record["natResultsDTO"] and record["natResultsDTO"]["exitStatus"] is not None :
      exitStatus = record["natResultsDTO"]["exitStatus"];
      discoveryResult = correctDiscoveryResult(discoveryResult, exitStatus)
    elif discoveryResult == -1 :
      exitStatus = 1
    elif discoveryResult == -3:
      exitStatus = -1
    else :
      exitStatus = 0
    tostring += ';' + str(discoveryResult)  # $25
    tostring += ';' + str(exitStatus)  # $26
    if "publicIP" in record["natResultsDTO"] and record["natResultsDTO"]["publicIP"] is not None:
      ipstring = replaceNullNA(replaceProblematicChars(str(record["natResultsDTO"]["publicIP"])))
      tostring += ';' + ipstring  # $27
    else:
      tostring += addNAToString(1)
    if "STUNserver" in record["natResultsDTO"] and record["natResultsDTO"]["STUNserver"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["natResultsDTO"]["STUNserver"])))  # $28
    else:
      tostring += addNAToString(1)
    if "lastDiscovery" in record["natResultsDTO"] and record["natResultsDTO"]["lastDiscovery"] is not None:
      tostring += ';' + replaceNullNA(str(record["natResultsDTO"]["lastDiscovery"]))  # $29
    else:
      tostring += addNAToString(1)
  else :
    if "discoveryResult" in record:
      discoveryResult = record["discoveryResult"]
    elif "discoveryResultCode" in record:
      discoveryResult = record["discoveryResultCode"]
    elif "resultCode" in record:
      discoveryResult = record["resultCode"]
    else:
      discoveryResult = -3
    if discoveryResult == -1:
      exitStatus = 1
    elif discoveryResult == -3:
      exitStatus = -1
    else:
      exitStatus = 0
    tostring += ';' + str(discoveryResult)  # $25
    tostring += ';' + str(exitStatus)  # $26
    if "publicIP" in record and record["publicIP"] is not None:
      ipstring = replaceNullNA(replaceProblematicChars(str(record["publicIP"])))
      tostring += ';' + ipstring  # $27
    else :
      tostring += addNAToString(1)
    tostring += addNAToString(2) # 28 # 29
  if "webRTCResultsDTO" in record and record["webRTCResultsDTO"] is not None:
    try:
      tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["connectionStart"]))  # $30
      tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["connectionEnd"]))  # $31
      tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["channelOpen"]))  # $32
      tostring += ';' + replaceNullNA(str(record["webRTCResultsDTO"]["channelClosed"]))  # $33
      tostring += ';' + str(record["webRTCResultsDTO"]["exitStatus"])  # $34
    except:
      tostring += addNAToString(5)
  else :
    tostring += addNAToString(5)
  if "lastDisconnect" in record:
    tostring += ';' + replaceNullNA(str(record["lastDisconnect"]))  # $35
  else :
    tostring += addNAToString(1)
  if "batteryDTO" in record and record["batteryDTO"] is not None:
    if "chargingState" in record["batteryDTO"] and record["batteryDTO"]["chargingState"] is not None:
      tostring += ';' + str(record["batteryDTO"]["chargingState"])  # $36
    else:
      tostring += addNAToString(1)
    if "pluggedState" in record["batteryDTO"] and record["batteryDTO"]["pluggedState"] is not None:
      tostring += ';' + str(record["batteryDTO"]["pluggedState"])  # $37
    else:
      tostring += addNAToString(1)
    if "percentage" in record["batteryDTO"] and record["batteryDTO"]["percentage"] is not None:
      tostring += ';' + str(record["batteryDTO"]["percentage"])  # $38
    else:
      tostring += addNAToString(1)
    if "health" in record["batteryDTO"] and record["batteryDTO"]["health"] is not None:
      tostring += ';' + str(record["batteryDTO"]["health"])  # $39
    else:
      tostring += addNAToString(1)
    if "present" in record["batteryDTO"] and record["batteryDTO"]["present"] is not None:
      tostring += ';' + str(record["batteryDTO"]["present"])  # $40
    else:
      tostring += addNAToString(1)
    if "technology" in record["batteryDTO"] and record["batteryDTO"]["technology"] is not None:
      tostring += ';' + replaceNullNA(replaceProblematicChars(str(record["batteryDTO"]["technology"])))  # $41
    else:
      tostring += addNAToString(1)
    if "temperature" in record["batteryDTO"] and record["batteryDTO"]["temperature"] is not None:
      tostring += ';' + str(record["batteryDTO"]["temperature"])  # $42
    else:
      tostring += addNAToString(1)
    if "voltage" in record["batteryDTO"] and record["batteryDTO"]["voltage"] is not None:
      tostring += ';' + str(record["batteryDTO"]["voltage"])  # $43
    else:
      tostring += addNAToString(1)
  elif "batteryInfo" in record and record["batteryInfo"] is not None:
    if "charging" in record["batteryInfo"] and record["batteryInfo"]["charging"] is not None:
      if str(record["batteryDTO"]["charging"]) == "true" :
        tostring += ';' + str(2)  # $36
        tostring += ';' + str(1)  # $37
      else :
        tostring += ';' + str(4)  # $36
        tostring += ';' + str(0)  # $37
    else:
      tostring += addNAToString(2)
    if "batteryLevel" in record["batteryInfo"] and record["batteryInfo"]["batteryLevel"] is not None:
      tostring += ';' + str(record["batteryInfo"]["batteryLevel"])  # $38
    else:
      tostring += addNAToString(1)
    tostring += addNAToString(5) # $39 $40 $41 $42 $43
  else :
    tostring += addNAToString(8)
  if "uptimeInfoDTO" in record and record["uptimeInfoDTO"] is not None:
    if "turnOnTimestamp" in record["uptimeInfoDTO"] and record["uptimeInfoDTO"]["turnOnTimestamp"] is not None:
      tostring += ';' + replaceNullNA(str(record["uptimeInfoDTO"]["turnOnTimestamp"]))  # $44
    else:
      tostring += addNAToString(1)
    if "shutDownTimestamp" in record["uptimeInfoDTO"] and record["uptimeInfoDTO"]["shutDownTimestamp"] is not None:
      tostring += ';' + replaceNullNA(str(record["uptimeInfoDTO"]["shutDownTimestamp"]))  # $45
    else:
      tostring += addNAToString(1)
    if "uptime" in record["uptimeInfoDTO"] and record["uptimeInfoDTO"]["uptime"] is not None:
      tostring += ';' + str(record["uptimeInfoDTO"]["uptime"])  # $46
    else:
      tostring += addNAToString(1)
  else:
    tostring += addNAToString(3)
  tostring += ';' + replaceNullNA(str(record["latitude"]))  # $47
  tostring += ';' + replaceNullNA(str(record["longitude"]))  # $48
  if "locationCaptureTimestamp" in record:
    tostring += ';' + replaceNullNA(str(record["locationCaptureTimestamp"]))  # $49
  else:
    tostring += addNAToString(1)
  if ipstring and ipstring is not None and ipstring != 'NA':
    country = ";"
    aso = ";"
    continent = ";"
    try:
      response = GEOLITE_CITY_READER.city(str(ipstring))
      country += replaceNullNA(str(response.country.name))  # $50
      continent += replaceNullNA(str(response.continent.name))  # $52
    except AddressNotFoundError:
      pass
    except ValueError:
      pass
    except TypeError:
      pass
    try:
      response2 = GEOLITE_ASN_READER.asn(str(ipstring))
      aso += replaceNullNA(str(response2.autonomous_system_organization))  # $51
    except AddressNotFoundError:
      pass
    except ValueError:
      pass
    except TypeError:
      pass
    tostring += country + aso + continent # $50 $51 $52
  else:
    tostring += addNAToString(3)
  tostring += ';' + replaceNullNA(str(record["platform"]))  # $53
  tostring += ';' + replaceNullNA(str(record["sourceRow"]))  # $54
  return tostring

def toStringV1(record):
  tostring = '' + str(record["fileCreationDate"])  # $1
  tostring += ';' + replaceNullNA(str(record["serverSideUploadDate"]))  # $2
  tostring += ';' + str(record["fileCreationDate"])  # $3
  tostring += ';' + str(record["previousValidUploadDate"])  # $4
  tostring += ';' + str(record["sourceFile"])  # $5
  tostring += ';' + str(record["sourceRow"])  # $6
  tostring += ';' + str(record["serverSideUploadDate"])  # $7
  tostring += ';' + str(record["deviceHash"])  # $8
  tostring += ';' + str(record["platform"])  # $9
  ipstring = "NA"
  if record["publicIP"] is not None:
    ipstring = replaceNullNA(replaceProblematicChars(str(record["publicIP"])))
    tostring += ';' + ipstring  # $10
  else :
    tostring += addNAToString(1)
  if record["localIP"] is not None:
    tostring += ';' + replaceProblematicChars(record["localIP"])  # $11
  else :
    tostring += addNAToString(1)
  if "timeStamp" in record :
    tostring += ';' + str(record["timeStamp"])  # $12
  else :
    tostring += addNAToString(1)
  tostring += ';' + str(record["latitude"])  # $13
  tostring += ';' + str(record["longitude"])  # $14
  if "androidVersion" in record :
    tostring += ';' + str(record["androidVersion"])  # $15
  else :
    tostring += addNAToString(1)
  if "discoveryResultCode" in record :
    tostring += ';' + str(record["discoveryResultCode"])  # $16
  else :
    tostring += addNAToString(1)
  try :
    tostring += ';' + str(record["connectionMode"])  # $17
  except:
    tostring += ';'
  try :
    tostring += toBatteryDTOString(record["batteryDTO"])  # $18 -- $25
  except:
    tostring += addNAToString(8)
  if "wifiDTO" in record and record["wifiDTO"] is not None:
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
  if "mobileDTO" in record and record["mobileDTO"] is not None:
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
  if "uptimeInfoDTO" in record and record["uptimeInfoDTO"] is not None:
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

def replaceProblematicCharsInJSON(inputString) :
  inputString = inputString.replace('":",','":"NA",')
  inputString = inputString.replace('"""', '"NA"')
  inputString = inputString.replace('"carrier":""', '"carrier":"NA"')
  inputString = inputString.replace('"simCountryIso":""','"simCountryIso":"NA"')
  inputString = inputString.replace('"networkCountryIso":""','"networkCountryIso":"NA"')
  inputString = inputString.replace('""', '"')
  inputString = inputString.replace('}NEWNEW','}')
  inputString = inputString.replace('"carrier":""TaiwanMobile""', '"carrier":"TaiwanMobile"')
  inputString = inputString.replace('"carrier":""O2 - UK""', '"carrier":"O2 - UK"')
  inputString = inputString.replace('"carrier":""AT&T""', '"carrier":"AT&T"')
  inputString = inputString.replace('"carrier":""OrangeF""', '"carrier":"OrangeF"')
  inputString = inputString.replace('"carrier":""BIMcell""', '"carrier":"BIMcell"')
  inputString = inputString.replace('"carrier":""', '"carrier":"NA"')
  inputString = inputString.replace('"technology":""','"technology":"NA"')
  inputString = inputString.replace('"{','{')
  inputString = inputString.replace('}"','}')
  return inputString

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

def addNAToString(times):
  nas = ''
  for i in range(0, times) :
    nas += ';'
  return nas

def correctDiscoveryResult(nat,exitStatus) :
  if nat == -2 and exitStatus ==  -1 :
    return -3
  if nat == -2  and exitStatus > 0 :
    return -1
  return nat

def readAndPrint(fileList,outSufix):
  differentServerTimePerUser = defaultdict(dict);
  previousValidUploadDate = defaultdict(dict);
  platform = STUNNER_APP_ID
  allRecord = 0
  allFiltered = 0
  counter = 0
  lastTime = time.time()
  lastTime = whatTheTime(lastTime)
  for fileName in fileList:
    counterPerFile = 0
    baseNameString = os.path.basename(fileName).split(".")
    try:
      fileCreationDate = int(baseNameString[0]) * 60 * 60 * 1000
    except:
      fileCreationDate = 0
    try:
      with open('' + INFILE_PATH + fileName) as csvfile:
        stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
        i = 0;
        for line in stunnerReader:
          #originLen = len(line)
          #originLine = line
          line = "|-|".join(line)
          line = replaceProblematicChars(line)
          line = line.split("|-|")
          # if(originLen != len(line)) :
          # print(originLine)
          # print(line)
          for record in line:
            # record = replaceProblematicChars(record)
            if i == 0:
              try:
                serverSideUploadDate = int(record)
              except:
                serverSideUploadDate = 0
            if i == 1:
              userName = str(record)
              if not previousValidUploadDate[userName]:
                previousValidUploadDate[userName] = 0
              if not differentServerTimePerUser[userName]:
                differentServerTimePerUser[userName] = 0
            if i >= 2:
              if re.match('^hu', record) is not None:
                platform = str(record)
              else:
                # record = record.decode('utf-8', errors='ignore').encode('utf-8', errors='ignore')
                # record = record.decode('ascii',errors='ignore')
                # record = record.decode('iso-8859-1',errors='ignore')
                try:
                  record = json.loads(record, strict=False)
                  if not type(record) == type({}):
                    raise ValueError
                except ValueError:
                  record = replaceProblematicCharsInJSON(record)
                  try:
                    record = json.loads(record, strict=False)
                    if not type(record) == type({}):
                      raise ValueError
                  except ValueError:
                    if i >= 4:
                      allFiltered += 1
                      print('Not a JSON! ', str(fileName), str(appVersion), str(userName), str(record), str(line))
                    record = {}
                if record:
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
                    if (int(record["serverSideUploadDate"]) == 0):
                      difInServerAndAndroidTime = 0
                    else:
                      difInServerAndAndroidTime = int(record["serverSideUploadDate"]) - int(record["timeStamp"])
                    if (int(record["fileCreationDate"]) == 0):
                      difInFileAndAndroidTime = 0
                    else:
                      difInFileAndAndroidTime = int(record["timeStamp"]) - int(record["fileCreationDate"])
                    try:
                      appVersion = int(record["appVersion"]);
                    except:
                      appVersion = 1
                    try:
                      triggerCode = int(record["triggerCode"])
                    except:
                      triggerCode = -1
                    if difInServerAndAndroidTime >= MIN_DIF_IN_ANDROID_AND_SERVER_TIME and \
                        difInFileAndAndroidTime <= MAX_DIF_IN_ANDROID_AND_FILE_TIME and \
                        versionReleasDate[appVersion] <= int(record["timeStamp"]):
                      if previousValidUploadDate[userName] != serverSideUploadDate:
                        differentServerTimePerUser[userName] += 1
                        previousValidUploadDate[userName] = serverSideUploadDate
                        record["previousValidUploadDate"] = previousValidUploadDate[userName]
                      if appVersion >= VERSION_TWO_SINCE:
                        outstr = toStringV2(record)
                      else:
                        outstr = toStringV1(record)
                      file = open('' + OUTFILE_PATH + str(outSufix) + '/' +  userName, "a+", encoding="utf-8")
                      file.write('' + outstr + '\n')
                      file.close()
                      # print(previousValidUploadDate[userName], serverSideUploadDate)
                    else:
                      allFiltered += 1
                      # print('Too OLD version of JSON!',fileName,str(appVersion),record["timeStamp"],\
                      #      str(difInServerAndAndroidTime >= MIN_DIF_IN_ANDROID_AND_SERVER_TIME),str(difInServerAndAndroidTime),str(record["serverSideUploadDate"]))
                  except Exception as e:
                    allFiltered += 1
                    print('Missing Record! ', str(fileName), str(userName), str(appVersion), str(line), type(e), e,
                          e.args)
            i += 1;
          if i >= 3:
            i = 0
            counter += 1
            counterPerFile += 1
            if counter % 100000 == 0:
              print(counter)
              sys.stdout.flush()
    except IsADirectoryError:
      print("Warning: " + str(fileName) + " is a directory")
  lastTime = whatTheTime(lastTime)
  print("JSON TO CSV END. ALL RECORD: " + str(allRecord) + " ALL FILTERED: " + str(allFiltered))



print("JSON TO CSV START")
# MAIN
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
  processes.append(multiprocessing.Process(target=readAndPrint, args=(fileList[core], core)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()
