import argparse
#import idigbio
import json
import requests

# rewrite to talk to ES directly

parser = argparse.ArgumentParser(description='Read list of values from file and search for records matching in specified field.')
parser.add_argument('-i', '--inputfile', dest='inputfile', required=True, help="Input file must be one value per line.")
parser.add_argument('-f', '--field', dest='field', default='scientificname', help="The specified field must be an iDigbio indexed term.")
parser.add_argument('--header-row', dest='header_row', default=False, action='store_true', help="Use this option if the first line of the input file is a header row.")
parser.add_argument('--stop-count', dest='stopcount', type=int, help="Stop reading inputfile after this many rows. Default: 10")
args = parser.parse_args()


inputfile = args.inputfile
field = args.field
header_needs_skipped = args.header_row
if args.stopcount:
# may have issues if stopcount > 7000
    stopcount=args.stopcount
else:
    stopcount = 10

inputset = set()

count = 0

with open(inputfile, 'r') as f:
    for line in f:
        if header_needs_skipped:
            header_needs_skipped = False
        else:
            inputset.add(line.strip())
            count += 1
        if count >= stopcount:
            break

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


answer = dict()
fields = ["uuid", "genus", "specificepithet", "geopoint", "country", "stateprovince", "county", "municipality"]

query = { "filter" : {
        "terms" : {
        "genus" : []
}}}

#query = {}
#values = list()
#place = 0


for each in inputset:
    query["filter"]["terms"]["genus"].append(each.lower())

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
        print answer[id]
#    print hit


raise SystemExit

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

api = idigbio.json()

#record_list = api.search_records(rq={"genus":["abelia","abelmoschus"]})
record_list = api.search_records(rq=query)

## output specification:
# Genus, specific epithet, lat, long, locality (all fields so that I could
# have country, state, county, etc. so that we can check the lat/long
# against the field)

#print record_list["itemCount"]


raise SystemExit

for item in record_list["items"]:
    for key in item["indexTerms"]:
        if key == "genus":
            print item["indexTerms"][key]
