#! /usr/bin/awk -f
BEGIN{
  FS=";"
  #OFS=";"
}
$38 < 14 {
  if(FNR==1){
    onlineLastSeenStateTimeStamp=""
    onlineLastSeenIP=""
    onlineLastSeenConnectionMod=""
    onlineLastSeenDiscovery=""
    discovery1=0;
    lastStateTimeStamp=$12;
    #file="out4/"FILENAME
  }
  sumOfAll++
  deltaTime=int(($12-lastStateTimeStamp)/60000);
  if(deltaTime>=0 && deltaTime<=15){ #regular online measurement
    regularTimeWindow=1;
  } else {
    regularTimeWindow=0;
  }
  drc=int($16)
  cm=int($17)
  tc=int($37)
  ip=$10
  if(drc!=-2 && drc!=-1 && drc!=1 && drc!=9 && drc!=13  && ip ~ /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/ ){ #online
    online=1;
  } else {
    online=0;
  }
  if(onlineLastSeenStateTimeStamp && discovery1  && regularTimeWindow && onlineLastSeenConnectionMod==cm && tc!=1 && tc!=6 && tc!=7 && tc!=8 && tc!=9 ){ // no need to check online because we only use it after the online check 
    secondOnline=1;
  } else {
    secondOnline=0;
  }
  if(online) {
    if(secondOnline){
      deltaOnlineTime=int(($12-onlineLastSeenStateTimeStamp)/60000);
      if(cm==onlineLastSeenConnectionMod){
        if(onlineLastSeenIP==ip){
          sumOfExaminedOnlineSessions++
          sumOfMinusTwoInOnlineSessions+=discovery1
          statNumberOfSessionWithMinusTwoByNumber[discovery1]++
          statNumberOfMinusTwoInOnlineSessionByNumber[discovery1]+=discovery1
          statNumberOfSessionWithMinusTwoByTime[deltaOnlineTime]++
          statNumberOfMinusTwoInOnlineSessionByTime[deltaOnlineTime]+=discovery1
        }
      }
    }
    discovery1=0;
    onlineLastSeenStateTimeStamp=$12;
    onlineLastSeenConnectionMod=cm;
    onlineLastSeenDiscovery=drc;
    onlineLastSeenIP=ip
  } else if (drc==1 && cm==onlineLastSeenConnectionMod && regularTimeWindow && tc!=1 && tc!=6 && tc!=7 && tc!=8 && tc!=9) {
    discovery1+=1;
  } else {
    onlineLastSeenStateTimeStamp=""
    onlineLastSeenIP=""
    onlineLastSeenConnectionMod=""
    onlineLastSeenDiscovery=""
    discovery1=0;
  }
  lastStateTimeStamp=$12;
}
END{
  for(discovery1 in statNumberOfSessionWithMinusTwoByNumber){
    avgOfAll=(statNumberOfMinusTwoInOnlineSessionByNumber[discovery1]/sumOfAll)*100
    avgOfAllOnline=(statNumberOfSessionWithMinusTwoByNumber[discovery1]/sumOfExaminedOnlineSessions)*100
    print(discovery1";"statNumberOfSessionWithMinusTwoByNumber[discovery1]";"avgOfAll";"avgOfAllOnline) >> "zzz_outNum1.csv"
  }
  print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
  for(deltaTime in statNumberOfSessionWithMinusTwoByTime){
    avgOfAll=(statNumberOfMinusTwoInOnlineSessionByTime[deltaTime]/sumOfAll)*100
    avgOfAllOnline=(statNumberOfSessionWithMinusTwoByTime[deltaTime]/sumOfExaminedOnlineSessions)*100
    print(deltaTime";"statNumberOfSessionWithMinusTwoByTime[deltaTime]";"avgOfAll";"avgOfAllOnline)  >> "zzz_outTime1.csv"
  }
}
