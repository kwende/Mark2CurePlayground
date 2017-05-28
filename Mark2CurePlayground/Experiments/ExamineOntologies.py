import requests
import json
import os
import sys
print(sys.version)

REST_URL = "http://data.bioontology.org"
API_KEY = "5cddf159-a650-4458-b802-cb5936567668"

def get_json(url):
    
    headers = {'Authorization': 'apikey token=' + API_KEY}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

jsonResponse = get_json(REST_URL + "/search?q=" + "Congenital disorders of glycosylation&ontologies=DOID")

for col in jsonResponse['collection']:
    print(col['links']['ontology'])