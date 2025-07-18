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

def isoDate():
  dt = datetime.now(timezone.utc)
  tz_dt = dt.astimezone()
  iso_date = str(tz_dt.isoformat())

  # remove fraction of seconds - not useful
  iso_date = re.sub(r"\x2e\d{6}\x2b", "+", str(iso_date), flags=re.IGNORECASE)
  return iso_date












def renderKML(data):
  elems = []

  if data == None:
    print("data empty")
    exit(0)
    return
  
  if "meta" in data:
    if data['meta'] == None:
      return

  ns = {
    None: "http://www.opengis.net/kml/2.2",
  }

  # Open root KML element
  kml = etree.Element("kml", nsmap = ns)

  comment = etree.Comment(" Source: https://github.com/cisene/se-poi ")
  kml.append(comment)

  document = etree.Element("Document")

  # Declare name
  document_name = etree.Element("name")
  document_name.text = data['meta']['name']
  document.append(document_name)

  # Declare empty description
  document_description = etree.Element("description")
  document.append(document_description)

  document_style = etree.Element("Style")
  document_style.set("id", "icon-22-normal")
  document_style_iconstyle = etree.Element("IconStyle")
  document_style_iconstyle_scale = etree.Element("scale")
  document_style_iconstyle_scale.text = "1.1"
  document_style_iconstyle_icon = etree.Element("Icon")
  document_style_iconstyle_icon_href = etree.Element("href")
  document_style_iconstyle_icon_href.text = "https://www.gstatic.com/mapspro/images/stock/22-blue-dot.png"
  document_style_iconstyle_icon.append(document_style_iconstyle_icon_href)
  document_style_iconstyle.append(document_style_iconstyle_icon)
  document_style_iconstyle_hotspot = etree.Element("hotSpot")
  document_style_iconstyle_hotspot.set("x", "16")
  document_style_iconstyle_hotspot.set("xunits", "pixels")
  document_style_iconstyle_hotspot.set("y", "32")
  document_style_iconstyle_hotspot.set("yunits", "insetPixels")
  document_style_iconstyle.append(document_style_iconstyle_hotspot)
  document_style_iconstyle.append(document_style_iconstyle_scale)
  document_style.append(document_style_iconstyle)
  document_style_labelstyle = etree.Element("LabelStyle")
  document_style_labelstyle_scale = etree.Element("scale")
  document_style_labelstyle_scale.text = "1"
  document_style_labelstyle.append(document_style_labelstyle_scale)
  document_style.append(document_style_labelstyle)
  document.append(document_style)

  document_style = etree.Element("Style")
  document_style.set("id", "icon-22-highlight")
  document_style_iconstyle = etree.Element("IconStyle")
  document_style_iconstyle_scale = etree.Element("scale")
  document_style_iconstyle_scale.text = "1.1"
  document_style_iconstyle.append(document_style_iconstyle_scale)
  document_style_iconstyle_icon = etree.Element("Icon")
  document_style_iconstyle_icon_href = etree.Element("href")
  document_style_iconstyle_icon_href.text = "https://www.gstatic.com/mapspro/images/stock/22-blue-dot.png"
  document_style_iconstyle_icon.append(document_style_iconstyle_icon_href)
  document_style_iconstyle.append(document_style_iconstyle_icon)
  document_style_iconstyle_hotspot = etree.Element("hotSpot")
  document_style_iconstyle_hotspot.set("x", "16")
  document_style_iconstyle_hotspot.set("xunits", "pixels")
  document_style_iconstyle_hotspot.set("y", "32")
  document_style_iconstyle_hotspot.set("yunits", "insetPixels")
  document_style_iconstyle.append(document_style_iconstyle_hotspot)

  document_style.append(document_style_iconstyle)

  document_style_labelstyle = etree.Element("LabelStyle")
  document_style_labelstyle_scale = etree.Element("scale")
  document_style_labelstyle_scale.text = "1"
  document_style_labelstyle.append(document_style_labelstyle_scale)
  document_style.append(document_style_labelstyle)

  document.append(document_style)

  document_stylemap = etree.Element("StyleMap")
  document_stylemap_pair = etree.Element("Pair")
  document_stylemap_pair_key = etree.Element("key")
  document_stylemap_pair_key.text = "normal"
  document_stylemap_pair.append(document_stylemap_pair_key)
  document_stylemap_pair_styleurl = etree.Element("styleUrl")
  document_stylemap_pair_styleurl.text = "#icon-22-normal"
  document_stylemap.append(document_stylemap_pair)
  document_stylemap_pair = etree.Element("Pair")
  document_stylemap_pair_key = etree.Element("key")
  document_stylemap_pair_key.text = "highlight"
  document_stylemap_pair.append(document_stylemap_pair_key)
  document_stylemap_pair_styleurl = etree.Element("styleUrl")
  document_stylemap_pair_styleurl.text = "#icon-22-highlight"
  document_stylemap.append(document_stylemap_pair)
  document.append(document_stylemap)

  # Delcare Folder
  document_folder = etree.Element("Folder")

  document_folder_name = etree.Element("name")
  document_folder_name.text = str(data['meta']['name'])
  document_folder.append(document_folder_name)

  for loc in data['locations']:
    document_folder_placemark = etree.Element("Placemark")
    
    document_folder_placemark_name = etree.Element("name")
    document_folder_placemark_name.text = str(loc['location'])
    document_folder_placemark.append(document_folder_placemark_name)

    document_folder_placemark_description = etree.Element("description")
    location_list = [loc['location']]
    
    if "city" in loc:
      if loc['city'] != None:
        location_list.append(loc['city'])

    if "country" in loc:
      if loc['country'] != None:
        location_list.append(loc['country'])

    location_text = ", ".join(location_list)

    document_folder_placemark_description.text = location_text
    document_folder_placemark.append(document_folder_placemark_description)

    document_folder_placemark_point = etree.Element("Point")
    document_folder_placemark_point_coordinates = etree.Element("coordinates")
    document_folder_placemark_point_coordinates.text = f"{loc['longitude']},{loc['latitude']},0"
    document_folder_placemark_point.append(document_folder_placemark_point_coordinates)
    document_folder_placemark.append(document_folder_placemark_point)

    document_folder_placemark_styleurl = etree.Element("styleUrl")
    document_folder_placemark_styleurl.text = "#icon-22"
    document_folder_placemark.append(document_folder_placemark_styleurl)

    document_folder.append(document_folder_placemark)

  document.append(document_folder)

  kml.append(document)

  kml_contents = etree.tostring(kml, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode()

  return kml_contents



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
