#! /usr/bin/awk -f
function determine_connection_bandwidth(networkType) { #slow: 0 ; fast: 1;
	if( networkType == "UNKNOWN" || networkType == "N/A"){ #0 kbps
		return 0;
	}
	#2G
	if( networkType == "CDMA" || networkType == "IS-95"){ #9.6-14.4 kbps
		return 0;
	}
	if( networkType == "iDen"){ #9.6-19.2 kbps
		return 0;
	}
	if( networkType == "GPRS"){	#56–114 kbps
		return 0;
	}
	#3G
	if( networkType == "EDGE"){ #120-384 kbps
		return 0;
	}
	if( networkType == "1xRTT"){ #144-384 kbps
		return 0;
	}
	if( networkType == "EVDO_0" || networkType == "EV-DO Rel.0" || networkType == "EV-DORel.0" ){ #2.4 Mbit/s 
		return 1;
	}
	if( networkType == "EVDO_A" || networkType == "EV-DO Rel.A"|| networkType == "EV-DORev.A" ){ #3.1 Mbit/s
		return 1;
	}
	if( networkType == "eHRPD"){ #same EVDO_A
		return 1;
	}
	if( networkType == "EVDO_B" || networkType == "EV-DO Rel.B" || networkType =="EV-DORev.B"){ #14.7 Mbit/s
		return 1;
	}
	if( networkType == "UMTS"){ #14.4 Mbit/s
		return 1;
	}
	#4G
	if( networkType == "HSPA" || networkType == "HSDPA" || networkType == "HSUPA" || networkType == "HSPDA"){ # 14.4 Mbit/s or more
		return 1;
	}
	if( networkType == "HSPA+"){ #43 Mbit/s or more
		return 1;
	}
	if( networkType == "LTE"){ #100 Mbit/s or more
		return 1;
	}
	if( networkType != "" ) {
	  print(networkType)
	}
	return 0;
}
BEGIN{
  FS=";"
  OFS=";"
}
{
  cm=int($17)
  if(cm==-1){
    $16="-2";
  }
  if(remove_slow_mobilenetwork == 1 && cm == 0 && determine_connection_bandwidth($32) == 0 ) {#remove_slow_mobilenetwork is a param{
    $16="-2"
    removedSlow++;
  }
  if(FNR==1){
    for(k=1; k<i; k++){
      print(memory[k]) >> file
    }
    i=1
    delete(memory) 
    onlineLastSeenStateTimeStamp=""
    onlineLastSeenIP=""
    onlineLastSeenConnectionMod=""
    onlineLastSeenDiscovery=""
    discoveryMinus2=0;
    lastStateTimeStamp=$12;
    split(FILENAME,filename,"/")
    file="out4/"filename[2]
  }
  if ($38 < 14) {   
    sumOfAll++
    deltaTime=int(($12-lastStateTimeStamp));
    if(deltaTime>=0 && deltaTime<=1199999){ #regular online measurement: less then 19.99999999 min
      regularTimeWindow=1;
    } else {
      regularTimeWindow=0;
    }

    drc=int($16)
    tc=int($37)
    ip=$10
    if(drc!=-2 && drc!=-1 && drc!=1 && drc!=9 && drc!=13 && ip ~ /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/){ #online
      online=1;
    } else {
      online=0;
    }
    if(onlineLastSeenStateTimeStamp && discoveryMinus2  && regularTimeWindow && onlineLastSeenConnectionMod==cm && tc!=1 && tc!=6 && tc!=7 && tc!=8 && tc!=9 ){ // no need to check online because we only use it after the online check 
      secondOnline=1;
    } else {
      secondOnline=0;
    }
    if(online) {
      if(secondOnline){
        deltaOnlineTime=int(($12-onlineLastSeenStateTimeStamp)/60000);
        if(cm==onlineLastSeenConnectionMod){
          if( onlineLastSeenIP==ip ){
            if(deltaOnlineTime<=50 && discoveryMinus2 <5 ){
              sumOfExaminedOnlineSessions++
              sumOfMinusTwoInOnlineSessions+=discoveryMinus2
              statNumberOfSessionWithMinusTwoByNumber[discoveryMinus2]++
              statNumberOfMinusTwoInOnlineSessionByNumber[discoveryMinus2]+=discoveryMinus2
              statNumberOfSessionWithMinusTwoByTime[deltaOnlineTime]++
              statNumberOfMinusTwoInOnlineSessionByTime[deltaOnlineTime]+=discoveryMinus2
              if(onlineLastSeenConnectionMod==1) {
                sumOfExaminedWifiSessions++
                sumOfMinusTwoInWifiSessions+=discoveryMinus2
              } else {
                sumOfExaminedMobileSessions++
                sumOfMinusTwoInMobileSessions+=discoveryMinus2
              }
              for(k=1; k<i; k++){
                n=split(memory[k], line, ";")
                line[10]=ip #publicIP
                line[11]=$11 #localIP
                line[16]=drc #discoveryResultCode
                line[26]=$26 #bandwidth
                line[27]=$27 #SSID
                line[28]=$28 #rssi
                line[29]=$29 #Carrier
                line[30]=$30 #simCountryIso
                line[31]=$31 #networkType
                line[32]=$32 #roaming
                outString=line[1]
                for(j=2; j<=n;j++){
                  outString=outString";"line[j];
                }
                print(outString) >> file
              }
              i=1
              delete(memory)
            }
          }
        }
      }
      discoveryMinus2=0;
      onlineLastSeenStateTimeStamp=$12;
      onlineLastSeenConnectionMod=cm;
      onlineLastSeenDiscovery=drc;
      onlineLastSeenIP=ip
      for(k=1; k<i; k++){
        print(memory[k]) >> file
      }
      i=1
      delete(memory)
      print($0) >> file
    } else if (onlineLastSeenStateTimeStamp && drc==1 && cm==onlineLastSeenConnectionMod && regularTimeWindow && tc!=1 && tc!=6 && tc!=7 && tc!=8 && tc!=9) {
      discoveryMinus2+=1;
      memory[i]=$0
      i++
    } else {
      onlineLastSeenStateTimeStamp=""
      onlineLastSeenIP=""
      onlineLastSeenConnectionMod=""
      onlineLastSeenDiscovery=""
      discoveryMinus2=0;
      for(k=1; k<i; k++){
        print(memory[k]) >> file
      }
      i=1
      delete(memory)
      print($0) >> file
    }
    lastStateTimeStamp=$12;
  } else {
    for(k=1; k<i; k++){
      print(memory[k]) >> file
    }
    i=1
    delete(memory)
    print($0) >> file
  }
}
END{  
  for(k=1; k<i; k++){
    print(memory[k]) >> file
  }
  i=1
  delete(memory)
  percent=(sumOfMinusTwoInOnlineSessions/sumOfAll)*100
  print(percent" "removedSlow)
}
