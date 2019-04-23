#! /usr/bin/awk -f
# input: ls -1 res/res_v1 | ./0001_examine_res_continuity.awk
BEGIN{
  FS="."
}
NR==1{
  prevDate=$1
}
NR>1{
  recDateNeedToBe=prevDate+1
  if($1 != recDateNeedToBe) {
    print(recDateNeedToBe)
  }
  prevDate=$1
}
