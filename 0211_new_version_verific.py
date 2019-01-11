import csv
import json

def natString(nat1, nat2):
  natA = [int(nat1), int(nat2)]
  natA.sort()
  retStr = ''.join(str(nat) for nat in natA)
  return retStr

def unOrderedNatString(senderNat, receiverNat):
  return ''+str(senderNat)+' '+str(receiverNat)
  
V23_RELEASEDATE = 1545004800000 #23 (2.0.3) 17 Dec 2018 
V22_RELEASEDATE = 1543190400000 #22 (2.0.2) 26 Nov 2018 
V21_RELEASEDATE = 1540944002000 #21 (2.0.1) 31 Okt 2018 
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
allConnection = 0
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
            if pairRecord["appVersion"] == AV or record["appVersion"] == AV  :
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
            break      
        if deletingIdx != -1 :  
          del lookingForPair[deletingIdx]  
        else :
          lookingForPair.append(record)  
      #print(conid,record)
    for record in lookingForPair :
      if record["appVersion"] == AV :
        p2pRes["unsuccessfulPairing"]+=1
        allConnection += 1
  else :
    if records[0]["appVersion"] == AV :
      p2pRes["unsuccessfulPairing"]+=1
      allConnection += 1
numberOfSuccessfulPairing=allConnection-p2pRes["unsuccessfulPairing"]
print(allConnection,numberOfSuccessfulPairing)
for resStr, hit in p2pRes.items() :
  if resStr != "unsuccessfulPairing" :
    print(resStr,hit,hit*1.0/allConnection*1.0,hit*1.0/numberOfSuccessfulPairing*1.0)
  else :
    print(resStr,hit,hit*1.0/allConnection*1.0,0.0)