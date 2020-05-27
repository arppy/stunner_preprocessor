#! /usr/bin/awk -f
{
  FS=";"
}
{
  versionNumber[$9]++
  for (i=1;i<=NF;i++) {
    if ($i!="") {
      versionField[$9][i]++
    }
  }
}
END{
  for (j=1;j<=30;j++){
    if(versionNumber[j] > 0) {
        outstr=j":"
        for (i=1;i<=62;i++){
           outstr=outstr"\t"i":"((versionField[j][i]*100)/(versionNumber[j]))
        }
        print(outstr)
    } else {
      print(j)
    }
  }
}