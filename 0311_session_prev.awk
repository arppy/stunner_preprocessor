#! /usr/bin/awk -f
BEGIN {
  max=0  
  natStringDictAbbreviation[0] = "OA"
  natStringDictAbbreviation[3] = "FC"
  natStringDictAbbreviation[4] = "RC"
  natStringDictAbbreviation[5] = "PRC"
  natStringDictAbbreviation[6] = "SC"
  natStringDictAbbreviation[2] = "SF"
  natStringDictAbbreviation[1] = "FB"
  natStringDictAbbreviation[-2] = "NO"
  #natStringDictAbbreviation[-1] = "ER"
  #natStringDictAbbreviation[-3] = "N/A"
  for ( natCode in natStringDictAbbreviation ) {
    natTansitionHeatmap["CON"][natStringDictAbbreviation[natCode]]=-1
    natTansitionHeatmap["CON"][natStringDictAbbreviation[natCode]]+=1
  }
  for ( natCode1 in natStringDictAbbreviation ) {
    for ( natCode2 in natStringDictAbbreviation ) {
      natTansitionHeatmap[natStringDictAbbreviation[natCode1]][natCode2]=-1
      natTansitionHeatmap[natStringDictAbbreviation[natCode1]][natCode2]+=1
    }
  }
  
  for ( natCode in natStringDictAbbreviation ) {
    natTansitionHeatmap[natStringDictAbbreviation[natCode]]["COF"]=-1
    natTansitionHeatmap[natStringDictAbbreviation[natCode]]["COF"]+=1
  }
}
{
  natTansitionHeatmap["CON"][natStringDictAbbreviation[$7]]+=1
  if (NF>7) {
    for(i=9;i<=NF-2;i+=2){
      natTansitionHeatmap[natStringDictAbbreviation[$(i-2)]][natStringDictAbbreviation[$i]]+=1
      $(i-2)
    } 
  }
  natTansitionHeatmap[natStringDictAbbreviation[$NF]]["COF"]+=1
}
END{
  outStr="prev"  
  for (nat1 in natTansitionHeatmap) {
    for (nat2 in natTansitionHeatmap[nat1] ) {
      outStr=outStr","nat2
    }
    break;
  }
  print(outStr)
  for (nat1 in natTansitionHeatmap) {
    outStr=nat1 
    for (nat2 in natTansitionHeatmap[nat1] ) {
      outStr=outStr","natTansitionHeatmap[nat1][nat2]
    }
    print(outStr)
  }
}
