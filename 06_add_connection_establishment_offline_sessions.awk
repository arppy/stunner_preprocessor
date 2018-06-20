#! /usr/bin/awk -f
function appendWithSpaceIfPrevStrNotEmpty(prevStr,str)
{
     if(prevStr){
      return ""prevStr" "str
     } else {
      return ""str
     }
}
{
 printStrSuf  = "";
 prevSessionLength = $6;
 prevSessionNatType = $7;
 if(prevSessionNatType != -2 && prevSessionNatType != -1  && prevSessionNatType != 1 && prevSessionLength-delay > 0) { #something online
   printStrSuf = ""delay" -2 "(prevSessionLength-delay)" "prevSessionNatType;
 } else if (recSessionNatType == -1  || recSessionNatType == 1 ){
   printStrSuf = ""prevSessionLength" "prevSessionNatType;
 } else {
   prevSessionNatType = "-2";
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
