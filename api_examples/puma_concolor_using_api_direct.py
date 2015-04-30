"""
Using the iDigBio API directly, fetch 10 records matching the
scientific name 'Puma concolor' and print the verbatim locality field.
"""

import requests

query_as_string = '{"rq":{"scientificname":"puma concolor"},"limit":10}'

r = requests.post('http://beta-search.idigbio.org/v2/search/records/',data=query_as_string, headers={'content-type': 'application/json'})

response_json = r.json()

for item in response_json["items"]:
     for key in item["indexTerms"]:
          if key == "verbatimlocality":
               print item["indexTerms"]["verbatimlocality"]


