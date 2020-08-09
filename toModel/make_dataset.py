import csv
import json
from itertools import count

import geoip2.database
from geoip2.errors import AddressNotFoundError
import datetime

def categoryToOneHotEncodeVector(pozDict, value, length=None) :
  if length is None :
    length = len(pozDict)
  n = length-1
  oneHotVector = [0] * n
  if value in pozDict and pozDict[value]>=0  :
    oneHotVector[pozDict[value]] = 1
  return oneHotVector

def categoryToIntegerEncodeVector(pozDict, value, startPoz) :
  integer = -1
  if value in pozDict :
   integer = startPoz+pozDict[value]+1
  return integer

def listToCsvStr(outList, delim=',') :
  outStr=''
  if len(outList) > 1 :
    outStr=str(outList[0])
  skipFirst = True
  for element in outList :
    if skipFirst == True :
      skipFirst = False
      continue
    outStr = outStr + str(delim) + str(element)
  return outStr

def listToSvmlightStr(outList) :
  outStr=''
  if len(outList) > 1 :
    outStr=str(outList[0])
  skipFirst = True
  i=0
  for element in outList :
    if skipFirst == True :
      skipFirst = False
      continue
    if element != 0 :
      outStr = outStr + " " + str(i) + ":" +str(element)
    i+=1
  return outStr

def natString(nat1, nat2):
  natA = [int(nat1), int(nat2)]
  natA.sort()
  retStr = ''.join(str(nat) for nat in natA)
  return retStr

def unOrderedNatString(senderNat, receiverNat):
  return ''+str(senderNat)+' '+str(receiverNat)

NA = "N/A"
ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT = r"Timed out with peer"
OFFER_IS_REJECTED_P2P_RES = r"Offer rejected"
FIREBASE_CONNECTION_ERROR_P2P_RES = r"Signaling server error"
UNKNOWN_ERROR_P2P_RES = r"unknownError"
PAIRING_WITH_PREV_VERSION_P2P_RES = r"pairingWithPrevVersion"
CONNECTION_TIMEOUT_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES = r"Timed out without peer"
CONNECTION_TIMEOUT_P2P_RES = r"Timed out"# after successful signaling"
CONNECTION_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES = r"startConnectingWithoutPairOfP2PRecord"
NOBODY_WAS_AVAILABLE_P2P_RES = r"nobodyIsAvailable"
OTHER_UNSUCCESFUL_PAIRING_P2P_RES = r"Others"
SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES = r"successfulConnection"
CONNECTION_FAILED_P2P_RES = r"Connection open failed"
CONNECTION_FAILED_SRLX_ICE_P2P_RES = r"Connection open FailedWithSRLXICE"
CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES = r"connectionOpenFailedWithoutSRLXICE"
PEER_CONNECTION_LOST_P2P_RES = r"Connection lost"
SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES = r"Connection open but transport error"
natStringDict = {}
natStringDict["0"] = "Open access"
natStringDict["3"] = "Full cone"
natStringDict["4"] = "Restricted cone"
natStringDict["5"] = "Port restricted cone"
natStringDict["6"] = "Symmetric cone"
natStringDict["2"] = "Symmetric UDP firewall"
natStringDict["1"] = "Firewall blocks"
natStringDict["-2"] = "No connection"
natStringDict["-1"] = "Measurement error"
natStringDict["-3"] = "NAT type is missing"
natStringDictAbbreviation  = {}
natStringDictAbbreviation["0"] = "OA"
natStringDictAbbreviation["3"] = "FC"
natStringDictAbbreviation["4"] = "RC"
natStringDictAbbreviation["5"] = "PRC"
natStringDictAbbreviation["6"] = "SC"
natStringDictAbbreviation["2"] = "SF"
natStringDictAbbreviation["1"] = "FB"
natStringDictAbbreviation["-2"] = "NA"
natStringDictAbbreviation["-1"] = "ER"
natStringDictAbbreviation["-3"] = "N/A"
p2pList = []
p2pList.append(NA)
p2pList.append(PAIRING_WITH_PREV_VERSION_P2P_RES)
p2pList.append(CONNECTION_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES)
p2pList.append(UNKNOWN_ERROR_P2P_RES)
p2pList.append(CONNECTION_FAILED_P2P_RES)
p2pList.append(CONNECTION_FAILED_SRLX_ICE_P2P_RES)
p2pList.append(CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES)
p2pList.append(SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES)
p2pList.append(PEER_CONNECTION_LOST_P2P_RES)
p2pList.append(CONNECTION_TIMEOUT_P2P_RES)
p2pList.append(SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES)
p2pList.append(CONNECTION_TIMEOUT_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES)
p2pList.append(OFFER_IS_REJECTED_P2P_RES)
p2pList.append(ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT)
p2pList.append(FIREBASE_CONNECTION_ERROR_P2P_RES)
p2pList.append(NOBODY_WAS_AVAILABLE_P2P_RES)
p2pList.append(OTHER_UNSUCCESFUL_PAIRING_P2P_RES)


GEOLITE_CITY_READER = geoip2.database.Reader('../res/geolite/GeoLite2-City.mmdb')
GEOLITE_ASN_READER = geoip2.database.Reader('../res/geolite/GeoLite2-ASN.mmdb')
filelist=[]
filelist.append('../res/res_v2/stuntest-2019-01-22.csv')
filelist.append('../res/res_v2/stuntest-2019-10-02Jakxg.csv')
filelist.append('../res/res_v2/stuntest-2020-04-28DN9pv.csv')
filelist.append('../res/res_v2/stuntest-2020-07-30epx0N.csv')


isHeaderPrinted = False
NUMBER_OF_TRAINING_SET_SIZE = 178778
AV=23
REDUCED_TO = 10
MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH = REDUCED_TO
MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET = REDUCED_TO
MINIMUM_NUMBER_OF_OCCURRENCE_ORG = REDUCED_TO
MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY = REDUCED_TO
haveToContainsHourOfDay = True
haveToContainsDayOfWeek = False
haveToContainsAndroidVersion = True
haveToContainsConnected = False
haveToContainsBandwidth = True
haveToContainsNetworkType = True
haveToContainsRoaming = True
haveToContainsNAT = True
haveToContainsSTUNServer = False
haveToContainsWebRTCTestResult = True
haveToContainsCountryName = True
haveToContainsAutonomousSystemOrganization = True

haveToCreateLookupFiles = True
haveToCreateConnectionDeltaDistribution = True
haveToCreateTimeFile = True
haveToCreateSeparateTestLookupFiles = False
haveToBandwidthBeReal = False
havaToCreateP2PPairExaminationFile = True
if havaToCreateP2PPairExaminationFile == True :
  OUTPUT_PATH_FOR_P2P_PAIR = "p2p_pair/"
  filesOpen = {}

MAX_BANDWIDTH = 1083.0

distConnectionEstablished = {}
numberOfConnectionEstablished = 0
distConnectionFailed = {}
numberOfConnectionFailed = 0

outFileNameCSV= ""
outFileNameSVMLight = ""
outFileNameCSV= outFileNameCSV + "1" if haveToContainsHourOfDay == True else outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsDayOfWeek == True else outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsAndroidVersion == True else outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsConnected == True else outFileNameCSV + "0"
if haveToContainsBandwidth == True :
  if haveToBandwidthBeReal :
    outFileNameSVMLight = outFileNameCSV + "f"
  if MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH <= 1 :
    outFileNameCSV = outFileNameCSV + "1"
  else :
    outFileNameCSV = outFileNameCSV + "r"
else :
  outFileNameCSV = outFileNameCSV + "0"
if haveToContainsNetworkType == True :
  if MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET <= 1 :
    outFileNameCSV = outFileNameCSV + "1"
  else :
    outFileNameCSV = outFileNameCSV + "r"
else :
  outFileNameCSV = outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsRoaming == True else outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsNAT == True else outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsSTUNServer == True else outFileNameCSV + "0"
outFileNameCSV= outFileNameCSV + "1" if haveToContainsWebRTCTestResult == True else outFileNameCSV + "0"
if haveToContainsCountryName == True :
  if MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY <= 1 :
    outFileNameCSV = outFileNameCSV + "1"
  else :
    outFileNameCSV = outFileNameCSV + "r"
else :
  outFileNameCSV = outFileNameCSV + "0"
if haveToContainsAutonomousSystemOrganization == True :
  if MINIMUM_NUMBER_OF_OCCURRENCE_ORG <= 1 :
    outFileNameCSV = outFileNameCSV + "1"
  else :
    outFileNameCSV = outFileNameCSV + "r"
else :
  outFileNameCSV = outFileNameCSV + "0"
#outFileName=outFileName+"1" if haveToContainsAutonomousSystemOrganization == True else outFileName+"0"
if "r" in outFileNameCSV :
  outFileNameCSV = outFileNameCSV + str(REDUCED_TO)
if haveToBandwidthBeReal :
  prefix = outFileNameCSV[len(outFileNameSVMLight):]
  outFileNameSVMLight = outFileNameSVMLight + prefix
  outSVNLightFileName = outFileNameSVMLight + ".svmlight"
else :
  outSVNLightFileName = outFileNameCSV + ".svmlight"
outCsvFileName = outFileNameCSV + ".csv"
fileSVNLight = open(outSVNLightFileName,"w")
fileCSV = open(outCsvFileName,"w")
if haveToCreateLookupFiles == True :
  fileHoursDict = open("dict_hours.csv","w")
  fileDaysDict = open("dict_days.csv","w")
  fileAndroidVersionDict = open("dict_android_versions.csv","w")
  fileOnlineDict = open("dict_online.csv","w")
  if MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH <= 1 :
    fileWifiBandwidthDict = open("dict_wifi_bandwidth.csv","w")
  else :
    fileWifiBandwidthDict = open("dict_wifi_bandwidth"+str(MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH)+".csv", "w")
  if MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET <= 1 :
    fileMobileNetTypeDict = open("dict_mobile_net_type.csv","w")
  else :
    fileMobileNetTypeDict = open("dict_mobile_net_type"+str(MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET)+".csv","w")
  fileRoamingDict = open("dict_roaming.csv","w")
  fileNATDict = open("dict_nat.csv","w")
  fileStunServerDict = open("dict_stunserver.csv","w")
  fileWebRTCTestDict = open("dict_webrtctest.csv","w")
  if MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY <= 1 :
    fileCountryDict = open("dict_country.csv", "w")
  else :
    fileCountryDict = open("dict_country"+str(MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY)+".csv", "w")
  if MINIMUM_NUMBER_OF_OCCURRENCE_ORG <= 1 :
    fileOrgDict = open("dict_org.csv", "w")
  else :
    fileOrgDict = open("dict_org"+str(MINIMUM_NUMBER_OF_OCCURRENCE_ORG)+".csv", "w")
  if haveToCreateSeparateTestLookupFiles == True :
    testFileHoursDict = open("test_dict_hours.csv", "w")
    testFileDaysDict = open("test_dict_days.csv", "w")
    testFileAndroidVersionDict = open("test_dict_android_versions.csv", "w")
    testFileOnlineDict = open("test_dict_online.csv", "w")
    if MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH <= 1:
      testFileWifiBandwidthDict = open("test_dict_wifi_bandwidth.csv", "w")
    else:
      testFileWifiBandwidthDict = open("test_dict_wifi_bandwidth" + str(MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH) + ".csv", "w")
    if MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET <= 1:
      testFileMobileNetTypeDict = open("test_dict_mobile_net_type.csv", "w")
    else:
      testFileMobileNetTypeDict = open("test_dict_mobile_net_type" + str(MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET) + ".csv", "w")
    testFileRoamingDict = open("test_dict_roaming.csv", "w")
    testFileNATDict = open("test_dict_nat.csv", "w")
    testFileStunServerDict = open("test_dict_stunserver.csv", "w")
    testFileWebRTCTestDict = open("test_dict_webrtctest.csv", "w")
    if MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY <= 1:
      testFileCountryDict = open("test_dict_country.csv", "w")
    else:
      testFileCountryDict = open("test_dict_country" + str(MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY) + ".csv", "w")
    if MINIMUM_NUMBER_OF_OCCURRENCE_ORG <= 1:
      testFileOrgDict = open("test_dict_org.csv", "w")
    else:
      testFileOrgDict = open("test_dict_org" + str(MINIMUM_NUMBER_OF_OCCURRENCE_ORG) + ".csv", "w")
m = {}
i=0
for file in filelist :
  with open(file, encoding='utf8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for line in reader:
      i+=1
      if line[0]!="" and line[1] !="" :
        p2pJson = {}
        try :
          p2pJson = json.loads(line[0])
        except :
           #print("p2p",i,line[0])
           pass
        discoveryJson = {}
        try :
          discoveryJson = json.loads(line[1])
        except :
          #print("nat",i,line[1])
          pass
        mJson = {}
        mJson.update(discoveryJson)
        mJson.update(p2pJson)
        ### consistency check
        if not 'androidVersion' in mJson :
          continue
        if not 'appVersion' in mJson :
          continue
        if not 'networkInfo' in mJson:
          continue
        if not 'connectionMode' in mJson :
          continue
        if 'connectionMode' == 1:
          if not 'bandwidth' in mJson['wifiDTO'] :
            continue
        if 'connectionMode' == 0:
          if not 'networkType' in mJson['mobileDTO'] :
            continue
          if not 'roaming' in mJson['mobileDTO'] :
            continue
        if not "natResultsDTO" in mJson:
          continue
        if not 'discoveryResult' in mJson["natResultsDTO"]:
          continue
        if not 'STUNserver' in mJson["natResultsDTO"] :
          continue
        if not 'webRTCResultsDTO' in mJson or not 'exitStatus' in mJson["webRTCResultsDTO"] :
          continue
        ipstring = discoveryJson["natResultsDTO"]['publicIP']
        if ipstring and ipstring is not None and ipstring != 'NA':
          try:
            response = GEOLITE_CITY_READER.city(str(ipstring))
            mJson["countryName"] = str(response.country.name)
          except AddressNotFoundError:
            pass
          except ValueError:
            pass
          except TypeError:
            pass
          try:
            response2 = GEOLITE_ASN_READER.asn(str(ipstring))
            mJson["autonomousSystemOrganization"] = str(response2.autonomous_system_organization)
          except AddressNotFoundError:
            pass
          except ValueError:
            pass
          except TypeError:
            pass
        if not 'countryName' in mJson:
          mJson["countryName"] = "N/A"
        if not 'autonomousSystemOrganization' in mJson :
          mJson["autonomousSystemOrganization"] = "N/A"
        if not 'connectionID' in mJson :
          continue
        if mJson['appVersion'] < AV:
          continue
        if mJson["natResultsDTO"]['discoveryResult'] == -2 or mJson["natResultsDTO"]['discoveryResult'] == -3 :
          continue
        if mJson["natResultsDTO"]['STUNserver'] == "N/A":
          continue
        if mJson['connectionID'] == -1 and mJson['connectionID'] == 0 :
          continue
        ### create connection groups
        if not mJson['connectionID'] in m :
          m[mJson['connectionID']] = {}
        keystring=''+mJson['androidID']+mJson['peerID']+str(mJson['connectionStart'])+str(mJson['recordID'])+str(mJson["natResultsDTO"]['discoveryResult'])
        if len(m[mJson['connectionID']]) < 1 :
          m[mJson['connectionID']][mJson['connectionStart']] = {}
          m[mJson['connectionID']][mJson['connectionStart']][keystring] = mJson
        else :
          isFoundPair = False
          for timestamp, records in m[mJson['connectionID']].items() :
            # 3.5 day => 1000*60*60*24*3.5
            if abs( mJson['connectionStart']-timestamp ) < 1000*60*60*24*3.5 :
              m[mJson['connectionID']][timestamp][keystring] = mJson
              isFoundPair = True
              break
          if isFoundPair == False :
            #print(str(p2pJson['connectionStart']),str(timestamp),str(abs( p2pJson['connectionStart']-timestamp )/1000/60/60/24))
            m[mJson['connectionID']][mJson['connectionStart']] = {}
            m[mJson['connectionID']][mJson['connectionStart']][keystring] = mJson

i=0
finalHourDict = {}
finalDayDict = {}
finalAndroidVersionDict = {}
finalOnlineDict = {}
finalWifiBandwidtDict = {}
finalMobNetDict = {}
finalRoamingDict = {}
finalNatDict = {}
finalStunServerDict = {}
finalWebRtcTestDict = {}
finalCountryDict = {}
finalOrgDict = {}
finalHourDictTest = {}
finalDayDictTest = {}
finalAndroidVersionDictTest = {}
finalOnlineDictTest = {}
finalWifiBandwidtDictTest = {}
finalMobNetDictTest = {}
finalRoamingDictTest = {}
finalNatDictTest = {}
finalStunServerDictTest = {}
finalWebRtcTestDictTest = {}
finalCountryDictTest = {}
finalOrgDictTest = {}
newConId=1
p2pConnectionPeer1 = {}
p2pConnectionPeer2 = {}
for conid, timegroup in m.items() :
  for timestamp, records in  timegroup.items() :
    if len(records) > 1 :
      recordsArray = [] 
      isAnyAboveAV = False
      for key, record in records.items() :
        recordsArray.append(record)    
        if record["appVersion"] >= AV :
          isAnyAboveAV = True
      if isAnyAboveAV == True : 
        isFind = False
        if len(records) == 2 :
          record = recordsArray[0]
          pairRecord = recordsArray[1]
          isFind = True
        else :
          #print('________len:'+str(len(records))+" "+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
          #for key, record in records.items() :
            #print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
          goodPair = []
          for i in range(len(recordsArray)):
            for j in range(i+1,len(recordsArray)) :
              if recordsArray[i]["natResultsDTO"]['discoveryResult'] != -3 and recordsArray[j]["natResultsDTO"]['discoveryResult'] != -3 and recordsArray[i]["natResultsDTO"]['discoveryResult'] != -2 and recordsArray[j]["natResultsDTO"]['discoveryResult'] != -2 :
                if recordsArray[i]["peerID"] == recordsArray[j]["androidID"] and recordsArray[j]["peerID"] == recordsArray[i]["androidID"] :
                  if recordsArray[i]["exitStatus"] == recordsArray[j]["exitStatus"] :
                    goodPair = []
                    goodPair.append((i,j))
                    isFind = True
                    break
                  else :
                    goodPair.append((i,j))
                elif ( recordsArray[i]["peerID"] == 'N/A' and recordsArray[j]["peerID"] == recordsArray[i]["androidID"] ) or ( recordsArray[j]["peerID"] == 'N/A' and recordsArray[i]["peerID"] == recordsArray[j]["androidID"] ) :
                  goodPair.append((i,j))
            if isFind == True :
              break
          if isFind == False :
            if len(goodPair) > 0 :
              #print(str(goodPair))
              #print(str(recordsArray[goodPair[0][0]]["natResultsDTO"]['discoveryResult']))
              #print(str(recordsArray[goodPair[0][1]]["natResultsDTO"]['discoveryResult']))
              if len(goodPair) > 1 :
                #print(str(recordsArray[goodPair[1][1]]["natResultsDTO"]['discoveryResult']))
                #print(str(recordsArray[goodPair[1][1]]["natResultsDTO"]['discoveryResult']))
                pass
              isFind = True
              record = recordsArray[goodPair[0][0]] 
              pairRecord = recordsArray[goodPair[0][1]]     
          else :
            record = recordsArray[goodPair[0][0]]          
            pairRecord = recordsArray[goodPair[0][1]] 
        if isFind == True and pairRecord["appVersion"] >= AV and record["appVersion"] >= AV :
          p2pKeyString = NA
          success = 0
          if pairRecord["peerID"] == record["androidID"] and record["peerID"] == pairRecord["androidID"] :
            if pairRecord["exitStatus"] == 5 or record["exitStatus"] == 5 :
              p2pKeyString = OFFER_IS_REJECTED_P2P_RES
              continue
            elif pairRecord["exitStatus"] == 3 or record["exitStatus"] == 3 :
              p2pKeyString = PEER_CONNECTION_LOST_P2P_RES
              success = 0
            elif pairRecord["exitStatus"] == -2 or record["exitStatus"] == -2 :
              if (pairRecord["appVersion"] >= AV and pairRecord["sender"] == True) or (record["appVersion"] >= AV and record["sender"] == True) :
                p2pKeyString = CONNECTION_TIMEOUT_P2P_RES
              else :
                p2pKeyString = ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT
                #print('_______ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT:'+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
                #print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
                #print(pairRecord["appVersion"],pairRecord["exitStatus"],pairRecord["triggerCode"],pairRecord["androidID"],pairRecord["peerID"],pairRecord["sender"],datetime.utcfromtimestamp(pairRecord["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(pairRecord["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
              success = 0
            elif pairRecord["exitStatus"] == -10 or record["exitStatus"] == -10 :
              p2pKeyString = UNKNOWN_ERROR_P2P_RES
              continue
            elif pairRecord["exitStatus"] == -1 or record["exitStatus"] == -1 :
              p2pKeyString = FIREBASE_CONNECTION_ERROR_P2P_RES
              continue
            elif pairRecord["exitStatus"] == 20 and pairRecord["exitStatus"] == record["exitStatus"] and abs(record["connectionStart"]-pairRecord["connectionStart"])<60000:
              p2pKeyString = SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES
              success = 1
            elif pairRecord["exitStatus"] == 11 and pairRecord["exitStatus"] == record["exitStatus"] :
              p2pKeyString = CONNECTION_FAILED_SRLX_ICE_P2P_RES
              success = 0
            elif (pairRecord["exitStatus"] == 11 and record["exitStatus"] == 10) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 11) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 10) :
              p2pKeyString = CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES
              success = 0
            elif (pairRecord["exitStatus"] == 20 and pairRecord["sender"] == False) or (record["exitStatus"] == 20 and record["sender"] == False) :
              p2pKeyString = SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES
              success = 0
            else :
              #print(conid,record["exitStatus"], pairRecord["exitStatus"])
              continue
          elif (pairRecord["peerID"] == 'N/A' and  record["peerID"] == pairRecord["androidID"])  or (record["peerID"] == 'N/A' and  pairRecord["peerID"] == record["androidID"]) : 
            if ( pairRecord["peerID"] == 'N/A' and pairRecord["exitStatus"] == -2 ) or ( record["peerID"] == 'N/A' and record["exitStatus"] == -2 ):
              p2pKeyString = ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT
              success = 0
            elif pairRecord["exitStatus"] == 5 or record["exitStatus"] == 5 :
              p2pKeyString = OFFER_IS_REJECTED_P2P_RES
              continue
            elif pairRecord["exitStatus"] == -2 or record["exitStatus"] == -2 :
              p2pKeyString = CONNECTION_TIMEOUT_P2P_RES
              success = 0
            elif ( pairRecord["exitStatus"] == 3 or record["exitStatus"] == 3 ) :
              p2pKeyString = PEER_CONNECTION_LOST_P2P_RES # maybe a good pairing, just peerID is not set
              success = 0
            elif pairRecord["exitStatus"] == 20 and pairRecord["exitStatus"] == record["exitStatus"] and abs(record["connectionStart"]-pairRecord["connectionStart"])<60000 :
              p2pKeyString = SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES
              success = 0
            elif pairRecord["exitStatus"] == 11 and pairRecord["exitStatus"] == record["exitStatus"] :
              p2pKeyString = CONNECTION_FAILED_SRLX_ICE_P2P_RES
              success = 0
            elif (pairRecord["exitStatus"] == 11 and record["exitStatus"] == 10) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 11) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 10) :
              p2pKeyString = CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES
              success = 0
            elif (pairRecord["exitStatus"] == 20 and pairRecord["sender"] == False) or (record["exitStatus"] == 20 and record["sender"] == False) :
              p2pKeyString = SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES
              success = 1
            else :
              #print('________notAPair:'+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
              #print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
              #print(pairRecord["appVersion"],pairRecord["exitStatus"],pairRecord["triggerCode"],pairRecord["androidID"],pairRecord["peerID"],pairRecord["sender"],datetime.utcfromtimestamp(pairRecord["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(pairRecord["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
              continue
          else :
            continue
          if record["sender"] == False :
            tmprecord = record
            record =  pairRecord
            pairRecord = tmprecord
          record["p2pResult"] = success
          pairRecord["p2pResult"] = success
          if success == 1 :
            recordDeltaConnection = int((int(record["channelOpen"]) - int(record["connectionStart"]))/1000)
            pairRecordDeltaConnection = int((int(pairRecord["channelOpen"]) - int(pairRecord["connectionStart"]))/1000)
            numberOfConnectionEstablished += 2
            if recordDeltaConnection in distConnectionEstablished :
              distConnectionEstablished[recordDeltaConnection] += 1
            else :
              distConnectionEstablished[recordDeltaConnection] = 1
            if pairRecordDeltaConnection in distConnectionEstablished:
              distConnectionEstablished[pairRecordDeltaConnection] += 1
            else:
              distConnectionEstablished[pairRecordDeltaConnection] = 1
          else :
            recordDeltaConnection = int((int(record["connectionEnd"]) - int(record["connectionStart"]))/1000)
            pairRecordDeltaConnection = int((int(pairRecord["connectionEnd"]) - int(pairRecord["connectionStart"]))/1000)
            numberOfConnectionFailed += 2
            if recordDeltaConnection in distConnectionFailed :
              distConnectionFailed[recordDeltaConnection] += 1
            else :
              distConnectionFailed[recordDeltaConnection] = 1
            if pairRecordDeltaConnection in distConnectionFailed:
              distConnectionFailed[pairRecordDeltaConnection] += 1
            else:
              distConnectionFailed[pairRecordDeltaConnection] = 1

          p2pConnectionPeer1[newConId] = record
          p2pConnectionPeer2[newConId] = pairRecord
          newConId+=1
          if haveToCreateSeparateTestLookupFiles == True and newConId >=  NUMBER_OF_TRAINING_SET_SIZE :
            ####timeInfo
            timeObj = datetime.datetime.utcfromtimestamp(round(timestamp / 1000.0))
            weekDay = timeObj.weekday()
            hour = timeObj.hour
            if not hour in finalHourDictTest:
              finalHourDictTest[hour] = 1
            else:
              finalHourDictTest[hour] += 1
            if not weekDay in finalDayDictTest:
              finalDayDictTest[weekDay] = 1
            else:
              finalDayDictTest[weekDay] += 1
            ####androidVersion
            if not record["androidVersion"] in finalAndroidVersionDictTest:
              finalAndroidVersionDictTest[record["androidVersion"]] = 1
            else:
              finalAndroidVersionDictTest[record["androidVersion"]] += 1
            if not pairRecord["androidVersion"] in finalAndroidVersionDictTest:
              finalAndroidVersionDictTest[pairRecord["androidVersion"]] = 1
            else:
              finalAndroidVersionDictTest[pairRecord["androidVersion"]] += 1
            ####networkInfo
            if not record["networkInfo"] in finalOnlineDictTest:
              finalOnlineDictTest[record["networkInfo"]] = 1
            else:
              finalOnlineDictTest[record["networkInfo"]] += 1
            if not pairRecord["networkInfo"] in finalOnlineDictTest:
              finalOnlineDictTest[pairRecord["networkInfo"]] = 1
            else:
              finalOnlineDictTest[pairRecord["networkInfo"]] += 1
            ####bandwidth
            if record["connectionMode"] == 1:
              if not record["wifiDTO"]["bandwidth"] in finalWifiBandwidtDictTest:
                finalWifiBandwidtDictTest[record["wifiDTO"]["bandwidth"]] = 1
              else:
                finalWifiBandwidtDictTest[record["wifiDTO"]["bandwidth"]] += 1
            if pairRecord["connectionMode"] == 1:
              if not pairRecord["wifiDTO"]["bandwidth"] in finalWifiBandwidtDictTest:
                finalWifiBandwidtDictTest[pairRecord["wifiDTO"]["bandwidth"]] = 1
              else:
                finalWifiBandwidtDictTest[pairRecord["wifiDTO"]["bandwidth"]] += 1
            ####networkType
            if record["connectionMode"] == 0:
              if not record["mobileDTO"]["networkType"] in finalMobNetDictTest:
                finalMobNetDictTest[record["mobileDTO"]["networkType"]] = 1
              else:
                finalMobNetDictTest[record["mobileDTO"]["networkType"]] += 1
            if pairRecord["connectionMode"] == 0:
              if not pairRecord["mobileDTO"]["networkType"] in finalMobNetDictTest:
                finalMobNetDictTest[pairRecord["mobileDTO"]["networkType"]] = 1
              else:
                finalMobNetDictTest[pairRecord["mobileDTO"]["networkType"]] += 1
            ####roaming
            if not record["mobileDTO"]["roaming"] in finalRoamingDictTest:
              finalRoamingDictTest[record["mobileDTO"]["roaming"]] = 1
            else:
              finalRoamingDictTest[record["mobileDTO"]["roaming"]] += 1
            if not pairRecord["mobileDTO"]["roaming"] in finalRoamingDictTest:
              finalRoamingDictTest[pairRecord["mobileDTO"]["roaming"]] = 1
            else:
              finalRoamingDictTest[pairRecord["mobileDTO"]["roaming"]] += 1
            ####discoveryResult
            if not record["natResultsDTO"]["discoveryResult"] in finalNatDictTest:
              finalNatDictTest[record["natResultsDTO"]["discoveryResult"]] = 1
            else:
              finalNatDictTest[record["natResultsDTO"]["discoveryResult"]] += 1
            if not pairRecord["natResultsDTO"]["discoveryResult"] in finalNatDictTest:
              finalNatDictTest[pairRecord["natResultsDTO"]["discoveryResult"]] = 1
            else:
              finalNatDictTest[pairRecord["natResultsDTO"]["discoveryResult"]] += 1
            ####STUNserver
            if not record["natResultsDTO"]["STUNserver"] in finalStunServerDictTest:
              finalStunServerDictTest[record["natResultsDTO"]["STUNserver"]] = 1
            else:
              finalStunServerDictTest[record["natResultsDTO"]["STUNserver"]] += 1
            if not pairRecord["natResultsDTO"]["STUNserver"] in finalStunServerDictTest:
              finalStunServerDictTest[pairRecord["natResultsDTO"]["STUNserver"]] = 1
            else:
              finalStunServerDictTest[pairRecord["natResultsDTO"]["STUNserver"]] += 1
            ####webRTCTestResult
            if not record["webRTCResultsDTO"]["exitStatus"] in finalWebRtcTestDictTest:
              finalWebRtcTestDictTest[record["webRTCResultsDTO"]["exitStatus"]] = 1
            else:
              finalWebRtcTestDictTest[record["webRTCResultsDTO"]["exitStatus"]] += 1
            if not pairRecord["webRTCResultsDTO"]["exitStatus"] in finalWebRtcTestDictTest:
              finalWebRtcTestDictTest[pairRecord["webRTCResultsDTO"]["exitStatus"]] = 1
            else:
              finalWebRtcTestDictTest[pairRecord["webRTCResultsDTO"]["exitStatus"]] += 1
            ####countryName
            if not record["countryName"] in finalCountryDictTest:
              finalCountryDictTest[record["countryName"]] = 1
            else:
              finalCountryDictTest[record["countryName"]] += 1
            if not pairRecord["countryName"] in finalCountryDictTest:
              finalCountryDictTest[pairRecord["countryName"]] = 1
            else:
              finalCountryDictTest[pairRecord["countryName"]] += 1
            ####autonomousSystemOrganization
            if not record["autonomousSystemOrganization"] in finalOrgDictTest:
              finalOrgDictTest[record["autonomousSystemOrganization"]] = 1
            else:
              finalOrgDictTest[record["autonomousSystemOrganization"]] += 1
            if not pairRecord["autonomousSystemOrganization"] in finalOrgDictTest:
              finalOrgDictTest[pairRecord["autonomousSystemOrganization"]] = 1
            else:
              finalOrgDictTest[pairRecord["autonomousSystemOrganization"]] += 1
          else :
            ####timeInfo
            timeObj = datetime.datetime.utcfromtimestamp(round(timestamp / 1000.0))
            weekDay = timeObj.weekday()
            hour = timeObj.hour
            if not hour in finalHourDict:
              finalHourDict[hour] = 1
            else:
              finalHourDict[hour] += 1
            if not weekDay in finalDayDict:
              finalDayDict[weekDay] = 1
            else:
              finalDayDict[weekDay] += 1
            ####androidVersion
            if not record["androidVersion"] in finalAndroidVersionDict:
              finalAndroidVersionDict[record["androidVersion"]] = 1
            else:
              finalAndroidVersionDict[record["androidVersion"]] += 1
            if not pairRecord["androidVersion"] in finalAndroidVersionDict:
              finalAndroidVersionDict[pairRecord["androidVersion"]] = 1
            else:
              finalAndroidVersionDict[pairRecord["androidVersion"]] += 1
            ####networkInfo
            if not record["networkInfo"] in finalOnlineDict:
              finalOnlineDict[record["networkInfo"]] = 1
            else:
              finalOnlineDict[record["networkInfo"]] += 1
            if not pairRecord["networkInfo"] in finalOnlineDict:
              finalOnlineDict[pairRecord["networkInfo"]] = 1
            else:
              finalOnlineDict[pairRecord["networkInfo"]] += 1
            ####bandwidth
            if record["connectionMode"] == 1:
              if not record["wifiDTO"]["bandwidth"] in finalWifiBandwidtDict:
                finalWifiBandwidtDict[record["wifiDTO"]["bandwidth"]] = 1
              else:
                finalWifiBandwidtDict[record["wifiDTO"]["bandwidth"]] += 1
            if pairRecord["connectionMode"] == 1:
              if not pairRecord["wifiDTO"]["bandwidth"] in finalWifiBandwidtDict:
                finalWifiBandwidtDict[pairRecord["wifiDTO"]["bandwidth"]] = 1
              else:
                finalWifiBandwidtDict[pairRecord["wifiDTO"]["bandwidth"]] += 1
            ####networkType
            if record["connectionMode"] == 0:
              if not record["mobileDTO"]["networkType"] in finalMobNetDict:
                finalMobNetDict[record["mobileDTO"]["networkType"]] = 1
              else:
                finalMobNetDict[record["mobileDTO"]["networkType"]] += 1
            if pairRecord["connectionMode"] == 0:
              if not pairRecord["mobileDTO"]["networkType"] in finalMobNetDict:
                finalMobNetDict[pairRecord["mobileDTO"]["networkType"]] = 1
              else:
                finalMobNetDict[pairRecord["mobileDTO"]["networkType"]] += 1
            ####roaming
            if not record["mobileDTO"]["roaming"] in finalRoamingDict:
              finalRoamingDict[record["mobileDTO"]["roaming"]] = 1
            else:
              finalRoamingDict[record["mobileDTO"]["roaming"]] += 1
            if not pairRecord["mobileDTO"]["roaming"] in finalRoamingDict:
              finalRoamingDict[pairRecord["mobileDTO"]["roaming"]] = 1
            else:
              finalRoamingDict[pairRecord["mobileDTO"]["roaming"]] += 1
            ####discoveryResult
            if not record["natResultsDTO"]["discoveryResult"] in finalNatDict :
              finalNatDict[record["natResultsDTO"]["discoveryResult"]] = 1
            else:
              finalNatDict[record["natResultsDTO"]["discoveryResult"]] += 1
            if not pairRecord["natResultsDTO"]["discoveryResult"] in finalNatDict:
              finalNatDict[pairRecord["natResultsDTO"]["discoveryResult"]] = 1
            else:
              finalNatDict[pairRecord["natResultsDTO"]["discoveryResult"]] += 1
            ####STUNserver
            if not record["natResultsDTO"]["STUNserver"] in finalStunServerDict:
              finalStunServerDict[record["natResultsDTO"]["STUNserver"]] = 1
            else:
              finalStunServerDict[record["natResultsDTO"]["STUNserver"]] += 1
            if not pairRecord["natResultsDTO"]["STUNserver"] in finalStunServerDict:
              finalStunServerDict[pairRecord["natResultsDTO"]["STUNserver"]] = 1
            else:
              finalStunServerDict[pairRecord["natResultsDTO"]["STUNserver"]] += 1
            ####webRTCTestResult
            if not record["webRTCResultsDTO"]["exitStatus"] in finalWebRtcTestDict:
              finalWebRtcTestDict[record["webRTCResultsDTO"]["exitStatus"]] = 1
            else:
              finalWebRtcTestDict[record["webRTCResultsDTO"]["exitStatus"]] += 1
            if not pairRecord["webRTCResultsDTO"]["exitStatus"] in finalWebRtcTestDict:
              finalWebRtcTestDict[pairRecord["webRTCResultsDTO"]["exitStatus"]] = 1
            else:
              finalWebRtcTestDict[pairRecord["webRTCResultsDTO"]["exitStatus"]] += 1
            ####countryName
            if not record["countryName"] in finalCountryDict:
              finalCountryDict[record["countryName"]] = 1
            else:
              finalCountryDict[record["countryName"]] += 1
            if not pairRecord["countryName"] in finalCountryDict:
              finalCountryDict[pairRecord["countryName"]] = 1
            else:
              finalCountryDict[pairRecord["countryName"]] += 1
            ####autonomousSystemOrganization
            if not record["autonomousSystemOrganization"] in finalOrgDict:
              finalOrgDict[record["autonomousSystemOrganization"]] = 1
            else:
              finalOrgDict[record["autonomousSystemOrganization"]] += 1
            if not pairRecord["autonomousSystemOrganization"] in finalOrgDict:
              finalOrgDict[pairRecord["autonomousSystemOrganization"]] = 1
            else:
              finalOrgDict[pairRecord["autonomousSystemOrganization"]] += 1

hoursOfDayPozDict = {}
daysOfWeekPozDict = {}
andverDictPozDict = {}
bandwidthDictPozDict = {}
mobnetDictPozDict = {}
natDictPozDict = {}
stunserDictPozDict = {}
countryDictPozDict = {}
orgDictPozDict = {}
poz = -1
for hour in range(24):
  hoursOfDayPozDict[hour] = poz
  poz += 1
poz = -1
for day in range(7):
  daysOfWeekPozDict[day] = poz
  poz += 1
poz = -1
for androidVersion in finalAndroidVersionDict :
  andverDictPozDict[androidVersion] = poz
  poz += 1
bandwidthDictPozDict["N/A"] = -1
if MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH == 1 :
  poz = 0
  for bandwidth in finalWifiBandwidtDict :
    if bandwidth == "N/A" :
      continue
    bandwidthDictPozDict[bandwidth] = poz
    poz += 1
  bandwidthDictLength = len(bandwidthDictPozDict)
else :
  poz = 1
  for bandwidth in finalWifiBandwidtDict:
    if bandwidth == "N/A" :
      continue
    if haveToCreateSeparateTestLookupFiles == True and bandwidth in finalWifiBandwidtDictTest:
      occurrence = finalWifiBandwidtDict[bandwidth]
      occurrence += finalWifiBandwidtDictTest[bandwidth]
    else :
      occurrence = finalWifiBandwidtDict[bandwidth]
    if occurrence >= MINIMUM_NUMBER_OF_OCCURRENCE_BANDWIDTH or bandwidth == "0	Mbps":
      bandwidthDictPozDict[bandwidth] = poz
      poz += 1
    else :
      bandwidthDictPozDict[bandwidth] = 0
  bandwidthDictLength = poz + 1
mobnetDictPozDict["N/A"] = -1
if MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET == 1 :
  poz = 0
  for netType in  finalMobNetDict:
    if netType == "N/A" :
      continue
    mobnetDictPozDict[netType] = poz
    poz += 1
  mobnetDictLength = len(mobnetDictPozDict)
else :
  poz = 1
  for netType in finalMobNetDict:
    if netType == "N/A" :
      continue
    if haveToCreateSeparateTestLookupFiles == True and netType in finalMobNetDictTest :
      occurrence = finalMobNetDict[netType] + finalMobNetDictTest[netType]
    else :
      occurrence = finalMobNetDict[netType]
    if occurrence >= MINIMUM_NUMBER_OF_OCCURRENCE_MOBNET :
      mobnetDictPozDict[netType] = poz
      poz += 1
    else:
      mobnetDictPozDict[netType] = 0
  mobnetDictLength = poz + 1
poz = -1
for natType in finalNatDict :
  natDictPozDict[natType] = poz
  poz += 1
poz = -1
for stunser in finalStunServerDict :
  stunserDictPozDict[stunser] = poz
  poz += 1
if MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY == 1 :
  poz = -1
  for country in finalCountryDict :
    countryDictPozDict[country] = poz
    poz += 1
  countryDictLength = len(countryDictPozDict)
else :
  poz = 0
  for country in finalCountryDict:
    if haveToCreateSeparateTestLookupFiles == True and country in finalCountryDictTest :
      occurrence = finalCountryDict[country] + finalCountryDictTest[country]
    else :
      occurrence = finalCountryDict[country]
    if occurrence >= MINIMUM_NUMBER_OF_OCCURRENCE_COUNTRY :
      countryDictPozDict[country] = poz
      poz += 1
    else :
      countryDictPozDict[country] = -1
  countryDictLength = poz+1
if MINIMUM_NUMBER_OF_OCCURRENCE_ORG == 1 :
  poz = -1
  for org in finalOrgDict:
    orgDictPozDict[org] = poz
    poz += 1
  orgDictLength = len(orgDictPozDict)
else :
  poz = 0
  for org in finalOrgDict :
    if haveToCreateSeparateTestLookupFiles == True and org in finalOrgDictTest :
      occurrence = finalOrgDict[org] + finalOrgDictTest[org]
    else :
      occurrence = finalOrgDict[org]
    if occurrence >= MINIMUM_NUMBER_OF_OCCURRENCE_ORG :
      orgDictPozDict[org] = poz
      poz += 1
    else :
      orgDictPozDict[org] = -1
  orgDictLength=poz+1
if haveToCreateTimeFile == True :
  timeFile = open("times.dat", "w")

if haveToCreateConnectionDeltaDistribution == True :
  establishedConnectionDeltaDistributionFile = open("establishedConnectionDeltaDistribution.out", "w")
  failedConnectionDeltaDistributionFile = open("failedConnectionDeltaDistribution.out", "w")
#print(len(p2pConnectionPeer1))

if havaToCreateP2PPairExaminationFile == True :
  numberOfOpenFile = 0

for newConId in p2pConnectionPeer1 :
  sampleListOneHot = []
  sampleListInteger = []
  listIntegerRange = []
  integerDict = 0
  record =  p2pConnectionPeer1[newConId]
  pairRecord = p2pConnectionPeer2[newConId]
  sampleListOneHot.append(record["p2pResult"])
  sampleListInteger.append(record["p2pResult"])
  listIntegerRange.append(0)
  ### time related features
  timestamp = record['connectionStart']
  timeObj = datetime.datetime.utcfromtimestamp(round(timestamp/1000.0))
  if haveToCreateTimeFile == True:
    print(str(timeObj), timestamp,file=timeFile)
  weekDay = timeObj.weekday()
  hour = timeObj.hour
  ####timeInfo
  if haveToContainsHourOfDay == True:
    sampleListOneHot.extend(categoryToOneHotEncodeVector(hoursOfDayPozDict, hour))
    sampleListInteger.append(categoryToIntegerEncodeVector(hoursOfDayPozDict, hour, integerDict))
    integerDict += len(hoursOfDayPozDict)
    listIntegerRange.append(integerDict)
  if haveToContainsDayOfWeek == True:
    sampleListOneHot.extend(categoryToOneHotEncodeVector(daysOfWeekPozDict, weekDay))
    sampleListInteger.append(categoryToIntegerEncodeVector(daysOfWeekPozDict, weekDay, integerDict))
    integerDict += len(daysOfWeekPozDict)
    listIntegerRange.append(integerDict)
  ####androidVersion
  if haveToContainsAndroidVersion == True :
    sampleListOneHot.extend(categoryToOneHotEncodeVector(andverDictPozDict, record["androidVersion"]))
    sampleListOneHot.extend(categoryToOneHotEncodeVector(andverDictPozDict, pairRecord["androidVersion"]))
    sampleListInteger.append(categoryToIntegerEncodeVector(andverDictPozDict, record["androidVersion"], integerDict))
    sampleListInteger.append(categoryToIntegerEncodeVector(andverDictPozDict, pairRecord["androidVersion"], integerDict))
    integerDict += len(andverDictPozDict)
    listIntegerRange.append(integerDict)
  ####networkInfo
  if haveToContainsConnected == True :
    if record["networkInfo"] == 5 :
      sampleListOneHot.append(1)
      sampleListInteger.append(integerDict+1)
    else :
      sampleListOneHot.append(0)
      sampleListInteger.append(integerDict + 0)
    if pairRecord["networkInfo"] == 5:
      sampleListOneHot.append(1)
      sampleListInteger.append(integerDict + 1)
    else:
      sampleListOneHot.append(0)
      sampleListInteger.append(integerDict + 0)
    integerDict += 2
    listIntegerRange.append(integerDict)
  ####bandwidth
  if haveToContainsBandwidth == True :
    if record["connectionMode"] == 1:
      if haveToBandwidthBeReal == True :
        bandwidth = int(record["wifiDTO"]["bandwidth"].split(" ")[0])
        if bandwidth <= 0 :
          result = 0
        elif bandwidth >= MAX_BANDWIDTH :
          result = 1
        else :
          result = bandwidth/MAX_BANDWIDTH
        sampleListOneHot.append(result)
        #print(record["wifiDTO"]["bandwidth"], str(bandwidth) , str(result))
      else :
        sampleListOneHot.extend(categoryToOneHotEncodeVector(bandwidthDictPozDict, record["wifiDTO"]["bandwidth"], bandwidthDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(bandwidthDictPozDict, record["wifiDTO"]["bandwidth"], integerDict))
    else:
      if haveToBandwidthBeReal == True:
        sampleListOneHot.append(0)
      else :
        sampleListOneHot.extend(categoryToOneHotEncodeVector(bandwidthDictPozDict, "N/A", bandwidthDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(bandwidthDictPozDict, "N/A", integerDict))
    if pairRecord["connectionMode"] == 1:
      if haveToBandwidthBeReal == True :
        bandwidth = int(pairRecord["wifiDTO"]["bandwidth"].split(" ")[0])
        if bandwidth <= 0 :
          result = 0
        elif bandwidth >= MAX_BANDWIDTH :
          result = 1
        else :
          result = bandwidth/MAX_BANDWIDTH
        sampleListOneHot.append(result)
      else :
        sampleListOneHot.extend(categoryToOneHotEncodeVector(bandwidthDictPozDict, pairRecord["wifiDTO"]["bandwidth"], bandwidthDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(bandwidthDictPozDict, pairRecord["wifiDTO"]["bandwidth"], integerDict))
    else:
      if haveToBandwidthBeReal == True:
        sampleListOneHot.append(0)
      else:
        sampleListOneHot.extend(categoryToOneHotEncodeVector(bandwidthDictPozDict, "N/A", bandwidthDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(bandwidthDictPozDict, "N/A", integerDict))
    integerDict += bandwidthDictLength
    listIntegerRange.append(integerDict)
  ####networkType
  if haveToContainsNetworkType == True :
    if record["connectionMode"] == 0:
      sampleListOneHot.extend(categoryToOneHotEncodeVector(mobnetDictPozDict, record["mobileDTO"]["networkType"], mobnetDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(mobnetDictPozDict, record["mobileDTO"]["networkType"], integerDict))
    else :
      sampleListOneHot.extend(categoryToOneHotEncodeVector(mobnetDictPozDict, "N/A", mobnetDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(mobnetDictPozDict, "N/A", integerDict))
    if pairRecord["connectionMode"] == 0:
      sampleListOneHot.extend(categoryToOneHotEncodeVector(mobnetDictPozDict, pairRecord["mobileDTO"]["networkType"], mobnetDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(mobnetDictPozDict, pairRecord["mobileDTO"]["networkType"], integerDict))
    else:
      sampleListOneHot.extend(categoryToOneHotEncodeVector(mobnetDictPozDict, "N/A", mobnetDictLength))
      sampleListInteger.append(categoryToIntegerEncodeVector(mobnetDictPozDict, "N/A", integerDict))
    integerDict += mobnetDictLength
    listIntegerRange.append(integerDict)
  ####roaming
  if haveToContainsRoaming == True :
    if str(record["mobileDTO"]["roaming"]) == "true" :
      sampleListOneHot.append(1)
      sampleListInteger.append(integerDict + 1)
    else :
      sampleListOneHot.append(0)
      sampleListInteger.append(integerDict + 0)
    if str(pairRecord["mobileDTO"]["roaming"]) == "true" :
      sampleListOneHot.append(1)
      sampleListInteger.append(integerDict + 1)
    else :
      sampleListOneHot.append(0)
      sampleListInteger.append(integerDict + 0)
    integerDict += 2
    listIntegerRange.append(integerDict)
  ####discoveryResult
  if haveToContainsNAT == True :
    sampleListOneHot.extend(categoryToOneHotEncodeVector(natDictPozDict, record["natResultsDTO"]["discoveryResult"]))
    sampleListInteger.append(categoryToIntegerEncodeVector(natDictPozDict, record["natResultsDTO"]["discoveryResult"], integerDict))
    sampleListOneHot.extend(categoryToOneHotEncodeVector(natDictPozDict, pairRecord["natResultsDTO"]["discoveryResult"]))
    sampleListInteger.append(categoryToIntegerEncodeVector(natDictPozDict, pairRecord["natResultsDTO"]["discoveryResult"], integerDict))
    integerDict += len(natDictPozDict)
    listIntegerRange.append(integerDict)
  ####STUNserver
  if haveToContainsSTUNServer == True :
    sampleListOneHot.extend(categoryToOneHotEncodeVector(stunserDictPozDict, record["natResultsDTO"]["STUNserver"]))
    sampleListInteger.append(categoryToIntegerEncodeVector(stunserDictPozDict, pairRecord["natResultsDTO"]["STUNserver"], integerDict))
    sampleListOneHot.extend(categoryToOneHotEncodeVector(stunserDictPozDict, pairRecord["natResultsDTO"]["STUNserver"]))
    sampleListInteger.append(categoryToIntegerEncodeVector(stunserDictPozDict, pairRecord["natResultsDTO"]["STUNserver"], integerDict))
    integerDict += len(stunserDictPozDict)
    listIntegerRange.append(integerDict)
  ####webRTCTestResult
  if str(record["webRTCResultsDTO"]["exitStatus"]) == "20":
    webRTCResults = 1
  else :
    webRTCResults = 0
  if str(pairRecord["webRTCResultsDTO"]["exitStatus"]) == "20":
    peerWebRTCResults = 1
  else:
    peerWebRTCResults = 0
  if haveToContainsWebRTCTestResult == True :
    sampleListOneHot.append(webRTCResults)
    sampleListInteger.append(integerDict + webRTCResults)
    sampleListOneHot.append(peerWebRTCResults)
    sampleListInteger.append(integerDict + peerWebRTCResults)
    integerDict += 2
    listIntegerRange.append(integerDict)
  ####countryName
  if haveToContainsCountryName ==  True :
    sampleListOneHot.extend(categoryToOneHotEncodeVector(countryDictPozDict, record["countryName"], countryDictLength))
    sampleListInteger.append(categoryToIntegerEncodeVector(countryDictPozDict, record["countryName"], integerDict))
    sampleListOneHot.extend(categoryToOneHotEncodeVector(countryDictPozDict, pairRecord["countryName"], countryDictLength))
    sampleListInteger.append(categoryToIntegerEncodeVector(countryDictPozDict, pairRecord["countryName"], integerDict))
    integerDict += countryDictLength
    listIntegerRange.append(integerDict)
  ####autonomousSystemOrganization
  if haveToContainsAutonomousSystemOrganization == True :
    sampleListOneHot.extend(categoryToOneHotEncodeVector(orgDictPozDict, record["autonomousSystemOrganization"], orgDictLength))
    sampleListInteger.append(categoryToIntegerEncodeVector(orgDictPozDict, record["autonomousSystemOrganization"], integerDict))
    sampleListOneHot.extend(categoryToOneHotEncodeVector(orgDictPozDict, pairRecord["autonomousSystemOrganization"], orgDictLength))
    sampleListInteger.append(categoryToIntegerEncodeVector(orgDictPozDict, pairRecord["autonomousSystemOrganization"], integerDict))
    integerDict += orgDictLength
    listIntegerRange.append(integerDict)
  if isHeaderPrinted == False :
    print("#vocab_size = "+str(integerDict),file=fileCSV)
    isHeaderPrinted = True
  if len(sampleListOneHot) >= 3 :
    print(listToSvmlightStr(sampleListOneHot),file=fileSVNLight)
  #print("#"+listToCsvStr(listIntegerRange))
  print(listToCsvStr(sampleListInteger),file=fileCSV)
  #print(listToCsvStr(sampleList))
  if havaToCreateP2PPairExaminationFile == True :
    pairID = [ str(record["androidID"]) , pairRecord["androidID"]]
    pairID.sort()
    pairID = "".join(pairID)
    pairID = pairID.replace("N/A","NA")
    filenamePairID = OUTPUT_PATH_FOR_P2P_PAIR + pairID
    if numberOfOpenFile >= 1000 :
      for fileN in list(filesOpen):
        filesOpen[fileN].close()
        del filesOpen[fileN]
        numberOfOpenFile -= 1
    if filenamePairID not in filesOpen :
      filesOpen[filenamePairID] = open(filenamePairID, "a+", encoding="utf-8")
      numberOfOpenFile+=1
    print(str(record["p2pResult"]), str(record["timeStamp"]),
          "1:", str(record["androidID"]), str(webRTCResults), str(record["natResultsDTO"]["discoveryResult"]), str(record["natResultsDTO"]["publicIP"]) ,
          "2:", str(pairRecord["androidID"]), str(peerWebRTCResults), str(pairRecord["natResultsDTO"]["discoveryResult"]), str(pairRecord["natResultsDTO"]["publicIP"]), file=filesOpen[filenamePairID])
fileSVNLight.close()
fileCSV.close()
if haveToCreateTimeFile == True :
  timeFile.close()
if havaToCreateP2PPairExaminationFile == True :
  for file in filesOpen :
    file.close()

if haveToCreateConnectionDeltaDistribution == True :
  sumOfRate= 0
  for timeKey in sorted(distConnectionEstablished) :
    rateOfConnectionEstablished = distConnectionEstablished[timeKey]/numberOfConnectionEstablished
    sumOfRate+=rateOfConnectionEstablished
    print(str(timeKey),str(distConnectionEstablished[timeKey]),str(rateOfConnectionEstablished),str(sumOfRate), file=establishedConnectionDeltaDistributionFile)
  sumOfRate= 0
  for timeKey in sorted(distConnectionFailed) :
    rateOfConnectionFailed = distConnectionFailed[timeKey]/numberOfConnectionFailed
    sumOfRate+=rateOfConnectionFailed
    print(str(timeKey),str(distConnectionFailed[timeKey]),str(rateOfConnectionFailed),str(sumOfRate), file=failedConnectionDeltaDistributionFile)
  establishedConnectionDeltaDistributionFile.close()
  failedConnectionDeltaDistributionFile.close()

if haveToCreateLookupFiles == True :
  for hour in hoursOfDayPozDict :
    try:
      print(finalHourDict[hour], hoursOfDayPozDict[hour], hour, sep=';', file=fileHoursDict)
    except KeyError:
      print("0", hoursOfDayPozDict[hour], hour, sep=';', file=fileHoursDict)
  for day in daysOfWeekPozDict :
    try:
      print(finalDayDict[day], daysOfWeekPozDict[day], day, sep=';', file=fileDaysDict)
    except KeyError:
      print("0", daysOfWeekPozDict[day], day, sep=';', file=fileDaysDict)
  for version in andverDictPozDict:
    try :
      print(finalAndroidVersionDict[version], andverDictPozDict[version], version, sep=';', file=fileAndroidVersionDict)
    except KeyError :
      print("0", andverDictPozDict[version], version, sep=';', file=fileAndroidVersionDict)
  for online in finalOnlineDict :
    if str(online) == "5" :
      print(finalOnlineDict[online], 1, str(online), sep=';', file=fileOnlineDict)
    else :
      print(finalOnlineDict[online], 0, str(online), sep=';', file=fileOnlineDict)
  for type_bandwidth in bandwidthDictPozDict :
    try:
      print(finalWifiBandwidtDict[type_bandwidth], bandwidthDictPozDict[type_bandwidth], type_bandwidth, sep=';', file=fileWifiBandwidthDict)
    except KeyError :
      print("0", bandwidthDictPozDict[type_bandwidth], type_bandwidth, sep=';', file=fileWifiBandwidthDict)
  for type_mobnet in mobnetDictPozDict :
    try :
      print(finalMobNetDict[type_mobnet], mobnetDictPozDict[type_mobnet], type_mobnet, sep=';', file=fileMobileNetTypeDict)
    except KeyError :
      print("0", mobnetDictPozDict[type_mobnet], type_mobnet, sep=';', file=fileMobileNetTypeDict)
  for roaming in finalRoamingDict :
    if str(roaming) == "True" :
      print(finalRoamingDict[roaming], 0, str(roaming), sep=';', file=fileRoamingDict)
    else :
      print(finalRoamingDict[roaming], -1, str(roaming), sep=';', file=fileRoamingDict)
  for nat in natDictPozDict :
    try :
      print(finalNatDict[nat], natDictPozDict[nat], nat, sep=';', file=fileNATDict)
    except KeyError:
      print("0", natDictPozDict[nat], nat, sep=';', file=fileNATDict)
  for stunserver in stunserDictPozDict :
    try:
      print(finalStunServerDict[stunserver], stunserDictPozDict[stunserver], stunserver, sep=';', file=fileStunServerDict)
    except KeyError:
      print("0", stunserDictPozDict[stunserver], stunserver, sep=';', file=fileStunServerDict)
  for result in finalWebRtcTestDict :
    if str(result) == "20" :
      print(finalWebRtcTestDict[result], 0, str(result), sep=';', file=fileWebRTCTestDict)
    else :
      print(finalWebRtcTestDict[result], -1, str(result), sep=';', file=fileWebRTCTestDict)
  for country in countryDictPozDict :
    try:
      print(finalCountryDict[country], countryDictPozDict[country], country, sep=';', file=fileCountryDict)
    except KeyError:
      print("0", countryDictPozDict[country], country, sep=';', file=fileCountryDict)
  for org in orgDictPozDict :
    try:
      print(finalOrgDict[org], orgDictPozDict[org], org, sep=';', file=fileOrgDict)
    except KeyError:
      print("0", orgDictPozDict[org], org, sep=';', file=fileOrgDict)
  if haveToCreateSeparateTestLookupFiles == True :
    for hour in hoursOfDayPozDict:
      try:
        print(finalHourDictTest[hour], hoursOfDayPozDict[hour], hour, sep=';', file=testFileHoursDict)
      except KeyError:
        print("0", hoursOfDayPozDict[hour], hour, sep=';', file=testFileHoursDict)
    for day in daysOfWeekPozDict:
      try:
        print(finalDayDictTest[day], daysOfWeekPozDict[day], day, sep=';', file=testFileDaysDict)
      except KeyError:
        print("0", daysOfWeekPozDict[day], day, sep=';', file=testFileDaysDict)
    for version in andverDictPozDict:
      try:
        print(finalAndroidVersionDictTest[version], andverDictPozDict[version], version, sep=';',
              file=testFileAndroidVersionDict)
      except KeyError:
        print("0", andverDictPozDict[version], version, sep=';', file=testFileAndroidVersionDict)
    for online in finalOnlineDictTest:
      if str(online) == "5":
        print(finalOnlineDictTest[online], 1, str(online), sep=';', file=testFileOnlineDict)
      else:
        print(finalOnlineDictTest[online], 0, str(online), sep=';', file=testFileOnlineDict)
    for type_bandwidth in bandwidthDictPozDict:
      try:
        print(finalWifiBandwidtDictTest[type_bandwidth], bandwidthDictPozDict[type_bandwidth], type_bandwidth, sep=';',
              file=testFileWifiBandwidthDict)
      except KeyError:
        print("0", bandwidthDictPozDict[type_bandwidth], type_bandwidth, sep=';', file=testFileWifiBandwidthDict)
    for type_mobnet in mobnetDictPozDict:
      try:
        print(finalMobNetDictTest[type_mobnet], mobnetDictPozDict[type_mobnet], type_mobnet, sep=';',
              file=testFileMobileNetTypeDict)
      except KeyError:
        print("0", mobnetDictPozDict[type_mobnet], type_mobnet, sep=';', file=testFileMobileNetTypeDict)
    for roaming in finalRoamingDictTest:
      if str(roaming) == "true":
        print(finalRoamingDictTest[roaming], 1, str(roaming), sep=';', file=testFileRoamingDict)
      else:
        print(finalRoamingDictTest[roaming], 0, str(roaming), sep=';', file=testFileRoamingDict)
    for nat in natDictPozDict:
      try:
        print(finalNatDictTest[nat], natDictPozDict[nat], nat, sep=';', file=testFileNATDict)
      except KeyError:
        print("0", natDictPozDict[nat], nat, sep=';', file=testFileNATDict)
    for stunserver in stunserDictPozDict:
      try:
        print(finalStunServerDictTest[stunserver], stunserDictPozDict[stunserver], stunserver, sep=';',
              file=testFileStunServerDict)
      except KeyError:
        print("0", stunserDictPozDict[stunserver], stunserver, sep=';', file=testFileStunServerDict)
    for result in finalWebRtcTestDictTest:
      if str(result) == "20":
        print(finalWebRtcTestDictTest[result], 1, str(result), sep=';', file=testFileWebRTCTestDict)
      else:
        print(finalWebRtcTestDictTest[result], 0, str(result), sep=';', file=testFileWebRTCTestDict)
    for country in countryDictPozDict:
      try:
        print(finalCountryDictTest[country], countryDictPozDict[country], country, sep=';', file=testFileCountryDict)
      except KeyError:
        print("0", countryDictPozDict[country], country, sep=';', file=testFileCountryDict)
    for org in orgDictPozDict:
      try:
        print(finalOrgDictTest[org], orgDictPozDict[org], org, sep=';', file=testFileOrgDict)
      except KeyError:
        print("0", orgDictPozDict[org], org, sep=';', file=testFileOrgDict)
    testFileHoursDict.close()
    testFileDaysDict.close()
    testFileAndroidVersionDict.close()
    testFileOnlineDict.close()
    testFileWifiBandwidthDict.close()
    testFileMobileNetTypeDict.close()
    testFileRoamingDict.close()
    testFileNATDict.close()
    testFileStunServerDict.close()
    testFileWebRTCTestDict.close()
    testFileCountryDict.close()
    testFileOrgDict.close()
  fileHoursDict.close()
  fileDaysDict.close()
  fileAndroidVersionDict.close()
  fileOnlineDict.close()
  fileWifiBandwidthDict.close()
  fileMobileNetTypeDict.close()
  fileRoamingDict.close()
  fileNATDict.close()
  fileStunServerDict.close()
  fileWebRTCTestDict.close()
  fileCountryDict.close()
  fileOrgDict.close()