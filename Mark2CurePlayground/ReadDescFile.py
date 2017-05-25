import lxml.etree
from nltk.stem import *
import nltk
from nltk import word_tokenize
import time
import pickle

#http://www.nltk.org/howto/metrics.html
#https://www.nlm.nih.gov/mesh/topsubscope.html*-
class Term:

    def __init__(self):
        self.MainEntry = None
        self.Synonyms = []

    # https://stackoverflow.com/questions/2489669/function-parameter-types-in-python
    def IsExactEntryFound(self, otherEntry):

        isPerfectMatch = False
        lineToMatch = otherEntry.Line.lower()

        if lineToMatch == self.MainEntry.Line.lower():
            isPerfectMatch = True
        else:
            for synonym in self.Synonyms:
                if synonym.Line.lower() == lineToMatch:
                    isPerfectMatch = True
                    break

        return isPerfectMatch

class Entry:

    def __init__(self, line):
        self.Line = ""
        self.Tokens = []
        self.Stems = []

        line = line.replace(',','').replace('\n','')
        self.Line = line
        self.Tokens = word_tokenize(line)
        porter = PorterStemmer()
        self.Stems = [porter.stem(t) for t in self.Tokens]
        #tags = nltk.pos_tag(self.Tokens)
        #okayTags = ['NN', 'NNS', 'JJ']

        #self.ImportantWords = [porter.stem(t[0]) for t in tags if t[1] in
        #okayTags or t[0].isdigit()]

def CreateAndSerializeMeshDescriptorRecords():
    descriptorNames = tree.xpath(".//DescriptorRecord/AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName/String[text()='diagnosis']/../../../../../DescriptorName/String/text()")
    number = len(descriptorNames)
    terms = []
    start = time.time()
    number = 1
    for descriptorName in descriptorNames:
        print(str(number) + "/" + str(len(descriptorNames)) + ": " + descriptorName)
        number = number + 1
        term = Term()
        term.MainEntry = Entry(descriptorName)
        synonymNames = tree.xpath('.//DescriptorRecord/DescriptorName/String[text()="' + descriptorName + '"]/../../ConceptList/Concept/TermList/Term/String/text()')
        for synonymName in synonymNames:
            if not synonymName == descriptorName:
                print('\t' + synonymName)
                term.Synonyms.append(Entry(synonymName))

        terms.append(term)

    print('serializing...')

    with open("c:/users/brush/desktop/parsed.pickle", "wb") as p:
        pickle.dump(terms, p)

def LoadAndDeserializeMeshDescriptorRecords():
    terms = []

    with open("c:/users/brush/desktop/parsed.pickle", "rb") as p:
        terms = pickle.load(p)

    return terms

# work desktop
nltk.data.path.append('D:/PythonData/nltk_data')
lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()
tree = lxml.etree.parse('D:/BioNLP/desc2017.xml')

# home laptop
#nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
#lines = open('c:/users/ben/desktop/bionlp/threeormore.txt', 'r').readlines()
#tree = lxml.etree.parse('C:/Users/Ben/Desktop/BioNLP/desc2017.xml')
toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

meshDescriptorRecords = LoadAndDeserializeMeshDescriptorRecords()

#matchableDescriptorNames = []
#for descriptorName in descriptorNames:
#    entry = Entry(descriptorName)
#    matchableDescriptorNames.append(entry)
perfectMatches = []
toMatchCount = 1
for toMatchEntry in toMatchEntries:
    print(str(toMatchCount) + "/" + str(len(toMatchEntries)))
    toMatchCount = toMatchCount + 1
    for meshDescriptorRecord in meshDescriptorRecords:
        if meshDescriptorRecord.IsExactEntryFound(toMatchEntry):
            perfectMatches.append(toMatchEntry)

numberOfPerfectMatches = len(perfectMatches)
#http://www.nltk.org/howto/wordnet.html
print("Found " + str(numberOfPerfectMatches) + " out of " + str(len(toMatchEntries)) + " perfect matches.")
