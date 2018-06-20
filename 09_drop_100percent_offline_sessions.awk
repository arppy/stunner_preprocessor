#! /usr/bin/awk -f
{
 sumOfTime=0
 sumOfOfflineTime=0
 for(i=6;i<=NF;i+=2) {
   sumOfTime+=$i
   if($(i+1) == -2){
      sumOfOfflineTime+=$i
   }
 }
 if(sumOfTime!=sumOfOfflineTime){
   print $0
 }
}
