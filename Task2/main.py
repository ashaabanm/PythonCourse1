import os
from pathlib import Path
import time
import fnmatch
from subprocess import PIPE, Popen
import json
import pandas as pd
from pandas.io.json import json_normalize
import argparse

start_time = time.time()

def getChecksumsAndDuplicates(dirPath="."):
    checksums = {}
    duplicates = []
    files = Path(dirPath)
    if (files.exists() == False):
        return checksums, duplicates, False
    for file in files.iterdir():
        if fnmatch.fnmatch(file, '*.json') and file.is_file() and file.name.find("_complete") == -1:
            with Popen(["md5sum", file.name], stdout=PIPE) as proc:

                checksum = proc.stdout.read().split()[0]

                if checksum in checksums:
                    duplicates.append(file.name)
                else:
                    checksums[checksum] = file.name
    return checksums, duplicates, True


def removeFiles(files):
    for file in files:
        os.remove(file)


def splitOS(word):
    if (type(word) == str and word != None):
        word = word.split(' ')
        if (len(word) > 1):
            return word[1][1:]
        else:
            return word[0]
    else:
        return word


def cleanUrl(url):
    if (type(url) == str):
        start = url.find("://")
        end = url.find(".com")
        if (start == -1 or end == -1):
            return url
        else:
            return url[start + 3:end + 4]
    else:
        return url


def cleanFile(df, toDate):
    df['web_browser'] = df['a'].str.split(' ', expand=True)[0]
    df['operating_sys'] = df['a'].apply(splitOS)
    df[["longitude", "latitude"]] = df['ll'].apply(pd.Series)
    df.rename(columns={'r': 'from_url',
                       'u': 'to_url',
                       'cy': 'city',
                       'tz': 'time_zone',
                       't': 'time_in',
                       'hc': 'time_out'}, inplace=True)

    if (toDate == False):
        df['time_in'] = pd.to_datetime(df['time_in']).apply(lambda x: x.date())
        df['time_out'] = pd.to_datetime(df['time_out']).apply(lambda x: x.date())

    df['from_url'] = df['from_url'].apply(cleanUrl)

    df['to_url'] = df['to_url'].apply(cleanUrl)
    df = df[['web_browser', 'operating_sys', 'from_url', 'to_url',
             'city', "longitude", "latitude", 'time_zone', 'time_in', 'time_out']]
    #     df.drop(['a', 'al','c','gr','g','h','hh','nk','l','ll'], axis=1, inplace=True)
    return df


checksums = {}
duplicates = []

parser = argparse.ArgumentParser()

parser.add_argument("dir", help="Enter Directory path")

parser.add_argument("-u", action="store_true", dest="timeStamp", default=False,
                    help="If you want to keep timestamp as it is")

args = parser.parse_args()

checksums, duplicates, flag = getChecksumsAndDuplicates(args.dir)

if (flag == False):
    print("this Directory doesn't exit!")
else:
    Path("target").mkdir(parents=True, exist_ok=True)

    removeFiles(duplicates)
    records = None
    for file in checksums.values():
        records = [json.loads(line) for line in open(file)]
        df = json_normalize(records)
        df = cleanFile(df, args.timeStamp).dropna()
        filePath = 'target/' + file[:-5] + '.csv'
        df.to_csv(filePath)
        print(f'file path is {filePath} num of rows is {df.shape[0]} ')
        os.rename(file, file[:-5] + '_complete' + '.json')

print("Duplicates files is :", duplicates)
print("Total execution time is %s seconds " % (time.time() - start_time))