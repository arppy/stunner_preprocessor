#! /usr/bin/awk -f
BEGIN{
  FS=";"
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
  startTimeStamp=$12
  prevTimeStamp=$12
  sessionDeltaTime=0
  sessionStartTimeStamp=$12
  timeZone=int($39)
  nat=int($16)
  prevIP=$10
  outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
}
FNR>1{
  recnat=int($16)
  tigerE=int($37)
  recIP=$10 
  if(nat==0 || nat==2 || nat==3 || nat==4 || nat==5 || nat==6) { 
    maxdif=1199999 #19.99999999 min
    online=1
  } else {
    maxdif=3599999 #59.99999999 min
    online=0
  }
  deltaTime=$12-prevTimeStamp
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
    sessionStartTimeStamp=$12
    line++
    startTimeStamp=$12
    timeZone=int($39)
    outStr=filename[1]" "line" "startTimeStamp" "timeZone" :"
  } else {
    if(recnat!=nat ){ #newSession
      if(recnat==-2 || recnat==-1 || recnat==1 ||
  	       ((recnat==6 || recnat==2) && (nat==0 || nat==3 || nat==4 || nat==5 )) ||
  	       (recnat==5 && (nat==0 ||nat==3 || nat==4) ) ||
  	       (recnat==4 && (nat==0 ||nat==3) ) ||
  	       (recnat==3 && nat==0) ) {       
  	   sessionDeltaTime+=(prevTimeStamp+1-startTimeStamp)       
    	 outStr=outStr" "(prevTimeStamp+1-startTimeStamp)" "nat
    	 startTimeStamp=prevTimeStamp+1
    	} else {
    	 if($12-startTimeStamp>0) {
    	  sessionDeltaTime+=($12-startTimeStamp)
    	  outStr=outStr" "($12-startTimeStamp)" "nat
    	 } 
    	 startTimeStamp=$12
    	}
    } else {
      if(nat != -2 && nat != -1  && nat != 1) { #recnat==nat
        if(tigerE==1 || tigerE==6 || tigerE==7 || tigerE==8 || recIP!=prevIP){
          sessionDeltaTime+=(prevTimeStamp+1-startTimeStamp)
          outStr=outStr" "(prevTimeStamp+1-startTimeStamp)" "nat
          startTimeStamp=prevTimeStamp+1
          if($12-startTimeStamp>0) {
           sessionDeltaTime+=($12-startTimeStamp)
    	     outStr=outStr" "($12-startTimeStamp)" -2"
    	    } 
    	    startTimeStamp=$12
        } 
      }
    }
  }
  nat=recnat
  prevIP=recIP
	prevTimeStamp=$12
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

