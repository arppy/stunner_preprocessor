#! /usr/bin/awk -f
FNR==1{
 minTS=$3
 maxTS=$3
 max=$6
}
{
  minTS=(minTS>$3)?$3:minTS
  maxTS=(maxTS<$3)?$3:maxTS
  for(i=6;i<=NF-1;i+=2){
    alltime+=$i
    sessionAllTime[$(i+1)]+=$i
    if($i>max) {
      max=$i
      #print($i,$0)
    }
  }
}
END{
  print("Maximum timestamp: "maxTS" Minimum timestamp: "minTS" Maximum session: "max)
  for (nat in sessionAllTime) {
    print(nat","sessionAllTime[nat]","sessionAllTime[nat]/alltime)
  } 
}
