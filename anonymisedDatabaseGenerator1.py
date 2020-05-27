# -*- coding: utf-8 -*-

import os
import csv
import geoip2.database
from geoip2.errors import AddressNotFoundError
import re
import datetime
#import _thread
import threading
import hashlib

startWithGtoL = []
startWithMtoS = []

for filename in os.listdir('D:/info2/tdk/Stunner_meresek/user_preproceed_v1/out4'):
    if re.match(r'^[g-lG-L]', filename):
        startWithGtoL.append(filename)
    elif re.match(r'^[m-rM-R]', filename):
        startWithMtoS.append(filename)

print("step1")

m = hashlib.sha256()

def readAndSortCSV(myArray):
    headers = ["fileRowCounter", "sequenceByServer", "fileCreationDate", "previousValidUploadDate", "sourceFile", "sourceRow", "serverSideUploadDate", "deviceHash", "platform", "publicIP", "privateIP", "androidTime", "latitude", "longitude", "androidversion", "discoveryResultCode", "connectionMode", "technology", "present", "pluggedState", "voltage", "temperature", "percentage", "health", "chargingState", "bandwidth", "ssid", "rssi", "carrier", "simCountryIso", "networkType", "roaming", "shutdownTimestamp", "turnOnStimestamp", "uptime", "triggerCode", "appVersion", "timeZone", "androidSortedID", "androidSortedValidation", "country", "system_organization", "continent"]
    tempDict = {}
    for filename in myArray:
        with open('D:/info2/tdk/Stunner_meresek/user_preproceed_v1/out4/' + filename, encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                geoReader = geoip2.database.Reader('D:/info2/tdk/GeoLite2-City_20181106/GeoLite2-City.mmdb')
                geoReader2 = geoip2.database.Reader('D:/info2/tdk/GeoLite2-ASN_20181106/GeoLite2-ASN.mmdb')
                try:
                    tempVersion = (int)(row[7])
                    epoch = int(row[4])/1000
                    tempDate = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m')
                    try:
                        if row[26] != 'NaN' and row[26] != 'NA':
                            response = geoReader.city(row[26])
                            response2 = geoReader2.asn(row[26]) 
                            row.append(response.country.name)
                            row.append(response2.autonomous_system_organization)
                            row.append(response.continent.name)
                        else:
                            row.append("NaN")
                            row.append("NaN")
                            row.append("NaN")
                    except AddressNotFoundError:
                        row.append("NaN")
                        row.append("NaN")
                        row.append("NaN")
                    except ValueError:
                        row.append("NaN")
                        row.append("NaN")
                        row.append("NaN")
                    except TypeError:
                        row.append("NaN")
                        row.append("NaN")
                        row.append("NaN")
                    row[11] = hashlib.sha256((row[11] + "-" + row[11]).encode()).digest()
                    row[26] = hashlib.sha256((row[26] + "-" + row[26]).encode()).digest()
                    row[46] = hashlib.sha256((row[46] + "-" + row[46]).encode()).digest()
                    row[47] = hashlib.sha256((row[47] + "-" + row[47]).encode()).digest()
                    if tempDate in tempDict:
                        tempDict[tempDate].append(row)
                    else:
                        tempList = []
                        tempList.append(row)
                        tempDict[tempDate] = tempList
                except ValueError:
                    epoch = int(row[11])/1000
                    tempDate = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m')
                    try:
                        if row[9] != 'NaN' and row[9] != 'NA':
                            response = geoReader.city(row[9])
                            response2 = geoReader2.asn(row[9]) 
                            row.append(response.country.name)
                            row.append(response2.autonomous_system_organization)
                            row.append(response.continent.name)
                        else:
                            row.append("NaN")
                            row.append("NaN")
                            row.append("NaN")
                    except AddressNotFoundError:
                        row.append("NaN")
                        row.append("NaN")
                        row.append("NaN")
                    except ValueError:
                        row.append("NaN")
                        row.append("NaN")
                        row.append("NaN")
                    except TypeError:
                        row.append("NaN")
                        row.append("NaN")
                        row.append("NaN")
                    row[9] = hashlib.sha256((row[9] + "-" + row[9]).encode()).digest()
                    row[10] = hashlib.sha256((row[10] + "-" + row[10]).encode()).digest()
                    row[12] = hashlib.sha256((row[12] + "-" + row[12]).encode()).digest()
                    row[13] = hashlib.sha256((row[13] + "-" + row[13]).encode()).digest()
                    if tempDate in tempDict:
                        tempDict[tempDate].append(row)
                    else:
                        tempList = []
                        tempList.append(row)
                        tempDict[tempDate] = tempList
        print("step2")
        for key in tempDict:
            fileEmpty = os.path.exists('D:/info2/tdk/Stunner_meresek/stunner/data/v1/' + key + '.csv')
            with open('D:/info2/tdk/Stunner_meresek/stunner/data/v1/' + key + '.csv', "a", newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                if not fileEmpty:
                    writer.writerow(headers)
                for value in tempDict[key]:
                    if len(value) != 0:
                        writer.writerow(value)
        tempDict.clear()
        print("step3")
    print("end")

try:
    threads = []
    t3 = threading.Thread(target=readAndSortCSV, args=(startWithGtoL,))
    t4 = threading.Thread(target=readAndSortCSV, args=(startWithMtoS,))
    threads.append(t3)
    threads.append(t4)
    t3.start()
    t4.start()
except Exception as e:
   print (e)  