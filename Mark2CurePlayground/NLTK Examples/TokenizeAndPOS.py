from nltk.stem import *
import nltk
from nltk import word_tokenize
import urllib.request
import urllib.parse
import json
import lxml.etree

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

def compute_score_for_stems(phrase, searchStringStems):
    phraseStems = build_stems(phrase)
    phraseTokens = word_tokenize(phrase)

    score = 0
    lenOfPhraseTokens = len(phraseTokens)

    for k,v in searchStringStems.items():
        if k in phraseStems:
            score = score + v
        else:
            score = score - .1 * lenOfPhraseTokens

    return score

def compute_scores_for_phrases(phrases, searchStringStems):
    scores = {}
    highestScore = -100000
    for phrase in phrases:
        score = compute_score_for_stems(phrase.PrefLabel, searchStringStems)

        for synonym in phrase.Synonyms:
            synonymScore = compute_score_for_stems(synonym, searchStringStems)
            if synonymScore > score:
                score = synonymScore

        scores[phrase.PrefLabel] = score

    return scores

def do_it(searchString, ontologiesOfInterest):
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

            synonyms = []
            if 'synonym' in jsonResponse:
                synonyms = jsonResponse['synonym']

            res = ResultWithSynonyms(jsonResponse['prefLabel'], synonyms)
            returnedOntologies[acronym].append(res)

    #3.  Which ontologies are missing?
    missingOntologies = []
    for ontologyOfInterest in ontologiesOfInterest:
        if not ontologyOfInterest in returnedOntologies.keys():
            missingOntologies.append(ontologyOfInterest)

    #4.  Which ontologies had an exact match?
    ontologiesWithExactMatch = []
    for key in returnedOntologies.keys():
        phrases = returnedOntologies[key]
        if len([p for p in phrases if p.PrefLabel.lower() == searchString]) > 0:
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
        
            scores = compute_scores_for_phrases(returnedPhrases, searchStringStems)
        
            highestScore = -100000
            for k,v in scores.items():
                if v > highestScore:
                    highestScore = v
    
            topMatches[key] = [k for k,v in scores.items() if v == highestScore] 

    for missingOntology in missingOntologies:
        for token in tokens:
            url = build_url(REST_URL, [missingOntology], token)
            jsonResponse = get_json(url)
        
            phrases = []
            for item in jsonResponse["collection"]:
                phrase = ResultWithSynonyms(item["prefLabel"], item["synonym"])
                phrases.append(phrase)

            scores = compute_scores_for_phrases(phrases, searchStringStems)
        
            highestScore = -100000
            for k,v in scores.items():
                if v > highestScore:
                    highestScore = v
    
            topMatches[missingOntology] = [k for k,v in scores.items() if v == highestScore] 

    return topMatches

#'.//document/passage/annotation/text'
#".//document/passage/annotation/infon[@key='type' and text() = 'disease']/../text"
#phrases = []
#tree = lxml.etree.parse('C:/Users/brush/desktop/group 25.xml')
#for atext in tree.xpath(".//document/passage/annotation/infon[@key='type' and text() = 'disease']"):
#    phrase = atext.text
#    if not phrase in phrases:
#        phrases.append(phrase)

#nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
nltk.data.path.append('D:/PythonData/nltk_data')

ontologiesOfInterest = ['MESH', 'DOID', 'RCD', 'MEDDRA']
#1.  Do a basic, dumb search using the original search string.  include all
#ontologies (we can break it up later).
searchString = 'CDG'.lower()

topMatches = do_it(searchString, ontologiesOfInterest)
print(topMatches)
