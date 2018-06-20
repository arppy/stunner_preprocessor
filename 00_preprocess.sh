#! /bin/bash
rm 000000000000000000000 2> /dev/null
rm 000000000000000000001 2> /dev/null
rm -r out 2> /dev/null
rm -r out2 2> /dev/null
rm -r out3 2> /dev/null
rm -r out4 2> /dev/null
is_add_delay=false;
is_append_nat=false;
is_drop_short_session=false
is_create_onedaylong_period=false
is_remove_slow_mobilenetwork=false
is_drop_100percent_offline_session=false
for param in $*; do
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
  if [ $param = removeSlow -o $param = removeSlowMobileNetwork ]; then
    is_remove_slow_mobilenetwork=true
  fi
done
mkdir out
python3 01_json_to_csv.py
rm out/null 2> /dev/null
mkdir out2
python3 02_sort_by_android_time.py
#rm -r out
#mv out2 out
mkdir out3
python3 03_correct_android_time.py
#rm -r out
#mv out3 out
mkdir out4
if [ $is_remove_slow_mobilenetwork = true ]; then
  ./04_makeTheNATCorrection.awk -v remove_slow_mobilenetwork=1 out3/*
else
  ./04_makeTheNATCorrection.awk -v remove_slow_mobilenetwork=0 out3/*
fi
#rm -r "out"
#mv out4 out
./05_1_createSessionsWithNAT.awk out4/* > peersim_session_NAT.txt
rm -r out 2> /dev/null
rm -r out2 2> /dev/null
rm -r out3 2> /dev/null
rm -r out4 2> /dev/null
cat peersim_session_NAT.txt > peersim_session_NATd.txt
if [ $is_append_nat = true ]; then
  ./05_2_appendSimilarNATtypes.awk peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_add_delay = true ]; then
  ./06_add_connection_establishment_offline_sessions.awk -v delay=10000 peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_drop_short_session = true ]; then  
  ./07_drop_short_sessions.awk -v threshold=86400000 peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_create_onedaylong_period = true ]; then  
  ./08_create_daylong_periods.awk peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
if [ $is_drop_100percent_offline_session = true ]; then
  ./09_drop_100percent_offline_sessions.awk peersim_session_NATd.txt > peersim_session_NATdbac.txt
  cat peersim_session_NATdbac.txt > peersim_session_NATd.txt
  rm peersim_session_NATdbac.txt
fi
cat peersim_session_NATd.txt > peersim_session_NAT.txt
rm peersim_session_NATd.txt
