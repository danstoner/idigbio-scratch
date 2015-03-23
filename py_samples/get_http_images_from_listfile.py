try:
    import os
    import time
    import argparse
    import requests
    import logging
    import urllib
    from PIL import Image
    from bs4 import BeautifulSoup
except ImportError, e:
    print "IMPORT ERROR: %s" % e
    raise SystemExit

outdir = os.getcwd()+"/"  # default to current directory

argparser = argparse.ArgumentParser(description='Script to download a list of images from an html or pseudo-html file.')
argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug level logging.")
argparser.add_argument("-o", "--outdir", help="The full path to an existing directory where the downloaded image files will be placed. Default: current directory")
argparser.add_argument("-a", "--anchors", action="store_true", help="Image urls are wrapped in <a> tags (anchors) instead of <img> tags. For example, the links are to redirectors or cloud storage urls rather than to final target image urls.")
argparser.add_argument('infile', help="The name of the input file containing the list of image urls.")

args = argparser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Debug enabled.")
else:
    logging.basicConfig(level=logging.INFO)

if args.outdir:
    # make sure path has trialing backslash
    outdir = args.outdir.rstrip('/')+'/'

logging.info("Output Directory (outdir): " + outdir)

infile = args.infile
logging.info("Input file (infile): "+infile)

tmpfilename = outdir + "safe_to_delete." + str(time.time()) + ".tmp"

try:
    # can we write to the specified output directory?
    t = open(tmpfilename,'w')
    t.write('0123456789abcdefg')
    t.close()
    os.remove(tmpfilename)
except:
    logging.error("Output directory is not writable or does not exist: " + outdir)
    argparser.print_help()
    raise SystemExit;
    
try:
    f = open(infile, 'r')
except:
    logging.error("Could not open input file (infile): " + infile)
    argparser.print_help()
    raise SystemExit;

soup = BeautifulSoup(f)

if args.anchors:
    img_wrap_tag = 'a'
    hyper_ref = 'href'
else:
    img_wrap_tag = 'img'
    hyper_ref = 'src'


# Consider doing something here to keep track of succeeds and failures


#s = requests.session()

for item in soup.find_all(img_wrap_tag):
    logging.info("Fetching: " + item[hyper_ref])
    try:
        fetchresult, msg = urllib.urlretrieve(item[hyper_ref])
    except:
        logging.error ("Could not GET url: " + r.url)
        break
    myimage=Image.open(fetchresult)
    streng = outdir + "outputfile." + myimage.format
#    myimage.save(outdir+"outputfile."+myimage.format)
    myimage.save(streng)

