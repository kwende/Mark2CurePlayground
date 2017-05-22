import lxml.etree
from nltk.stem import *
import nltk
from nltk import word_tokenize
import time
import pickle

#http://www.nltk.org/howto/metrics.html
#https://www.nlm.nih.gov/mesh/topsubscope.html*-
class Term:
    MainEntry = None
    Synonyms = []

class Entry:
    
    Line = ""
    Tokens = []
    ImportantWords = []

    def __init__(self, line):
        line = line.replace(',','')
        self.Line = line
        self.Tokens = word_tokenize(line)
        porter = PorterStemmer()
        tags = nltk.pos_tag(self.Tokens)
        okayTags = ['NN', 'NNS', 'JJ']    

        self.ImportantWords = [porter.stem(t[0]) for t in tags if t[1] in okayTags or t[0].isdigit()]

    # https://stackoverflow.com/questions/2489669/function-parameter-types-in-python
    #def ComputeDistance(Entry: otherEntry):


#nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
nltk.data.path.append('D:/PythonData/nltk_data')
lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()
#lines = open('c:/users/ben/desktop/bionlp/threeormore.txt', 'r').readlines()

toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

#tree = lxml.etree.parse('C:/Users/Ben/Desktop/BioNLP/desc2017.xml')
tree = lxml.etree.parse('D:/BioNLP/desc2017.xml')

descriptorNames = tree.xpath(".//DescriptorRecord/AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName/String[text()='diagnosis']/../../../../../DescriptorName/String/text()")
number = len(descriptorNames)
terms = []

start = time.time()
for descriptorName in descriptorNames:
    term = Term()
    term.MainEntry = Entry(descriptorName)
    synonymNames = tree.xpath('.//DescriptorRecord/DescriptorName/String[text()="' + descriptorName + '"]/../../ConceptList/Concept/TermList/Term/String/text()')
    for synonymName in synonymNames:
        print(synonymName)
        if not synonymName == descriptorName:
            term.Synonyms.append(Entry(synonymName))

    terms.append(term)    

with open("c:/users/brush/desktop/parsed.pickle", "wb") as p:
    pickle.dump(terms, p)

end = time.time()
elapsed = end - start
print(elapsed)

#matchableDescriptorNames = []
#for descriptorName in descriptorNames:
#    entry = Entry(descriptorName)
#    matchableDescriptorNames.append(entry)

#http://www.nltk.org/howto/wordnet.html

