import os
import csv
import shutil
import sys
import multiprocessing

INFILE_PATH = 'out6/'
OUTFILE_PATH = 'out7/'

if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] is not None and str.isnumeric(sys.argv[1]):
  NUMBER_OF_CORES = int(sys.argv[1])
else :
  NUMBER_OF_CORES = 1

def remove_short_online(fileList) :
  for fileName in fileList:
    with open('' + INFILE_PATH + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      file = open('' + OUTFILE_PATH + fileName, "a+", encoding="utf-8")
      prevPrintedLine = []
      line = []
      lineI = 0
      for nextLine in stunnerReader:
        if lineI > 0 :
          if len(prevPrintedLine) > 0 and int(prevPrintedLine[1]) == 0 and int(line[1]) == 0 :
            lineI += 1
            line = nextLine
            continue
          timeDif = int(nextLine[0]) - int(line[0])
          if timeDif >= 1000:
            outStr = str(line[0])
            for record in line[1:]:
              outStr += ";" + str(record)
            #if len(prevPrintedLine) > 0 :
            #  outStr += "(prevPrintedLine:"+ str(prevPrintedLine[0])
            #  for record in prevPrintedLine[1:]:
            #    outStr += ";" + str(record)
            #  outStr += ")"+str(len(prevPrintedLine) > 0)+str(prevPrintedLine[1] == 0)+str(int(line[1]) == 0)
            file.write('' + outStr + '\n')
            prevPrintedLine = line
          else :
            if len(prevPrintedLine) < 1 or int(prevPrintedLine[1]) == 1:
              outStr = str(line[0]) + ";0"
              file.write('' + outStr + '\n')
              prevPrintedLine = [line[0],0]
        lineI += 1
        line = nextLine
      print(fileName, str(lineI))
      if len(prevPrintedLine) < 1 :
        outStr = str(line[0])
        for record in line[1:]:
          outStr += ";" + str(record)
        file.write('' + outStr + '\n')
      elif int(prevPrintedLine[1]) != 0 or int(line[1]) != 0:
        outStr = str(line[0])
        for record in line[1:]:
          outStr += ";" + str(record)
        file.write('' + outStr + '\n')
      file.close()

# MAIN
fileList = {}
for core in range(NUMBER_OF_CORES):
  fileList[core] = []
# FILE_READING
files = os.listdir(INFILE_PATH)
files.sort()
THREAD_FILE_NUMBER_BLOCK_SIZE = int(len(files) / NUMBER_OF_CORES)
fi = 0
core = 0
print(str(os.path.getsize(INFILE_PATH)), os.stat(INFILE_PATH))
sumOfSize = 0
for fileName in files:
  sumOfSize += os.path.getsize(INFILE_PATH + '/' + fileName)
THREAD_FILE_SIZE_BLOCK_SIZE = int(sumOfSize / NUMBER_OF_CORES)
# print(str(0),sumOfSize,str(THREAD_FILE_SIZE_BLOCK_SIZE),str(NUMBER_OF_CORES*THREAD_FILE_SIZE_BLOCK_SIZE))
for fileName in files:
  # searchObj = re.search(r'^[0-9]{6}_2014[0-9]{4}-[0-9]{4}\.csv$', fileName)
  path = os.path.join(INFILE_PATH, fileName)
  if os.path.isdir(path):
    continue
  fileList[core].append(fileName)
  fi += os.path.getsize(INFILE_PATH + '/' + fileName)
  if fi / THREAD_FILE_SIZE_BLOCK_SIZE > 1 and core != NUMBER_OF_CORES - 1:
    sumOfSize -= fi
    core += 1
    THREAD_FILE_SIZE_BLOCK_SIZE = int(sumOfSize / (NUMBER_OF_CORES - core))
    # print(fi, sumOfSize, str(THREAD_FILE_SIZE_BLOCK_SIZE), str(NUMBER_OF_CORES-core))
    fi = 0
# print(fi, sumOfSize, str(THREAD_FILE_SIZE_BLOCK_SIZE), str(NUMBER_OF_CORES-core))
processes = []
for core in range(NUMBER_OF_CORES):
  processes.append(multiprocessing.Process(target=remove_short_online, args=(fileList[core],)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()
