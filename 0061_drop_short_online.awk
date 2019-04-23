#! /usr/bin/awk -f
BEGIN{
  onlineNat[0]=1
  onlineNat[1]=1
  onlineNat[2]=1
  onlineNat[3]=1
  onlineNat[4]=1
  onlineNat[5]=1
  onlineNat[6]=1
}
function appendWithSpaceIfPrevStrNotEmpty(prevStr,str)
{
     if(prevStr){
      return ""prevStr" "str
     } else {
      return ""str
     }
}
function isOnline(nat){
  if (nat in onlineNat) {
    return 1
  }
  return 0
}
{
 printStrSuf  = "";
 prevSessionLength = $6;
 prevSessionNatType = $7;
 if(isOnline(prevSessionNatType)==1 &) { #something online
   printStrSuf = ""delay" -2 "(prevSessionLength-delay)" "prevSessionNatType;
 } else {
   printStrSuf = ""prevSessionLength" "prevSessionNatType;
 }
 if(NF>7){
  for(i=8;i<=NF;i+=2) {
    recSessionLength = $i;
    recSessionNatType = $(i+1);
    #TODO complite it!! LEHETHOGYJÓÓ!!
    if(prevSessionNatType == -2){
     prevSessionNatType = recSessionNatType;
     if(recSessionNatType != -2 && recSessionNatType != -1  && recSessionNatType != 1 && recSessionLength-delay > 0) { #something online
      printStrSuf = appendWithSpaceIfPrevStrNotEmpty(printStrSuf,""prevSessionLength+delay" -2 "(recSessionLength-delay)" "recSessionNatType);
      prevSessionLength = recSessionLength;
     } else if (recSessionNatType == -1  || recSessionNatType == 1 ){
      printStrSuf = appendWithSpaceIfPrevStrNotEmpty(printStrSuf,""prevSessionLength" -2 "recSessionLength" "recSessionNatType);
      prevSessionLength = recSessionLength;
     } else {
      prevSessionLength = recSessionLength+prevSessionLength;
      prevSessionNatType = "-2";
     }
    } else {
     prevSessionLength = recSessionLength;
     prevSessionNatType = recSessionNatType;
     if(recSessionNatType != -2 && recSessionNatType != -1  && recSessionNatType != 1  && recSessionLength-delay > 0) { #something online
      printStrSuf = appendWithSpaceIfPrevStrNotEmpty(printStrSuf,""delay" -2 "(recSessionLength-delay)" "recSessionNatType);
     } else if (recSessionNatType != -2 ){
      printStrSuf = appendWithSpaceIfPrevStrNotEmpty(printStrSuf,""recSessionLength" "recSessionNatType);
     } else {
      prevSessionNatType = "-2";
     }
    }
  }
 }
 if(prevSessionNatType == -2){
   printStrSuf = appendWithSpaceIfPrevStrNotEmpty(printStrSuf,""prevSessionLength" "prevSessionNatType);
 }
 print $1" "$2" "$3" "$4" "$5" "printStrSuf
}
