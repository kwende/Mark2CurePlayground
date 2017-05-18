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


nltk.data.path.append('D:/PythonData/nltk_data')
lines = open('c:/users/brush/desktop/threeormore.txt', 'r').readlines()

toMatchEntries = []
for line in lines:
    entry = Entry(line)
    toMatchEntries.append(entry)

tree = lxml.etree.parse('D:/BioNLP/desc2017.xml')
descriptorNames = tree.xpath(".//DescriptorRecord/DescriptorName/String/text()")

matchableDescriptorNames = []
for descriptorName in descriptorNames:
    entry = Entry(descriptorName)
    matchableDescriptorNames.append(entry)

    #http://www.nltk.org/howto/wordnet.html
print()
