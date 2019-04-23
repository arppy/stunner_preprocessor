#! /usr/bin/awk -f
BEGIN{
  onlineNat[0]=1
  onlineNat[1]=1
  onlineNat[2]=1
  onlineNat[3]=1
  onlineNat[4]=1
  onlineNat[5]=1
  onlineNat[6]=1
  minTS["v2"]=1545004800000
  maxTS["v2"]=1548805470075
  minTS["v1"]=1398643200000
  maxTS["v1"]=1524009600000

  blockSize=1000*60*60*24
}
function isOnline(nat){
  if (nat in onlineNat) {
    return 1
  }
  return 0
}
FNR==1{
  nf = split(FILENAME,fileStr,/[_\.]/)
  for (i=1;i<=nf;i++) {
    if (fileStr[i]~/v[0-9]/) {
      version=fileStr[i]
      #print("### "version)
    }
  }
  minimumTS=minimumTS>0?minimumTS:minTS[version]
  if( minTS[version]<minimumTS) {
    print("ERROR, file order is wrong. Look at its version.") >> "/dev/stderr"
    exit
  }
  minimumTS=minTS[version]<minimumTS?minTS[version]:minimumTS
  newVeryLastBlock=int((maxTS[version]-minimumTS)/blockSize)
  veryLastBlock=newVeryLastBlock>veryLastBlock?newVeryLastBlock:veryLastBlock
}
{
  startTS=$3
  if(startTS)
  for(i=6;i<=NF-1;i+=2){
    deltaFromStart=startTS-minimumTS
    deltaFromEnd=startTS+$i-minimumTS
    firstBlock=int(deltaFromStart/blockSize)
    lastBlock=int(deltaFromEnd/blockSize)
    sessionLength=$i
    online=isOnline($(i+1))
    if(firstBlock==lastBlock) {
      sessionTimeline[firstBlock][online]+=sessionLength
    } else {
      spentFromBlock=deltaFromStart%blockSize
      sessionTimeline[firstBlock][online]+=blockSize-spentFromBlock
      sessionLength=sessionLength-(blockSize-spentFromBlock)
      for(j=firstBlock+1; j<=lastBlock-1; j++){
        sessionTimeline[j][online]+=blockSize
        sessionLength=sessionLength-blockSize
      }
      sessionTimeline[lastBlock][online]+=sessionLength
      #if((lastBlock-1)-(firstBlock+1)+1>0){
      #  print($i,$i==(blockSize-spentFromBlock)+(((lastBlock-1)-(firstBlock+1)+1)*blockSize)+sessionLength,(blockSize-spentFromBlock),(((lastBlock-1)-(firstBlock+1)+1)*blockSize),sessionLength) 
      #} else {
      #  print($i,$i==(blockSize-spentFromBlock)+(0*blockSize)+sessionLength,(blockSize-spentFromBlock),(0*blockSize),sessionLength) 
      #}
    }
    startTS+=$i
  }
}
END{
  outStr="#,online,ofline"
  print(outStr) > "OnlineDistDay.csv"
  for(i=0;i<=veryLastBlock;i++){
    numberOfAll=0
    for(nat in sessionTimeline[i]){
      numberOfAll+=sessionTimeline[i][nat]
    }
    outStr=""
    sum=0
    for(j=1;j>=0;j--){
      sum+=sessionTimeline[i][j]/numberOfAll
      if(sum<0 || sum>1){
        print(sessionTimeline[i][j],numberOfAll)
      }
      outStr=outStr","sum
    }
    ts=minimumTS+i*blockSize
    print(ts""outStr) >> "OnlineDistDay.csv"
  }
}
