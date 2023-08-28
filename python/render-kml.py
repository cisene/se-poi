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
  elems.append(f"    <name>{data['meta']['name']}</name>")
  
  # Declare empty description
  elems.append(f"    <description/>")

  # Declare static style icon-22-normal
  elems.append(f"    <Style id=\"icon-22-normal\">")
  elems.append(f"      <IconStyle>")
  elems.append(f"        <scale>1.1</scale>")
  elems.append(f"        <Icon>")
  elems.append(f"          <href>https://www.gstatic.com/mapspro/images/stock/22-blue-dot.png</href>")
  elems.append(f"        </Icon>")
  elems.append(f"        <hotSpot x=\"16\" xunits=\"pixels\" y=\"32\" yunits=\"insetPixels\"/>")
  elems.append(f"      </IconStyle>")
  elems.append(f"      <LabelStyle>")
  elems.append(f"        <scale>0</scale>")
  elems.append(f"      </LabelStyle>")
  elems.append(f"    </Style>")

  # Declare static style icon-22-highlight
  elems.append(f"    <Style id=\"icon-22-highlight\">")
  elems.append(f"      <IconStyle>")
  elems.append(f"        <scale>1.1</scale>")
  elems.append(f"        <Icon>")
  elems.append(f"          <href>https://www.gstatic.com/mapspro/images/stock/22-blue-dot.png</href>")
  elems.append(f"        </Icon>")
  elems.append(f"        <hotSpot x=\"16\" xunits=\"pixels\" y=\"32\" yunits=\"insetPixels\"/>")
  elems.append(f"      </IconStyle>")
  elems.append(f"      <LabelStyle>")
  elems.append(f"        <scale>1.1</scale>")
  elems.append(f"      </LabelStyle>")
  elems.append(f"    </Style>")

  # Declare static stylemap icon-22
  elems.append(f"    <StyleMap id=\"icon-22\">")
  elems.append(f"      <Pair>")
  elems.append(f"        <key>normal</key>")
  elems.append(f"        <styleUrl>#icon-22-normal</styleUrl>")
  elems.append(f"      </Pair>")
  elems.append(f"      <Pair>")
  elems.append(f"        <key>highlight</key>")
  elems.append(f"        <styleUrl>#icon-22-highlight</styleUrl>")
  elems.append(f"      </Pair>")
  elems.append(f"    </StyleMap>")

  elems.append(f"    <Folder>")

  elems.append(f"      <name><![CDATA[{data['meta']['name']}]]></name>")

  for loc in data['locations']:
    elems.append('      <Placemark>')
    
    elems.append(f"        <name><![CDATA[{loc['location']}]]></name>")

    if "country" in loc:
      elems.append(f"        <description>{loc['location']}, {loc['city']}, {loc['country']}</description>")
    else:
      elems.append(f"        <description>{loc['location']}, {loc['city']}</description>")

    elems.append(f"        <styleUrl>#icon-22</styleUrl>")

    elems.append(f"        <Point><coordinates>{loc['longitude']},{loc['latitude']},0</coordinates></Point>")

    elems.append('      </Placemark>')

  elems.append(f"    </Folder>")
  elems.append(f"  </Document>")

  # Close root GPX element
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
