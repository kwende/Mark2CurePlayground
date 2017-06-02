import lxml.etree
from nltk.stem import *
import nltk
from nltk import word_tokenize
import time
import pickle
import re
import string
import datetime as dt

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
import numpy as np

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

    def IsExactMatchAbbreviationAfterEllipsesRemoved(self, otherEntry):
        line = otherEntry.Line.lower()
        isMatch = False

        if line == re.sub("[\(\[].*?[\)\]]", "", self.MainEntry.Line).lower().strip():
            isMatch = True
        else:
            for synonym in self.Synonyms:
                if line == re.sub("[\(\[].*?[\)\]]", "", synonym.Line).lower().strip():
                    isMatch = True
                    break
        return isMatch

    def IsMatchableAbbreviation(self, otherEntry):
        isAbbreviationMatch = False
        match = re.fullmatch(r'\b[A-Z]*', otherEntry.Line)
        if match:
            abbreviation = otherEntry.Abbreviation.lower()
            if abbreviation == self.MainEntry.Abbreviation.lower():
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

    def ExactMatchOfStems(self, otherEntry):
        
        isMatch = False

        if len(self.MainEntry.Stems) == len(otherEntry.Stems):
            matches = 0
            # Check main entry
            for mainStem in self.MainEntry.Stems:
                for otherStem in otherEntry.Stems:
                    if mainStem.lower() == otherStem.lower():
                        matches = matches + 1

            if matches == len(otherEntry.Stems):
                isMatch = True
            else:
                # Check synonyms
                for synonym in self.Synonyms:
                    for mainStem in synonym.Stems:
                        for otherStem in otherEntry.Stems:
                            if mainStem.lower() == otherStem.lower():
                                matches = matches + 1             

        return isMatch

    def PhraseExistsIn(self, otherEntry):
        isMatch = False 

        if len(otherEntry.Tokens) > 0:
            if self.MainEntry.Line.lower() in otherEntry.Line.lower() and \
                (len(self.MainEntry.Line) / len(otherEntry.Line)) > .7:
                isMatch = True
            else:
                for synonym in self.Synonyms:
                    if synonym.Line.lower() in otherEntry.Line.lower() and \
                    (len(synonym.Line) / len(otherEntry.Line)) > .7:
                        isMatch = True

        return isMatch

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
nltk.data.path.append('D:/PythonData/nltk_data')
lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()
descFilePath = 'D:/BioNLP/desc2017.xml'
suppFilePath = 'D:/BioNLP/supp2017.xml'
descriptorPath = 'D:/BioNLP/parsed.pickle'
errorsFilePath = 'D:/BioNLP/errors.txt'
matchFilesPath = 'D:/BioNLP/matchFile.txt'

# home laptop
#nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
#lines = open('c:/users/ben/desktop/bionlp/threeormore_trimmed.txt',
#'r').readlines()
#descriptorPath = "c:/users/ben/desktop/bionlp/parsed.pickle"
#descFilePath = 'C:/Users/Ben/Desktop/BioNLP/desc2017.xml'
#suppFilePath = 'C:/Users/Ben/Desktop/BioNLP/supp2017.xml'
#errorsFilePath = 'C:/Users/Ben/Desktop/BioNLP/errors.txt'
toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

#meshDescriptorRecords = CreateAndSerializeMeshDescriptorRecords(descFilePath,
#    suppFilePath, descriptorPath)
meshDescriptorRecords = LoadAndDeserializeMeshDescriptorRecords(descriptorPath)

corpus = []
translator = str.maketrans('', '', string.punctuation)
for meshDescriptorRecord in meshDescriptorRecords:
    corpus.append(meshDescriptorRecord.MainEntry.Line.lower().translate(translator))

    for synonym in meshDescriptorRecord.Synonyms:
        corpus.append(synonym.Line.lower().translate(str.maketrans(translator)))

print("...starting the transform.")
start = dt.datetime.now()
tfidf = TfidfVectorizer(stop_words="english")
featuresMatrix = tfidf.fit_transform(corpus)
end = dt.datetime.now()

#output = tfidf.transform(["type-2 diabetes"])
#result = ((output * features.T).A[0])
#choices = np.argpartition(result, -4)[-4:]

#pickedPhrases = []
#for choice in choices:
#    pickedPhrases.append(corpus[choice])

#print("Process took " + str((end - start).total_seconds()) + " seconds.")

#with open("c:/users/brush/desktop/tfidf.pickle", "wb") as p:
#    pickle.dump(tfidf, p)

#with open("c:/users/brush/desktop/features.pickle", "wb") as p:
#    pickle.dump(features, p)
matchFile = open(matchFilesPath,'w+')
matches = []
toMatchCount = 1

fullMatch = 0
abbreviationMatch = 0
sansTypeMatch = 0
failureCount = 0
spacingFix = 0
exactStemMatch = 0
existsIn = 0

#toMatchEntries = [e for e in toMatchEntries if e.Line == "ALS"]
#meshDescriptorRecords = [d for d in meshDescriptorRecords if d.MainEntry.Line == "Amyotrophic Lateral Sclerosis"]

for toMatchEntry in toMatchEntries:
    print(str(toMatchCount) + "/" + str(len(toMatchEntries)))
    toMatchCount = toMatchCount + 1

    exactMatchDescriptor = None
    highestScore = 0
    currentScore = 0
    # try to find exact matches, or very, very close to exact.
    for meshDescriptorRecord in meshDescriptorRecords:
        if meshDescriptorRecord.IsExactMatch(toMatchEntry):
            fullMatch = fullMatch + 1
            currentScore = 6
        elif meshDescriptorRecord.ExactMatchOfStems(toMatchEntry):
            exactStemMatch = exactStemMatch + 1
            currentScore = 5
        elif meshDescriptorRecord.ExactMatchButErroneousSpacePlacement(toMatchEntry):
            spacingFix = spacingFix + 1
            currentScore = 5
        elif meshDescriptorRecord.IsExactMatchAbbreviationAfterEllipsesRemoved(toMatchEntry):
            currentScore = 4.5
        elif meshDescriptorRecord.PhraseExistsIn(toMatchEntry):
            existsIn = existsIn + 1
            currentScore = 4
        elif meshDescriptorRecord.IsExactMatchSansType(toMatchEntry):
            sansTypeMatch = sansTypeMatch + 1
            currentScore = 3
        elif meshDescriptorRecord.IsMatchableAbbreviation(toMatchEntry):
            abbreviationMatch = abbreviationMatch + 1
            currentScore = 2
        
        if highestScore < currentScore:
            exactMatchDescriptor = meshDescriptorRecord
            highestScore = currentScore

    if highestScore == 0:
        # find best.  couldn't get best match.
        matchMatrix = tfidf.transform([toMatchEntry.Line])
        resultMatrix = ((matchMatrix * featuresMatrix.T).A[0])
        bestChoicesIndices = np.argpartition(resultMatrix, -4)[-4:]
        matchFile.write(toMatchEntry.Line + ": \n")
        for bestChoiceIndex in bestChoicesIndices:
            matchFile.write("\t" + corpus[bestChoiceIndex] + "\n")
    else:
        matchFile.write(toMatchEntry.Line + ": \n\t" + exactMatchDescriptor.MainEntry.Line + "\n")

    #if not exactFound:
    #    failureCount = failureCount + 1
    #    #errors.write(toMatchEntry.Line + "\n")
    #else:
    #    matches.append(toMatchEntry)
matchFile.close()

#http://www.nltk.org/howto/wordnet.html
print("Match score is " + str((len(matches) / (len(toMatchEntries)) * 100)) + "%")
print("Full match " + str(fullMatch))
print("Abbreviation Match: " + str(abbreviationMatch))
print("Sans Type: " + str(sansTypeMatch) + ", Spacing fix: " + str(spacingFix))
print("Exact stem match: " + str(exactStemMatch))
print("Exists in: " + str(existsIn))
#print("====")
#print("Failure count: " + str(failureCount))