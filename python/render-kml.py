#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random
import yaml

import glob

DATAROOT = './yaml/'
MASTER_DATAFILE = './yaml/master.yaml'

DESTROOT = './export/kml/'

def writeFile(contents, filepath):
  with open(filepath, "w") as f:
    f.write(contents)

def loadYAML(filepath):
  result = None
  file_contents = None
  if os.path.isfile(filepath):
    fp = None
    try:
      fp = open(filepath)
      file_contents = fp.read()
      fp.close()

    finally:
      pass

  if file_contents != None:
    result = yaml.safe_load(file_contents)

  return result


def renderKML(data):
  elems = []

  # Declare XML
  elems.append('<?xml version="1.0" encoding="UTF-8"?>')

  # Open root KML element
  elems.append('<kml xmlns="http://www.opengis.net/kml/2.2">')

  elems.append('  <Document>')

  # Declare name
  elems.append(f"    <name><![CDATA[{data['meta']['name']}]]></name>")
  
  # Declare empty description
  elems.append(f"    <description/>")

  elems.append(f"    <Style id=\"icon-22-normal\"><IconStyle><scale>1.1</scale><Icon><href>https://www.gstatic.com/mapspro/images/stock/22-blue-dot.png</href></Icon><hotSpot x=\"16\" xunits=\"pixels\" y=\"32\" yunits=\"insetPixels\"/></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>")

  elems.append(f"    <Style id=\"icon-22-highlight\"><IconStyle><scale>1.1</scale><Icon><href>https://www.gstatic.com/mapspro/images/stock/22-blue-dot.png</href></Icon><hotSpot x=\"16\" xunits=\"pixels\" y=\"32\" yunits=\"insetPixels\"/></IconStyle><LabelStyle><scale>1.1</scale></LabelStyle></Style>")

  elems.append(f"    <StyleMap id=\"icon-22\"><Pair><key>normal</key><styleUrl>#icon-22-normal</styleUrl></Pair><Pair><key>highlight</key><styleUrl>#icon-22-highlight</styleUrl></Pair></StyleMap>")

  # Delcare Folder
  elems.append(f"    <Folder>")

  elems.append(f"      <name><![CDATA[{data['meta']['name']}]]></name>")

  for loc in data['locations']:
    elems.append('      <Placemark>')
    
    elems.append(f"        <name><![CDATA[{loc['location']}]]></name>")

    if "country" in loc:
      elems.append(f"        <description><![CDATA[{loc['location']}, {loc['city']}, {loc['country']}]]></description>")
    else:
      elems.append(f"        <description><![CDATA[{loc['location']}, {loc['city']}]]></description>")

    elems.append(f"        <Point><coordinates>{loc['longitude']},{loc['latitude']},0</coordinates></Point>")
    elems.append(f"        <styleUrl>#icon-22</styleUrl>")

    elems.append('      </Placemark>')

  elems.append(f"    </Folder>")
  elems.append(f"  </Document>")

  # Close root KML element
  elems.append('</kml>')

  return "\n".join(elems)



def main():
  masterlist = loadYAML(MASTER_DATAFILE)

  for file in masterlist['files']:
    print(f"Processing {file} ..")

    filename = f"{DATAROOT}{file}"
    data = loadYAML(filename)
    
    kml = renderKML(data)

    filename = file
    filename = re.sub(r"^(.*)\x2f", "", str(filename), flags=re.IGNORECASE)
    filename = re.sub(r"\x2eyaml", ".kml", str(filename), flags=re.IGNORECASE)
    kmlfile = f"{DESTROOT}{filename}"

    writeFile(kml, kmlfile)
    print(f".. wrote {kmlfile}")

if __name__ == '__main__':
  main()
