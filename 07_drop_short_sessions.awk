#! /usr/bin/awk -f
{
 sumOfTime=0
 for(i=6;i<=NF;i+=2) {
   sumOfTime+=$i
 }
 if(sumOfTime>=threshold){
   print $0
 }
}
