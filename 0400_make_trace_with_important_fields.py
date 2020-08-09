import os
import csv
import datetime
import sys
import multiprocessing

#OPEN LOOKUP DICTS
HOUR_LOOKUP = {}
HOUR_INPUT_FILE_PATH = "toModel/dict_hours.csv"
with open(HOUR_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    HOUR_LOOKUP[str(line[2])] = line[1]

minAndroidVersion = 999999
maxAndroidVersion = 0
ANDROID_VERSION_LOOKUP = {}
ANDROID_VERSION_INPUT_FILE_PATH = "toModel/dict_android_versions.csv"
with open(ANDROID_VERSION_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    ANDROID_VERSION_LOOKUP[str(line[2])] = line[1]
    if maxAndroidVersion < int(line[2]) :
      maxAndroidVersion = int(line[2])
    if minAndroidVersion > int(line[2]) :
      minAndroidVersion = int(line[2])

WIFI_LOOKUP = {}
WIFI_INPUT_FILE_PATH = "toModel/dict_wifi_bandwidth10.csv"
with open(WIFI_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    WIFI_LOOKUP[str(line[2]).replace(" ", "")] = line[1]

MOBNET_LOOKUP = {}
MOBNET_INPUT_FILE_PATH = "toModel/dict_mobile_net_type10.csv"
with open(MOBNET_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    MOBNET_LOOKUP[str(line[2])] = line[1]

ROAMING_LOOKUP = {}
ROAMING_INPUT_FILE_PATH = "toModel/dict_roaming.csv"
with open(ROAMING_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    ROAMING_LOOKUP[str(line[2])] = line[1]

NAT_LOOKUP = {}
NAT_INPUT_FILE_PATH = "toModel/dict_nat.csv"
with open(NAT_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    NAT_LOOKUP[str(line[2])] = line[1]

WEBRTC_TEST_LOOKUP = {}
WEBRTC_TEST_INPUT_FILE_PATH = "toModel/dict_webrtctest.csv"
with open(WEBRTC_TEST_INPUT_FILE_PATH) as csvfile :
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader :
    WEBRTC_TEST_LOOKUP[str(line[2])] = line[1]

COUNTRY_LOOKUP = {}
COUNTRY_INPUT_FILE_PATH = "toModel/dict_country10.csv"
with open(COUNTRY_INPUT_FILE_PATH) as csvfile:
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader:
    COUNTRY_LOOKUP[str(line[2])] = line[1]

ORG_LOOKUP = {}
ORG_INPUT_FILE_PATH = "toModel/dict_org10.csv"
with open(ORG_INPUT_FILE_PATH) as csvfile:
  dictReader = csv.reader(csvfile, delimiter=';')
  for line in dictReader:
    ORG_LOOKUP[str(line[2])] = line[1]

INFILE_PATH = 'out5/'
OUTFILE_PATH = 'out6/'

if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] is not None and str.isnumeric(sys.argv[1]):
  NUMBER_OF_CORES = int(sys.argv[1])
else :
  NUMBER_OF_CORES = 1

MAX_ONLINE_DIF=780000

def make_trace_with_important_fields(fileList) :
  orgOut = {}
  countryOut = {}
  for fileName in fileList:
    with open('' + INFILE_PATH + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
      prevOnline = 0
      prevTime = 0
      prevHour = 0
      prevOutStr = ""
      #checkTheMinusOneNAT = False
      i=0
      for line in stunnerReader:
        i+=1
        online = 0
        time = int(line[4])
        newOutStr = "" + str(time)
        timeObj = datetime.datetime.utcfromtimestamp(int(float(time) / 1000.0))
        hour = timeObj.hour
        if int(HOUR_LOOKUP[str(prevHour)]) != -1 and int(int(HOUR_LOOKUP[str(prevHour)]) / 10) == 0 :
          substrStartIndexForPrev = 18
        else:
          substrStartIndexForPrev = 19
        if int(HOUR_LOOKUP[str(hour)]) != -1 and int(int(HOUR_LOOKUP[str(hour)]) / 10) == 0 :
          substrStartIndexForRec = 18
        else:
          substrStartIndexForRec = 19
        if str(line[10]) == "5" and str(line[24]) != "1" and str(line[24]) != "-1" and \
            (str(line[36]) == "1" or str(line[36]) == "2" or str(line[36]) == "4" or \
             str(line[35]) == "2" or str(line[35]) == "5") :  # networkInfo == CONNECTED and NATtype is online and onCharger == True
          online = 1
          if str(line[24]) == "-3" :
            if prevOnline == 0 or time-prevTime>MAX_ONLINE_DIF :
              online = 0
              newOutStr = newOutStr + ";0"
            else :
              newOutStr = newOutStr + ";1;" + str(HOUR_LOOKUP[str(hour)]) + ";" + prevOutStr[substrStartIndexForPrev:] # + "GGGGGG" + str(prevHour) + " " + str(int(HOUR_LOOKUP[str(prevHour)]) != -1) + " " + str(int(int(HOUR_LOOKUP[str(prevHour)]) / 10) == 0) + " " + str(substrStartIndexForRec) + " "
          else:
            newOutStr = newOutStr + ";1"
            newOutStr = newOutStr + ";" + str(HOUR_LOOKUP[str(hour)])
            try:
              newOutStr = newOutStr + ";" + str(ANDROID_VERSION_LOOKUP[str(line[7])])
            except:
              if int(line[7]) > maxAndroidVersion :
                newOutStr = newOutStr + ";" + str(ANDROID_VERSION_LOOKUP[str(maxAndroidVersion)])
              elif int(line[7]) < minAndroidVersion :
                newOutStr = newOutStr + ";" + str(ANDROID_VERSION_LOOKUP[str(minAndroidVersion)])
              else :
                newOutStr = newOutStr + ";" + str(ANDROID_VERSION_LOOKUP[str(int(line[7])+1)])
            if str(line[9]) == "1" :
              try:
                newOutStr = newOutStr + ";" + str(WIFI_LOOKUP[str(line[15])])
              except:
                newOutStr = newOutStr + ";-1"
            else :
              newOutStr = newOutStr + ";" + str(WIFI_LOOKUP["N/A"])
            if str(line[9]) == "0" :
              try:
                newOutStr = newOutStr + ";" + str(MOBNET_LOOKUP[str(line[18])])
              except:
                newOutStr = newOutStr + ";-1"
            else :
              newOutStr = newOutStr + ";" + str(MOBNET_LOOKUP["N/A"])
            newOutStr = newOutStr + ";" + str(ROAMING_LOOKUP[str(line[21])])
            try:
              newOutStr = newOutStr + ";" + str(NAT_LOOKUP[str(line[24])])
            except :
              #if str(line[24]) == "-3" or str(line[24]) == "-1" or str(line[24]) == "1":
              newOutStr = newOutStr + ";NATERROR"
              print("NONAT",str(line[24]),str(fileName), str(i))
            try :
              newOutStr = newOutStr + ";" + str(WEBRTC_TEST_LOOKUP[str(line[33])])
            except :
              newOutStr = newOutStr + ";RTCERROR"
              print("NOWEBRTC",str(line[33]),str(fileName), str(i))
            try :
              if str(line[49]) is None or str(line[49]) == "" :
                country = "N/A"
              else :
                country = str(line[49])
              newOutStr = newOutStr + ";" + str(COUNTRY_LOOKUP[country])
            except :
              newOutStr = newOutStr + ";-1"
            try :
              if str(line[50]) is None or str(line[50]) == "" :
                org = "N/A"
              else :
                org = str(line[50])
              newOutStr = newOutStr + ";" + str(ORG_LOOKUP[org])
            except :
              newOutStr = newOutStr + ";-1"
        else :
          newOutStr = newOutStr + ";0"
        if prevOnline == 1 and online == 1 and time-prevTime>MAX_ONLINE_DIF :
          tmpOutStr = "" + str(prevTime+1)+";0"
          #'1V '+str(prevOnline)+" "+str(online)+" "+str(time-prevTime)+" "+str(time)+" "+str(prevTime)+'\t' +
          file.write(tmpOutStr + '\n')
          file.write(newOutStr + '\n')
        elif prevOnline == 1 and online == 0 and time-prevTime>MAX_ONLINE_DIF :
          tmpOutStr = "" + str(prevTime+1)+";0"
          file.write('' + tmpOutStr + '\n')
        elif prevOnline == 1 and hour > prevHour :
          HOUR_UNIT = 1000*60*60
          startTime = int(time/HOUR_UNIT)*HOUR_UNIT
          tmpOutStr = "" + str(startTime) + ";1;" + str(HOUR_LOOKUP[str(hour)]) + ";" + prevOutStr[substrStartIndexForPrev:]
          file.write('' + tmpOutStr + '\n')
          if newOutStr[substrStartIndexForRec:] != prevOutStr[substrStartIndexForPrev:]:
            file.write('' + newOutStr + '\n')
        elif (i == 1) or (prevOnline == 0 and online == 1) or (prevOnline == 1 and online == 0) or \
            (newOutStr[13:] != prevOutStr[13:]) :
          file.write(''+ newOutStr + '\n')
        prevTime = time
        prevHour = hour
        prevOnline = online
        prevOutStr = newOutStr
      if prevOnline == 1 :
        tmpOutStr = '' + str(prevTime+1) + ";0"
        file.write('' + tmpOutStr + '\n')
      file.close()

#MAIN
fileList = {}
for core in range(NUMBER_OF_CORES) :
  fileList[core] = []
# FILE_READING
files = os.listdir(INFILE_PATH)
files.sort()
THREAD_FILE_NUMBER_BLOCK_SIZE = int(len(files)/NUMBER_OF_CORES)
fi=0
core = 0
print(str(os.path.getsize(INFILE_PATH)),os.stat(INFILE_PATH))
sumOfSize = 0
for fileName in files:
  sumOfSize+=os.path.getsize(INFILE_PATH+'/'+fileName)
THREAD_FILE_SIZE_BLOCK_SIZE = int(sumOfSize/NUMBER_OF_CORES)
#print(str(0),sumOfSize,str(THREAD_FILE_SIZE_BLOCK_SIZE),str(NUMBER_OF_CORES*THREAD_FILE_SIZE_BLOCK_SIZE))
for fileName in files:
  #searchObj = re.search(r'^[0-9]{6}_2014[0-9]{4}-[0-9]{4}\.csv$', fileName)
  fileList[core].append(fileName)
  fi+=os.path.getsize(INFILE_PATH+'/'+fileName)
  if fi / THREAD_FILE_SIZE_BLOCK_SIZE > 1 and core != NUMBER_OF_CORES-1:
    sumOfSize -= fi
    core += 1
    THREAD_FILE_SIZE_BLOCK_SIZE = int(sumOfSize / (NUMBER_OF_CORES-core))
    #print(fi, sumOfSize, str(THREAD_FILE_SIZE_BLOCK_SIZE), str(NUMBER_OF_CORES-core))
    fi = 0
#print(fi, sumOfSize, str(THREAD_FILE_SIZE_BLOCK_SIZE), str(NUMBER_OF_CORES-core))
processes = []
for core in range(NUMBER_OF_CORES) :
  processes.append(multiprocessing.Process(target=make_trace_with_important_fields, args=(fileList[core],)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()


