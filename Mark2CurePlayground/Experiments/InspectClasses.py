import urllib.request
import urllib.parse
import json
import os
from pprint import pprint
import xml.etree.ElementTree

REST_URL = "http://data.bioontology.org"
API_KEY = ""

def get_json(url):
    request = urllib.request.Request(url, data = None, headers ={
        'Authorization': 'apikey token=' + '5cddf159-a650-4458-b802-cb5936567668'    
        })
    r = urllib.request.urlopen(request)
    return json.loads(r.read().decode('utf-8'))

phrases = []
tree = xml.etree.ElementTree.parse('C:/Users/Ben/Downloads/group 25/group 25.xml')
for atext in tree.findall('.//document/passage/annotation/text'):
    phrase = atext.text
    if not phrase in phrases:
        phrases.append(phrase)

with open('c:/users/ben/desktop/results.txt', 'w+') as f:
    search_results = []
    for phrase in phrases:
        requestUrl = REST_URL + "/search?q=" + urllib.parse.quote_plus(phrase)
        phraseString = "Phrase " + "'" + phrase + "'"
        print(phraseString)
        f.write(phraseString + '\n')
        responses = get_json(requestUrl)
        count = 0
        #search_results.append(termResponse["collection"])
        for response in [r for r in responses["collection"] if r['matchType'] == 'prefLabel']:
            ontology = get_json(response['links']['ontology'])
            prefLabel = response['prefLabel']  
            if prefLabel.lower() == phrase:
                foundString = '\t' + ontology['name']
                print(foundString)
                f.write(foundString + '\n')
                count= count + 1
        if count == 0:
            nothingResponse = 'Nothing found.'
            print(nothingResponse)
            f.write(nothingResponse + '\n')
        f.flush()
        
        #print(prefLabel + ': ' + ontology['name'] + ' (' + ontology['acronym'] + ')')

# Print the results
#for result in search_results:
#    for response in result:
#        ontology = get_json(response['links']['ontology'])
#        print(response['prefLabel'] + ': ' + ontology['name'] + ' (' + ontology['acronym'] + ')')