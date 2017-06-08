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

#regex to use: \( ?[A-Z]* ?\)

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

    def FindAbbreviationText(self, abbreviation, txt):

        ret = None
        match = re.search(r"\( ?" + abbreviation.upper() + " ?\)", txt)
        if match:
            str = match.group(0).replace(")","").replace("(","").strip()
            strAsCharsReversed = list(reversed(list(str.lower())))
            strIndex = txt.index(match.group(0))
            curIndex = strIndex - 1
            failureCount = 0
            indices = []
            stillGood = True

            for char in strAsCharsReversed:

                for i in reversed(range(curIndex)):
                    if txt[i].lower() == char and i > 0 and txt[i - 1] == ' ':
                        failureCount = 0
                        indices.append(i)
                        curIndex = i
                        break
                    elif i == 0 and txt[i].lower() == char:
                        failureCount = 0
                        indices.append(i)
                        break
                    elif txt[i] == ' ':
                        failureCount = failureCount + 1

                    if failureCount >= 3:
                        stillGood = False
                        break

                if not stillGood:
                    break

            if stillGood:
                ret = txt[indices[len(indices) - 1]:strIndex - 1].strip()

            return ret

    def __init__(self, line, context):
        self.Line = ""
        self.Tokens = []
        self.Stems = []
        self.IsAbbreviation = False
        self.LikelyAbbreviationWords = ""
        self.Context = context

        line = line.replace(',','').replace('\n','')
        self.Line = line
        self.Tokens = word_tokenize(line)
        porter = PorterStemmer()
        self.Stems = [porter.stem(t) for t in self.Tokens]
        self.PosTags = nltk.pos_tag(self.Tokens)
        self.PossibleAbbreviation = ""

        # is this already an abbreviation?
        match = re.fullmatch(r'\b[A-Z]+', line)
        
        if match and context:
            self.IsAbbreviation = True
            self.LikelyAbbreviationWords = self.FindAbbreviationText(line.strip(), self.Context)
            if self.LikelyAbbreviationWords:
                print(line + "--->" + self.LikelyAbbreviationWords)

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

def LoadEntriesFromMark2CureFile(path, minToCount):
    phrases = {}
    #tree = lxml.etree.parse('C:/Users/ben/desktop/group 25.xml')
    tree = lxml.etree.parse(path)

    passages = tree.xpath(".//document/passage/text")

    for passage in passages:

        phrasesThatMatter = []
        annotationTexts = passage.xpath("../annotation/infon[@key='type' and text() = 'disease']/../text/text()")
        annotationCounts = {}
        for annotationText in annotationTexts:
            if not annotationText in annotationCounts:
                annotationCounts[annotationText] = 1
            else:
                annotationCounts[annotationText] = annotationCounts[annotationText] + 1
        phrasesThatMatter = [k for k,v in annotationCounts.items() if v > minToCount]

        phrases[passage.text] = phrasesThatMatter

    ret = []
    for k,vs in phrases.items():
        for v in vs:
            ret.append(Entry(v, k))
            
    return ret 

def FindAllPossibleIfAbbreviation(text, meshDescriptorRecords):
    match = re.fullmatch(r'\b[A-Z0-9]+(-[A-Z0-9]*)?', text)

    if match: 
        str = match.group(0)
        toMatchItems = []
        if "-" in str:
            toMatchItems = str.split("-")
        else:
            toMatchItems = [str]

        bestMatchScore = 0

        for toMatchItem in toMatchItems:
            for meshDescriptorRecord in meshDescriptorRecords:
                tokens = word_tokenize(meshDescriptorRecord.MainEntry.Line)
                posTags = nltk.pos_tag(tokens)
                abbreviationChars = [t[0][0] for t in posTags if not t[1] == "IN"]
                
                print()

    return

# work desktop
nltk.data.path.append('D:/PythonData/nltk_data')
descFilePath = 'D:/BioNLP/desc2017.xml'
suppFilePath = 'D:/BioNLP/supp2017.xml'
descriptorPath = 'D:/BioNLP/parsed.pickle'
errorsFilePath = 'D:/BioNLP/errors.txt'
matchFilesPath = 'D:/BioNLP/matchFile.txt'
mark2CureFile = 'D:/BioNLP/group 25.xml'
failureFile = 'D:/BioNLP/failures.txt'

# home laptop
#nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
#lines = open('c:/users/ben/desktop/bionlp/threeormore_trimmed.txt',
#'r').readlines()
#descriptorPath = "c:/users/ben/desktop/bionlp/parsed.pickle"
#descFilePath = 'C:/Users/Ben/Desktop/BioNLP/desc2017.xml'
#suppFilePath = 'C:/Users/Ben/Desktop/BioNLP/supp2017.xml'
#errorsFilePath = 'C:/Users/Ben/Desktop/BioNLP/errors.txt'
toMatchEntries = LoadEntriesFromMark2CureFile(mark2CureFile, 4)

meshDescriptorRecords = CreateAndSerializeMeshDescriptorRecords(descFilePath,
    suppFilePath, descriptorPath)
#meshDescriptorRecords = LoadAndDeserializeMeshDescriptorRecords(descriptorPath)

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

matchFile = open(matchFilesPath,'w+')
failureFile = open(failureFile, 'w+')
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
#meshDescriptorRecords = [d for d in meshDescriptorRecords if d.MainEntry.Line
#== "Amyotrophic Lateral Sclerosis"]
for toMatchEntry in toMatchEntries:
    print(str(toMatchCount) + "/" + str(len(toMatchEntries)) + "(" + toMatchEntry.Line + ")")
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
        
        if highestScore < currentScore:
            exactMatchDescriptor = meshDescriptorRecord
            highestScore = currentScore

    if highestScore == 0:
        # find best.  couldn't get best match.
        toFind = ""
        if toMatchEntry.IsAbbreviation and toMatchEntry.LikelyAbbreviationWords:
            toFind = toMatchEntry.LikelyAbbreviationWords
        else:
            toFind = toMatchEntry.Line

        matchMatrix = tfidf.transform([toFind])
        resultMatrix = ((matchMatrix * featuresMatrix.T).A[0])

        if not np.any(resultMatrix):
            FindAllPossibleIfAbbreviation(toMatchEntry.Line, meshDescriptorRecords)
            failureFile.write(toMatchEntry.Line + "\n")
        else:
            bestChoicesIndices = np.argpartition(resultMatrix, -4)[-4:]
            matchFile.write(toMatchEntry.Line + ": \n")
            for bestChoiceIndex in bestChoicesIndices:
                matchFile.write("\t" + corpus[bestChoiceIndex] + "\n")
    else:
        matchFile.write(toMatchEntry.Line + ": \n\t" + exactMatchDescriptor.MainEntry.Line + "\n")

matchFile.close()
failureFile.close()

#http://www.nltk.org/howto/wordnet.html
print("Match score is " + str((len(matches) / (len(toMatchEntries)) * 100)) + "%")
print("Full match " + str(fullMatch))
print("Abbreviation Match: " + str(abbreviationMatch))
print("Sans Type: " + str(sansTypeMatch) + ", Spacing fix: " + str(spacingFix))
print("Exact stem match: " + str(exactStemMatch))
print("Exists in: " + str(existsIn))
