"""
Using the iDigBio python client library, fetch 10 records matching the 
scientific name 'Puma concolor' and print the verbatim locality field.
"""

import idigbio

query = {"scientificname":"puma concolor"}

api = idigbio.json()

record_list = api.search_records(rq=query,limit=10)

for item in record_list["items"]:
      for key in item["indexTerms"]:
          if key == "verbatimlocality":
              print item["indexTerms"]["verbatimlocality"]



