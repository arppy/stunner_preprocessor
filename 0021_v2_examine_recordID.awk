#! /usr/bin/awk -f
BEGIN{
  FS=";"
  VERSIONS_SINCE_VERSION_2=20
}
FNR==1{
  if ( numberOfError >  1 ) {
    print(filename,maxDif/1000/60/60,minDif/1000/60/60,fnr,numberOfError,errorRecords)
  }
  numberOfError=0
  maxDif=0
  minDif=0
  errorRecords=""
  prevAT = $5
  prevRecID = $4
  filename = FILENAME
}
FNR>1{
  appversion=int($9)
  maxDif=($5-$1)>maxDif?($5-$1):maxDif
  minDif=($5-$1)<minDif?($5-$1):minDif
  if (appversion >= VERSIONS_SINCE_VERSION_2) {
    if ($4 < prevRecID && prevAT != $5  && $4 != 1) {
      numberOfError+=1
      errorRecords=errorRecords" "$4":{"((($5-prevAT)/1000)/60)","($5-$1)/1000/60","(prevRecID-$4)","$7"}"
    }
    prevAT = $5
    prevRecID = $4
  }
  fnr=FNR
}
END {
  if ( numberOfError >  1 ) {
    print(filename,maxDif/1000/60/60,minDif/1000/60/60,fnr,numberOfError,errorRecords)
  }
}