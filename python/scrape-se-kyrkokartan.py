#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
#import random
import yaml
#import json
#import uuid
import requests
from io import StringIO, BytesIO

from bs4 import BeautifulSoup

#from parsel import Selector

from lxml import etree

import xml.etree.ElementTree as ET



#DATAROOT = './yaml/'
#MASTER_DATAFILE = './yaml/master.yaml'

SOURCE_URL = 'https://www.kyrkokartan.se/'
DEST_YAML = '../yaml/layers/kyrkor.yaml'

LOG = './kyrkokartan.txt'

DOMAIN = 'www.kyrkokartan.se'

NAMESPACE = 'kyrkor'

def writeLog(contents):
  with open(LOG, "a") as f:
    f.write(contents + "\n")

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

def urlTranslate(url):
  if url == None:
    return url
  url = re.sub(r"\xc3\xa5", "å", url, flags=re.IGNORECASE)
  url = re.sub(r"\xc3\xa4", "ä", url, flags=re.IGNORECASE)
  url = re.sub(r"\xc3\xb6", "ö", url, flags=re.IGNORECASE)

  url = re.sub(r"\xc3\x85", "Å", url, flags=re.IGNORECASE)
  url = re.sub(r"\xc3\x84", "Ä", url, flags=re.IGNORECASE)
  url = re.sub(r"\xc3\x96", "Ö", url, flags=re.IGNORECASE)

  url = re.sub(r"\xc3\xa9", "é", url, flags=re.IGNORECASE)

  url = re.sub(r"\x25C3\x25A5", "å", url, flags=re.IGNORECASE)
  url = re.sub(r"\x25C3\x25A4", "ä", url, flags=re.IGNORECASE)
  url = re.sub(r"\x25C3\x25B6", "ö", url, flags=re.IGNORECASE)

  url = re.sub(r"\x25C3\x2585", "Å", url, flags=re.IGNORECASE)
  url = re.sub(r"\x25C3\x2584", "Ä", url, flags=re.IGNORECASE)
  url = re.sub(r"\x25C3\x2596", "Ö", url, flags=re.IGNORECASE)

  url = re.sub(r"\x25C3\x25A9", "é", url, flags=re.IGNORECASE)

  url = re.sub(r"\x253A", ":", url, flags=re.IGNORECASE)
  url = re.sub(r"\x252F", "/", url, flags=re.IGNORECASE)
  url = re.sub(r"\x255F", "_", url, flags=re.IGNORECASE)

  return url

# https://www.kyrkokartan.se/V%C3%A4xj%C3%B6/Tegn%C3%A9rkyrkog%C3%A5rden/


def parseScript(script):
  result = []

  text = script.text

  text = re.sub(r"^\s{1,}", "", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\s{1,}$", "", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\x2f\x2f\s.+?\n", "", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\t", " ", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\r\n", " ", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\r", " ", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\n", " ", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\s{2,}\x7b", " {", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\x7b\s{2,}", "{ ", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\s{2,}\x7d", " }", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\x7d\s{2,}", "} ", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\s{2,}", " ", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\xc3\xa5", "å", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\xc3\xa4", "ä", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\xc3\xb6", "ö", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\xc3\x85", "Å", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\xc3\x84", "Ä", str(text), flags=re.IGNORECASE)
  text = re.sub(r"\xc3\x96", "Ö", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\xc3\xa9", "é", str(text), flags=re.IGNORECASE)

  text = re.sub(r"\x5c\x22", '"', str(text), flags=re.IGNORECASE)
  text = re.sub(r"\x5c\x2f", '/', str(text), flags=re.IGNORECASE)

  lines = re.split(r"\B\x3b\s", str(text), flags=re.IGNORECASE)

  for line in lines:
    if re.search(r"^xml\x5fdata\s\x3d", str(line), flags=re.IGNORECASE):
      markers = re.sub(r"^xml\x5fdata\s\x3d\s\x22", "", str(line), flags=re.IGNORECASE)
      markers = re.sub(r"\x22$", "", str(markers), flags=re.IGNORECASE)

      print(markers)

      tree = etree.parse(StringIO(markers))
      root = tree.getroot()

      for marker in root.findall(".//marker"):
        marker_lat = marker.get("lat")
        marker_lng = marker.get("long")
        marker_point_link = marker.get("point_link")
        marker_point_name = marker.get("point_message")
        marker_urn = re.sub(r"^\x2f(\d{1,})\x2f.+?$", "urn:kyrkkartan:locationId:\\1", str(marker_point_link), flags=re.IGNORECASE)

        marker_struct = {
          'location': str(marker_point_name),
          'urn': str(marker_urn),
          'city': None,
          'country': "Sverige",
          'latitude': float(marker_lat),
          'longitude': float(marker_lng)
        }
        result.append(marker_struct)

  #exit(0)
  return result


def traverseSite(url):
  links = []
  links.append(url)
  links.append('https://www.kyrkokartan.se/populara_omraden/')

  skip_links = [
    'http://www.restaurangkartan.se',
    'http://www.hotellkartan.se',
    'http://www.cafekartan.se',
    'http://www.pizzakartan.se',
    'http://www.sushikartan.se',
    'http://www.badkartan.se',
    'http://www.campingkartan.se',
    'http://www.vandrarhemskartan.se',
    'http://www.slottskartan.se',
    'https://www.kyrkokartan.se',
    'http://www.vintagekartan.se',
    'http://www.wifikartan.se',
    'https://small-luxury-hotels.net',
    'https://amazing-hotel-suites.com',


    '/om/sajten',
    '/om/sa_funkar_det',
    '/om/bli_medlem/',
    '/om/lagg_till/',

    '/senaste/',
    '/senaste/?sorting=1',
    '/mest_aktiva_medlemmar/',

    'https://www.kyrkokartan.se/uppdatera/',


  ]

  re_rule_sorting = re.compile(r"^\x3fsorting\x3d\d{1,}", flags=re.IGNORECASE)
  re_rule_javascript = re.compile(r"^javascript", flags=re.IGNORECASE)


  re_rule_link = re.compile(r"^https\x3a\x2f\x2f([a-z0-9\x2e]{1,})\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f([a-z0-9åäöÅÄÖéÉ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f$", flags=re.IGNORECASE)


  link_counter = 1

  for link in links:
    print(f"[{link_counter}/{len(links)}] {link}")
    navigation_counter = 0

    location_counter = 0

    res = requests.get(link)
    if int(res.status_code) == 200:
      soup = BeautifulSoup(str(res.text), 'html.parser')

      for a in soup.find_all('a'):
        if a == None:
          continue

        a_href = a.get('href')
        a_href = urlTranslate(a_href)

        if a_href == None:
          continue

        if a_href == "/":
          continue

        if a_href == "#":
          continue

        if str(a_href) in links:
          continue


        if re.search(re_rule_sorting, str(a_href)):
          continue

        if re.search(re_rule_javascript, str(a_href)):
          continue

        if str(a_href) in skip_links:
          continue

        if re.search(r"^https\x3a\x2f\x2f([a-z0-9\x2e]{1,})\x2f(\d{1,})\x2fimages\x2f([\d\x5f]{1,})$", str(a_href), flags=re.IGNORECASE):
          continue

        if re.search(r"^http(s)?\x3a\x2f\x2fwww\x2eminkarta\x2ese\x2f", str(a_href), flags=re.IGNORECASE):
          continue

        if re.search(r"^\x2f(\d{1,})\x2fimages\x2f", str(a_href), flags=re.IGNORECASE):
          continue

        # hunt for navigatable links
        if re.search(r"^https\x3a\x2f\x2f([a-z0-9\x2e]{1,})\x2f(\d{1,})\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})$", str(a_href), flags=re.IGNORECASE):
          if str(a_href) not in links:
            links.append(url)
            print(f"\tNavigation: {url}")
          continue

        if re.search(r"^\x2f(\d{1,})\x2f([a-zåäöÅÄÖ0-9\x5f]{1,})(\x2f)?$", str(a_href), flags=re.IGNORECASE):
          url = f"https://{DOMAIN}{a_href}"
          a_href = url

          if str(url) not in links:
            links.append(url)
            navigation_counter += 1
            print(f"\tNavigation: {url}")
          continue

        if re.search(r"^\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2e\x5f]{1,})\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})(\x2f)?$", str(a_href), flags=re.IGNORECASE):
          url = f"https://{DOMAIN}{a_href}"
          a_href = url

          if str(url) not in links:
            links.append(url)
            navigation_counter += 1
            print(f"\tNavigation: {url}")
          continue

        if re.search(r"^\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})(\x2f)?$", str(a_href), flags=re.IGNORECASE):
          url = f"https://{DOMAIN}{a_href}"
          a_href = url

          if str(url) not in links:
            links.append(url)
            navigation_counter += 1
            print(f"\tNavigation: {url}")
          continue

        if re.search(r"^\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f\x3fsida\x3d(\d{1,})$", str(a_href), flags=re.IGNORECASE):
          url = f"https://{DOMAIN}{a_href}"
          a_href = url

          if str(url) not in links:
            links.append(url)
            navigation_counter += 1
            print(f"\tNavigation: {url}")
          continue

        if re.search(r"^\x2f([a-z0-9åäöÅÄÖéÉ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f([a-z0-9åäöÅÄÖéÉ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f\x3fsida\x3d\d{1,}$", str(a_href), flags=re.IGNORECASE):
          url = f"https://{DOMAIN}{a_href}"
          a_href = url

          if str(url) not in links:
            links.append(url)
            navigation_counter += 1
            print(f"\tNavigation: {url}")
          continue



        if re.search(r"^https\x3a\x2f\x2f([a-z0-9\x2e]{1,})\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f$", str(a_href), flags=re.IGNORECASE):
          if str(a_href) not in links:
            links.append(a_href)
            navigation_counter += 1
            print(f"\tNavigation: {a_href}")
          continue

        if re.search(r"^https\x3a\x2f\x2f([a-z0-9\x2e]{1,})\x2f([a-z0-9åäöÅÄÖ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f([a-z0-9åäöÅÄÖéÉ\x25\x2c\x2d\x2e\x3a\x5f]{1,})\x2f$", str(a_href), flags=re.IGNORECASE):
          if str(a_href) not in links:
            links.append(a_href)
            navigation_counter += 1
            print(f"\tNavigation: {a_href}")
          continue


        print(a_href)

      for script in soup.find_all('script'):
        #print(script)
        if re.search(r"xml\x5fdata\s\x3d", str(script), flags=re.IGNORECASE):
          location_list = parseScript(script)
          #print(location_list)
          for location in location_list:
            writeLog(str(location))

    print(f"\tFound: Navigation links: {navigation_counter}")
    time.sleep(15)
    link_counter += 1
    print("")


def main():

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

  res_extr = traverseSite(SOURCE_URL)

  struct["locations"].append(res_extr)

  struct['meta']['locations'] = len(struct['locations'])

  writeYAML(DEST_YAML, struct)


if __name__ == '__main__':
  main()
