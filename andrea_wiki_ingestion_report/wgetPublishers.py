#!/usr/bin/env python
# Outputs all dataset iDigBio GUIDs, the source URL (when available), and
# count into a local CSV file
import csv
import datautil

f = open('publishers.csv','wb')
fw = csv.writer(f, dialect='excel')
ft = open('timingsPublishers.csv','w')
h = ["PublisherGUID", "PublisherVersion", "PublisherDateModified", "PublisherName",
     "PublisherType", "ingest", "SrcDataFile", "IdbDataFile", "Publisher", "Code", "RecordsetGUID",
     "Specimens Provided", "Media Provided", "Identifications Provided",
     "Relationships Provided", "Specimens Ingested", "Media Ingested",
     "Specimens Indexed", "Media Indexed", "Remaining RecordSets"]
fw.writerow(h)
f.flush()
tw = [] # Wget timings
tl = [] # Load data timings

# Get all publishers
j = datautil.wgetLoadJsonTime('http://api.idigbio.org/v1/publishers', tw, tl)

for item in j['idigbio:items']:
    print item['idigbio:links']['publisher']
    # Get one particular publisher
    j2 = datautil.wgetLoadJsonTime(item['idigbio:links']['publisher'], tw, tl)
    if j2['idigbio:data']['name']:
        pubShortName = datautil.getPublisherShortName(j2['idigbio:data']['name'])
    else:
        pubShortName = datautil.getPublisherShortName(j2['idigbio:data']['base_url'])
    # Get current RSS feed for this publisher
    rss = datautil.wgetLoadRssTime(j2['idigbio:data']['rss_url'], tw, tl)
    r = [item['idigbio:uuid'], item['idigbio:version'], item['idigbio:dateModified'],
        j2['idigbio:data']['name'], j2['idigbio:data']['publisher_type']]
    # Get all recordsets of this publisher, if it is a link to the list of recordsets.
    # Otherwise make a copy of the recordset list.
    recordsets = []
    if j2['idigbio:links'].get('recordset', None):
        if len(j2['idigbio:links']['recordset']) == 1 and \
            j2['idigbio:links']['recordset'][0].endswith("recordsets"):
            j3 = datautil.wgetLoadJsonTime(j2['idigbio:links']['recordset'][0], tw, tl)
            for item3 in j3['idigbio:items']:
                recordsets.append(item3['idigbio:links']['recordset'])
        else:
            recordsets = j2['idigbio:links']['recordset']
    # For each recordset of the publisher
    for key2, item2 in j2['idigbio:data']['recordsets'].iteritems():
        # Find the previously published dataset in the current RSS
        currDatafile = datautil.findDatafileRssByGuid(rss, key2)
        datafile = item2['link'].encode('ascii','ignore')
        print currDatafile == datafile, currDatafile, key2
        if currDatafile is None:
            code = datautil.getCode(datafile)
            numRec = ['0', '0', '0', '0']
            status = "UNPUBLISHED"
        else:
            code = datautil.getCode(currDatafile)
            numRec = datautil.wgetLoadFileTime(currDatafile, item['idigbio:uuid'], tw, tl)
            status = item2['ingest']
        ingested = ['0', '0']
        indexed = ['0', '0']
        if j2['idigbio:links'].get('recordset', None):
            if len(recordsets) > 0:
                ingested, recset = datautil.findPubRecords(recordsets, datafile, tw, tl)
                if datafile.endswith(".csv") or datafile.endswith(".tsv"):
                    if int(ingested[0]) == 0 and int(ingested[1]) > 0:
                        numRec[1] = numRec[0]
                        numRec[0] = 0
                if recset:
                    indj = datautil.wgetLoadJsonTime('http://search.idigbio.org/idigbio/records/_search?q=recordset:' + recset, tw, tl)
                    indj2 = datautil.wgetLoadJsonTime('http://search.idigbio.org/idigbio/mediarecords/_search?q=recordset:' + recset, tw, tl)
                    indexed = [indj["hits"]["total"], indj2["hits"]["total"]]
        print r + [status, currDatafile, datafile, pubShortName, code, recset] + numRec + ingested + indexed + [len(recordsets)]
        fw.writerow(r + [status, currDatafile, datafile, pubShortName, code, recset] + numRec + ingested + indexed + [len(recordsets)])
        f.flush()
    # Look all recordsets not in publishers
    for recordset in recordsets:
        j3 = datautil.wgetLoadJsonTime(recordset, tw, tl)
        datafile = j3['idigbio:data']['link']
        # Find the previously published dataset in the current RSS
        if j3['idigbio:data'].get('id', None):
            currDatafile = datautil.findDatafileRssByGuid(rss, j3['idigbio:data']['id'])
        else:
            currDatafile = datautil.findDatafileRssByGuid(rss, j3['idigbio:recordIds'][0])
        if currDatafile is None:
            code = datautil.getCode(datafile)
            numRec = ['0', '0', '0', '0']
            status = "UNPUBLISHED"
        else:
            code = datautil.getCode(currDatafile)
            numRec = datautil.wgetLoadFileTime(currDatafile, item['idigbio:uuid'], tw, tl)
            status = "NOTINPUBLISHERS"
        ingested, recset = datautil.findPubRecordsAndDatafile(recordset, datafile, tw, tl)
        if datafile.endswith(".csv") or datafile.endswith(".tsv"):
            if int(ingested[0]) == 0 and int(ingested[1]) > 0:
                numRec[1] = numRec[0]
                numRec[0] = 0
        indj = datautil.wgetLoadJsonTime('http://search.idigbio.org/idigbio/records/_search?q=recordset:' + recset, tw, tl)
        indj2 = datautil.wgetLoadJsonTime('http://search.idigbio.org/idigbio/mediarecords/_search?q=recordset:' + recset, tw, tl)
        indexed = [indj["hits"]["total"], indj2["hits"]["total"]]
        print r + [status, currDatafile, datafile, pubShortName, code, recset] + numRec + ingested + indexed + [len(recordsets)]
        fw.writerow(r + [status, currDatafile, datafile, pubShortName, code, recset] + numRec + ingested + indexed + [len(recordsets)])
        f.flush()
    # Find all remaining new datasets for this publisher
    newData = datautil.getDatafileGuidInRss(rss)
    for dataset in newData:
        print "===New:", dataset[0], dataset[1]
        code = datautil.getCode(dataset[1])
        numRec = datautil.wgetLoadFileTime(dataset[1], item['idigbio:uuid'], tw, tl)
        print r + ["NEW", '', dataset[1], pubShortName, code, dataset[0]] + numRec + ['0', '0'] + ['0', '0'] + [len(recordsets)]
        fw.writerow(r + ["NEW", '', dataset[1], pubShortName, code, dataset[0]] + numRec + ['0', '0'] + ['0', '0'] + [len(recordsets)])
        f.flush()
        

sw = sum(tw)
sl = sum(tl)
print "Wget total: " + str(sw) + "s #: " + str(len(tw)) + " Avg: " + str(sw / len(tw))
print "Load total: " + str(sl) + "s #: " + str(len(tl)) + " Avg: " + str(sl / len(tl))
for item1, item2 in zip(tw, tl):
    ft.write(str(item1) + ',' + str(item2) + '\n')
f.close()
ft.close()

