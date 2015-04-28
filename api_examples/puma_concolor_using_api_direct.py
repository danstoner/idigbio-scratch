import requests
import json

query_as_string = '{"rq":{"scientificname":"puma concolor"}}'

r = requests.post('http://beta-search.idigbio.org/v2/search/records/',data=query_as_string, headers={'content-type': 'application/json'})

response = r.json()

for item in response["items"]:
     for key in item["indexTerms"]:
         if key == "verbatimlocality":
             print item["indexTerms"]["verbatimlocality"]

