#! /bin/bash
rm -r out6/shorts 2> /dev/null; mkdir out6/shorts
#rm -r out6/only_offline 2> /dev/null; mkdir out6/only_offline
for user in $(ls -ld out6/* | egrep "^-" | awk '{print($NF)}'); do
  isMoved=$(awk -F";" 'BEGIN{
      deleteFile=1;
      isPrinted=0
    }
    FNR==1 {
      startTime=$1;
      prevTime=$1
      prevOnline=$2
      sumOfOnline=0
    }
    FNR>1 {
     deltaTime=$1-startTime;
     if(prevOnline == 1) {
       sumOfOnline+=$1-prevTime
     }
     //$1-prevTime
     if(deltaTime>=86400000 && sumOfOnline>=600000) {
       print(0);
       deleteFile=0;
       isPrinted=1
       exit;
     }
     prevTime=$1
     prevOnline=$2
    }
    END {
     if(deleteFile==1){
      print(1)
      isPrinted=1
     } else if (isPrinted==0) {
      print(0)
     }
    }' $user)
  #echo $isMoved
  if [ $isMoved -eq 1 ] ; then
    mv $user out6/shorts/
  fi
done
