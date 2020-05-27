import csv
import json
from datetime import datetime

def natString(nat1, nat2):
  natA = [int(nat1), int(nat2)]
  natA.sort()
  retStr = ''.join(str(nat) for nat in natA)
  return retStr

def unOrderedNatString(senderNat, receiverNat):
  return ''+str(senderNat)+' '+str(receiverNat)

AV=23
filelist=[]
filelist.append('res/res_v2/stuntest-2019-01-22.csv')
filelist.append('res/res_v2/stuntest-2019-02-21.csv')
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
          print("p2p",i,line[0])
        discoveryJson = {}
        try :
          discoveryJson = json.loads(line[1])
        except :
          print("nat",i,line[1])
        mJson = {}
        mJson.update(discoveryJson)
        mJson.update(p2pJson)
        if "natResultsDTO" in discoveryJson and discoveryJson["natResultsDTO"]['STUNserver']=="N/A" and discoveryJson["natResultsDTO"]['discoveryResult']==-2 :
          #print(mJson)
          mJson["natResultsDTO"]['discoveryResult']=-3
        if 'appVersion' in discoveryJson and discoveryJson['appVersion'] >= 20 and 'connectionID' in p2pJson and p2pJson['connectionID'] != -1 and p2pJson['connectionID'] != 0 :
          if not p2pJson['connectionID'] in m :
            m[p2pJson['connectionID']] = {}
          keystring=''+p2pJson['androidID']+p2pJson['peerID']+str(p2pJson['connectionStart'])+str(discoveryJson['recordID'])+str(mJson["natResultsDTO"]['discoveryResult'])
          if len(m[p2pJson['connectionID']]) < 1 :
            m[p2pJson['connectionID']][p2pJson['connectionStart']] = {}
            m[p2pJson['connectionID']][p2pJson['connectionStart']][keystring] = mJson
          else :
            isFoundPair = False
            for timestamp, records in m[p2pJson['connectionID']].items() :
              # 3.5 day => 1000*60*60*24*3.5
              if abs( p2pJson['connectionStart']-timestamp ) < 1000*60*60*24*3.5 :
                m[p2pJson['connectionID']][timestamp][keystring] = mJson
                isFoundPair = True
                break
            if isFoundPair == False :
              #print(str(p2pJson['connectionStart']),str(timestamp),str(abs( p2pJson['connectionStart']-timestamp )/1000/60/60/24))
              m[p2pJson['connectionID']][p2pJson['connectionStart']] = {}
              m[p2pJson['connectionID']][p2pJson['connectionStart']][keystring] = mJson
i=0
p2pRes = {}

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


p2pRes = {}
for p2pResName in p2pList :
  p2pRes[p2pResName] = 0

natRes = {}
for p2pResName in p2pList :
  natRes[p2pResName] = {}

natByNatRes = {}
for j in range(-3,7) :
  for k in range(-3,7) :
    natKeyString = unOrderedNatString(k,j)
    natByNatRes[natKeyString] = {}
    for p2pResName in p2pList :
      natByNatRes[natKeyString][p2pResName] = 0
    

webRTCtestResults = [-3,-2,10,11,19,20]
rtcRes = {}
for j in webRTCtestResults :
  for k in webRTCtestResults :
    webRTCtestResultsKeyString = natString(j,k)
    rtcRes[webRTCtestResultsKeyString] = {}
    for p2pResName in p2pList :
      rtcRes[webRTCtestResultsKeyString][p2pResName] = 0

networkNatResSender = {}
numberOfConnectionPerSenderNetwork = {}
networkNatResReceiver = {}
numberOfConnectionPerReceiverNetwork = {}
numOfOddNumConid = 0
statTimegroup = {}
statRecords = {}
statForOneRecords = {}
numOfOneRecords = 0
allConnection=0

for conid, timegroup in m.items() :
  if not len(timegroup) in statTimegroup :
    statTimegroup[len(timegroup)]=0
  statTimegroup[len(timegroup)]+=1
  for timestamp, records in  timegroup.items() :
    if not len(records) in statRecords :
      statRecords[len(records)]=0
    statRecords[len(records)]+=1
    if len(records) == 1 :
      for key, record in records.items() :
        if record["appVersion"] == AV :
          if not record["exitStatus"] in statForOneRecords :
            statForOneRecords[record["exitStatus"]] = 0
          statForOneRecords[record["exitStatus"]]+=1
          numOfOneRecords += 1
          allConnection += 1 
          if record["exitStatus"] == -10 :  
            p2pRes[UNKNOWN_ERROR_P2P_RES]+=1
          elif record["exitStatus"] == 5 :
            p2pRes[OFFER_IS_REJECTED_P2P_RES]+=1
          elif record["exitStatus"] == -1 : 
            p2pRes[FIREBASE_CONNECTION_ERROR_P2P_RES]+=1
          elif record["exitStatus"] == -2 :
            p2pRes[CONNECTION_TIMEOUT_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES]+=1
          elif record["exitStatus"] == 1 :  
            p2pRes[NOBODY_WAS_AVAILABLE_P2P_RES]+=1
          elif record["exitStatus"] == 10 or record["exitStatus"] == 11 or record["exitStatus"] == 19 or record["exitStatus"] == 20 or record["exitStatus"] == 3: 
            p2pRes[CONNECTION_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES]+=1 
          else : 
            print(conid,record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
    else : 
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
            #print(str(goodPair))
            if len(goodPair) > 0 :
              isFind = True
              record = recordsArray[goodPair[0][0]] 
              pairRecord = recordsArray[goodPair[0][1]]     
          else :
            record = recordsArray[goodPair[0][0]]          
            pairRecord = recordsArray[goodPair[0][1]] 
        if isFind == False :
          allConnection += 1   
          p2pRes[UNKNOWN_ERROR_P2P_RES]+=1      
        elif isFind == True and pairRecord["appVersion"] >= AV and record["appVersion"] >= AV :
          allConnection += 1
          if pairRecord["sender"] == False :
            natKeyString = unOrderedNatString(record["natResultsDTO"]["discoveryResult"],pairRecord["natResultsDTO"]["discoveryResult"])
            if record["connectionMode"] == 0 :
              senderNetworkKey = record["mobileDTO"]["carrier"]
            elif record["connectionMode"] == 1 :
              senderNetworkKey = record["wifiDTO"]["ssid"]
            else :
              senderNetworkKey = NA
            if pairRecord["connectionMode"] == 0 :
              receiverNetworkKey = pairRecord["mobileDTO"]["carrier"]
            elif pairRecord["connectionMode"] == 1 :
              receiverNetworkKey = pairRecord["wifiDTO"]["ssid"]
            else :
              receiverNetworkKey = NA
          else :
            natKeyString = unOrderedNatString(pairRecord["natResultsDTO"]["discoveryResult"],record["natResultsDTO"]["discoveryResult"])
            if pairRecord["connectionMode"] == 0 :
              senderNetworkKey = pairRecord["mobileDTO"]["carrier"]
            elif pairRecord["connectionMode"] == 1 :
              senderNetworkKey = pairRecord["wifiDTO"]["ssid"]
            else :
              senderNetworkKey = NA
            if record["connectionMode"] == 0 :
              receiverNetworkKey = record["mobileDTO"]["carrier"]
            elif record["connectionMode"] == 1 :
              receiverNetworkKey = record["wifiDTO"]["ssid"]
            else :
              receiverNetworkKey = NA
          webRTCtestResultsKeyString = natString(record["webRTCResultsDTO"]["exitStatus"],pairRecord["webRTCResultsDTO"]["exitStatus"])
          p2pKeyString = NA 
          if pairRecord["peerID"] == record["androidID"] and record["peerID"] == pairRecord["androidID"] :
            if pairRecord["exitStatus"] == 5 or record["exitStatus"] == 5 :
              p2pKeyString = OFFER_IS_REJECTED_P2P_RES
            elif pairRecord["exitStatus"] == 3 or record["exitStatus"] == 3 :
              p2pKeyString = PEER_CONNECTION_LOST_P2P_RES
            elif pairRecord["exitStatus"] == -2 or record["exitStatus"] == -2 :
              if (pairRecord["appVersion"] == AV and pairRecord["sender"] == True) or (record["appVersion"] == AV and record["sender"] == True) :
                p2pKeyString = CONNECTION_TIMEOUT_P2P_RES
              else :
                p2pKeyString = ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT
                print('_______ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT:'+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
                print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
                print(pairRecord["appVersion"],pairRecord["exitStatus"],pairRecord["triggerCode"],pairRecord["androidID"],pairRecord["peerID"],pairRecord["sender"],datetime.utcfromtimestamp(pairRecord["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(pairRecord["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
            elif pairRecord["exitStatus"] == -10 or record["exitStatus"] == -10 :
              p2pKeyString = UNKNOWN_ERROR_P2P_RES
            elif pairRecord["exitStatus"] == -1 or record["exitStatus"] == -1 :
              p2pKeyString = FIREBASE_CONNECTION_ERROR_P2P_RES
            elif pairRecord["exitStatus"] == 20 and pairRecord["exitStatus"] == record["exitStatus"] and abs(record["connectionStart"]-pairRecord["connectionStart"])<60000:
              p2pKeyString = SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES 
            elif pairRecord["exitStatus"] == 11 and pairRecord["exitStatus"] == record["exitStatus"] :
              p2pKeyString = CONNECTION_FAILED_SRLX_ICE_P2P_RES     
            elif (pairRecord["exitStatus"] == 11 and record["exitStatus"] == 10) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 11) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 10) :
              p2pKeyString = CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES
            elif (pairRecord["exitStatus"] == 20 and pairRecord["sender"] == False) or (record["exitStatus"] == 20 and record["sender"] == False) :
              p2pKeyString = SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES  
            else :
              print(conid,record["exitStatus"], pairRecord["exitStatus"])
          elif (pairRecord["peerID"] == 'N/A' and  record["peerID"] == pairRecord["androidID"])  or (record["peerID"] == 'N/A' and  pairRecord["peerID"] == record["androidID"]) : 
            if ( pairRecord["peerID"] == 'N/A' and pairRecord["exitStatus"] == -2 ) or ( record["peerID"] == 'N/A' and record["exitStatus"] == -2 ):
              p2pKeyString = ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT
            elif pairRecord["exitStatus"] == 5 or record["exitStatus"] == 5 :
              p2pKeyString = OFFER_IS_REJECTED_P2P_RES
            elif pairRecord["exitStatus"] == -2 or record["exitStatus"] == -2 :
              p2pKeyString = CONNECTION_TIMEOUT_P2P_RES
            elif ( pairRecord["exitStatus"] == 3 or record["exitStatus"] == 3 ) :
              p2pKeyString = PEER_CONNECTION_LOST_P2P_RES # maybe a good pairing, just peerID is not set
            elif pairRecord["exitStatus"] == 20 and pairRecord["exitStatus"] == record["exitStatus"] and abs(record["connectionStart"]-pairRecord["connectionStart"])<60000 :
              p2pKeyString = SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES 
            elif pairRecord["exitStatus"] == 11 and pairRecord["exitStatus"] == record["exitStatus"] :
              p2pKeyString = CONNECTION_FAILED_SRLX_ICE_P2P_RES     
            elif (pairRecord["exitStatus"] == 11 and record["exitStatus"] == 10) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 11) \
            or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 10) :
              p2pKeyString = CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES
            elif (pairRecord["exitStatus"] == 20 and pairRecord["sender"] == False) or (record["exitStatus"] == 20 and record["sender"] == False) :
              p2pKeyString = SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES    
            else :
              print('________notAPair:'+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
              print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
              print(pairRecord["appVersion"],pairRecord["exitStatus"],pairRecord["triggerCode"],pairRecord["androidID"],pairRecord["peerID"],pairRecord["sender"],datetime.utcfromtimestamp(pairRecord["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(pairRecord["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
          elif ((pairRecord["peerID"]  == 'N/A' and  pairRecord["androidID"] == 'N/A' and record["sender"] == True ) or (record["peerID"]  == 'N/A' and  record["androidID"] == 'N/A' and pairRecord["sender"] == True)) :
            if abs(record["connectionStart"]-pairRecord["connectionStart"]) > 1000*60*10 :
              p2pKeyString = FIREBASE_CONNECTION_ERROR_P2P_RES
            elif (abs(record["connectionStart"]-pairRecord["connectionStart"]) < 1000*60*60*24*2 ) :
              p2pKeyString = CONNECTION_TIMEOUT_P2P_RES
            else:
              print('N/A_N/A_with_a_lot_of_time_hour',str(abs(record["connectionStart"]-pairRecord["connectionStart"])/1000/60/60))
          elif ((pairRecord["peerID"]  == 'N/A' and  pairRecord["androidID"] == 'N/A') or (record["peerID"]  == 'N/A' and  record["androidID"] == 'N/A')) and pairRecord["sender"]  != record["sender"] :
            if (pairRecord["appVersion"] != AV or record["appVersion"] != AV) and (pairRecord["appVersion"] == AV or record["appVersion"] == AV) :
              p2pKeyString = PAIRING_WITH_PREV_VERSION_P2P_RES
            elif pairRecord["exitStatus"] == 5 or record["exitStatus"] == 5 :
              p2pKeyString = OFFER_IS_REJECTED_P2P_RES
            else :
              p2pKeyString = UNKNOWN_ERROR_P2P_RES
              print('________notAPair:'+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
              print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
              print(pairRecord["appVersion"],pairRecord["exitStatus"],pairRecord["triggerCode"],pairRecord["androidID"],pairRecord["peerID"],pairRecord["sender"],datetime.utcfromtimestamp(pairRecord["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(pairRecord["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
          else :
            if pairRecord["appVersion"] == AV and record["appVersion"] == AV :
              p2pKeyString = UNKNOWN_ERROR_P2P_RES
            else :
              p2pKeyString = PAIRING_WITH_PREV_VERSION_P2P_RES  
            #print('________notAPair:'+str(conid)+" "+datetime.utcfromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')+'__________')
            #print(record["appVersion"],record["exitStatus"],record["triggerCode"],record["androidID"],record["peerID"],record["sender"],datetime.utcfromtimestamp(record["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(record["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
            #print(pairRecord["appVersion"],pairRecord["exitStatus"],pairRecord["triggerCode"],pairRecord["androidID"],pairRecord["peerID"],pairRecord["sender"],datetime.utcfromtimestamp(pairRecord["connectionStart"]/1000).strftime('%Y-%m-%d %H:%M:%S'),datetime.utcfromtimestamp(pairRecord["timeStamp"]/1000).strftime('%Y-%m-%d %H:%M:%S'))
          p2pRes[p2pKeyString] += 1
          natByNatRes[natKeyString][p2pKeyString] += 1
          rtcRes[webRTCtestResultsKeyString][p2pKeyString] += 1
          if natKeyString in natRes[p2pKeyString] :
            natRes[p2pKeyString][natKeyString] += 1
          else :
            natRes[p2pKeyString][natKeyString] = 1  
          if senderNetworkKey in networkNatResSender :
            numberOfConnectionPerSenderNetwork[senderNetworkKey] += 1
            if natKeyString in networkNatResSender[senderNetworkKey] :
              if p2pKeyString in networkNatResSender[senderNetworkKey][natKeyString] :
                networkNatResSender[senderNetworkKey][natKeyString][p2pKeyString] += 1
              else :
                networkNatResSender[senderNetworkKey][natKeyString][p2pKeyString] = 1
            else :
              networkNatResSender[senderNetworkKey][natKeyString] = {}
              networkNatResSender[senderNetworkKey][natKeyString][p2pKeyString] = 1
          else :
            numberOfConnectionPerSenderNetwork[senderNetworkKey] = 1
            networkNatResSender[senderNetworkKey] = {}
            networkNatResSender[senderNetworkKey][natKeyString] = {}
            networkNatResSender[senderNetworkKey][natKeyString][p2pKeyString] = 1   
          if receiverNetworkKey in networkNatResReceiver :
            numberOfConnectionPerReceiverNetwork[receiverNetworkKey] += 1
            if natKeyString in networkNatResReceiver[receiverNetworkKey] :
              if p2pKeyString in networkNatResReceiver[receiverNetworkKey][natKeyString] :
                networkNatResReceiver[receiverNetworkKey][natKeyString][p2pKeyString] += 1
              else :
                networkNatResReceiver[receiverNetworkKey][natKeyString][p2pKeyString] = 1
            else :
              networkNatResReceiver[receiverNetworkKey][natKeyString] = {}
              networkNatResReceiver[receiverNetworkKey][natKeyString][p2pKeyString] = 1
          else :
            numberOfConnectionPerReceiverNetwork[receiverNetworkKey] = 1
            networkNatResReceiver[receiverNetworkKey] = {}
            networkNatResReceiver[receiverNetworkKey][natKeyString] = {}
            networkNatResReceiver[receiverNetworkKey][natKeyString][p2pKeyString] = 1           
print("____number of timegroups per connectionID_______")
for length, num in statTimegroup.items() :
  print(length,num,num/len(m))
print("____number of record per timegroups__________")
for length, num in statRecords.items() :
  print(length,num,num/len(m))
print("____number of exitStatus per only one record__________")
for exitStatus, num in statForOneRecords.items() :
  print(exitStatus,num,num/numOfOneRecords)
print("____allConnection:"+str(allConnection)+"______________")  

allConnection=allConnection-p2pRes[NA]-p2pRes[PAIRING_WITH_PREV_VERSION_P2P_RES]-p2pRes[UNKNOWN_ERROR_P2P_RES]-p2pRes[CONNECTION_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES]

p2pRes[CONNECTION_FAILED_P2P_RES] = p2pRes[CONNECTION_FAILED_SRLX_ICE_P2P_RES]+p2pRes[CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES]
del p2pRes[CONNECTION_FAILED_SRLX_ICE_P2P_RES]
del p2pRes[CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES]
p2pRes[OTHER_UNSUCCESFUL_PAIRING_P2P_RES] = p2pRes[FIREBASE_CONNECTION_ERROR_P2P_RES]+p2pRes[NOBODY_WAS_AVAILABLE_P2P_RES]
del p2pRes[FIREBASE_CONNECTION_ERROR_P2P_RES]
del p2pRes[NOBODY_WAS_AVAILABLE_P2P_RES]
print("____exitStatus__________")
for resStr, hit in p2pRes.items() :
  if resStr == SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES :
    resStr = ""
  if resStr == OTHER_UNSUCCESFUL_PAIRING_P2P_RES :
    resStr = "" 
  print(str("%.2f"%float(hit*1.0/allConnection*1.0*100.0))+";"+str(hit)+";"+resStr+";")

unSuccesfulPairing = p2pRes[CONNECTION_TIMEOUT_WITHOUT_MEASUREMENT_FROM_PEER_P2P_RES]+p2pRes[OFFER_IS_REJECTED_P2P_RES]+p2pRes[ANSWER_NEVER_ARRIVED_CONNECTION_TIMEOUT]+p2pRes[OTHER_UNSUCCESFUL_PAIRING_P2P_RES]
succesfulConnection = p2pRes[SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES]
unSuccesfulConnection = p2pRes[CONNECTION_FAILED_P2P_RES] + p2pRes[SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES] + p2pRes[PEER_CONNECTION_LOST_P2P_RES] + p2pRes[CONNECTION_TIMEOUT_P2P_RES]
  
print(str("%.2f"%float(unSuccesfulConnection*1.0/allConnection*1.0*100.0))+";"+str(unSuccesfulConnection)+";Unsuccessful connection or transport ("+str("%.0f"%float(unSuccesfulConnection*1.0/allConnection*1.0*100.0))+"%)")
print(str("%.2f"%float(succesfulConnection*1.0/allConnection*1.0*100.0))+";"+str(succesfulConnection)+";Successful connection and transport ("+str("%.0f"%float(succesfulConnection*1.0/allConnection*1.0*100.0))+"%)")
print(str("%.2f"%float(unSuccesfulPairing*1.0/allConnection*1.0*100.0))+";"+str(unSuccesfulPairing)+";Signaling related error ("+str("%.0f"%float(unSuccesfulPairing*1.0/allConnection*1.0*100.0))+"%)")
  
  
natPrintPercent = {}  
natPrintNumber = {}  
allConnection=succesfulConnection+unSuccesfulConnection
for natKeyString, natDict in natByNatRes.items() :
  succesfulConnectionByNat = natDict[SUCCESSFUL_CONNECTION_AND_MESSAGE_EXCHANGED_P2P_RES]
  unSuccesfulConnectionByNat = natDict[CONNECTION_FAILED_SRLX_ICE_P2P_RES]+ natDict[CONNECTION_FAILED_NO_SRLX_ICE_P2P_RES] + natDict[SUCCESSFUL_CONNECTION_BUT_FAILED_TO_EXCHANG_MESSAGE_P2P_RES] + natDict[PEER_CONNECTION_LOST_P2P_RES] + natDict[CONNECTION_TIMEOUT_P2P_RES]
  natKeys=natKeyString.split()
  if not natKeys[0] in natPrintPercent :
    natPrintPercent[natKeys[0]]={}
    natPrintNumber[natKeys[0]]={}
  natPrintNumber[natKeys[0]][natKeys[1]]= str(succesfulConnectionByNat+unSuccesfulConnectionByNat)  
  if (succesfulConnectionByNat+unSuccesfulConnectionByNat) >= 1 :
    natPrintPercent[natKeys[0]][natKeys[1]]= str("%.0f"%float(succesfulConnectionByNat*1.0/(succesfulConnectionByNat+unSuccesfulConnectionByNat)*100.0))
  else :
    natPrintPercent[natKeys[0]][natKeys[1]]= str("")

#del natStringDictAbbreviation["0"]
#del natStringDictAbbreviation["2"]
#del natStringDictAbbreviation["1"]
del natStringDictAbbreviation["-2"]
del natStringDictAbbreviation["-1"]
#del natStringDictAbbreviation["-3"]

for number1, natKey1 in natStringDictAbbreviation.items() :
  for number2, natKey2 in natStringDictAbbreviation.items() :
    print(natKey1+";"+natKey2+";"+natPrintPercent[number1][number2]+";"+natPrintNumber[number1][number2])
    
outStr = "initiator"   
for number, natKey in natStringDictAbbreviation.items() :
  outStr = outStr+","+natKey
print(outStr)   
for number1, natKey1 in natStringDictAbbreviation.items() :
  outStr = natKey1
  for number2, natKey2 in natStringDictAbbreviation.items() :
    outStr = outStr+","+natPrintPercent[number1][number2]
  print(outStr) 
  
outStr = "initiator"   
for number, natKey in natStringDictAbbreviation.items() :
  outStr = outStr+","+natKey
print(outStr)   
for number1, natKey1 in natStringDictAbbreviation.items() :
  outStr = natKey1
  for number2, natKey2 in natStringDictAbbreviation.items() :
    outStr = outStr+","+natPrintNumber[number1][number2]
  print(outStr)  
'''
numberOfSuccessfulPairing=allConnection-p2pRes["unsuccessfulPairing"]
print(len(m),numOfOddNumConid,numOfOddNumConid/len(m))
print(allConnection,numberOfSuccessfulPairing)
for resStr, hit in p2pRes.items() :
  if resStr != "unsuccessfulPairing" :
    print(resStr,hit,hit*1.0/allConnection*1.0,hit*1.0/numberOfSuccessfulPairing*1.0)
  else :
    print(resStr,hit,hit*1.0/allConnection*1.0,0.0)
for resStr, hit in unsuccessfulPairing.items() :
  print(resStr,hit,hit*1.0/allConnection*1.0,hit*1.0/p2pRes["unsuccessfulPairing"]*1.0)
#print("________________AS_SENDER____________________")    
#for network, natResReceiver in networkNatResSender.items() :
#  if numberOfConnectionPerSenderNetwork[network] > 100 :
#    print(" ")
#    print("__________",network) 
#    for natPair, natDict in natResReceiver.items() :
#      print("      __",natPair,"__________") 
#      for resStr, hit in natDict.items() :
#        print("      ",resStr,hit)  
#print("________________AS_RECEIVER____________________")            
#for network, natResReceiver in networkNatResReceiver.items() :
#  if numberOfConnectionPerReceiverNetwork[network] > 100 :
#    print(" ")
#    print("__________",network) 
#    for natPair, natDict in natResReceiver.items() :
#      print("      __",natPair,"__________") 
#      for resStr, hit in natDict.items() :
#        print("      ",resStr,hit)      
    
for resStr, natDict in natRes.items() :
  print("__________",resStr,"__________")
  for natStr, hit in natDict.items() :
    print(natStr,hit)
print("__________________________________________________")    
for natStr, natDict in natByNatRes.items() :
  print("__________",natStr,"__________")
  for resStr, hit in natDict.items() :
    print(resStr,hit)  
print("__________________________________________________")    
for natStr, natDict in rtcRes.items() :
  print("__________",natStr,"__________")
  for resStr, hit in natDict.items() :
    print(resStr,hit)  
    '''  
             