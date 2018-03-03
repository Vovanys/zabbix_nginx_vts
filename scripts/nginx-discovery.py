#! /usr/bin/python2
# -*- coding: utf-8 -*-
# parse json from nginx again
# we need to make /another/ json for zabbix
# warning: this script not send any values to Zabbiz, only upstreams and peers names.
# this script doing just one thing - make json for zabbix with right format
# unfortunately, json.dumps gives a slightly different format

import json, sys, os, re, urllib

# parse json from nginx to dict data
#url="https://site.ru/status/format/json"
url = str(sys.argv[1])
response = urllib.urlopen(url)
data = json.loads(response.read())

# forming json for LLD zabbix where {#UPSTREAM} - upstream's name
# {#NODE_IP} - peer's IP address


result="{\n\"data\":[\n"

# ищем server-ы

for i in sorted(data['serverZones'].keys()):
	if str(i) == "*": 
		continue
	result = result + "{\n"
	result = result + "\"{#ZONE}\":\""+str(i)+"\"\n"
	result = result + "},\n"

# ищем upstream-ы, если нету забиваем
try:
    'server' in sorted(data['upstreamZones'].keys())
except KeyError as e:
    pass
else:
 for i in sorted(data['upstreamZones'].keys()):
         ip_data = dict([[v['server'],v] for v in data['upstreamZones'][i]])
         for j in sorted(ip_data.keys()):
                 result = result + "{\n"
                 result = result + "\"{#UPSTREAM}\":\""+str(i)+"\",\n"
                 result = result + "\"{#NODE_IP}\":\""+str(j)+"\"\n"
                 result = result + "},\n"

result = re.sub("},\n$", "", result) + "}]\n}\n"
print result

