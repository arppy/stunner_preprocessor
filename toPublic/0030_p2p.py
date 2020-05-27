import csv
import json
import os




#print("duplicated=", str(numberOfDuplicated), str(numberOfDuplicated/numberOfP2PRecord))
#print("##listOfUsers###")
i=0
numberOfP2PUser = 0.0
numberOfError = 0.0
for androidID, recordIDs in p2pM.items() :
  file="out/"+androidID+"u003dn"
  numberOfP2PUser+=1.0
  try:
    with open(file, encoding='utf8') as csvfile:
      i=i+1
  except:
    numberOfError+=1
    print(file,androidID)
#print("cant open=", str(numberOfError), str(numberOfError/numberOfP2PUser))
