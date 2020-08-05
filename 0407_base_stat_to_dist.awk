BEGIN {
  print("#@arppy")>"onlinePercentDist.out"
  print("#@arppy")>"offlinePercentDist.out"
}
{
 onlineDist[int($1*100)]++;
 offlineDist[int($2*100)]++;
 sum++
}
END{
 for (p=0;p<=100;p++) {
   if (p in onlineDist) {
     print(p,onlineDist[p],onlineDist[p]/sum)>>"onlinePercentDist.out"
   } else {
     print(p,0,0)>>"onlinePercentDist.out"
   }
   if (p in offlineDist) {
     print(p,offlineDist[p],offlineDist[p]/sum)>>"offlinePercentDist.out"
   } else {
      print(p,0,0)>>"offlinePercentDist.out"
   }
 }
}