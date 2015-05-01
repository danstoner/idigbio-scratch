import argparse

parser = argparse.ArgumentParser(description='read list from file and search for records.')
parser.add_argument('-i', '--inputfile', dest='inputfile', required=True)
parser.add_argument('-f', '--field', dest='field', default='scientificname')
args = parser.parse_args()


print args.inputfile
print args.field
