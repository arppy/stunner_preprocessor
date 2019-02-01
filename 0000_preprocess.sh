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
done
rm -r out 2> /dev/null
mkdir out  
python3 0010_json_to_csv.py
rm out/null 2> /dev/null
rm -r out2  2> /dev/null
mkdir out2  
python3 0020_sort_by_android_time.py
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
./0050_prefilterBeforeSessionCreation.awk out4/*
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
