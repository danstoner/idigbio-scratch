import argparse
import idigbio

parser = argparse.ArgumentParser(description='Read list of values from file and search for records matching in specified field.')
parser.add_argument('-i', '--inputfile', dest='inputfile', required=True, help="Input file must be one value per line.")
parser.add_argument('-f', '--field', dest='field', default='scientificname', help="The specified field must be an iDigbio indexed term.")
parser.add_argument('--header-row', dest='header_row', default=False, action='store_true', help="Use this option if the first line of the input file is a header row.")
parser.add_argument('--stop-count', dest='stopcount', type=int, help="Stop reading inputfile after this many rows. Default: 10")
args = parser.parse_args()


inputfile = args.inputfile
field = args.field
header_row = args.header_row
if args.stopcount:
    stopcount=args.stopcount
else:
    stopcount = 10

inputset = set()
header_needs_skipped = True

count = 0

with open(inputfile, 'r') as f:
    for line in f:
        if header_needs_skipped and header_row:
            header_needs_skipped = False
        else:
            inputset.add(line)
            count += 1
        if count >= stopcount:
            break


query = {}
values = list()

for value in inputset:
    values.append(value.lower().strip())

query = { field : values}

print query

api = idigbio.json()
#record_list = api.search_records(rq={"genus":["abelia","abelmoschus"]})
#record_list = api.search_records(rq={field:[values]})
record_list = api.search_records(rq=query)

for item in record_list["items"]:
    for key in item["indexTerms"]:
        if key == "genus":
            print item["indexTerms"][key]
