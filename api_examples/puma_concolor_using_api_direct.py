import requests
import json

query_as_string = '{"rq":{"scientificname":"puma concolor"}}'

query_json = json.loads(query_as_string)

r = requests.post('http://beta-search.idigbio.org/v2/search/records/',data=json.dumps(query_json), headers={'content-type': 'application/json'})

response = r.json()

for item in response["items"]:
# not all items will have all fields
     for key in item["indexTerms"]:
         if key == "verbatimlocality":
             print item["indexTerms"]["verbatimlocality"]

