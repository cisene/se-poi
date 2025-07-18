#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random
import yaml

import glob

from datetime import datetime, timezone

DATAROOT = './yaml/'
MASTER_DATAFILE = './yaml/master.yaml'

DESTROOT = './export/gpx/'

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

def isoDate():
  dt = datetime.now(timezone.utc)
  tz_dt = dt.astimezone()
  iso_date = str(tz_dt.isoformat())

  # remove fraction of seconds - not useful
  iso_date = re.sub(r"\x2e\d{6}\x2b", "+", str(iso_date), flags=re.IGNORECASE)
  return iso_date

def findBounds(data):
  result = {
    'minlat': None,
    'maxlat': None,
    'minlon': None,
    'maxlon': None,
  }

  for loc in data:
    lat = loc['latitude']
    lon = loc['longitude']

    # Set initial value from lat
    if result['minlat'] == None:
      result['minlat'] = lat

    # Set initial value from lat
    if result['maxlat'] == None:
      result['maxlat'] = lat

    # Set initial value from lon
    if result['minlon'] == None:
      result['minlon'] = lon

    # Set initial value from lon
    if result['maxlon'] == None:
      result['maxlon'] = lon

    # Adjust value if lat is less than previous value
    if lat < result['minlat']:
      result['minlat'] = lat

    # Adjust value if lat is greater than previous value
    if lat > result['maxlat']:
      result['maxlat'] = lat

    # Adjust value if lon is less than previous value
    if lon < result['minlon']:
      result['minlon'] = lon

    # Adjust value if lon is greater than previouos value
    if lon > result['maxlon']:
      result['maxlon'] = lon

  return result

def renderGPX(data):
  elems = []

  # Find bounds in dataset
  bounds = findBounds(data['locations'])

  # Get current date and time
  now = isoDate()

  elems.append('<?xml version="1.0" encoding="UTF-8"?>')

  elems.append('<!-- Source: https://github.com/cisene/se-poi -->')

  # Open root GPX element
  elems.append('<gpx creator="se-poi" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1">')

  # Declare metadata element
  elems.append('  <metadata>')

  # Declare metadata name element
  elems.append(f"    <name><![CDATA[{data['meta']['name']}]]></name>")

  # Declare metadata desc(ription) element
  elems.append(f"    <desc><![CDATA[Koordinater - {data['meta']['name']}]]></desc>")
  
  # Declare metadata link element
  elems.append(f"    <link href=\"{data['meta']['web']}\">")
  
  # Declare metadata link text element
  elems.append(f"      <text><![CDATA[{data['meta']['name']}]]></text>")

  # Declare metadata link type (as in MIME-type)
  elems.append('       <type>text/html</type>')

  # Close metadata link element
  elems.append('    </link>')

  # Timestamp with current date and time
  elems.append(f"   <time>{now}</time>")

  # Close metadata element
  elems.append('  </metadata>')

  # Timestamp with current date and time
  #elems.append(f"<time>{now}</time>")

  # Declare element bounds with attributes of Latitude min/max and Longitude min/max
  elems.append(f"  <bounds minlat=\"{bounds['minlat']}\" minlon=\"{bounds['minlon']}\" maxlat=\"{bounds['maxlat']}\" maxlon=\"{bounds['maxlon']}\" />")

  for loc in data['locations']:
    # Declare wps in a more compact format
    elems.append(f"  <wpt lat=\"{loc['latitude']}\" lon=\"{loc['longitude']}\"><name><![CDATA[{loc['location']}, {loc['city']}]]></name></wpt>")

  # Close root GPX element
  elems.append('</gpx>')

  return "\n".join(elems)



def main():
  inventory = {}
  category_list = {}
  masterlist = loadYAML(MASTER_DATAFILE)

  for file in masterlist['files']:
    print(f"Processing {file} ..")

    filename = f"{DATAROOT}{file}"
    data = loadYAML(filename)
    
    gpx = renderGPX(data)

    filename = file
    filename = re.sub(r"^(.*)\x2f", "", str(filename), flags=re.IGNORECASE)
    filename = re.sub(r"\x2eyaml", ".gpx", str(filename), flags=re.IGNORECASE)
    #print(filename)
    gpxfile = f"{DESTROOT}{filename}"


    writeFile(gpx, gpxfile)
    print(f".. wrote {gpxfile}")

if __name__ == '__main__':
  main()
