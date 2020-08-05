#! /bin/bash
#rm -r $1/shorts 2> /dev/null; mkdir $1/shorts
rm -r $1/only_offline 2> /dev/null; mkdir $1/only_offline
for user in $1/*; do
  if [ -f $user ] ; then
    isMoved=$(awk -F";" 'BEGIN{
      deleteFile=1;
    }
    {
     if($2==1) {
       print(0);
       deleteFile=0;
       exit;
     }
    }
    END {
     if(deleteFile==1){
      print(1)
     }
    }' $user)
    if [ $isMoved -eq 1 ] ; then
      mv $user $1/only_offline/
    fi
  fi
done
