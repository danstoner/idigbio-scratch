#!/usr/bin/env python
import datautil

source = "https://invertnet.org/idigbio?task=download&format=raw"
outFolder = "520dcbb3-f35a-424c-8778-6df11afc9f95"
tw = []
tl = []
counts = datautil.wgetLoadFileTime(source, outFolder, tw, tl, headerLines=1)
print counts

source = "http://imperialis.inhs.illinois.edu/dmitriev/insects.zip"
outFolder = "520dcbb3-f35a-424c-8778-6df11afc9f95"
counts = datautil.wgetLoadFileTime(source, outFolder, tw, tl, headerLines=1)
print counts
