#! /bin/bash
rm 000000000000000000000 2> /dev/null
rm 000000000000000000001 2> /dev/null
is_add_delay=false;
is_append_nat=false;
is_drop_short_session=false
is_create_onedaylong_period=false
is_remove_slow_mobilenetwork=1
is_drop_100percent_offline_session=false
is_charging_important=1
is_keep_temporary_directories=false
is_make_sessions=false
number_of_cores=2
for param in $*; do
  if [ $param = keepTmp -o $param = keepTemporaryDirectories ]; then 
    is_keep_temporary_directories=true
  fi
  if [ $param = chargingStateNoCharger -o $param = noCharger ]; then
    is_charging_important=0;
  fi
  if [ $param = addDelay  ]; then
    is_add_delay=true;
  fi
  if [ $param = appendNAT -o $param = appendNat ]; then
    is_append_nat=true;
  fi
  if [ $param = oneDayLong ]; then
    is_create_onedaylong_period=true;
  fi
  if [ $param = drop100offline ]; then
    is_drop_100percent_offline_session=true;
  fi
  if [ $param = dropShort ]; then
    is_drop_short_session=true;
  fi
  if [ $param = noRemoveSlow -o $param = doNotRemoveSlowMobileNetwork ]; then
    is_remove_slow_mobilenetwork=0
  fi
  if echo $param | egrep -q "^[0-9]+$" ; then
    number_of_cores=$param
  fi
  if [ $param = makeSessions -o $param = session ]; then
    is_make_sessions=true
  fi
done
rm -r out 2> /dev/null; mkdir out; cd out; mkdir $(seq 0 $(($number_of_cores-1))); cd ..
python3 0010_json_to_csv.py $number_of_cores
for core in $(ls -l out | awk '/^d/{print($NF)}'); do rm ${core}/null 2> /dev/null; for filename in ${core}/*; do cat $filename >> out/$(echo $filename | cut -d"/" -f3); done; rm -r ${core} 2> /dev/null; done
rm -r out2 2> /dev/null; mkdir out2;
if [ $is_make_sessions = false ]; then
  python3 0020_delete_duplication.py $number_of_cores toPublic
  mkdir toPublic 2> /dev/null; cd toPublic/; for year in $(seq 2010 2030); do for i in  $(seq 1 12); do if (($i<10)); then fname=$year"-0"$i; else fname=$year"-"$i; fi; mkdir $fname 2> /dev/null ; done done; cd ..
  for filename in out2/*; do mv $filename "toPublic/"$(echo $filename | awk -F"." '{print($NF)}')"/"$(basename $filename | awk -F"." '{str="";for(i=1;i<NF;i++){str=str""$i;}print(str)}'); done
  for fold in toPublic/*; do if (( $(ls -1 $fold | wc -l) == 0 )); then rm -r $fold; fi done
else
  python3 0020_delete_duplication.py $number_of_cores
fi



#for core in out2/*; do rm ${core}/*. 2> /dev/null; done
if [ $is_keep_temporary_directories = false ]; then
  rm -r out
fi
rm -r out3  2> /dev/null
mkdir out3
python3 0030_correct_android_time.py
if [ $is_keep_temporary_directories = false ]; then
  rm -r out2  2> /dev/null
fi
rm out3/*REMOVED
rm -r out4 2> /dev/null
mkdir out4
./0040_makeTheNATCorrection.awk out3/*
if [ $is_keep_temporary_directories = false ]; then
  rm -r out3  2> /dev/null
fi
rm -r out5  2> /dev/null
mkdir out5
./0050_prefilterBeforeSessionCreation.awk out4/*  # -v versionSupport=2
if [ $is_keep_temporary_directories = false ]; then
  rm -r out4
fi
./0051_createSessionsWithNAT.awk -v is_charging_important="$is_charging_important" -v remove_slow_mobilenetwork="$is_remove_slow_mobilenetwork" out5/* > peersim_session_NAT.txt
#if [ $is_keep_temporary_directories = false ]; then
#  rm -r out5
#fi
cat peersim_session_NAT.txt > peersim_session_NATd.txt
if [ $is_append_nat = true ]; then
  ./0052_appendSimilarNATtypes.awk peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_add_delay = true ]; then
  ./0060_add_connection_establishment_offline_sessions.awk -v delay=10000 peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_drop_short_session = true ]; then  
  ./0070_drop_short_sessions.awk -v threshold=86400000 peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_create_onedaylong_period = true ]; then  
  ./0080_create_daylong_periods.awk peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_drop_100percent_offline_session = true ]; then
  ./0090_drop_100percent_offline_sessions.awk peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
cat peersim_session_NATd.txt > peersim_session_NAT.txt
rm peersim_session_NATd.txt
