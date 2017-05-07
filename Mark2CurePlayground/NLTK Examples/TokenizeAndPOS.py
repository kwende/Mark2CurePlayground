from nltk.stem import *
import nltk
from nltk import word_tokenize
import urllib.request
import urllib.parse
import json

REST_URL = "http://data.bioontology.org"

class ResultWithSynonyms:
    PrefLabel = ""
    Synonyms = []

    def __init__(self, prefLabel, synonyms):
        self.PrefLabel = prefLabel
        self.Synonyms = synonyms

def get_json(url):
    request = urllib.request.Request(url, data = None, headers ={
        'Authorization': 'apikey token=' + '5cddf159-a650-4458-b802-cb5936567668'    
        })
    r = urllib.request.urlopen(request)
    return json.loads(r.read().decode('utf-8'))

def build_stems(input):
    porter = PorterStemmer()
    tokens = word_tokenize(input)
    tags = nltk.pos_tag(tokens)
    okayTags = ['NN','NNS']    

    ret = [porter.stem(t[0]) for t in tags if t[1] in okayTags]
    return ret

def build_stems_with_weights(input):
    porter = PorterStemmer()
    tokens = word_tokenize(input)
    tags = nltk.pos_tag(tokens)
    okayTags = ['NN','NNS']

    wordAndWeight = {}
    weight = 1
    for tag in tags:
        if tag[1] in okayTags:
            wordAndWeight[porter.stem(tag[0])] = weight
        elif tag[1] == "IN":
               weight = .5
    return wordAndWeight

def build_url(baseUrl, ontologies, searchString):
    ontologiesString = "&ontologies="
    for ontology in ontologies:
        ontologiesString = ontologiesString + ontology + ","
    requestUrl = baseUrl + "/search?q=" + urllib.parse.quote_plus(searchString) + ontologiesString + "&exact_match=false" #search for this class
    return requestUrl

nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
ontologiesOfInterest = ['MESH', 'DOID', 'RCD', 'MEDDRA']

#1.  Do a basic, dumb search using the original search string.  include all
#ontologies (we can break it up later).
searchString = 'Heat stress'.lower()
tokens = word_tokenize(searchString)
tags = nltk.pos_tag(tokens)

requestUrl = build_url(REST_URL, ontologiesOfInterest, searchString)
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

#5.  Find the closest match out of the ones we do have.  Trim the words to
#their
# stems, and then count how many stem matches we get for each of the responses
# to the
# search phrase.  Order by response quality.  Return top-3.  Be mindful as to
# NOT return
# the same phrase.
searchStringStems = build_stems_with_weights(searchString)

topMatches = {}
for key in returnedOntologies.keys():
    if not key in ontologiesWithExactMatch and not key in missingOntologies:
        returnedPhrases = returnedOntologies[key]
        
        scores = {}
        highestScore = -100000
        for returnedPhrase in returnedPhrases:
            returnedPhraseStems = build_stems(returnedPhrase)
            
            returnedPhraseTokens = word_tokenize(returnedPhrase)

            score = 0
            lenOfPhraseTokens = len(returnedPhraseTokens)

            for k,v in searchStringStems.items():
                if k in returnedPhraseStems:
                    score = score + v
                else:
                    score = score - .1 * lenOfPhraseTokens

            if score > highestScore:
                highestScore = score

            scores[returnedPhrase] = score

        topMatches[key] = [k for k,v in scores.items() if v == highestScore] 

print(topMatches)
print(ontologiesWithExactMatch)
print(missingOntologies)

for missingOntology in missingOntologies:
    for token in tokens:
        url = build_url(REST_URL, [missingOntology], token)
        jsonResponse = get_json(url)
        print(url)