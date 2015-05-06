"""
This script uses a hybrid of iDigBio search api and direct Elasticsearch queries.

Generates a CSV for a query that uses a large number of distinct input values on a single field (e.g. 16k genera)
"""
try:
    import argparse
    import idigbio
    import json
    import requests
    import csv
    import cStringIO
    import codecs
    import copy
except ImportError, e:
    print "IMPORT ERROR: %s" % e
    raise SystemExit

## output specification:
# Genus, specific epithet, lat, long, locality (all fields so that I could
# have country, state, county, etc. so that we can check the lat/long
# against the field)

parser = argparse.ArgumentParser(description='Read list of values from file and search for records matching in specified field, output as CSV.')
parser.add_argument('-i', '--inputfile', dest='inputfile', required=True, help="Input file must be one value per line.")
parser.add_argument('-o', '--outputfile', dest='outputfile', required=True, help="Output filename for results (something.csv).")
parser.add_argument('-f', '--field', dest='field', default='scientificname', help="The specified field must be an iDigbio indexed term.")
parser.add_argument('--header-row', dest='header_row', default=False, action='store_true', help="Use this option if the first line of the input file is a header row.")
parser.add_argument('--stop-count', dest='stopcount', type=int, help="Stop reading inputfile after this many rows. Default: 10")
parser.add_argument('--only-count', dest='onlycount', default=False, action='store_true', help="Aborts after gathering counts and building the working sets.")

args = parser.parse_args()


inputfile = args.inputfile
outputfile = args.outputfile
searchfield = args.field
header_needs_skipped = args.header_row
only_do_counts = args.onlycount

if args.stopcount:
# may have issues if stopcount > 7000
    stopcount=args.stopcount
else:
    stopcount = 10

# These are the fields we pull out of the search results. geopoint is special since it includes "lon" and "lat"
fields = ["uuid", "genus", "specificepithet", "scientificname", "geopoint", "country", "stateprovince", "county", "municipality"]
outputheaderrow = ["uuid", "genus", "specificepithet", "scientificname", "lon", "lat", "country", "stateprovince", "county", "municipality"]

# UnicodeWriter class taken straight out of python docs
# https://docs.python.org/2.7/library/csv.html#examples
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# If we cannot open output file for write, might as well stop now.
with open(outputfile,"w") as f:
    writer = UnicodeWriter(f,quoting=csv.QUOTE_ALL)
    writer.writerow(outputheaderrow)


# inputset will hold the lines we actually want to work on
inputset = set()
smallinputset = set()
# zerorecordset will hold the lines that don't have any matching records
zerorecordsset = set()


def getmatchingcount(apiobj,thingtocount):  
    num = api.count_records(rq={searchfield: thingtocount})
    return num

count = 0
api = idigbio.json()

print "Reading input file, getting counts for each value..."

with open(inputfile, 'r') as f:
    for line in f:
        stripped = line.strip()
        la_record_count = getmatchingcount(api,stripped)
        if header_needs_skipped:
            header_needs_skipped = False
        else:
            if la_record_count > 5:
                inputset.add(stripped)
            elif la_record_count == 0:
                zerorecordsset.add(stripped)
            else:
                smallinputset.add(stripped)
            count += 1
            if count % 100 == 0:
                print 'input row:', count
        if count >= stopcount:
            break

print "Number of values that did not match any records in iDigBio (zerorecordsset): ", len(zerorecordsset)
print "Number of values with small number of matches (smallinputset): ", len(smallinputset)
print "Number of values with more than a small number of matches (inputset):", len(inputset)

print "Writing zerorecordsset to last_zerorecordsset.csv..."
# write to a file the list of values that did not match any records in iDigBio
with open("last_zerorecordsset.csv", "w") as f:
    for b in zerorecordsset:
        f.write(b+"\n")

print "Writing smallinputset to last_smallinputset.csv..."
with open("last_smallinputset.csv", "w") as f:
    for c in smallinputset:
        f.write(c+"\n")

print "Writing inputset to last_inputset.csv..."
with open("last_inputset.csv", "w") as f:
    for c in inputset:
        f.write(c+"\n")

print ""

if only_do_counts:
    raise SystemExit

 

### big loop, search 1 record at a time

answer = dict()
querycount = 0
print "Begin iterating searches on ", len(inputset)+len(smallinputset), "values."


basequery = {
      "query" : {
      "filtered" : {
         "query" : {
            "match_all" : {}
         },
         "filter" : {
            "and" : [
               {
                  "exists" : {
                     "field" : "geopoint"
                  }
               },
               {
                  "terms" : {
                     searchfield : []
                  }
               }
            ]
         }
      }
   },
   "_source" : {
      "include" : fields
   }
}

#################################### BIG WORK #######################
## smallinputset get lumped into single query, inputset will run one by one
for each in inputset:
    query=copy.deepcopy(basequery)
    query["query"]["filtered"]["filter"]["and"][1]["terms"][searchfield].append(each.lower())
    query_json = json.dumps(query)
    querycount += 1
    if querycount % 500 == 0:
        print 'Queries (inputset):', querycount
    try:
        r = requests.post('http://search.idigbio.org/idigbio/records/_search/?size=1000000',data=query_json, headers={'content-type': 'application/json'})
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print "error on:", each
        print e
        continue

    response_json = r.json()
    for hit in response_json["hits"]["hits"]:
        if "uuid" in hit["_source"]:
            id = hit["_source"]["uuid"]
            answer[id]=[]
            for field in fields:
                # have to add checking since each field might not exist in data
                if field == "geopoint":
                    if field in hit["_source"]:
                        answer[id].append(str(hit["_source"][field]["lon"]))
                        answer[id].append(str(hit["_source"][field]["lat"]))
                    else:
                        answer[id].append("")
                        answer[id].append("")
                else:
                    if field in hit["_source"]:
                        answer[id].append(hit["_source"][field])
                    else:
                        answer[id].append("")
    #        print answer[id]
    #    print hit


query=copy.deepcopy(basequery)
querycount = 0
for each in smallinputset:
    query["query"]["filtered"]["filter"]["and"][1]["terms"][searchfield].append(each.lower())
    querycount += 1
    if querycount % 500 == 0:
        print 'Values added to query terms:', querycount

query_json = json.dumps(query)

try:
    r = requests.post('http://search.idigbio.org/idigbio/records/_search/?size=1000000',data=query_json, headers={'content-type': 'application/json'})
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print "Error on query:"
    print query
    print "####"
    print e

response_json = r.json()
for hit in response_json["hits"]["hits"]:
    if "uuid" in hit["_source"]:
        id = hit["_source"]["uuid"]
        answer[id]=[]
        for field in fields:
            # have to add checking since each field might not exist in data
            if field == "geopoint":
                if field in hit["_source"]:
                    answer[id].append(str(hit["_source"][field]["lon"]))
                    answer[id].append(str(hit["_source"][field]["lat"]))
                else:
                    answer[id].append("")
                    answer[id].append("")
            else:
                if field in hit["_source"]:
                    answer[id].append(hit["_source"][field])
                else:
                    answer[id].append("")




print "Number of records for CSV output: ", len(answer)
# write the data to csv     
keys = answer.keys()

with open(outputfile,"a") as f:
    writer = UnicodeWriter(f,quoting=csv.QUOTE_ALL)
    for a in keys:
        try:
            writer.writerow(answer[a])
        except Exception as e:
            print e
            print "Row = ", answer[a]



raise SystemExit
## END ##

##### sample json query with a few entries
# {
#    "filter" : {
#       "terms" : {
#          "genus" : [
#             "acanthus",
#             "aechmanthera"
#          ]
#       }
#    }
# }

##### sample json query with a few genus entries AND exists
# {
#    "query" : {
#       "filtered" : {
#          "query" : {
#             "match_all" : {}
#          },
#          "filter" : {
#             "and" : [
#                {
#                   "exists" : {
#                      "field" : "geopoint"
#                   }
#                },
#                {
#                   "terms" : {
#                      "genus" : [
#                         "acanthus",
#                         "aechmanthera",
#                         "acanthura",
#                         "afrofittonia",
#                         "acanthopale",
#                         "acanthopsis",
#                         "ancistranthus",
#                         "ambongia",
#                         "adhatoda",
#                         "achyrocalyx"
#                      ]
#                   }
#                }
#             ]
#          }
#       }
#    }
# }


#### sample iDigBio Elasticsearch response structure ####
# {
#    "hits" : {
#       "hits" : [
#          {
#             "_source" : {
#                "geopoint" : {
#                   "lon" : -121.80862,
#                   "lat" : 39.744167
#                "county" : "butte",
# 	       ...
