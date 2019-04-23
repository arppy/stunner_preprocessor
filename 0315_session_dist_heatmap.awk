#! /usr/bin/awk -f
BEGIN{
  timeBlock=60000.0
  onlineNat[0]=1
  onlineNat[1]=1
  onlineNat[2]=1
  onlineNat[3]=1
  onlineNat[4]=1
  onlineNat[5]=1
  onlineNat[6]=1
}
function isOnline(nat){
  if (nat in onlineNat) {
    return 1
  }
  return 0
}
FNR==1{
  maxRec=0
  minRec=20
  nf = split(FILENAME,fileStr,/[_\.]/)
  for (i=1;i<=nf;i++) {
    if (fileStr[i]~/v[0-9]/) {
      version=fileStr[i]
      #print("### "version)
    }
  }
}
{
  if (version=="v2") { # || startTS<=FIRST_SHUT_DOWN
    onlineNat[1]=1
  } else {
    delete onlineNat[1]
  }
  for(i=6;i<=NF-1;i+=2){
    if (isOnline($(i+1)) == 1) {
      recType=$(i+1)
      recTime=int(log($i/timeBlock))
      #if(recTime==0){
      #  print(recTime" "$i" "recType" "$1" "$2)
      #}
      maxRec=recTime>maxRec?recTime:maxRec
      minRec=recTime<minRec?recTime:minRec
      sessionDist[recTime][recType]+=1
    }
  }
}
END{
  minTime=21
  maxTime=0
  minTime=minRec<minTime?minRec:minTime
  maxTime=maxRec>maxTime?maxRec:maxTime
  outStr="NAT type"
  for (i=0;i<=6;i++) {
    outStr=outStr","i
  }
  printMaxTime=8
  if (version=="v2") {
     printMinTime=0
  } else {
     printMinTime=2
  }
  for(j=minTime;j<printMinTime;j++){
    for (i=0;i<=6;i++) {
       sessionDist[printMinTime][i]+=sessionDist[j][i]
    }
  }
  print(outStr) > "sessionLengthDistStackedBar"version".csv"
  for(j=printMinTime;j<=printMaxTime;j++){
    if (j == printMinTime) {
      outStr="<="j
    } else {
      outStr=""j#exp(i)""
    }
    sum=0
    for (i=0;i<=6;i++) {
       sum+=sessionDist[j][i]
       outStr=outStr","sum
    }
    print(outStr) >> "sessionLengthDistStackedBar"version".csv"
  }

}
