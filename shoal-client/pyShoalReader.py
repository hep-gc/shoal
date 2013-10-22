import re


def parseValue(val):
    if val.isdigit():
      return int(val)
    else:
      try:
        return double(val)
      except:
        if "null" in val:
          return None
        else:
          return val.strip("\"")

#read the shoal server data (will be curl)
f=open("/root/10", "r")
jStr = f.read()
f.close()

#don't put geo data in there
props = ["load", "distance", "squid_port", "last_active", "created", "external_ip", "hostname", "public_ip", "private_ip"]

outDict = {}
p = re.compile("\""+props[0]+"\": ([^,}]+)")
tempList = p.findall(jStr)
numNearest = len(tempList)
for i in range(0, numNearest):
  outDict[str(i)] = {}
  outDict[str(i)]["geo_data"] = {}

for prop in props:
  p = re.compile("\""+prop+"\": ([^,]+),")
  valList = p.findall(jStr)
  i = 0
  for i, val in enumerate(valList):
    outDict[str(i)][prop] = parseValue(val)

geoProps = ["city", "region_name", "area_code", "time_zone", "dma_code", "metro_code", "country_code3", "latitude", "postal_code", "longitude", "country_code", "country_name", "continet"]

for geoProp in geoProps:
   p = re.compile("\""+geoProp+"\": ([^,]+),")
   valList = p.findall(jStr)
   for i, val in enumerate(valList):
     outDict[str(i)]["geo_data"][geoProp] = parseValue(val)

print outDict
  
     
