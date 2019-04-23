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
  maxPrev=0
  maxRec=0
  minPrev=20
  minRec=20
}
{
  prevType=isOnline($7)
  prevTime=int(log($6/timeBlock))
  for(i=8;i<=NF-1;i+=2){
    recType=isOnline($(i+1))
    recTime=int(log($i/timeBlock))
    if(prevType == recType && recType == 0) {
      print($i" "$(i+1)" "$0)
    }
    prevSessionDist[prevType][recType][prevTime][recTime]+=1
    maxPrev=prevTime>maxPrev?prevTime:maxPrev
    maxRec=recTime>maxRec?recTime:maxRec
    minPrev=prevTime<minPrev?prevTime:minPrev
    minRec=recTime<minRec?recTime:minRec
    prevType=recType
    prevTime=recTime
  }
}
END{
  minTime=21
  maxTime=0
  minTime=minPrev<minTime?minPrev:minTime
  minTime=minRec<minTime?minRec:minTime
  maxTime=maxPrev>maxTime?maxPrev:maxTime
  maxTime=maxRec>maxTime?maxRec:maxTime
  for (prevType in prevSessionDist) {
    for (recType in prevSessionDist[prevType]) {
      fileName=""prevType"-"recType"SessionLengthDist.csv"
      outStr="Length (ln)"
      for(i=minTime;i<=maxTime;i++){
        outStr=outStr","i#exp(i)
      }
      print(outStr) >> fileName
      for(i=minTime;i<=maxTime;i++){
        outStr=""i#exp(i)""
        for(j=minTime;j<=maxTime;j++){
           outStr=outStr","prevSessionDist[prevType][recType][i][j]
        }
        print(outStr) >> fileName
      }
    }
  } 
}
