import urllib.request
import urllib.parse
import json
import os
from pprint import pprint
import xml.etree.ElementTree
import time

REST_URL = "http://data.bioontology.org"
API_KEY = ""

def get_json(url):
    request = urllib.request.Request(url, data = None, headers ={
        'Authorization': 'apikey token=' + '5cddf159-a650-4458-b802-cb5936567668'    
        })
    r = urllib.request.urlopen(request)
    return json.loads(r.read().decode('utf-8'))

lines = open('c:/users/ben/desktop/bionlp/errors.txt', 'r+').readlines()

number = 1
with open('c:/users/ben/desktop/bionlp/matches.txt', 'w+') as f:
    for line in lines:
        line = line.replace('\n','')
        requestUrl = REST_URL + "/search?q=" + urllib.parse.quote_plus(line) + "&ontologies=MESH&exact_match=false"
        readJson = get_json(requestUrl)
        f.write(line + '\n')
        print("Line " + str(number) + " of " + str(len(lines)))
        number = number + 1
        for item in readJson['collection']:
            f.write('\t' + item['prefLabel'] + '\n')
            #print('\t' + item['prefLabel'])

        time.sleep(1)


