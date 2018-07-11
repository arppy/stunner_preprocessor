#! /usr/bin/awk -f
{
  numOfDays=0
  aDay=1000*60*60*24
  thisDayStartTimeStamp = int($3/aDay)*aDay
  if(thisDayStartTimeStamp==$3){
    numOfDays=1
  }
  timeStamp=$3
  outStr=$1" "$2"_"numOfDays" "thisDayStartTimeStamp" "$4" :"
  for (i=6;i<=NF;i+=2) {
     while(timeStamp+$i > thisDayStartTimeStamp+aDay){ # a new day begins
       difToMidnight = thisDayStartTimeStamp+aDay-timeStamp
       outStr=outStr" "difToMidnight" "$(i+1)
       if(numOfDays > 0) {
         print(outStr)
       }# else {
         #print("SHORT "timeStamp-$3" "outStr)
       #}
       timeStamp+=difToMidnight
       $i-=difToMidnight
       thisDayStartTimeStamp+=aDay
       numOfDays+=1
       outStr=$1" "$2"_"numOfDays" "thisDayStartTimeStamp" "$4" :"
     }
     outStr=outStr" "$i" "$(i+1)
     timeStamp+=$i
  }
  #if(numOfDays > 0) {
  #   print("SHORT "timeStamp-thisDayStartTimeStamp" "outStr)
  #} else {
  #   print("SHORT "timeStamp-$3" "outStr)
  #}
}
