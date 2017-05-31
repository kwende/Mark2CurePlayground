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
    def IsExactMatch(self, otherEntry):

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

    def IsMatchableAbbreviation(self, otherEntry):
        isAbbreviationMatch = False
        match = re.fullmatch(r'\b[A-Z]*', otherEntry.Line)
        if match:
            abbreviation = otherEntry.Abbreviation.lower()
            if abbreviation == self.MainEntry.Line.lower():
                isAbbreviationMatch = True
            else:
                for synonym in self.Synonyms:
                    if synonym.Abbreviation.lower() == abbreviation:
                        isAbbreviationMatch = True
                        break
        return isAbbreviationMatch
        
    def IsExactMatchSansType(self, otherEntry):
        isMatch = False
        matchLineSansType = otherEntry.Line.lower()
        if 'type' in matchLineSansType:
            index = matchLineSansType.index('type')
            matchLineSansType = matchLineSansType[:index - 1]
            if self.MainEntry.Line.lower() == matchLineSansType:
                isMatch = True
            else:
                for synonym in self.Synonyms:
                    if synonym.Line.lower() == matchLineSansType:
                        isMatch = True
                        break
        return isMatch

    def ExactMatchButErroneousSpacePlacement(self, otherEntry):
        isMatch = False
        line = otherEntry.Line.lower()
        match = re.search(r' *\'', line)
        if match:
            line = re.sub(r' *\'', '\'', line)
            if self.MainEntry.Line.lower() == line:
                isMatch = True
            else:
                for synonym in self.Synonyms:
                    if synonym.Line.lower() == line:
                        isMatch = True
                        break
        return isMatch

    def ExactMatchSubstring(self, otherEntry):
        
        return False

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
        self.PosTags = nltk.pos_tag(self.Tokens)

        # is this already an abbreviation?
        match = re.fullmatch(r'\b[A-Z]+', line)
        
        if match:
            self.Abbreviation = line
        else:
            self.Abbreviation = ''.join([t[0][0].upper() for t in self.PosTags if t[1] != "IN"])

def CreateAndSerializeMeshDescriptorRecords(xmlDescPath, xmlSupplePath, outputPicklePath):
    descTree = lxml.etree.parse(xmlDescPath)
    
    diseases = descTree.xpath(".//DescriptorRecord/TreeNumberList/TreeNumber[starts-with(text(), 'C')]/../../DescriptorName/String/text()")

    terms = []
    start = time.time()
    number = 1
    for disease in diseases:
        print(str(number) + "/" + str(len(diseases)) + ": " + disease)
        number = number + 1
        term = Term()
        term.MainEntry = Entry(disease)
        synonymNames = descTree.xpath('.//DescriptorRecord/DescriptorName/String[text()="' + disease + '"]/../../ConceptList/Concept/TermList/Term/String/text()')
        for synonymName in synonymNames:
            if not synonymName == disease:
                print('\t' + synonymName)
                term.Synonyms.append(Entry(synonymName))

        terms.append(term)

    with open(outputPicklePath, "wb") as p:
        pickle.dump(terms, p)

    return terms

def LoadAndDeserializeMeshDescriptorRecords(descriptorPath):
    terms = []

    with open(descriptorPath, "rb") as p:
        terms = pickle.load(p)

    return terms

# work desktop
#nltk.data.path.append('D:/PythonData/nltk_data')
#lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()
#descFilePath = 'D:/BioNLP/desc2017.xml'
#suppFilePath = 'D:/BioNLP/supp2017.xml'
#descriptorPath = 'D:/BioNLP/parsed.pickle'
#errorsFilePath = 'D:/BioNLP/errors.txt'

# home laptop
nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
lines = open('c:/users/ben/desktop/bionlp/threeormore.txt', 'r').readlines()
descriptorPath = "c:/users/ben/desktop/bionlp/parsed.pickle"
descFilePath = 'C:/Users/Ben/Desktop/BioNLP/desc2017.xml'
suppFilePath = 'C:/Users/Ben/Desktop/BioNLP/supp2017.xml'
errorsFilePath = 'C:/Users/Ben/Desktop/BioNLP/errors.txt'

toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

#meshDescriptorRecords = CreateAndSerializeMeshDescriptorRecords(descFilePath,
#    suppFilePath, descriptorPath)
meshDescriptorRecords = LoadAndDeserializeMeshDescriptorRecords(descriptorPath)

errors = open(errorsFilePath,'w+')
matches = []
toMatchCount = 1

fullMatch = 0
abbreviationMatch = 0
sansTypeMatch = 0
failureCount = 0
spacingFix = 0

for toMatchEntry in toMatchEntries:
    print(str(toMatchCount) + "/" + str(len(toMatchEntries)))
    toMatchCount = toMatchCount + 1

    found = False
    for meshDescriptorRecord in meshDescriptorRecords:

        if meshDescriptorRecord.IsExactMatch(toMatchEntry):
            fullMatch = fullMatch + 1
            found = True
            break
        elif meshDescriptorRecord.IsMatchableAbbreviation(toMatchEntry):
            found = True
            abbreviationMatch = abbreviationMatch + 1
            break
        elif meshDescriptorRecord.IsExactMatchSansType(toMatchEntry):
            found = True
            sansTypeMatch = sansTypeMatch + 1
            break
        elif meshDescriptorRecord.ExactMatchButErroneousSpacePlacement(toMatchEntry):
            spacingFix = spacingFix + 1
            found = True
            break

    if not found:
        failureCount = failureCount + 1
        errors.write(toMatchEntry.Line + "\n")
    else:
        matches.append(toMatchEntry)

errors.close()

#http://www.nltk.org/howto/wordnet.html
print("Match score is " + str((len(matches) / (len(toMatchEntries)) * 100)) + "%")
print("Full match " + str(fullMatch) + ", Abbreviation Match: " + str(abbreviationMatch) + \
    ", Sans Type: " + str(sansTypeMatch) + ", Spacing fix: " + str(spacingFix))
print("Failure count: " + str(failureCount))