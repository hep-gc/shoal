import re
import json


def parseValue(val):
    if val.isdigit():
      return int(val)
    else:
      try:
        return float(val)
      except:
        if "null" in val:
          return None
        else:
          return unicode(val.strip("\""))

#read the shoal server data (will be curl)
f=open("/root/10", "r")
jStr = f.read()
f.close()

#don't put geo data in there
props = ["load", "distance", u"squid_port", "last_active", "created", "external_ip", "hostname", "public_ip", "private_ip"]

outDict = {}
p = re.compile("\""+props[0]+"\": ([^,}]+)")
tempList = p.findall(jStr)
numNearest = len(tempList)
for i in range(0, numNearest):
  outDict[unicode(str(i))] = {}
  outDict[unicode(str(i))][unicode("geo_data")] = {}

for prop in props:
  p = re.compile("\""+prop+"\": ([^,]+)[,|}]")
  valList = p.findall(jStr)
  i = 0
  for i, val in enumerate(valList):
    outDict[unicode(str(i))][unicode(prop)] = parseValue(val)

geoProps = ["city", "region_name", "area_code", "time_zone", "dma_code", "metro_code", "country_code3", "latitude", "postal_code", "longitude", "country_code", "country_name", "continent"]

for geoProp in geoProps:
   p = re.compile("\""+geoProp+"\": (\"[^\"]*|[^,]*)")
   valList = p.findall(jStr)
   for i, val in enumerate(valList):
     outDict[unicode(str(i))][unicode("geo_data")][unicode(geoProp)] = parseValue(val)


jsonOut = json.loads(jStr)




class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect 
    def removed(self):
        return self.set_past - self.intersect 
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


for key in outDict:
  d = DictDiffer(outDict[key], jsonOut[key])
  print "Testing squid node ", key
  if not len(d.added()) == 0:
    print "Added:", d.added()
  if not len(d.removed()) == 0:
    print "removed:", d.removed()
  for change in d.changed():
    if outDict[key][change] != jsonOut[key][change]:
      print "OutDict:", outDict[key][change]
      print "Json:   ", jsonOut[key][change]
