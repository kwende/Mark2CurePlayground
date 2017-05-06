from nltk.stem import *
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download()

#stemm =  PorterStemmer()
#stemm = SnowballStemmer("english")
stemm = LancasterStemmer()

nltk.data.path.append('D:/PythonData/nltk_data')

wnl = WordNetLemmatizer()
print(wnl.lemmatize('seizures'))

plurals = ['seizures']

singles = [stemm.stem(plural) for plural in plurals]

for single in singles:
    print(single)