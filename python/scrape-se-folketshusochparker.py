#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
#import time
import random
import yaml
import json
import uuid

from parsel import Selector

#import glob

#DATAROOT = './yaml/'
#MASTER_DATAFILE = './yaml/master.yaml'

SOURCE_URL = 'https://www.folketshusochparker.se/wp-content/themes/fhp/inc/ajax.php'
DEST_YAML = '../yaml/layers/folketshusochparker.yaml'

NAMESPACE = 'folketshusochparker'

def writeYAML(filepath, contents):
  s = yaml.safe_dump(
    contents,
    indent=2,
    width=1000,
    canonical=False,
    sort_keys=False,
    explicit_start=False,
    default_flow_style=False,
    default_style='',
    allow_unicode=True,
    line_break='\n'
  )
  with open(filepath, "w") as f:
    #f.write(s)
    f.write(s.replace('\n- ', '\n\n- '))

def loadJSON(filepath):
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
    result = json.loads(file_contents)

  return result

def cleanerHTML(data):
  
  # Remove Windows style CRLF
  data = re.sub(r"\r\n", " ", str(data), flags=re.IGNORECASE)
  
  # Remove Mac style CR
  data = re.sub(r"\r", " ", str(data), flags=re.IGNORECASE)

  # Remove Unix style LF
  data = re.sub(r"\n", " ", str(data), flags=re.IGNORECASE)

  # Remove Tab
  data = re.sub(r"\t", " ", str(data), flags=re.IGNORECASE)

  # Remove empty space between elements
  data = re.sub(r"\x3e\s{1,}\x3c", "><", str(data), flags=re.IGNORECASE)

  # class="card-content"
  data = re.sub(r"\sclass\x3d\x22card\x2dcontent\x22", "", str(data), flags=re.IGNORECASE)
  
  # class="card-title"
  data = re.sub(r"\sclass\x3d\x22card\x2dtitle\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-body--link"
  data = re.sub(r"\sclass\x3d\x22card\x2dbody\x2d\x2dlink\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-body--link card-body--link-term h7"
  data = re.sub(r"\sclass\x3d\x22card\x2dbody\x2d\x2dlink\scard\x2dbody\x2d\x2dlink\x2dterm\sh7\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-body"
  data = re.sub(r"\sclass\x3d\x22card\x2dbody\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-meta--border"
  data = re.sub(r"\sclass\x3d\x22card\x2dmeta\x2d\x2dborder\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-meta--inner"
  data = re.sub(r"\sclass\x3d\x22card\x2dmeta\x2d\x2dinner\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-meta"
  data = re.sub(r"\sclass\x3d\x22card\x2dmeta\x22", "", str(data), flags=re.IGNORECASE)

  # class="card-inner"
  data = re.sub(r"\sclass\x3d\x22card\x2dinner\x22", "", str(data), flags=re.IGNORECASE)

  # class="col-xs-12 card expandable" / class="col-xs-12 card"
  data = re.sub(r"\sclass\x3d\x22col\x2dxs\x2d12\scard(\sexpandable)?\x22", "", str(data), flags=re.IGNORECASE)

  # <span></span>
  data = re.sub(r"\x3cspan\x3e\x3c\x2fspan\x3e", "", str(data), flags=re.IGNORECASE)

  # <div></div>
  data = re.sub(r"\x3cdiv\x3e\x3c\x2fdiv\x3e", "", str(data), flags=re.IGNORECASE)

  # Trims
  data = re.sub(r"\x3e\s{1,}", ">", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\s{1,}\x3c", "<", str(data), flags=re.IGNORECASE)

  return data

def generateUUIDFromName(namespace, name):
  return uuid.uuid5(namespace, name)


def extractData(data):
  obj = {
    'location': None,
    'urn': None,
    'city': None,
    'county': None,
    'country': None,
    'latitude': None,
    'longitude': None,
  }
  sel = Selector(text=data)

  # Location Name
  obj['location'] = sel.xpath('//h3/text()').extract_first()

  # City Name and County
  temp = sel.xpath('//div[1]/text()').extract_first()
  if temp != None:
    temp = str(temp).title()
    #print(temp)
    if re.search(r"\x2c\s", str(temp)):
      elements = re.split(r"\x2c\s", temp, flags=re.IGNORECASE)
      if elements[0] != None and elements[1] !=  None:
        obj['city'] = elements[0]
        obj['county'] = elements[1]
    else:
      if temp != None:
        obj['city'] = temp
        obj['county'] = temp

  # Country Name
  obj['country'] = 'Sverige'

  # Latitude
  temp = sel.xpath('//article/@data-lat').extract_first()
  if temp != None and temp != '':
    obj['latitude'] = float(temp)

  # Longitude
  temp = sel.xpath('//article/@data-lng').extract_first()
  if temp != None and temp != '':
    obj['longitude'] = float(temp)

  #print(sel.xpath('//article/@data-lng').extract_first())

  #print(obj)
  return obj


def main():
  data = loadJSON('../import/json/folketshusochparker-se-wp-content-themes-fhp-inc-ajax-php.json')

  struct = {
    'meta': {
      'name': 'Folkets Hus och Parker',
      'web': 'https://www.folketshusochparker.se/',
      'wikipedia': None,
      'category': 'Folkets Hus och Parker',
      'locations': None,
    },
    'locations': None
  }

  struct["locations"] = []

  if "success" in data:
    data_success = data["success"]
    print(f"success: {data_success}")

    if "data" in data:
      if "results" in data["data"]:
        results = data["data"]["results"]
        for res in results:
          res_clean = cleanerHTML(res)
          #print(res_clean)
          res_extr = extractData(res_clean)
          print(res_extr)
          print()

          struct["locations"].append(res_extr)


  print(struct)
  struct['meta']['locations'] = len(struct['locations'])

  writeYAML(DEST_YAML, struct)


if __name__ == '__main__':
  main()
