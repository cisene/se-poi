#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random
import yaml
import json
import uuid
import requests



from bs4 import BeautifulSoup

SOURCE_URL = 'https://www.uttagsautomater.se/'
DEST_YAML = '../yaml/layers/uttagsautomater.yaml'

NAMESPACE = "uttagsautomater"

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
    f.write(s.replace('\n- ', '\n\n- '))

def generateUUIDFromName(namespace, name):
  return uuid.uuid5(namespace.encode("utf-8"), name)


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

def flatten(data):
  data = re.sub(r"\x26amp\x3b", "&", str(data), flags=re.IGNORECASE)

  data = re.sub(r"\t", " ", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\r", " ", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\n", " ", str(data), flags=re.IGNORECASE)
  return data

def fulltrim(data):
  data = re.sub(r"^\s{1,}", "", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\s{1,}$", "", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\s{2,}", " ", str(data), flags=re.IGNORECASE)
  return data


def lmarkerExtract(data):
  obj = {
    'location': None,
    'address': None,
    'city': None,
    'country': None,
    'urn:uttagsautomater:location:id': None,
    'latitude': None,
    'longitude': None
  }

  if data != None:
    pattern = re.sub(r"\x2c\s", ",", str(data), flags=re.IGNORECASE)
    pattern = re.sub(r"^L\x2emarker\x28\x5b(.+?)\x2c(.+?)\x5d\x29\x2eaddTo\x28map\x29\x2ebindPopup\x28\x27([a-z0-9\s\x26\x2c-\x2f]{1,})\x3cbr\s\x2f\x3e(.+?)\x27\x29", "\\1|\\2|\\3|\\4", str(pattern), flags=re.IGNORECASE)

    parts = re.split(r"\x7c", str(pattern), flags=re.IGNORECASE)
    if len(parts) == 4:
      if parts[0] != None:
        obj['latitude'] = float(parts[0])

      if parts[1] != None:
        obj['longitude'] = float(parts[1])

      if parts[2] != None:
        obj['location'] = str(parts[2])

      if parts[3] != None:
        obj['address'] = str(parts[3])

  return obj


def scrapeIndex(url):
  result = []
  print(f"Requesting '{url}' ...")
  res = requests.get(url)
  if int(res.status_code) == 200:
    soup = BeautifulSoup(str(res.text), 'html.parser')
    for o in soup.find_all('option'):
      if re.search(r"^\x3coption\svalue\x3d\x22(.+?)\x22\x3e(.+?)\x3c\x2foption\x3e$", str(o), flags=re.IGNORECASE):
        link = re.sub(r"^\x3coption\svalue\x3d\x22(.+?)\x22\x3e(.+?)\x3c\x2foption\x3e$", "\\1", str(o), flags=re.IGNORECASE)
        if link not in result:
          result.append(link)

  random.shuffle(result) # Shuffle to NOT go alphabetically
  print(f"\tFound {len(result)} links ...")
  return result

def scrapePage(url):
  result = []
  print(f"\tProcessing '{url}' ...")
  res = requests.get(url)
  if int(res.status_code) == 200:
    obj_count = 0
    soup = BeautifulSoup(str(res.text), 'html.parser')
    for s in soup.find_all('script'):

      s = fulltrim(flatten(s))

      for line in re.split(r"\x3b(\s)?", str(s)):
        if re.search(r"L\x2emarker\x28", str(line), flags=re.IGNORECASE):
          props = lmarkerExtract(line)

          obj = {
            'location': None,
            'address': None,
            'city': None,
            'country': 'Sverige',
            'urn:uttagsautomater:location:id': None,
            'latitude': None,
            'longitude': None
          }

          if props['location'] != None:
            obj['location'] = props['location']
          else:
            continue

          if props['address'] != None:
            obj['address'] = props['address']

          if props['latitude'] != None:
            obj['latitude'] = props['latitude']

          if props['longitude'] != None:
            obj['longitude'] = props['longitude']

          obj['city'] = re.sub(r"^https\x3a\x2f\x2fwww\x2euttagsautomater\x2ese\x2f(.+?)\x2f$", "\\1", str(url), flags=re.IGNORECASE)

          if obj not in result:
            result.append(obj)
            obj_count += 1

    print(f"\t\t\tFound {obj_count} object(s) ..")
  return result



def scrape(url):
  result = []
  urls = scrapeIndex(url)

  for u in urls:
    locations = scrapePage(u)
    for loc in locations:
      if loc not in result:
        result.append(loc)

  return result

def main():
  struct = {
    'meta': {
      'name': 'Uttagsautomater',
      'web': SOURCE_URL,
      'wikipedia': None,
      'category': 'Uttagsautomater',
      'locations': None,
    },
    'locations': None
  }

  struct["locations"] = []

  locations = scrape(SOURCE_URL)

  if locations != None:
    struct['locations'] = locations

  struct['meta']['locations'] = len(struct['locations'])

  writeYAML(DEST_YAML, struct)


if __name__ == '__main__':
  main()
