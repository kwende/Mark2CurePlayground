import lxml.etree
from nltk.stem import *
import nltk
from nltk import word_tokenize
import time
import pickle
import re

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

    def IsPossibleAbbreviationMatch(self, otherEntry):
        
        isAbbreviationMatch = False
        
        match = re.match(r'\b[A-Z]*', otherEntry.Line)

        if match:
            matchedGroup = match.group()
            

        return isAbbreviationMatch
        

class Entry:

    def __init__(self, line):
        self.Line = ""
        self.Tokens = []
        self.Stems = []
        self.Abbreviation = ""

        line = line.replace(',','').replace('\n','')
        self.Line = line
        self.Tokens = word_tokenize(line)
        porter = PorterStemmer()
        self.Stems = [porter.stem(t) for t in self.Tokens]

        # is this already an abbreviation?
        match = re.fullmatch(r'\b[A-Z]+', line)
        
        if match:
            self.Abbreviation = line
        else:
            tags = nltk.pos_tag(self.Tokens)
            self.Abbreviation = ''.join([t[0][0].upper() for t in tags if t[1] != "IN"])

def CreateAndSerializeMeshDescriptorRecords(tree):
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

    return terms

def LoadAndDeserializeMeshDescriptorRecords(descriptorPath):
    terms = []

    with open(descriptorPath, "rb") as p:
        terms = pickle.load(p)

    return terms

# work desktop
nltk.data.path.append('D:/PythonData/nltk_data')
lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()
tree = lxml.etree.parse('D:/BioNLP/desc2017.xml')
descriptorPath = ""

# home laptop
#nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
#lines = open('c:/users/ben/desktop/bionlp/threeormore.txt', 'r').readlines()
#tree = lxml.etree.parse('C:/Users/Ben/Desktop/BioNLP/desc2017.xml')
#descriptorPath = "c:/users/ben/desktop/bionlp/parsed.pickle"

toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

meshDescriptorRecords = CreateAndSerializeMeshDescriptorRecords(tree)
#meshDescriptorRecords = LoadAndDeserializeMeshDescriptorRecords(descriptorPath)

#matchableDescriptorNames = []
#for descriptorName in descriptorNames:
#    entry = Entry(descriptorName)
#    matchableDescriptorNames.append(entry)

#errors = open('c:/users/ben/desktop/errors.txt','w+')
#perfectMatches = []
#toMatchCount = 1
#for toMatchEntry in toMatchEntries:
#    print(str(toMatchCount) + "/" + str(len(toMatchEntries)))
#    toMatchCount = toMatchCount + 1

#    found = False
#    for meshDescriptorRecord in meshDescriptorRecords:
#        if meshDescriptorRecord.IsExactEntryFound(toMatchEntry):
#            perfectMatches.append(toMatchEntry)
#            found = True
#        elif meshDescriptorRecord.IsPossibleAbbreviationMatch(toMatchEntry):
#            found = True
#            break

#    if not found:
#        errors.write(toMatchEntry.Line + "\n")

#errors.close()

##http://www.nltk.org/howto/wordnet.html
#print("Match score is " + str((len(perfectMatches) / (len(toMatchEntries)) * 100)) + "%")