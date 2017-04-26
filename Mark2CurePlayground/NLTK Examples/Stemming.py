from nltk.stem import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download()

#stemm =  PorterStemmer()
#stemm = SnowballStemmer("english")
stemm = LancasterStemmer()

wnl = WordNetLemmatizer()
print(wnl.lemmatize('dogs'))

plurals = ['seizures']

singles = [stemm.stem(plural) for plural in plurals]

for single in singles:
    print(single)