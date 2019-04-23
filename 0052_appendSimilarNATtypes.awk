#! /usr/bin/awk -f
{
 printStrSuf  = "";
 prevSessionLength = $6;
 prevSessionNatType = $7;
 if(prevSessionNatType != -3 && prevSessionNatType != -2 && prevSessionNatType != -1 ) { #something online && prevSessionNatType != 1
   printStrSuf = " "prevSessionLength" "prevSessionNatType;
 }
 if(NF>7){
  for(i=8;i<=NF;i+=2) {
    recSessionLength = $i;
    recSessionNatType = $(i+1);
    if(prevSessionNatType != -3 && prevSessionNatType != -2 && prevSessionNatType != -1 ) { #prev something online && prevSessionNatType != 1
     if(recSessionNatType != -3 && recSessionNatType != -2 && recSessionNatType != -1 ) { #rec something online && prev something online  && recSessionNatType != 1
      printStrSuf = printStrSuf" "recSessionLength" "recSessionNatType; 
     }
     prevSessionLength = recSessionLength;
    } else { 
     if(recSessionNatType != -3 && recSessionNatType != -2 && recSessionNatType != -1 ) { #rec something online && prev something ofline && recSessionNatType != 1
      printStrSuf = printStrSuf" "prevSessionLength" -2 "recSessionLength" "recSessionNatType;
      prevSessionLength = recSessionLength;
     } else { #rec something ofline && prev something ofline
      prevSessionLength = recSessionLength+prevSessionLength;
     }
    } 
    prevSessionNatType = recSessionNatType;
  }
  if(prevSessionNatType == -3 || prevSessionNatType == -2 || prevSessionNatType == -1 ) { #something ofline  || prevSessionNatType == 1
    printStrSuf = printStrSuf" "prevSessionLength" -2";
  }
 }
 if(!printStrSuf) {
   printStrSuf = " "prevSessionLength" -2";
 }
 print $1" "$2" "$3" "$4" "$5""printStrSuf
}
