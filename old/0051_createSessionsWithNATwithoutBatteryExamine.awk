#! /usr/bin/awk -f
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
  VERSIONS_SINCE_VERSION_2=20
}
FNR==1{
  if(prevTimeStamp-startTimeStamp>0){
    sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
    outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
  } 
  #sessionDeltaTimeValid=prevTimeStamp-sessionStartTimeStamp
  #outStr=sessionDeltaTime/3600000";"outStr#" |"sessionDeltaTime"?=?"sessionDeltaTimeValid
  if (sessionDeltaTime > 0)  {
    print(outStr)
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
    prevchargestate=isOnCharger($36,$37)
    nat=(prevchargestate==0)?-2:int($25)
    prevIP=$27
    pervNetworkInfo=int($11)
  } else {
    startTimeStamp=$12
    prevTimeStamp=$12
    sessionDeltaTime=0
    sessionStartTimeStamp=$12
    timeZone=int($39)
    nat=(is_charging_important==1&&isOnCharger($25,$22)==0)?-2:int($16)
    prevIP=$10
    prevappversion=VERSIONS_SINCE_VERSION_2-1
  }
  outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
}
FNR>1{
  appversion=int($9)
  if (prevappversion < VERSIONS_SINCE_VERSION_2 && appversion >= VERSIONS_SINCE_VERSION_2 ) {
    if(prevTimeStamp-startTimeStamp>0){
      sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
      outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
    } 
    if (sessionDeltaTime > 0)  {
      print(outStr)
    }
    startTimeStamp=$5
    prevTimeStamp=$5
    sessionDeltaTime=0
    sessionStartTimeStamp=$5
    timeZone=int($6)
    prevchargestate=isOnCharger($36,$37)
    nat=(prevchargestate==0)?-2:int($25)
    prevIP=$27
    line++
    outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
  }
  if (appversion >= VERSIONS_SINCE_VERSION_2) {
    rectime=$5
    chargestate=isOnCharger($36,$37)
    recnat=(chargestate==0)?-2:int($25);
    recOrigNat=int($25)
    tigerE=int($7)
    recIP=$27
    timeZone=int($6)
    networkInfo=int($11)
  } else {
    rectime=$12
    recnat=(is_charging_important==1&&isOnCharger($25,$22)==0)?-2:int($16)
    recOrigNat=int($16)
    tigerE=int($37)
    recIP=$10
    timeZone=int($39)
    appversion = VERSIONS_SINCE_VERSION_2-1
  }
  if (appversion >= VERSIONS_SINCE_VERSION_2) {
    deltaTime=rectime-prevTimeStamp
    if (prevchargestate==0 && chargestate==1 ) { #turn charger ON => new line
    
    } else if (prevchargestate==1 && chargestate==1 ) { #stay charging
      if(pervNetworkInfo != 5 && networkInfo == 5) {
      
      } else if(pervNetworkInfo == 5 && networkInfo == 5) {
        maxdif=719999 #11.99999999 minute
        if (deltaTime<0 || deltaTime>maxdif) ) {  #newLine
          if(prevTimeStamp-startTimeStamp>0){
            sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
            outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
          } 
          #sessionDeltaTimeValid=prevTimeStamp-sessionStartTimeStamp
          #outStr=sessionDeltaTime/3600000";"outStr#" |"sessionDeltaTime"?=?"sessionDeltaTimeValid
          if (sessionDeltaTime > 0)  {
            print(outStr)
          }
          sessionDeltaTime=0
          sessionStartTimeStamp=rectime
          line++
          startTimeStamp=rectime
          outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
        } else {
          ##TODO NAT/IP változott-e
        }
      } else if(pervNetworkInfo == 5 && networkInfo == 5) {
      
      } else {
        ## offline session
      }
    } else if (prevchargestate==1 && chargestate==0 ) { #turn charger OFF => newLine
      ##TODO NAT/IP változott-e
      if(prevTimeStamp-startTimeStamp>0){
        sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
        outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
      } 
      #sessionDeltaTimeValid=prevTimeStamp-sessionStartTimeStamp
      #outStr=sessionDeltaTime/3600000";"outStr#" |"sessionDeltaTime"?=?"sessionDeltaTimeValid
      if (sessionDeltaTime > 0)  {
        print(outStr)
      }
      sessionDeltaTime=0
      startTimeStamp=0
      prevTimeStamp=0
    } else { # NO charging
        if(prevTimeStamp-startTimeStamp>0){
          sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
          outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
        } 
        #sessionDeltaTimeValid=prevTimeStamp-sessionStartTimeStamp
        #outStr=sessionDeltaTime/3600000";"outStr#" |"sessionDeltaTime"?=?"sessionDeltaTimeValid
        if (sessionDeltaTime > 0)  {
          print(outStr)
        }
        sessionDeltaTime=0
        startTimeStamp=0
        prevTimeStamp=0
    }
  } else {
    if(nat==0 || nat==2 || nat==3 || nat==4 || nat==5 || nat==6) { 
      maxdif=1199999 #19.99999999 minute
      online=1
    } else {
      maxdif=3599999 #59.99999999 minute
      online=0
    }
    deltaTime=rectime-prevTimeStamp
    if(deltaTime<0 || deltaTime>maxdif){  #newLine
      if(prevTimeStamp-startTimeStamp>0){
        sessionDeltaTime+=(prevTimeStamp-startTimeStamp)
        outStr=outStr" "(prevTimeStamp-startTimeStamp)" "nat
      } 
      #sessionDeltaTimeValid=prevTimeStamp-sessionStartTimeStamp
      #outStr=sessionDeltaTime/3600000";"outStr#" |"sessionDeltaTime"?=?"sessionDeltaTimeValid
      if (sessionDeltaTime > 0)  {
        print(outStr)
      }
      sessionDeltaTime=0
      sessionStartTimeStamp=rectime
      line++
      startTimeStamp=rectime
      outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
    } else {
      if(recnat!=nat ){ #newSession
        if ( tigerE!=1 && 
        ( recOrigNat==-2 || recOrigNat==-1 || recOrigNat==1 || 
          ((recOrigNat==6 || recOrigNat==2) && (nat==0 || nat==3 || nat==4 || nat==5 )) ||
          (recOrigNat==5 && (nat==0 ||nat==3 || nat==4) ) ) ) {
        #(recOrigNat==-2 || recOrigNat==-1 || recOrigNat==1 || ((recOrigNat==6 || recOrigNat==2) && (nat==0 || nat==3 || nat==4 || nat==5 )) || (recOrigNat==5 && (nat==0 ||nat==3 || nat==4) ) || (recOrigNat==4 && (nat==0 ||nat==3) ) || (recOrigNat==3 && nat==0) ) ) {       
    	   sessionDeltaTime+=(prevTimeStamp+1-startTimeStamp)       
      	 outStr=outStr" "(prevTimeStamp+1-startTimeStamp)" "nat
      	 startTimeStamp=prevTimeStamp+1
      	} else {
      	 if(rectime-startTimeStamp>0) {
      	  sessionDeltaTime+=(rectime-startTimeStamp)
      	  outStr=outStr" "(rectime-startTimeStamp)" "nat
      	 } 
      	 startTimeStamp=rectime
      	}
      } else {
        if(nat != -2 && nat != -1  && nat != 1) { #recnat==nat
          if( tigerE==6 || tigerE==8 || recIP!=prevIP) {
            sessionDeltaTime+=(prevTimeStamp+1-startTimeStamp)
            outStr=outStr" "(prevTimeStamp+1-startTimeStamp)" "nat
            startTimeStamp=prevTimeStamp+1
            if(rectime-startTimeStamp>0) {
             sessionDeltaTime+=(rectime-startTimeStamp)
      	     outStr=outStr" "(rectime-startTimeStamp)" -2"
      	    } 
      	    startTimeStamp=rectime
          }
        }
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
  #sessionDeltaTimeValid=prevTimeStamp-sessionStartTimeStamp
  #outStr=sessionDeltaTime/3600000";"outStr#" |"sessionDeltaTime"?=?"sessionDeltaTimeValid
  if (sessionDeltaTime > 0)  {
    print(outStr)
  }
}

