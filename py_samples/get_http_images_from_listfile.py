try:
    import argparse
    import requests
    import logging
    from bs4 import BeautifulSoup
except ImportError, e:
    print "IMPORT ERROR: %s" % e
    raise SystemExit

argparser = argparse.ArgumentParser(description='Script to download a list of images from an html or pseudo-html file.')
argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug level logging.")
argparser.add_argument("infile", help="The name of the input file containing the list of image urls.")

args = argparser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

infile = args.infile

try:
    f = open('infile', 'r')
except:
    logging.error("Could not open file: " + infile)
