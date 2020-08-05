import os
import csv
import shutil
import sys
import multiprocessing

INFILE_PATH = 'out8/'
OUTFILE_PATH = 'out8/only_offline/'

if len(sys.argv) > 1 and sys.argv[1] and sys.argv[1] is not None and str.isnumeric(sys.argv[1]):
  NUMBER_OF_CORES = int(sys.argv[1])
else :
  NUMBER_OF_CORES = 1

def remove_all_offline(fileList) :
  for fileName in fileList:
    with open('' + INFILE_PATH + fileName) as csvfile:
      stunnerReader = csv.reader(csvfile, delimiter=';', quotechar='|')
      isDelete = 1
      for line in stunnerReader:
        if str(line[1]) == "1" :
          isDelete = 0
          break
      if isDelete == 1 :
        src = os.path.join(INFILE_PATH, fileName)
        destination = os.path.join(OUTFILE_PATH, fileName)
        shutil.move(src,destination)

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
  processes.append(multiprocessing.Process(target=remove_all_offline, args=(fileList[core],)))
  processes[-1].start()  # start the thread we just created
  print(len(fileList[core]))
for t in processes:
  t.join()