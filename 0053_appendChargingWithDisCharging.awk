#! /usr/bin/awk -f
{
 #print(FNR" OUTSTR: "outStr)
 recUser=$1
 recTime=$3
 deltaBetweenRows=recTime-(prevTime+prevRowDeltaTime)
 if ( recUser!=prevUser || deltaBetweenRows<0 ) { #print prev + new line
  if (additionalMinusTwo > 0) {
    outStr=outStr" "additionalMinusTwo" -2"
  }
  if (outStr != "") {
    print(outStr)
  }
  outStr=recUser" "$2" "$3" "$4" :"
  startI=6
  prevUser=recUser
 } else {
  if( NF == 7 && $7 == -2)  {
    additionalMinusTwo+=deltaBetweenRows
    startI=6
  } else {
    if ( $7 == -2) {
      deltaBetweenRows+=$6
      startI=8
    } else {
      startI=6
    }
    deltaBetweenRows+=additionalMinusTwo
    outStr=outStr" "deltaBetweenRows" -2" 
  }
 }
 for(i=startI;i<=NF-3;i+=2) {
  outStr=outStr" "$i" "$(i+1)
 }
 if($NF == -2){
  additionalMinusTwo+=$(NF-1)
 } else {
  outStr=outStr" "$(NF-1)" "$NF
  additionalMinusTwo=0  
 }
 prevRowDeltaTime=0
 for(i=6;i<=NF;i+=2) {
  prevRowDeltaTime+=$i
 }
 prevTime=recTime
 printStrSuf  = "";
 prevSessionLength = $6;
 prevSessionNatType = $7;
}
