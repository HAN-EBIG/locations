#!/usr/bin/env python

import json
from pprint import pprint
import sys
import re

LOCATIONS = 'locations.json'

with open(LOCATIONS) as locations_file:
  locations = json.load(locations_file)

assigned = {}
known_buildings = []
for location, data in locations.iteritems():
  building = location.split('-')[0]
  if not building in known_buildings: known_buildings.append(building)

  if not 'accesspoints' in data and not 'accesspoint' in data: continue
  if 'accesspoints' in data and 'accesspoint' in data: raise Exception(location + ' has both "accesspoint" and "accesspoints"')

  # expand single-ap assignment
  if 'accesspoint' in data:
    data['accesspoints'] = [data['accesspoint']]
    del data['accesspoint']

  if 'accesspoints' in data and len(data['accesspoints']) == 0: raise Exception(location + ' has empty accesspoints array')

  for ap in data['accesspoints']:
    if ap in assigned: raise Exception(ap + ' is assigned to both ' + assigned[ap] + ' and ' + location)
    assigned[ap] = location

ap = sys.argv[1].upper()
location = sys.argv[2]

if not re.search('^[0-9A-F]{12}$', ap): raise Exception (ap + ' not recognized as MAC address')
if not location.split('-')[0] in known_buildings: raise Exception('Unknown building in ' + location)

# internal MAC address of the AP is the external mac address with the last higit changed to '0'
ap = ap[:-1] + '0'

# remove if it was assigned elsewhere
if ap in assigned:
  locations[assigned[ap]]['accesspoints'].remove(ap)

  # if no more accesspoints left, remove the empty list
  if len(locations[assigned[ap]]['accesspoints']) == 0:
    del locations[assigned[ap]]['accesspoints']

  # if no more data left, remove the location
  if len(locations[assigned[ap]].keys()) == 0:
    del locations[assigned[ap]]

# create location if it does not exist
if not location in locations:
  locations[location] = {}

# create accesspoints array if it does not exist
if not 'accesspoints' in locations[location]:
  locations[location]['accesspoints'] = []

locations[location]['accesspoints'].append(ap)

# simplify single-ap assignment
for location, data in locations.iteritems():
  if not 'accesspoints' in data: continue

  if len(data['accesspoints']) == 1:
    data['accesspoint'] = data['accesspoints'][0]
    del data['accesspoints']

with open(LOCATIONS, 'w') as locations_file:
  json.dump(locations, locations_file, sort_keys=True, indent=2, separators=(',', ': '))
