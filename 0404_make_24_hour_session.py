import os
import csv
import sys
import multiprocessing

INFILE_PATH = 'out7/'
OUTFILE_PATH = 'out8/'

if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] is not None and str.isnumeric(sys.argv[1]):
  NUMBER_OF_CORES = int(sys.argv[1])
else :
  NUMBER_OF_CORES = 1



def make_24_hour_session(fileList) :
  for fileName in fileList:
    with open('' + INFILE_PATH + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      day = 0
      lineI = 0
      file = open('' + OUTFILE_PATH + fileName+str(day), "a+", encoding="utf-8")
      prevDay = 0
      prevLine = []
      for line in stunnerReader:
        dayTimeStamp = int(int(line[0]) / 1000 / 60 / 60 / 24) * 1000 * 60 * 60 * 24
        if lineI == 0 :
          outStr = "" + str(dayTimeStamp) + ";0"
          file.write('' + outStr + '\n')
          if str(line[1]) == "1" :
            outStr = "" + str(line[0])
            for record in line[1:] :
              outStr += ";" + str(record)
            file.write('' + outStr + '\n')
        else :
          if dayTimeStamp != prevDay :
            j = 0
            while True :
              outStr = "" + str(prevDay + (1000 * 60 * 60 * 24)) + ";-1"
              file.write('' + outStr + '\n')
              file.close()
              day+=1
              file = open('' + OUTFILE_PATH + fileName + str(day), "a+", encoding="utf-8")
              #if str(prevLine[1]) == "1" :
              #  print(fileName + str(day) )
              outStr = "" + str(dayTimeStamp) + ";" + str(prevLine[1])
              for record in prevLine[2:]:
                outStr += ";" + str(record)
              file.write('' + outStr + '\n')
              if prevDay + (1000 * 60 * 60 * 24) < dayTimeStamp :
                prevDay += (1000 * 60 * 60 * 24)
              else :
                break
          outStr = "" + str(line[0])
          for record in line[1:] :
            outStr += ";" + str(record)
          file.write('' + outStr + '\n')
        prevDay = dayTimeStamp
        prevLine = line
        lineI += 1
      dayTimeStamp = int((int(prevLine[0])+1) / 1000 / 60 / 60 / 24) * 1000 * 60 * 60 * 24
      if prevDay != dayTimeStamp :
        outStr = "" + str(dayTimeStamp) + ";-1"
        file.write('' + outStr + '\n')
        file.close()
      else :
        if str(prevLine[1])=="1" :
          outStr = "" + str(int(prevLine[0])+1) + ";0"
          file.write('' + outStr + '\n')
        dayTimeStamp = prevDay + (1000 * 60 * 60 * 24)
        outStr = "" + str(dayTimeStamp) + ";-1"
        file.write('' + outStr + '\n')
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
  path = os.path.join(INFILE_PATH, fileName)
  if os.path.isdir(path) :
    continue
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
  processes.append(multiprocessing.Process(target=make_24_hour_session, args=(fileList[core],)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()
