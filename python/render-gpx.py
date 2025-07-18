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
#import xml.etree.ElementTree as ET
from lxml import etree

DATAROOT = '../yaml/'
MASTER_DATAFILE = '../yaml/master.yaml'

DESTROOT = '../export/gpx/'

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

  min_lat = str(bounds['minlat'])
  min_lon = str(bounds['minlon'])
  max_lat = str(bounds['maxlat'])
  max_lon = str(bounds['maxlon'])

  # Get current date and time
  now = isoDate()

  #elems.append('<?xml version="1.0" encoding="UTF-8"?>')

  ns = {
    None: "http://www.topografix.com/GPX/1/1",
    #"xsi": "http://www.w3.org/2001/XMLSchema-instance",
    #"xsi:schemaLocation": "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd",
    #"xsd": "http://www.topografix.com/GPX/1/1/gpx.xsd"
  }

  # Open GPX
  gpx = etree.Element("gpx", nsmap = ns)
  gpx.set("creator", "se-poi")
  gpx.set("version", "1.1")


  comment = etree.Comment(" Source: https://github.com/cisene/se-poi ")
  gpx.append(comment)

  # Declare metadata element
  metadata = etree.Element("metadata")

  # Declare metadata name element
  metadata_name = etree.Element("name")
  metadata_name.text = str(data['meta']['name'])
  metadata.append(metadata_name)

  # Declare metadata desc(ription) element
  metadata_desc = etree.Element("desc")
  metadata_desc.text = f"Koordinater - {data['meta']['name']}"
  metadata.append(metadata_desc)

  # Declare metadata link element
  metadata_link = etree.Element("link")
  metadata_link.set("href", str(data['meta']['web']))
  metadata.append(metadata_link)

  # Declare metadata link text element
  metadata_text = etree.Element("text")
  metadata_text.text = str(data['meta']['name'])

  # Declare metadata link type (as in MIME-type)
  metadata_link_type = etree.Element("type")
  metadata_link_type.text = "text/html"
  metadata_link.append(metadata_link_type)

  # Close metadata link element
  metadata.append(metadata_text)

  # Timestamp with current date and time
  metadata_time = etree.Element("time")
  metadata_time.text = str(now)
  metadata.append(metadata_time)

  # Close metadata element
  gpx.append(metadata)

  # Declare element bounds with attributes of Latitude min/max and Longitude min/max
  bounds = etree.Element("bounds")
  bounds.set("minlat", f"{min_lat}")
  bounds.set("minlon", f"{min_lon}")
  bounds.set("maxlat", f"{max_lat}")
  bounds.set("maxlon", f"{max_lon}")
  gpx.append(bounds)

  for loc in data['locations']:
    # Declare wps in a more compact format
    #elems.append(f"  <wpt lat=\"{loc['latitude']}\" lon=\"{loc['longitude']}\"><name><![CDATA[{loc['location']}, {loc['city']}]]></name></wpt>")

    wpt = etree.Element("wpt")
    wpt.set("lat", str(loc['latitude']))
    wpt.set("lon", str(loc['longitude']))

    wpt_name = etree.Element("name")
    location_list = [loc['location']]
    
    if "city" in loc:
      if loc['city'] != None:
        location_list.append(loc['city'])

    if "country" in loc:
      if loc['country'] != None:
        location_list.append(loc['country'])

    location_text = ", ".join(location_list)
    wpt_name.text = str(location_text)

    wpt.append(wpt_name)

    gpx.append(wpt)

  # Close root GPX element
  #elems.append('</gpx>')

  gpx_contents = etree.tostring(gpx, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode()
  #print(gpx_contents)

  return gpx_contents

  #return "\n".join(elems)



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
    gpxfile = f"{DESTROOT}{filename}"


    writeFile(gpx, gpxfile)
    print(f".. wrote {gpxfile}")

if __name__ == '__main__':
  main()
