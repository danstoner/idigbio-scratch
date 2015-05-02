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
except ImportError, e:
    print "IMPORT ERROR: %s" % e
    raise SystemExit

## output specification:
# Genus, specific epithet, lat, long, locality (all fields so that I could
# have country, state, county, etc. so that we can check the lat/long
# against the field)

parser = argparse.ArgumentParser(description='Read list of values from file and search for records matching in specified field.')
parser.add_argument('-i', '--inputfile', dest='inputfile', required=True, help="Input file must be one value per line.")
parser.add_argument('-o', '--outputfile', dest='outputfile', required=True, help="Output filename for results (something.csv).")
parser.add_argument('-f', '--field', dest='field', default='scientificname', help="The specified field must be an iDigbio indexed term.")
parser.add_argument('--header-row', dest='header_row', default=False, action='store_true', help="Use this option if the first line of the input file is a header row.")
parser.add_argument('--stop-count', dest='stopcount', type=int, help="Stop reading inputfile after this many rows. Default: 10")
args = parser.parse_args()


inputfile = args.inputfile
outputfile = args.outputfile
searchfield = args.field
header_needs_skipped = args.header_row
if args.stopcount:
# may have issues if stopcount > 7000
    stopcount=args.stopcount
else:
    stopcount = 10

# These are output fields, same as the fields we pull out of the search results
fields = ["uuid", "genus", "specificepithet", "geopoint", "country", "stateprovince", "county", "municipality"]

# If we cannot open output file for write, might as well stop now.
with open(outputfile,"w") as f:
    writer = csv.writer(f)
    writer.writerow(fields)



# inputset will hold the lines we actually want to work on
inputset = set()
# zerorecordset will hold the lines that don't have any matching records
zerorecordsset = set()

count = 0

def getmatchingcount(apiobj,thingtocount):  
    num = api.count_records(rq={searchfield: thingtocount})
    return num

api = idigbio.json()

with open(inputfile, 'r') as f:
    for line in f:
        if header_needs_skipped:
            header_needs_skipped = False
        else:
            if getmatchingcount(api,line.strip()) > 0:
                inputset.add(line.strip())
            else:
                zerorecordsset.add(line.strip())
            count += 1
        if count >= stopcount:
            break

# print zerorecordsset

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



 
# answer will hold the items that have geopoint
answer = dict()
# answer_nogeopoint will hold the items that were thrown out because they lack geopoint
answer_nogeopoint = dict()



query = { "filter" : {
        "terms" : {
        searchfield : []
}}}

#query = {}
#values = list()
#place = 0


for each in inputset:
    query["filter"]["terms"][searchfield].append(each.lower())

print query
query_json = json.dumps(query)

r = requests.post('http://search.idigbio.org/idigbio/records/_search/?size=1000000',data=query_json, headers={'content-type': 'application/json'})

response_json = r.json()

#### response structure ####
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

answer = dict()


## need to move set popping here and consider querying for each row
for hit in response_json["hits"]["hits"]:
    if "uuid" in hit["_source"]:
        id = hit["_source"]["uuid"]
        answer[id]=[]
        for field in fields:
            # have to add checking since each field might not exist in data
            if field in hit["_source"]:
                answer[id].append(hit["_source"][field])
            else:
                answer[id].append("")
#        print answer[id]
#    print hit



print "Number of records for output: ", len(answer)
# write the data to csv     
with open(outputfile,"a") as f:
    writer = csv.writer(f)
    for a in answer:
        writer.writerow(answer[a])

raise SystemExit


### __END__

while len(inputset) > 0:
    while (place < 100) and len(inputset) > 0:
        value = inputset.pop()
        values.append(value.lower().strip())
        place += 1
        query = { field : values}
        query_as_string = json.dumps( { field : values })
#        print query
        print query_as_string
#    record_list = 
#    answer.append(api.search_records(rq=query))
    r = requests.post('http://beta-search.idigbio.org/v2/search/records/',data=query_as_string, headers={'content-type': 'application/json'})
    response_json = r.json()
    for item in response_json["items"]:
        item_uuid = item["indexTerms"]["uuid"]
        answer[item_uuid]=[]
        for key in fields:
            if key in item["indexTerms"]:
                answer[item_uuid].append[item["indexTerms"][key]]
        print type(answer[item_uuid])
                
    #print query
#    print answer
    values=list()
    place = 0
    break

#print answer

#query_as_string = '{"query" : "rq":{"scientificname":"puma concolor"},"limit":10},"email":"dstoner"}'
#q_json = json.dumps(query_as_string)

#r = requests.post('http://csv.idigbio.org/', data=json.loads(q_json), headers={'content-type': 'application/json'})
#print r.text

#r = requests.post('http://search.idigbio.org/idigbio/records/_search', data=json.loads(q_json), headers={'content-type': 'application/json'})



raise SystemExit


# for item in record_list["items"]:
#     for key in item["indexTerms"]:
#         if key == "genus":
#             print item["indexTerms"][key]
