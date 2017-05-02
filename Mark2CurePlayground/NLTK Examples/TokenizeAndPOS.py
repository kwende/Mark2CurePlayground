import nltk
from nltk import word_tokenize
import urllib.request
import urllib.parse
import json

REST_URL = "http://data.bioontology.org"
nltk.data.path.append('D:/PythonData/nltk_data')

def get_json(url):
    request = urllib.request.Request(url, data = None, headers ={
        'Authorization': 'apikey token=' + '5cddf159-a650-4458-b802-cb5936567668'    
        })
    r = urllib.request.urlopen(request)
    return json.loads(r.read().decode('utf-8'))

#1. Do a basic, dumb search using the original search string. include all ontologies (we can break it up later). 

#2. Take the response and break it up into individual ontologies. That way we can investigate the quality of the response for each ontology. 

searchString = 'profound hypoproteinemia with massive ascites'
requestUrl = REST_URL + "/search?q=" + urllib.parse.quote_plus(searchString) + "ontologies=DOID%2CHP%2CMEDDRA%2CMESH%2CRCD%2CSNOMEDCT&exact_match=false" #search for this class
jsonResponses = get_json(requestUrl) # get the json

prefResponses = []
for jsonResponse in [r for r in jsonResponses["collection"] if r['matchType'] == 'prefLabel']: #for each response that is a preferred label
    prefLabel = jsonResponse['prefLabel'] #get the response
    prefResponses.append(prefLabel)

tokens = word_tokenize()

pos = nltk.pos_tag(tokens)

for p in pos:
    if(p[1] == 'NN' or p[1] == 'NNS'):
        print(p[0])
    #print(p[0] + ':' + str(v))

print()
