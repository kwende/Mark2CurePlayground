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

class Entry:

    def __init__(self, line):
        self.Line = ""
        self.Tokens = []
        self.ImportantWords = []

        line = line.replace(',','')
        self.Line = line
        self.Tokens = word_tokenize(line)
        porter = PorterStemmer()
        tags = nltk.pos_tag(self.Tokens)
        okayTags = ['NN', 'NNS', 'JJ']    

        self.ImportantWords = [porter.stem(t[0]) for t in tags if t[1] in okayTags or t[0].isdigit()]

    # https://stackoverflow.com/questions/2489669/function-parameter-types-in-python
    #def ComputeDistance(Entry: otherEntry):


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

#terms = []
#with open("c:/users/brush/desktop/parsed.pickle", "rb") as f:
#    terms = pickle.load(f)

#term = None
#with open("c:/users/brush/desktop/parsed.pickle", "rb") as f:
#    term = pickle.load(f)
descriptorNames = tree.xpath(".//DescriptorRecord/AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName/String[text()='diagnosis']/../../../../../DescriptorName/String/text()")
number = len(descriptorNames)
terms = []
start = time.time()
for descriptorName in descriptorNames:
    term = Term()
    term.MainEntry = Entry(descriptorName)
    synonymNames = tree.xpath('.//DescriptorRecord/DescriptorName/String[text()="' + descriptorName + '"]/../../ConceptList/Concept/TermList/Term/String/text()')
    for synonymName in synonymNames:
        if not synonymName == descriptorName:
            term.Synonyms.append(Entry(synonymName))

    terms.append(term) 

end = time.time()
elapsed = end - start
print(elapsed)

with open("c:/users/brush/desktop/parsed.pickle", "wb") as p:
    pickle.dump(term, p)

print()
#matchableDescriptorNames = []
#for descriptorName in descriptorNames:
#    entry = Entry(descriptorName)
#    matchableDescriptorNames.append(entry)

#http://www.nltk.org/howto/wordnet.html

