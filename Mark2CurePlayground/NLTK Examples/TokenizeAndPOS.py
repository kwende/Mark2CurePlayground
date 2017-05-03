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

ontologiesOfInterest = ['MESH', 'DOID', 'RCD', 'MEDDRA']

#1.  Do a basic, dumb search using the original search string.  include all
#ontologies (we can break it up later).
searchString = 'profound hypoproteinemia with massive ascites'.lower()
ontologiesString = "&ontologies="
for ontologyOfInterest in ontologiesOfInterest:
    ontologiesString = ontologiesString + ontologyOfInterest + ","
requestUrl = REST_URL + "/search?q=" + urllib.parse.quote_plus(searchString) + ontologiesString + "&exact_match=false" #search for this class
jsonResponses = get_json(requestUrl) # get the json

#2.  Take the response and break it up into individual ontologies.  That way we
#can investigate the quality of the response for each ontology.
returnedOntologies = {}
for jsonResponse in jsonResponses["collection"]:
    ontology = get_json(jsonResponse['links']['ontology'])
    acronym = ontology['acronym'].upper()

    if acronym in ontologiesOfInterest:
        if not acronym in returnedOntologies:
            returnedOntologies[acronym] = []

        returnedOntologies[acronym].append(jsonResponse['prefLabel'])

#3.  Which ontologies are missing?
missingOntologies = []
for ontologyOfInterest in ontologiesOfInterest:
    if not ontologyOfInterest in returnedOntologies.keys():
        missingOntologies.append(ontologyOfInterest)

#4.  Which ontologies had an exact match?
ontologiesWithExactMatch = []
for key in returnedOntologies.keys():
    phrases = returnedOntologies[key]
    if len([p for p in phrases if p.lower() == searchString]) > 0:
        ontologiesWithExactMatch.append(key)

#5. Find the closest match out of the ones we do have. Trim the words to their 
# stems, and then count how many stem matches we get for each of the responses to the
# search phrase. Order by response quality. Return top-3. Be mindful as to NOT return
# the same phrase. 

