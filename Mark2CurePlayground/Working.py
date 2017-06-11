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

import os.path

from nltk.metrics import *

class MeshRecord:

    def __init__(self, mainLine, synonyms):

        self.MainLine = self.CleanText(mainLine)
        self.Synonyms = [self.CleanText(s) for s in synonyms]

        return

    def CleanText(self, text):

        toReturn = text
        toReturn = toReturn.replace(" 's","'s")

        return toReturn

    def IsExactMatch(self, mark2CureQuery):
        
        textToMatch = mark2CureQuery.Tag.lower()

        if self.MainLine.lower() == textToMatch:
            quality = 1
        else:
            for synonym in self.Synonyms:
                if synonym.lower() == textToMatch:
                    quality = 1
                    break

    def GetAbbreviationQuality(self, abbreviation):

        tokens = word_tokenize(self.MainLine)
        probableAbbreviationLetters = "".join([t[0][0] for t in nltk.pos_tag(tokens) if t[1] != "IN"])

        smallestDistance = edit_distance(abbreviation, probableAbbreviationLetters)

        for synonym in self.Synonyms:
            tokens = word_tokenize(self.MainLine)
            probableAbbreviationLetters = "".join([t[0][0] for t in nltk.pos_tag(tokens) if t[1] != "IN"])

            curDistance = edit_distance(abbreviation, probableAbbreviationLetters)
            if curDistance < smallestDistance:
                smallestDistance = curDistance

        return smallestDistance


class Mark2CureQuery:

    def __init__(self, tag, sourceText):
        self.Tag = tag
        self.SourceText = sourceText

        return

    def FindAbbreviationMeaningInSource(self, abbreviation):
        sourceText = self.SourceText
        ret = None
        match = re.search(r"\( ?" + abbreviation.upper() + " ?\)", sourceText)
        if match:
            str = match.group(0).replace(")","").replace("(","").strip()
            strAsCharsReversed = list(reversed(list(str.lower())))
            strIndex = sourceText.index(match.group(0))
            curIndex = strIndex - 1
            failureCount = 0
            indices = []
            stillGood = True

            for char in strAsCharsReversed:

                for i in reversed(range(curIndex)):
                    if sourceText[i].lower() == char and i > 0 and sourceText[i - 1] == ' ':
                        failureCount = 0
                        indices.append(i)
                        curIndex = i
                        break
                    elif i == 0 and sourceText[i].lower() == char:
                        failureCount = 0
                        indices.append(i)
                        break
                    elif sourceText[i] == ' ':
                        failureCount = failureCount + 1

                    if failureCount >= 3:
                        stillGood = False
                        break

                if not stillGood:
                    break

            if stillGood:
                ret = sourceText[indices[len(indices) - 1]:strIndex - 1].strip()

            return ret

class TFIDF:

    def __init__(self):
        self.Model = None
        self.RecordsTrainedOn = []
        self.Vectorizer = TfidfVectorizer(stop_words="english")
        self.Corpus = []
        self.RecordMap = []

    def TrainModel(self, meshRecords):
        translator = str.maketrans('', '', string.punctuation)

        recordIndex = 0
        for meshRecord in meshRecords:
            self.Corpus.append(meshRecord.MainLine.lower().translate(translator))
            self.RecordMap.append(recordIndex)

            for synonym in meshRecord.Synonyms:
                self.Corpus.append(synonym.lower().translate(str.maketrans(translator)))
                self.RecordMap.append(recordIndex)

            recordIndex = recordIndex + 1

        self.Model = self.Vectorizer.fit_transform(self.Corpus)
        self.RecordsTrainedOn = meshRecords

        return

    def FindClosestMatches(self, queryText, numberToReturn):
        translator = str.maketrans('', '', string.punctuation)
        matchMatrix = self.Vectorizer.transform([queryText.lower().translate(translator)])
        resultMatrix = ((matchMatrix * self.Model.T).A[0])

        matchedRecords = []
        if np.any(resultMatrix):
            bestChoicesIndices = np.argpartition(resultMatrix, -numberToReturn)[-numberToReturn:]

            for bestChoiceIndex in bestChoicesIndices:
                record = self.RecordsTrainedOn[self.RecordMap[bestChoiceIndex]]
                if not record in matchedRecords:
                    matchedRecords.append(record)

        return matchedRecords

def BuildMeshRecordsFromDisk(xmlFilePath):
    meshRecords = []
    descTree = lxml.etree.parse(xmlFilePath)
    
    num = 0
    diseases = descTree.xpath(".//DescriptorRecord/TreeNumberList/TreeNumber[starts-with(text(), 'C')]/../../DescriptorName/String/text()")
    for disease in diseases:
        synonymNames = descTree.xpath('.//DescriptorRecord/DescriptorName/String[text()="' + disease + '"]/../../ConceptList/Concept/TermList/Term/String/text()')
        synonymsToUse = []
        for synonymName in synonymNames:
            if not synonymName == disease:
                synonymsToUse.append(synonymName)

        meshRecords.append(MeshRecord(disease, synonymsToUse))

        print("Finished " + str(num) + " of " + str(len(diseases)))
        num = num + 1

    return meshRecords

def ReadMeshRecordsFromDisk(picklePath):
    meshRecords = []

    with open(picklePath, "rb") as p:
        meshRecords = pickle.load(p)

    return meshRecords

def FindRecommendations(query, meshRecords, tfidf, numberOfRecommendations):
    
    meshRecordsToReturn = []

    # can i find an exact match?
    for meshRecord in meshRecords:
        if meshRecord.IsExactMatch(query):
            meshRecordsToReturn.append(meshRecord)
            break

    # if no perfect matches found, use if-idf to find best we can
    if len(meshRecordsToReturn) == 0:
        meshRecordsToReturn = meshRecordsToReturn + tfidf.FindClosestMatches(query.Tag, numberOfRecommendations)

    # still nothing?  is this an abbreviation?  Can we pull out its meaning
    # from the source text?
    if len(meshRecordsToReturn) == 0:
        matches = re.fullmatch(r"[A-Z0-9]*(-[A-Z0-9a-z]*)?", query.Tag)
        if matches:
            possibleMeaning = query.FindAbbreviationMeaningInSource(query.Tag)
            if possibleMeaning:
                meshRecordsToReturn = meshRecordsToReturn + tfidf.FindClosestMatches(possibleMeaning, numberOfRecommendations)

    # still nothing?  is this an abbreviation that we can
    # maybe try finding matching letters in the mesh list?
    if len(meshRecordsToReturn) == 0:
        matches = re.fullmatch(r"[A-Z0-9]*(-[A-Z0-9a-z]*)?", query.Tag)
        if matches:
            smallestDistance = 100000000

            bestDistances = []
            for meshRecord in meshRecords:
                curDistance = meshRecord.GetAbbreviationQuality(query.Tag)
                if curDistance < len(query.Tag) * .5:
                    if curDistance < smallestDistance:
                        smallestDistance = curDistance
                        bestDistances = []
                        bestDistances.append(meshRecord)
                    elif curDistance == smallestDistance:
                        bestDistances.append(meshRecord)

            meshRecordsToReturn = meshRecordsToReturn + bestDistances

    return meshRecordsToReturn

def ReadMark2CureQueriesFromDisk(mark2CureFile, minToCount):
    phrases = {}
    tree = lxml.etree.parse(mark2CureFile)

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
            ret.append(Mark2CureQuery(v, k))
            
    return ret 

###########################################################
# MAIN
###########################################################

# work desktop constants
#nltk.data.path.append('D:/PythonData/nltk_data')
#descFilePath = 'D:/BioNLP/desc2017.xml'
#suppFilePath = 'D:/BioNLP/supp2017.xml'
#pickledDescriptorsPath = 'D:/BioNLP/descriptors.pickle'
#errorsFilePath = 'D:/BioNLP/errors.txt'
#matchFilesPath = 'D:/BioNLP/matchFile.txt'
#mark2CureFile = 'D:/BioNLP/group 25.xml'
#failureFile = 'D:/BioNLP/failures.txt'

# surface constants
nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
descFilePath = 'c:/users/ben/desktop/BioNLP/desc2017.xml'
suppFilePath = 'c:/users/ben/desktop/BioNLP/supp2017.xml'
pickledDescriptorsPath = 'c:/users/ben/desktop/BioNLP/descriptors.pickle'
errorsFilePath = 'c:/users/ben/desktop/BioNLP/errors.txt'
matchFilesPath = 'c:/users/ben/desktop/BioNLP/matchFile.txt'
mark2CureFile = 'c:/users/ben/desktop/BioNLP/group 25.xml'
failureFile = 'c:/users/ben/desktop/BioNLP/failures.txt'

# either read anew and serialize, or deserialize from disk
print("Reading records disk...")
#records = BuildMeshRecordsFromDisk(descFilePath)
#with open(pickledDescriptorsPath, "wb") as p:
#    pickle.dump(records, p)
meshRecords = ReadMeshRecordsFromDisk(pickledDescriptorsPath)
print("...done")

print("Training model from records...")
tfidf = TFIDF()
tfidf.TrainModel(meshRecords)
print("...done")

print("Load Mark2Cure data from disk...")
mark2CureQueries = ReadMark2CureQueriesFromDisk(mark2CureFile, 4)
print("...done")

print("Find matches...")
if os.path.isfile(errorsFilePath):
    os.remove(errorsFilePath)
if os.path.isfile(matchFilesPath):
    os.remove(matchFilesPath)
errors = open(errorsFilePath, "w+")
matches = open(matchFilesPath, "w+")
count = 1
for mark2CureQuery in mark2CureQueries:
    recommendations = FindRecommendations(mark2CureQuery, meshRecords, tfidf, 4)
    if len(recommendations) > 0:
        matches.write(mark2CureQuery.Tag + "\n")
        for recommendation in recommendations:
            matches.write("\t" + recommendation.MainLine + "\n")
    else:
        errors.write(mark2CureQuery.Tag + "\n")
    print(str(count) + " of " + str(len(mark2CureQueries)))
    count = count + 1
errors.close()
matches.close()

print("...done")