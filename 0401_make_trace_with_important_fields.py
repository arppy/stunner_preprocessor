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



def make_trace_with_important_fields(fileList) :
  orgOut = {}
  countryOut = {}
  for fileName in fileList:
    with open('' + INFILE_PATH + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
      prevLine = []
      #checkTheMinusOneNAT = False
      i=0
      for line in stunnerReader:
        i+=1
        newOutStr = "" + str(line[4])
        timeObj = datetime.datetime.utcfromtimestamp(round(float(line[4]) / 1000.0))
        if str(line[10]) == "5" and str(line[24]) != "1" and str(line[24]) != "-1" and \
                ( str(line[36]) == "1" or str(line[36]) == "2" or str(line[36]) == "4" or str(line[35]) == "2" or str(line[35]) == "5" ):  # networkInfo == CONNECTED and NATtype is online and onCharger == True
          if str(line[24]) == "-3" :
            newOutStr = prevOutStr
          else:
            newOutStr = newOutStr + ";1;"+str(line[6])
            hour = timeObj.hour
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
            if line[9] == 1 :
              newOutStr = newOutStr + ";" + str(WIFI_LOOKUP[str(line[15])])
            else :
              newOutStr = newOutStr + ";" + str(WIFI_LOOKUP["N/A"])
            if line[9] == 0 :
              newOutStr = newOutStr + ";" + str(MOBNET_LOOKUP[str(line[18])])
            else :
              newOutStr = newOutStr + ";" + str(MOBNET_LOOKUP["N/A"])
            newOutStr = newOutStr + ";" + str(ROAMING_LOOKUP[str(line[21])])
            try:
              newOutStr = newOutStr + ";" + str(NAT_LOOKUP[str(line[24])])
            except :
              #if str(line[24]) == "-3" or str(line[24]) == "-1" or str(line[24]) == "1":
              newOutStr = newOutStr + ";NATERROR"
              print("NONAT",str(fileName), str(i))
            try :
              newOutStr = newOutStr + ";" + str(WEBRTC_TEST_LOOKUP[str(line[33])])
            except :
              newOutStr = newOutStr + ";RTCERROR"
              print("NOWEBRTC",str(fileName), str(i))
            try :
              newOutStr = newOutStr + ";" + str(COUNTRY_LOOKUP[str(line[49])])
            except :
              newOutStr = newOutStr + ";-1"
              if str(line[49]) == "" or str(line[49]) == " " or str(line[49]) == "None":
                print("NOCOUNTRY", str(fileName), str(i))
            try :
              newOutStr = newOutStr + ";" + str(ORG_LOOKUP[str(line[50])])
            except :
              newOutStr = newOutStr + ";-1"
              if str(line[50]) == "" or str(line[50]) == " " or str(line[50]) == "None":
                print("NOORG", str(fileName), str(i))
        else :
          newOutStr = newOutStr + ";0;"+str(line[6])
        file.write('' + newOutStr + '\n')
        prevLine = line
        prevOutStr = newOutStr
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


