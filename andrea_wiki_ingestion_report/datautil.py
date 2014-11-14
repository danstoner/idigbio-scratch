import codecs
import csv
import json
import os
import re
import time
import urllib
import urllib2
import xml.etree.ElementTree as ET
import zipfile

# Get number of records in a CSV
def getRowCount(fn, headerLines=1):
    fc = open(fn, "r")
    filenameOnly, fileExtension = os.path.splitext(fn)
    # Try to get data at least n times (in case the server is loaded and returning 504 - timeout)
    tries = 5
    for i in range(0,tries):
        try:
            if fileExtension == '.csv':
                readerc = csv.reader((x.replace('\0', '') for x in fc), dialect=csv.excel)
            elif fileExtension == '.tsv' or fileExtension == '.txt':
                x = fc.next()
                if x.startswith('\xff\xfe'):
                    fc = open(fn, "r")
                    sr = codecs.StreamRecoder(fc,codecs.getencoder('utf-8'),codecs.getdecoder('utf-8'),codecs.getreader('utf-16'),codecs.getwriter('utf-16'))
                    readerc = csv.reader(sr, dialect='excel-tab',quoting=csv.QUOTE_NONE)
                    headerLines = 0
                else:
                    readerc = csv.reader((x.replace('\0', '') for x in fc), dialect='excel-tab',quoting=csv.QUOTE_NONE)
                    headerLines = 0
            count = sum(1 for row in readerc if (len(row[0]) > 0))
        except csv.Error, e:
            print fn, "csv Error:", e, fn
            if i == tries:
                count = headerLines
            continue
        break
    fc.close()
    return count - headerLines

# Wgets the content of the URL, loads the content as JSON and times both operations
def wgetLoadJsonTime(url, tw, tl):
    start = time.time()
    # Try to get data at least n times (in case the server is loaded and returning 504 - timeout)
    tries = 5
    data = []
    for i in range(0,tries):
        try:
            data = urllib2.urlopen(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, url, "Retrying in", (i + 1), "seconds"
            time.sleep(i + 1)
            continue
        except urllib2.URLError, e:
            print "URL Error:", e.reason, url
            continue
        break
    tw.append(time.time() - start)
    start = time.time()
    if data:
        j = json.load(data)
    tl.append(time.time() - start)
    return j

# Wgets the content of the URL, loads the content as JSON and times both operations
def wgetLoadRssTime(url, tw=[], tl=[]):
    start = time.time()
    # Try to get data at least n times (in case the server is loaded and returning 504 - timeout)
    tries = 5
    data = []
    root = []
    for i in range(0,tries):
        try:
            data = urllib2.urlopen(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, url
            continue
        except urllib2.URLError, e:
            print "URL Error:", e.reason, url
            continue
        break
    tw.append(time.time() - start)
    start = time.time()
    if data:
        root = ET.fromstring(data.read())
    tl.append(time.time() - start)
    return root

# Wgets the content of the URL saving the content to a local file, and opens it
# to get number of records from the file, timing both operations
def wgetLoadFileTime(url, outFolder, tw, tl, headerLines=1):
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
    start = time.time()
    gotFile = False
    # Try to get data at least n times (in case the server is loaded and returning 304)
    tries = 5
    print url
    for i in range(0,tries):
        try:
            filename = os.path.basename(url)
            if filename.startswith("archive.do"):
                filename = filename.split("=")[1] + ".zip"
            if filename.startswith("idigbio?"):
                filename = "invertnet.csv"
            if not os.path.isfile(os.path.join(outFolder, filename)):
                fh = urllib2.urlopen(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
                # Open our local file for writing
                with open(os.path.join(outFolder, filename), "wb") as datafile:
                    datafile.write(fh.read())
            gotFile = True
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, url
            continue
        except urllib2.URLError, e:
            print "URL Error:", e.reason, url
            continue
        break
    tw.append(time.time() - start)
    start = time.time()
    filenameOnly, fileExtension = os.path.splitext(filename)
    counts = []
    if gotFile:
        if fileExtension == '.zip':
            targetData = [["occurrence.txt", "occurrences.csv", "occurrence.csv"],
                          ["multimedia.txt", "images.csv", "occurrence_images.txt", "occurrence_recordings.txt", "image.txt"],
                          ["identifications.csv"], ["resourcerelationship.txt"]]
            zf = zipfile.ZipFile(os.path.join(outFolder, filename), "r")
            for altTargets in targetData:
                recordCount = 0
                for myfile in zf.namelist():
                    if myfile.startswith('\\'):
                        filenameOnly = myfile[1:]
                    else:
                        filenameOnly = os.path.basename(myfile)
                    print myfile, os.path.basename(myfile)
                    if filenameOnly in altTargets:
                        if myfile.startswith('\\'):
                            fd = open(os.path.join(outFolder,"data.txt"),"w")
                            fd.write(zf.read(myfile))
                            fd.close()
                            recordCount = recordCount + getRowCount(os.path.join(outFolder, "data.txt"))
                        else:
                            zf.extract(myfile, outFolder)
                            if myfile.startswith('/'):
                                myfile = myfile.replace('/','')
                            recordCount = recordCount + getRowCount(os.path.join(outFolder, myfile))
                counts.append(str(recordCount))
            zf.close()
            print filename, counts
        elif fileExtension == '.csv' or fileExtension == '.tsv':
            recordCount = getRowCount(os.path.join(outFolder, filename), headerLines)
            counts.append(str(recordCount))
            counts.append("0")
            counts.append("0")
            counts.append("0")
    else:
        counts = ["Fail", "Fail", "Fail", "Fail"]
    tl.append(time.time() - start)
    return counts

# Given a URL to a DwC-A, retrieves some important characteristics about it
# the number of records, the type of record and a sample GUID for the occurrence
# The downloaded file is stored in a predefined folder
def wgetSourceDwcaStats(dwcaUrl, tw=[], tl=[]):
    outFolder = "gbif"
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
    start = time.time()
    gotFile = False
    # Try to get data at least n times (in case the server is loaded and returning 304)
    tries = 5
    for i in range(0,tries):
        try:
            filename = os.path.basename(dwcaUrl)
            if filename.startswith("archive.do"):
                filename = filename.split("=")[1] + ".zip"
            if filename.startswith("idigbio?"):
                filename = "invertnet.csv"
            if not os.path.isfile(os.path.join(outFolder, filename)):
                fh = urllib2.urlopen(urllib.quote(dwcaUrl, safe="%/:=&?~#+!$,;'@()*[]"))
                # Open our local file for writing
                with open(os.path.join(outFolder, filename), "wb") as datafile:
                    datafile.write(fh.read())
            gotFile = True
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, dwcaUrl
            continue
        except urllib2.URLError, e:
            print "URL Error:", e.reason, dwcaUrl
            continue
        break
    tw.append(time.time() - start)
    start = time.time()
    filenameOnly, fileExtension = os.path.splitext(filename)
    if gotFile:
        if fileExtension == '.zip':
            zf = zipfile.ZipFile(os.path.join(outFolder, filename), "r")
            for myfile in zf.namelist():
                if "meta.xml" in myfile:
                    fd = open(os.path.join(outFolder,"data.txt"), "w")
                    fd.write(zf.read(myfile))
                    fd.close()
                    coreType, coreFile, delimiter, quoteChar, headerLines, idCol, basisCol, occCol = readMetaStats(os.path.join(outFolder,"data.txt"))
                    break
            for myfile in zf.namelist():
                if coreFile in myfile:
                    fd = open(os.path.join(outFolder,"data.txt"), "w")
                    fd.write(zf.read(myfile))
                    fd.close()
                    count, uniqCount, basisOfRecord, sampleGuid = readCoreStats(os.path.join(outFolder,"data.txt"), delimiter, quoteChar, headerLines, idCol, basisCol, occCol)
                    return [count, uniqCount, basisOfRecord, sampleGuid]
            zf.close()
    return [0, 0, "URL Error" if not gotFile else "", ""]

def readMetaStats(metaFile):
    root = ET.parse(metaFile).getroot()
    coreType = ''
    coreFile = ''
    idCol = -1
    basisCol = -1
    occCol = -1
    for c in root:
        if c.tag.endswith("core"):
            coreType = c.attrib["rowType"].split("/")[-1]
            delimiter = c.attrib["fieldsTerminatedBy"]
            quoteChar = c.attrib["fieldsEnclosedBy"]
            headerLines = int(c.attrib["ignoreHeaderLines"])
            for f in c:
                if f.tag.endswith("files"):
                    coreFile = f[0].text
                if f.tag.endswith("id"):
                    idCol = int(f.attrib.get("index"))
                if f.tag.endswith("field") and f.attrib.get("term").endswith("basisOfRecord"):
                    if f.attrib.get("index"):
                        basisCol = int(f.attrib.get("index"))
                    if f.attrib.get("default"):
                        basisCol = f.attrib.get("default")
                if f.tag.endswith("field") and f.attrib.get("term").endswith("occurrenceID"):
                    occCol = int(f.attrib.get("index"))
    return coreType, coreFile, delimiter, quoteChar, headerLines, idCol, basisCol, occCol

def readCoreStats(coreFile, delimiter, quoteChar, headerLines, idCol, basisCol, occCol):
    fc = open(coreFile, "r")
    x = fc.next()
    fc = open(coreFile, "r")
    if "\\t" == delimiter:
        if 0 == len(quoteChar):
            if x.startswith('\xff\xfe'):
                sr = codecs.StreamRecoder(fc,codecs.getencoder('utf-8'),codecs.getdecoder('utf-8'),codecs.getreader('utf-16'),codecs.getwriter('utf-16'))
                readerc = csv.reader(sr, dialect='excel-tab',quoting=csv.QUOTE_NONE)
            else:
                readerc = csv.reader((x.replace('\0', '') for x in fc), dialect='excel-tab', quoting=csv.QUOTE_NONE)
        else:
            readerc = csv.reader((x.replace('\0', '') for x in fc), dialect='excel-tab', quotechar=quoteChar)
    else:
        if 0 == len(quoteChar):
            readerc = csv.reader((x.replace('\0', '') for x in fc), delimiter=delimiter, quoting=csv.QUOTE_NONE)
        else:
            readerc = csv.reader((x.replace('\0', '') for x in fc), delimiter=delimiter, quotechar=quoteChar)
    for i in range(0, headerLines):
        readerc.next()
    row = readerc.next()
    count = 1
    uniqIds = {}
    basisOfRecord = ''
    if type(basisCol) == str:
        basisOfRecord = basisCol
    elif -1 < basisCol:
        basisOfRecord = row[basisCol]
    sampleGuid = "NOID"
    selectedIdCol = -1
    if -1 < idCol and 0 < len(row[idCol]):
        sampleGuid = row[idCol]
        uniqIds[row[idCol]] = ""
        selectedIdCol = idCol
    elif -1 < occCol and 0 < len(row[occCol]):
        sampleGuid = row[occCol]
        uniqIds[row[occCol]] = ""
        selectedIdCol = occCol
    for row in readerc:
        if -1 < selectedIdCol:
            if row[selectedIdCol] not in uniqIds:
                uniqIds[row[selectedIdCol]] = ""
        count = count + 1
    fc.close()
    return count, len(uniqIds), basisOfRecord, sampleGuid

# Given a dataset URL, extracts the best code for the dataset
def getCode(datafile):
    code = ""
    m = re.search('/([^/]+)_DwC-A.zip$', datafile)
    if m:
        code = m.group(1)
    else:
        m = re.search('/([^/]+).zip$', datafile)
        if m:
            code = m.group(1)
        else:
            m = re.search('=([^=]+)$', datafile)
            if m:
                code = m.group(1)
            else:
                m = re.search('/([^/]+)\.[ct]sv$', datafile)
                if m:
                    code = m.group(1)
                    if code == "285a4be0-5cfe-4d4f-9c8b-b0f0f3571079":
                        code = "nybg_app"
                    if code == "252a0a12-f114-4fb5-aa9a-678c523d6dcd":
                        code = "flmnh_inv_app"
    return code

# Given a publisher name, extracts the best short name for the publisher
def getPublisherShortName(publisher):
    shortName = ""
    m = re.search('.*(SCAN|Intermountain|KU|iDigBio|SEINet|SNOMNH|Morphbank|Macroalgal) .+$', publisher)
    if m:
        shortName = m.group(1)
    else:
        if "Ohio State" in publisher:
            shortName = "OSU"
        elif "Bryophyte" in publisher:
            shortName = "LBCC-B"
        elif "CNALH" in publisher:
            shortName = "LBCC-L"
        elif "Florida Museum" in publisher:
            shortName = "FLMNH"
        elif "MyCoPortal" in publisher:
            shortName = "MaCC"
        elif "Comparative Zoology" in publisher:
            shortName = "MCZ"
        elif "University of Connecticut" in publisher:
            shortName = "UCONN"
        elif "CAS-IPT" in publisher:
            shortName = "CalAcademy"
        elif "VertNet" in publisher:
            shortName = "VertNet"
        elif "Harvard University Herbaria" in publisher:
            shortName = "Harvard"
        elif "Museum of Comparative Zoology" in publisher:
            shortName = "MCZ"
        elif "Small Herbaria" in publisher:
            shortName = "NANSH"
        elif "CNH " in publisher:
            shortName = "CNH"
        elif "Northern Great Plains Herbaria " in publisher:
            shortName = "NGP"
        elif "Berkeley" in publisher:
            shortName = "Berkeley"
        elif "sprout018" in publisher:
            shortName = "Yale"
        elif "Oregon State" in publisher:
            shortName = "Oregon"
        elif "thomasmore" in publisher:
            shortName = "CMC"
        elif "bio.fsu" in publisher:
            shortName = "FSU"
        else:
            shortName = "unknown"
    return shortName
    
# Given a list of potential recordsets, find the one that matches a particular
# dataset by URL, and get statistics on the number of records in the system
def findPubRecords(recordsets, datafile, tw, tl):
    for item in recordsets:
        print "Published:", item
        rec = wgetLoadJsonTime(item, tw, tl)
        counts = []
        # Try to match the recordset through dataset URL
        if rec['idigbio:data']['link'] == datafile:
            print item
            if rec['idigbio:links'].get('record', None):
                if len(rec['idigbio:links']['record']) == 1 and \
                    rec['idigbio:links']['record'][0].endswith("records"):
                    recs = wgetLoadJsonTime(rec['idigbio:links']['record'][0], tw, tl)
                    print "Getcount:", rec['idigbio:links']['record'][0], recs['idigbio:itemCount']
                    counts.append(recs['idigbio:itemCount'])
                else:
                    counts.append(len(rec['idigbio:links']['record']))
                    print "ExistingCount:",rec['idigbio:links']['record']
            else:
                counts.append("0")
            if rec['idigbio:links'].get('mediarecord', None):
                if len(rec['idigbio:links']['mediarecord']) == 1 and \
                    rec['idigbio:links']['mediarecord'][0].endswith("records"):
                    print rec['idigbio:links']['mediarecord'][0]
                    recs = wgetLoadJsonTime(rec['idigbio:links']['mediarecord'][0], tw, tl)
                    counts.append(recs['idigbio:itemCount'])
                else:
                    counts.append(len(rec['idigbio:links']['mediarecord']))
            else:
                counts.append("0")
            recordsets.remove(item)
            return counts, os.path.basename(item)
    return ["0","0"], ""

# From a recordset, get the corresponding dataset by URL, and get statistics
# on the number of records in the system
def findPubRecordsAndDatafile(recordset, datafile, tw, tl):
    rec = wgetLoadJsonTime(recordset, tw, tl)
    counts = []
    # Ensure recordset is for the expected datafile
    if rec['idigbio:data']['link'] == datafile:
        if rec['idigbio:links'].get('record', None):
            if len(rec['idigbio:links']['record']) == 1 and \
                rec['idigbio:links']['record'][0].endswith("records"):
                recs = wgetLoadJsonTime(rec['idigbio:links']['record'][0], tw, tl)
                print "Getcount:", rec['idigbio:links']['record'][0], recs['idigbio:itemCount']
                counts.append(recs['idigbio:itemCount'])
            else:
                counts.append(len(rec['idigbio:links']['record']))
                print "ExistingCount:",rec['idigbio:links']['record']
        else:
            counts.append("0")
        if rec['idigbio:links'].get('mediarecord', None):
            if len(rec['idigbio:links']['mediarecord']) == 1 and \
                rec['idigbio:links']['mediarecord'][0].endswith("records"):
                print rec['idigbio:links']['mediarecord'][0]
                recs = wgetLoadJsonTime(rec['idigbio:links']['mediarecord'][0], tw, tl)
                counts.append(recs['idigbio:itemCount'])
            else:
                counts.append(len(rec['idigbio:links']['mediarecord']))
        else:
            counts.append("0")
        return counts, os.path.basename(recordset)
    return ["0","0"], ""

def findDatafileRssByGuid(rss, guid):
    if not rss:
        return None
    channels = rss.findall('channel')
    for channel in channels:
        for item in channel.findall('item'):
            rssGuid = item.findtext('guid')
            print "GUID in RSS:", rssGuid
            if rssGuid:
                rssGuid = os.path.dirname(rssGuid)
            else:
                rssGuid = item.findtext('id')
            if rssGuid == guid:
                datafile = item.findtext('{http://ipt.gbif.org/}dwca')
                if datafile == None:
                    datafile = item.findtext('link')
                print "Found RSS:", guid, "with link:", datafile
                channel.remove(item)
                return datafile
    # Fallback to match Symbiota guids based only on collection id (or more recently only on UUID)
    for channel in channels:
        for item in channel.findall('item'):
            for guidItem in item.findall('guid'):
                print "Symbiota GUID in RSS:", guidItem.text
                rssGuid = guidItem.text
                if rssGuid:
                    rssGuid = os.path.basename(rssGuid)
                    if rssGuid == os.path.basename(guid):
                        datafile = item.findtext('link')
                        print "Found RSS:", guid, "with link:", datafile
                        channel.remove(item)
                        return datafile
    print "Could not find RSS:", guid
    return None

def getDatafileGuidInRss(rss):
    data = []
    if rss:
        channels = rss.findall('channel')
        for channel in channels:
            for item in channel.findall('item'):
                rssGuids = item.findall('guid')
                rssGuid = None
                for guid in rssGuids:
                    print guid.text
                    m = re.search('([0-9a-h]{8}-[0-9a-h]{4}-[0-9a-h]{4}-[0-9a-h]{4}-[0-9a-h]{12}).*$', guid.text)
                    if m:
                        rssGuid = m.group(1)
                        break
                if rssGuid is None:
                    rssGuid = item.findtext('id')
                datafile = item.findtext('{http://ipt.gbif.org/}dwca')
                if datafile == None:
                    datafile = item.findtext('link')
                data.append([rssGuid, datafile])
    return data

def removeFromRecordsets(recordsets, datafile):
    for item in recordsets:
        rec = wgetLoadJsonTime(item, [], [])
        # Try to match the recordset through dataset URL
        if rec['idigbio:data']['link'] == datafile:
            recordsets.remove(item)

def getIDigBioIngestedDwcas(pubFile):
    csvPubFile = open(pubFile, 'rb')
    csvPubFileReader = csv.reader(csvPubFile, dialect='excel')

    # Read the header line
    header = csvPubFileReader.next()
    ingestedCol = header.index("ingest")
    dwcaCol = header.index("IdbDataFile")
    indexedCol = header.index("Specimens Indexed")
    dwcas = []
    count = []
    for row in csvPubFileReader:
        if row[ingestedCol] == "TRUE":
            dwcas.append(row[dwcaCol])
            count.append(row[indexedCol])
    return dwcas, count