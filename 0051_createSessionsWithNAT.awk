#! /usr/bin/awk -f
BEGIN{
  onlineNat[0]=1
  onlineNat[1]=1
  onlineNat[2]=1
  onlineNat[3]=1
  onlineNat[4]=1
  onlineNat[5]=1
  onlineNat[6]=1
  FS=";"
  VERSIONS_SINCE_VERSION_2=20
  VERSIONS_SINCE_LAST_DISCONNECT_IS_OK=25
  ANDROID_VERSION_SINCE_NO_BROADCAST=24
  MAXDIF_OFFLINE_V2=604800000 # 1 week
  MAXDIF_ONLINE_V2=1499999 # 24.99999999 minute
  MINUTE=60*1000
}

function isOnline(nat){
  if (nat in onlineNat) {
    return 1
  }
  return 0
}
function isOnCharger(chargingState, pluggedinState){
  if(chargingState == 2 || chargingState == 5) {
    return 1;
  }
  if(pluggedinState == 1 || pluggedinState == 2 || pluggedinState == 4) {
    return 1
  }
  return 0;
}

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
	if( networkType == "EVDO_0" || networkType == "EV-DO Rel.0" || networkType == "EV-DORel.0" || networkType == "EV-DO_Rel.0" ){ #2.4 Mbit/s 
		return 1;
	}
	if( networkType == "EVDO_A" || networkType == "EV-DO Rel.A"|| networkType == "EV-DORev.A" || networkType == "EV-DO_Rev.A" ){ #3.1 Mbit/s
		return 1;
	}
	if( networkType == "eHRPD"){ #same EVDO_A
		return 1;
	}
	if( networkType == "EVDO_B" || networkType == "EV-DO Rel.B" || networkType =="EV-DORev.B" || networkType == "EV-DO_Rev.B" ){ #14.7 Mbit/s
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

function getNatType(natType, connectionMode, mobileNetworkType, prevNatType, networkInfo, rectime, prevtime) {
  if (connectionMode == 0 && remove_slow_mobilenetwork == 1 && determine_connection_bandwidth(mobileNetworkType) == 0 ){
    return -2
  }
  if (natType == -3 || natType == -1) {
    if(networkInfo == 5 && rectime-prevtime<=MAXDIF_ONLINE_V2) {
      return prevNatType
    } else {
      return -2
    }
  }
  return natType
}

FNR==1{
  if(prevTimeStamp-startTimeStamp>0){
    sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
    outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
  } 
  if (sessionDeltaTime > 0)  {
    if (is_charging_important==1 || prevappversion >= VERSIONS_SINCE_VERSION_2 ) {
      if (prevchargestate==1) {
        print(outStr)
      }
    } else {
      print(outStr)
    }
  }
  split(FILENAME,fileArr,"/")
  split(fileArr[2],filename,".")
  line=1
  prevappversion=int($9)
  if (prevappversion >= VERSIONS_SINCE_VERSION_2) {
    startTimeStamp=$5
    prevTimeStamp=$5
    sessionDeltaTime=0
    sessionStartTimeStamp=$5
    timeZone=int($6)
    pervNetworkInfo=int($11)
    prevchargestate=isOnCharger(int($36),int($37))
    nat=getNatType(int($25),int($10),$19,-2,pervNetworkInfo,prevTimeStamp,prevTimeStamp)
    prevIP=$27
  } else {
    startTimeStamp=$12
    prevTimeStamp=$12
    sessionDeltaTime=0
    sessionStartTimeStamp=$12
    timeZone=int($39)
    pervNetworkInfo=int($17)==-1?8:5
    prevchargestate=isOnCharger(int($25),int($20))
    nat=getNatType(int($16),int($17),$32,-2,pervNetworkInfo,prevTimeStamp,prevTimeStamp)
    prevIP=$10
    prevappversion=int($38)
  }
  outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
}
FNR>1{
  appversion=int($9)
  if (appversion >= VERSIONS_SINCE_VERSION_2) {
    if (prevappversion < VERSIONS_SINCE_VERSION_2) {
      if(prevTimeStamp-startTimeStamp>0){
        sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
        outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
      } 
      if (sessionDeltaTime > 0)  {
        if (is_charging_important==1) {
          if (prevchargestate==1) {
            print(outStr)
          }
        } else {
          print(outStr)
        }
      }
      startTimeStamp=$5
      prevTimeStamp=$5
      sessionDeltaTime=0
      sessionStartTimeStamp=$5
      timeZone=int($6)
      pervNetworkInfo=int($11)
      prevchargestate=isOnCharger($36,$37)
      nat=getNatType(int($25),int($10),$19,-2,pervNetworkInfo,$5,prevTimeStamp)
      prevIP=$27
      line++
      outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
    }
    rectime=$5
    networkInfo=int($11)
    chargestate=isOnCharger($36,$37)
    recnat=getNatType(int($25),int($10),$19,nat,networkInfo,rectime,prevTimeStamp)
    tigerE=int($7)
    recIP=((int($25)==-3||int($25)==-1)&&networkInfo==5)?prevIP:$27
    timeZone=int($6)
    lastDisconnect=int($35)
    deltaTime=rectime-prevTimeStamp
    if (deltaTime<0 || deltaTime>MAXDIF_OFFLINE_V2 || prevchargestate!=chargestate) {
      newLineIsNecessary = 1
    } else {
      newLineIsNecessary = 0
    }
    if (appversion >= VERSIONS_SINCE_LAST_DISCONNECT_IS_OK ) {
      if( deltaTime<0 || deltaTime>MAXDIF_OFFLINE_V2 ) {
        if (prevTimeStamp-startTimeStamp>0) {
          sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
          outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
        }
        startTimeStamp=prevTimeStamp
      } else if (pervNetworkInfo == 5 && (deltaTime>MAXDIF_ONLINE_V2 || networkInfo != 5 ))  {
        if (lastDisconnect>prevTimeStamp && (lastDisconnect-prevTimeStamp)<=MAXDIF_ONLINE_V2) {
          if (lastDisconnect-startTimeStamp>0) {
            sessionDeltaTime+=(lastDisconnect-startTimeStamp)
            outStr=outStr" "(lastDisconnect-startTimeStamp)" "nat
          }
          startTimeStamp=lastDisconnect
        } else {
          if (prevTimeStamp-startTimeStamp>0) {
            sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
            outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
          }
          startTimeStamp=prevTimeStamp
        }
        if(rectime-startTimeStamp>0) {
           sessionDeltaTime+=(rectime-startTimeStamp)
           outStr=outStr" "(rectime-startTimeStamp)" -2"
        }
        startTimeStamp=rectime
      } else if( recnat!=nat || recIP!=prevIP || prevchargestate!=chargestate ) {
        if(rectime-startTimeStamp>0) {
          sessionDeltaTime+=(rectime-startTimeStamp)
          outStr=outStr" "(rectime-startTimeStamp)" "nat
        }
        startTimeStamp=rectime
      }
    } else {
      if( deltaTime<0 || deltaTime>MAXDIF_OFFLINE_V2 ) {
        if (prevTimeStamp-startTimeStamp>0) {
          sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
          outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
        }
        startTimeStamp=prevTimeStamp
      } else if (pervNetworkInfo == 5 && networkInfo != 5 && deltaTime<=MAXDIF_ONLINE_V2 ) {
        if(androidVersion >= ANDROID_VERSION_SINCE_NO_BROADCAST) {
          if(rectime-MINUTE-startTimeStamp>0) {
            sessionDeltaTime+=(rectime-startTimeStamp)
            outStr=outStr" "(rectime-startTimeStamp)" "nat
            startTimeStamp=rectime-MINUTE
          } else {
            if (prevTimeStamp-startTimeStamp>0) {
              sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
              outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
            }
            startTimeStamp=prevTimeStamp
          }
          if(rectime-startTimeStamp>0) {
            sessionDeltaTime+=(rectime-startTimeStamp)
            outStr=outStr" "(rectime-startTimeStamp)" -2"
          }
          startTimeStamp=rectime
        } else {
          if(rectime-startTimeStamp>0) {
            sessionDeltaTime+=(rectime-startTimeStamp)
            outStr=outStr" "(rectime-startTimeStamp)" "nat
          }
          startTimeStamp=rectime
        }
      } else if (pervNetworkInfo == 5 && deltaTime>MAXDIF_ONLINE_V2 ) {
        if (prevTimeStamp-startTimeStamp>0) {
          sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
          outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
        }
        startTimeStamp=prevTimeStamp
        if(rectime-startTimeStamp>0) {
          sessionDeltaTime+=(rectime-startTimeStamp)
          outStr=outStr" "(rectime-startTimeStamp)" -2"
        }
        startTimeStamp=rectime
      } else if( recnat!=nat || recIP!=prevIP || prevchargestate!=chargestate ) {
        if(rectime-startTimeStamp>0) {
          sessionDeltaTime+=(rectime-startTimeStamp)
          outStr=outStr" "(rectime-startTimeStamp)" "nat
        }
        startTimeStamp=rectime
      }
    }
    if (newLineIsNecessary==1) {
      if (sessionDeltaTime > 0 && prevchargestate==1) {
        print(outStr)
      }
      sessionDeltaTime=0
      sessionStartTimeStamp=rectime
      line++
      startTimeStamp=rectime
      outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
    }
  } else {
    rectime=$12
    networkInfo=int($17)==-1?8:5
    chargestate=isOnCharger(int($25),int($20))
    recnat=getNatType(int($16),int($17),$32,nat,networkInfo,rectime,prevTimeStamp)
    tigerE=int($37)
    recIP=$10
    timeZone=int($39)
    appversion = int($38)
    if(isOnline(nat)==1) {
      maxdif=1199999 #19.99999999 minute
      online=1
    } else {
      maxdif=3599999 #59.99999999 minute
      online=0
    }
    deltaTime=rectime-prevTimeStamp
    if (deltaTime<0 || deltaTime>maxdif || (is_charging_important==1 && prevchargestate!=chargestate) ) {  #newLine
      if(is_charging_important==1 && prevchargestate!=chargestate && deltaTime>=0 && deltaTime<=maxdif){
        if (rectime-startTimeStamp>0) {
          sessionDeltaTime+=(rectime-startTimeStamp)
          outStr=outStr" "(rectime-startTimeStamp)" "nat
  	    } 
      } else {
        if (prevTimeStamp-startTimeStamp>0) {
          sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
          outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
        } 
      }
      if (sessionDeltaTime>0)  {
        if (is_charging_important==1) {
          if (prevchargestate==1) {
            print(outStr)
          }
        } else {
          print(outStr)
        }
      }
      sessionDeltaTime=0
      sessionStartTimeStamp=rectime
      line++
      startTimeStamp=rectime
      outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
    } else {
      if(recnat!=nat || recIP!=prevIP){ #newSession
        if(rectime-startTimeStamp>0) {
          sessionDeltaTime+=(rectime-startTimeStamp)
          outStr=outStr" "(rectime-startTimeStamp)" "nat
        } 
        startTimeStamp=rectime
      }
    }
  }
  nat=recnat
  prevIP=recIP
	prevTimeStamp=rectime
	pervNetworkInfo=networkInfo
	prevappversion=appversion
	prevchargestate=chargestate
}
END{
  if(prevTimeStamp-startTimeStamp>0){
    sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
    outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
  } 
  if (sessionDeltaTime > 0)  {
    if (is_charging_important==1 || prevappversion >= VERSIONS_SINCE_VERSION_2 ) {
      if (prevchargestate==1) {
        print(outStr)
      }
    } else {
      print(outStr)
    }
  }
}

