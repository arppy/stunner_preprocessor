import csv
import json

def natString(nat1, nat2):
  natA = [int(nat1), int(nat2)]
  natA.sort()
  retStr = ''.join(str(nat) for nat in natA)
  return retStr

def unOrderedNatString(senderNat, receiverNat):
  return ''+str(senderNat)+' '+str(receiverNat)

AV=23
  
m = {}
i=0
with open('res/res_v2/stuntest-2019-01-03.csv', encoding='utf8') as csvfile:
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
      if 'appVersion' in discoveryJson and discoveryJson['appVersion'] >= 20 and 'connectionID' in p2pJson and p2pJson['connectionID'] != -1 and p2pJson['connectionID'] != 0 : 
        if not p2pJson['connectionID'] in m :
          m[p2pJson['connectionID']] = []
        m[p2pJson['connectionID']].append(mJson)      
i=0
p2pRes = {}
p2pRes["N/A"] = 0
p2pRes["unsuccessfulPairing"] = 0
p2pRes["successfulConnection"] = 0
p2pRes["connectionOpenFailedWithSRLXICE"] = 0
p2pRes["connectionOpenFailedWithoutSRLXICE"] = 0
p2pRes["peerConnectionLost"] = 0
p2pRes["connectionTimeOut"] = 0
p2pRes["connectionOpenButFailedBeforeMessageSend"] = 0
natRes = {}
natRes["N/A"] = {}
natRes["unsuccessfulPairing"] = {}
natRes["successfulConnection"] = {}
natRes["connectionOpenFailedWithSRLXICE"] = {}
natRes["connectionOpenFailedWithoutSRLXICE"] = {}
natRes["peerConnectionLost"] = {}
natRes["connectionTimeOut"] = {}
natRes["connectionOpenButFailedBeforeMessageSend"] = {}
natByNatRes = {}
for j in range(-2,7) :
  for k in range(-2,7) :
    natKeyString = unOrderedNatString(k,j)
    natByNatRes[natKeyString] = {}
    natByNatRes[natKeyString]["N/A"] = 0
    natByNatRes[natKeyString]["unsuccessfulPairing"] = 0
    natByNatRes[natKeyString]["successfulConnection"] = 0
    natByNatRes[natKeyString]["connectionOpenFailedWithSRLXICE"] = 0
    natByNatRes[natKeyString]["connectionOpenFailedWithoutSRLXICE"] = 0
    natByNatRes[natKeyString]["peerConnectionLost"] = 0
    natByNatRes[natKeyString]["connectionTimeOut"] = 0
    natByNatRes[natKeyString]["connectionOpenButFailedBeforeMessageSend"] = 0
allConnection=0

webRTCtestResults = [-3,-2,10,11,19,20]
rtcRes = {}
for j in webRTCtestResults :
  for k in webRTCtestResults :
    webRTCtestResultsKeyString = natString(j,k)
    rtcRes[webRTCtestResultsKeyString] = {}
    rtcRes[webRTCtestResultsKeyString]["N/A"] = 0
    rtcRes[webRTCtestResultsKeyString]["unsuccessfulPairing"] = 0
    rtcRes[webRTCtestResultsKeyString]["successfulConnection"] = 0
    rtcRes[webRTCtestResultsKeyString]["connectionOpenFailedWithSRLXICE"] = 0
    rtcRes[webRTCtestResultsKeyString]["connectionOpenFailedWithoutSRLXICE"] = 0
    rtcRes[webRTCtestResultsKeyString]["peerConnectionLost"] = 0
    rtcRes[webRTCtestResultsKeyString]["connectionTimeOut"] = 0
    rtcRes[webRTCtestResultsKeyString]["connectionOpenButFailedBeforeMessageSend"] = 0

networkNatResSender = {}
numberOfConnectionPerSenderNetwork = {}
networkNatResReceiver = {}
numberOfConnectionPerReceiverNetwork = {}
for conid, records in m.items() :
  if(len(records)>1) :
    lookingForPair = []
    for record in records :
      if len(lookingForPair) < 1 :
        lookingForPair.append(record)
      else :
        deletingIdx = -1;
        for idx, pairRecord in enumerate(lookingForPair):
          if pairRecord["peerID"] == record["androidID"] and record["peerID"] == pairRecord["androidID"] and abs(pairRecord["timeStamp"]-record["timeStamp"])<60000 :
            #natString(record["natResultsDTO"]["discoveryResult"],pairRecord["natResultsDTO"]["discoveryResult"])
            if pairRecord["appVersion"] == AV or record["appVersion"] == AV  :
              if pairRecord["sender"] == False :
                natKeyString = unOrderedNatString(record["natResultsDTO"]["discoveryResult"],pairRecord["natResultsDTO"]["discoveryResult"])
                if record["connectionMode"] == 0 :
                  senderNetworkKey = record["mobileDTO"]["carrier"]
                elif record["connectionMode"] == 1 :
                  senderNetworkKey = record["wifiDTO"]["ssid"]
                else :
                  senderNetworkKey = "N/A"
                if pairRecord["connectionMode"] == 0 :
                  receiverNetworkKey = pairRecord["mobileDTO"]["carrier"]
                elif pairRecord["connectionMode"] == 1 :
                  receiverNetworkKey = pairRecord["wifiDTO"]["ssid"]
                else :
                  receiverNetworkKey = "N/A"
              else :
                natKeyString = unOrderedNatString(pairRecord["natResultsDTO"]["discoveryResult"],record["natResultsDTO"]["discoveryResult"])
                if pairRecord["connectionMode"] == 0 :
                  senderNetworkKey = pairRecord["mobileDTO"]["carrier"]
                elif pairRecord["connectionMode"] == 1 :
                  senderNetworkKey = pairRecord["wifiDTO"]["ssid"]
                else :
                  senderNetworkKey = "N/A"
                if record["connectionMode"] == 0 :
                  receiverNetworkKey = record["mobileDTO"]["carrier"]
                elif record["connectionMode"] == 1 :
                  receiverNetworkKey = record["wifiDTO"]["ssid"]
                else :
                  receiverNetworkKey = "N/A"
              webRTCtestResultsKeyString = natString(record["webRTCResultsDTO"]["exitStatus"],pairRecord["webRTCResultsDTO"]["exitStatus"])
              p2pKeyString = "N/A" 
              allConnection += 1
              if pairRecord["exitStatus"] == -10 or record["exitStatus"] == -10 :
                p2pKeyString = "unsuccessfulPairing"
              elif pairRecord["exitStatus"] == 5 or record["exitStatus"] == 5 :
                p2pKeyString = "unsuccessfulPairing"
              elif pairRecord["exitStatus"] == 3 or record["exitStatus"] == 3 :
                p2pKeyString = "peerConnectionLost"
              elif pairRecord["exitStatus"] == -1 or record["exitStatus"] == -1 :
                p2pKeyString = "unsuccessfulPairing"
              elif pairRecord["exitStatus"] == -2 or record["exitStatus"] == -2 :
                p2pKeyString = "connectionTimeOut"
              elif pairRecord["exitStatus"] == 20 and pairRecord["exitStatus"] == record["exitStatus"] :
                p2pKeyString = "successfulConnection" 
              elif pairRecord["exitStatus"] == 11 and pairRecord["exitStatus"] == record["exitStatus"] :
                p2pKeyString = "connectionOpenFailedWithSRLXICE"     
              elif (pairRecord["exitStatus"] == 11 and record["exitStatus"] == 10) \
              or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 11) \
              or (pairRecord["exitStatus"] == 10 and record["exitStatus"] == 10) :
                p2pKeyString = "connectionOpenFailedWithoutSRLXICE"
              elif (pairRecord["exitStatus"] == 20 and pairRecord["sender"] == False) or (record["exitStatus"] == 20 and record["sender"] == False) :
                p2pKeyString = "connectionOpenButFailedBeforeMessageSend"  
              else :
                print(conid,record["exitStatus"], pairRecord["exitStatus"])
              deletingIdx = idx
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
            break      
        if deletingIdx != -1 :  
          del lookingForPair[deletingIdx]  
        else :
          lookingForPair.append(record)  
      #print(conid,record)
    for record in lookingForPair :
      p2pRes["unsuccessfulPairing"]+=1
      allConnection += 1
  else :
    p2pRes["unsuccessfulPairing"]+=1
    allConnection += 1
numberOfSuccessfulPairing=allConnection-p2pRes["unsuccessfulPairing"]
print(allConnection,numberOfSuccessfulPairing)
for resStr, hit in p2pRes.items() :
  if resStr != "unsuccessfulPairing" :
    print(resStr,hit,hit*1.0/allConnection*1.0,hit*1.0/numberOfSuccessfulPairing*1.0)
  else :
    print(resStr,hit,hit*1.0/allConnection*1.0,0.0)
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
             