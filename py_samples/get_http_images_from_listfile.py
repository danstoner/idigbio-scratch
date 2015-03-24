try:
    import os
    import time
    import argparse
    import requests
    import logging
    import urllib
    import hashlib
    import io
#    import cStringIO
    import StringIO
    from PIL import Image
    from bs4 import BeautifulSoup
except ImportError, e:
    print "IMPORT ERROR: %s" % e
    raise SystemExit

outdir = os.getcwd()+"/"  # default output to current directory

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
    # make sure path has trailing backslash
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

seen_count = 0;
success_count = 0;
fail_count = 0;

for item in soup.find_all(img_wrap_tag):
    seen_count += 1
    logging.info("Fetching: " + item[hyper_ref])
    try:
        request = requests.get(item[hyper_ref])
    except:
        logging.error ("Could not GET url: " + item[hyper_ref])
        fail_count += 1
        continue
    imgbuf = StringIO.StringIO(request.content)
    try:
        myimage = Image.open(imgbuf)   # only using pillow to determine if we really have an image
    except Exception, e:
        logging.error ("Does not look like image: " + item[hyper_ref] + " **Exception: " + str(e))
        fail_count += 1
        continue
    myhash = hashlib.md5()   # We will compute an md5 sum on the buffer to get a unique filename
    imgbuf.seek(0)
    myhash.update(imgbuf.read())
    fulloutfilepath = outdir + myhash.hexdigest() + "." + myimage.format.lower()
    if not os.path.exists(fulloutfilepath):   # skip files that already exist
        with open(fulloutfilepath, 'wb') as outputfile:
            imgbuf.seek(0)
            outputfile.write(imgbuf.read())
            success_count += 1
    else:
        logging.warning("File already exists: " + fulloutfilepath)
        success_count += 1   # file exists will count as "success"

print "------------------------------------------"
print "File output dir: ", outdir
print "------------------------------------------"
print "COUNTS"
print "Seen: ", seen_count
print "Success: ", success_count
print "Fail: ", fail_count
print "------------------------------------------"
