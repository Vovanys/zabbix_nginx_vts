#! /usr/bin/python2
# -*- coding: utf-8 -*-
# script awaits command line args for input
# json keys from nginx status use as args
# examples:
# nginx-stats.py requests current (get current requests count)
# nginx-stats.py upstreams hg-backend peers 10.0.0.1 requests (get count requests to peer 10.0.0.1, for upstream hg-backend)
# into Zabbix templates it looks like:
# 1) all active connections            [connections,active]
# 2) all current requests                [requests,current]
# Upstreams:
# 4) active connections                 [upstreams,{#UPSTREAM},peers,{#NODE_IP},active]
# 5) status                                     [upstreams,{#UPSTREAM},peers,{#NODE_IP},state]
# 7) requests per second               [upstreams,{#UPSTREAM},peers,{#NODE_IP},requests]
# 8) responses for every HTTP-code per second  [upstreams,{#UPSTREAM},peers,{#NODE_IP},responses,Xxx]
# 9) summ active connections                 [upstreams,{#UPSTREAM},active]
# 10) summ requests per second               [upstreams,{#UPSTREAM},requests]
# 11) summ responses for every HTTP-code per second  [upstreams,{#UPSTREAM},responses,Xxx]

import json, sys, os, urllib

# parse json from nginx to doct data
#url="https://site.ru/status/format/json"
url = str(sys.argv[1])
directory="/tmp/nginx-stats/"
response = urllib.urlopen(url)
data = json.loads(response.read())
maxTime = float(3600)  # in seconds
avgTime = float(60) # average during, in seconds

def printInt(float):
  print(int(round(float)))

if not os.path.exists(directory):
    os.makedirs(directory)

tmpfile = directory + str(sys.argv[2])
for i in range(2, len(sys.argv)):
    tmpfile = tmpfile + "." + str(sys.argv[i])

# test for file with data from previous run
# if not - create it with current data and exit
# if yes - read it to timestampDelta for count req/s and res/s
try:
    json.loads(open(tmpfile).read())
except IOError as e:
    with open(tmpfile, 'w') as delta_file:
        json.dump(data, delta_file)
    sys.exit()
except ValueError as e:
    with open(tmpfile, 'w') as delta_file:
        json.dump(data, delta_file)
        sys.exit()
else:
    with open(tmpfile) as data_file:
        data_delta = json.load(data_file)
        timestampDelta = data_delta["nowMsec"]

# check load_timestamp with data from previous run
# if it have another value, create temp file
# with current data and exit.
if int(data['loadMsec']) <> int(data_delta['loadMsec']):
    with open(tmpfile, 'w') as delta_file:
        json.dump(data, delta_file)
    sys.exit()

# check timestamp file with data from previous run
# if it older then maxTime (1 hour by default)
# create it with current data and exit.
if int(data['nowMsec']) - int(timestampDelta) > (maxTime * 1000) :
    with open(tmpfile, 'w') as delta_file:
        json.dump(data, delta_file)
    sys.exit()

delta = (data['nowMsec'] - timestampDelta) / (avgTime * 1000)

if ((str(sys.argv[2])) == "connections") or ((str(sys.argv[2])) == "requests"):
  print data['connections'][str(sys.argv[3])] # print all active connections or all current connections
elif (str(sys.argv[2])) == "upstreams":
  ip_data = dict([[v['server'],v] for v in data['upstreamZones'][str(sys.argv[3])]])
  ip_data_delta = dict([[v['server'],v] for v in data_delta['upstreamZones'][str(sys.argv[3])]])

  if ((str(sys.argv[4])) == "active") or ((str(sys.argv[4])) == "requests") or ((str(sys.argv[4])) == "responses"):
    summ_active = summ_requests = summ_responses_1xx = summ_responses_2xx = summ_responses_3xx = summ_responses_4xx = summ_responses_5xx = 0
    for i in ip_data.keys():
      summ_active = summ_active + ip_data[i]['requestCounter']
      summ_requests = summ_requests + (ip_data[i]['requestCounter'] - ip_data_delta[i]['requestCounter']) / delta
      summ_responses_1xx = summ_responses_1xx + (ip_data[i]['responses']['1xx'] - ip_data_delta[i]['responses']['1xx']) / delta
      summ_responses_2xx = summ_responses_2xx + (ip_data[i]['responses']['2xx'] - ip_data_delta[i]['responses']['2xx']) / delta
      summ_responses_3xx = summ_responses_3xx + (ip_data[i]['responses']['3xx'] - ip_data_delta[i]['responses']['3xx']) / delta
      summ_responses_4xx = summ_responses_4xx + (ip_data[i]['responses']['4xx'] - ip_data_delta[i]['responses']['4xx']) / delta
      summ_responses_5xx = summ_responses_5xx + (ip_data[i]['responses']['5xx'] - ip_data_delta[i]['responses']['5xx']) / delta

    if (str(sys.argv[4])) == "active":
      print summ_active
    elif (str(sys.argv[4])) == "requests":
      printInt (summ_requests)
    elif (str(sys.argv[4])) == "responses":
      if (str(sys.argv[5])) == "1xx":
        printInt (summ_responses_1xx)
      elif (str(sys.argv[5])) == "2xx":
        printInt (summ_responses_2xx)
      elif (str(sys.argv[5])) == "3xx":
        printInt (summ_responses_3xx)
      elif (str(sys.argv[5])) == "4xx":
        printInt (summ_responses_4xx)
      elif (str(sys.argv[5])) == "5xx":
        printInt (summ_responses_5xx)
      else:
        sys.exit()
    else:
      sys.exit()

  elif ((str(sys.argv[6])) == "active") or ((str(sys.argv[6])) == "state"):
    print ip_data[str(sys.argv[5])][str(sys.argv[6])] # print peer's active connections or peer's state
  elif (str(sys.argv[6])) == "requests":
    printInt ((ip_data[str(sys.argv[5])]['requestCounter'] - ip_data_delta[str(sys.argv[5])]['requestCounter']) / delta)
  elif (str(sys.argv[6])) == "responses":
    if (str(sys.argv[7])) == "1xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['1xx'] - ip_data_delta[str(sys.argv[5])]['responses']['1xx']) / delta)
    elif (str(sys.argv[7])) == "2xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['2xx'] - ip_data_delta[str(sys.argv[5])]['responses']['2xx']) / delta)
    elif (str(sys.argv[7])) == "3xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['3xx'] - ip_data_delta[str(sys.argv[5])]['responses']['3xx']) / delta)
    elif (str(sys.argv[7])) == "4xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['4xx'] - ip_data_delta[str(sys.argv[5])]['responses']['4xx']) / delta)
    elif (str(sys.argv[7])) == "5xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['5xx'] - ip_data_delta[str(sys.argv[5])]['responses']['5xx']) / delta)
    else:
      sys.exit()
elif (str(sys.argv[2])) == "zones":
  ip_data = dict(data['serverZones'][str(sys.argv[3])])
  ip_data_delta = dict(data_delta['serverZones'][str(sys.argv[3])])

  if ((str(sys.argv[4])) == "active") or ((str(sys.argv[4])) == "requests") or ((str(sys.argv[4])) == "responses"):
    summ_active = summ_requests = summ_responses_1xx = summ_responses_2xx = summ_responses_3xx = summ_responses_4xx = summ_responses_5xx = 0
    for i in ip_data.keys():
	  #print ip_data['responses']['4xx']
      summ_active = summ_active + ip_data['requestCounter']
      summ_requests = summ_requests + (ip_data['requestCounter'] - ip_data_delta['requestCounter']) / delta
      summ_responses_1xx = summ_responses_1xx + (ip_data['responses']['1xx'] - ip_data_delta['responses']['1xx']) / delta
      summ_responses_2xx = summ_responses_2xx + (ip_data['responses']['2xx'] - ip_data_delta['responses']['2xx']) / delta
      summ_responses_3xx = summ_responses_3xx + (ip_data['responses']['3xx'] - ip_data_delta['responses']['3xx']) / delta
      summ_responses_4xx = summ_responses_4xx + (ip_data['responses']['4xx'] - ip_data_delta['responses']['4xx']) / delta
      summ_responses_5xx = summ_responses_5xx + (ip_data['responses']['5xx'] - ip_data_delta['responses']['5xx']) / delta

    if (str(sys.argv[4])) == "active":
      print summ_active
    elif (str(sys.argv[4])) == "requests":
      printInt (summ_requests)
    elif (str(sys.argv[4])) == "responses":
      if (str(sys.argv[5])) == "1xx":
        printInt (summ_responses_1xx)
      elif (str(sys.argv[5])) == "2xx":
        printInt (summ_responses_2xx)
      elif (str(sys.argv[5])) == "3xx":
        printInt (summ_responses_3xx)
      elif (str(sys.argv[5])) == "4xx":
        printInt (summ_responses_4xx)
      elif (str(sys.argv[5])) == "5xx":
        printInt (summ_responses_5xx)
      else:
        sys.exit()
    else:
      sys.exit()

  elif ((str(sys.argv[6])) == "active") or ((str(sys.argv[6])) == "state"):
    print ip_data[str(sys.argv[5])][str(sys.argv[6])] # print peer's active connections or peer's state
  elif (str(sys.argv[6])) == "requests":
    printInt ((ip_data[str(sys.argv[5])]['requestCounter'] - ip_data_delta[str(sys.argv[5])]['requestCounter']) / delta)
  elif (str(sys.argv[6])) == "responses":
    if (str(sys.argv[7])) == "1xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['1xx'] - ip_data_delta[str(sys.argv[5])]['responses']['1xx']) / delta)
    elif (str(sys.argv[7])) == "2xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['2xx'] - ip_data_delta[str(sys.argv[5])]['responses']['2xx']) / delta)
    elif (str(sys.argv[7])) == "3xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['3xx'] - ip_data_delta[str(sys.argv[5])]['responses']['3xx']) / delta)
    elif (str(sys.argv[7])) == "4xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['4xx'] - ip_data_delta[str(sys.argv[5])]['responses']['4xx']) / delta)
    elif (str(sys.argv[7])) == "5xx":
      printInt ((ip_data[str(sys.argv[5])]['responses']['5xx'] - ip_data_delta[str(sys.argv[5])]['responses']['5xx']) / delta)
    else:
      sys.exit()
  else:
	sys.exit()

else:
  sys.exit()

with open(tmpfile, 'w') as delta_file:
    json.dump(data, delta_file)
