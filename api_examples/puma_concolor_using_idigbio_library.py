import idigbio

query_as_string = '{"rq":{"scientificname":"puma concolor"}}'

api = idigbio.json()

record_list = api.search_records(query_as_string)

for item in record_list["items"]:
      for key in item["indexTerms"]:
          if key == "verbatimlocality":
              print item["indexTerms"]["verbatimlocality"]


