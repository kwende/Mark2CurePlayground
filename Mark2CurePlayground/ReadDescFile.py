import lxml.etree
from nltk.stem import *
import nltk
from nltk import word_tokenize

class Entry:
    
    Line = ""
    Tokens = []
    ImportantWords = []

    def __init__(self, line):
        self.Line = line
        self.Tokens = word_tokenize(line)
        porter = PorterStemmer()
        tags = nltk.pos_tag(self.Tokens)
        okayTags = ['NN','NNS', 'JJ']    

        self.ImportantWords = [porter.stem(t[0]) for t in tags if t[1] in okayTags]

    # https://stackoverflow.com/questions/2489669/function-parameter-types-in-python
    #def ComputeDistance(Entry: otherEntry):

nltk.data.path.append('C:/Users/Ben/AppData/Roaming/nltk_data')
#nltk.data.path.append('D:/PythonData/nltk_data')
#lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()
lines = open('c:/users/ben/desktop/threeormore.txt', 'r').readlines()

toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

tree = lxml.etree.parse('C:/Users/Ben/Desktop/BioNLP/desc2017.xml')
#tree = lxml.etree.parse('D:/BioNLP/desc2017.xml')
descriptorNames = tree.xpath(".//DescriptorRecord/DescriptorName/String/text()")

for descriptorName in descriptorNames:
    if "CDG" in descriptorName:
        print(descriptorName)

matchableDescriptorNames = []
for descriptorName in descriptorNames:
    entry = Entry(descriptorName)
    matchableDescriptorNames.append(entry)

#http://www.nltk.org/howto/wordnet.html

