#! /bin/bash
rm -r base_stat.out 2> /dev/null;
for user in out8/*; do
  if [ -f $user ] ; then
    awk -F";" 'BEGIN{
      sumOfOnline=0
      sumOfOffline=0
    }
    FNR==1{
      startTimestamp=$1
      online=$2
    }
    FNR>1{
      if (online == 1) {
        sumOfOnline+=$1-startTimestamp
      } else {
        sumOfOffline+=$1-startTimestamp
      }
      startTimestamp=$1
      online=$2
    }
    END {
      all = sumOfOnline + sumOfOffline
      if(all != 86400000) {
        print("!!!",all,sumOfOffline,sumOfOnline,FILENAME)
      } else {
        print(sumOfOnline/all,sumOfOffline/all)
      }
    }' $user >> base_stat.out
  fi
done
