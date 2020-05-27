#! /usr/bin/awk -f
{
  FS=";"
  codedField[7] = 1
  codedField[10] = 1
  codedField[11] = 1
  codedField[15] = 1
  codedField[23] = 1
  codedField[25] = 1
  codedField[26] = 1
  codedField[34] = 1
  codedField[36] = 1
  codedField[37] = 1
  codedField[39] = 1
  codedField[60] = 1
}
{
  versionNumber[$9]++
  for (i in codedField) {
    versionField[$9][i][$i]++
  }
}
END{
  for (l in codedField) {
    for (j=1;j<=30;j++){
      if(versionNumber[j] > 0) {
          outstr=j":\t-10:"versionField[j][l][-10]
          for (i=-3;i<=20;i++){
             outstr=outstr"\t"i":"int(versionField[j][l][i])
          }
          print(outstr) >> l".out"
      } else {
        print(j) >> l".out"
      }
    }
  }
}