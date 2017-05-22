from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
from nltk.stem import *
import nltk

#http://parrotprediction.com/dive-into-wordnet-with-nltk/

nltk.data.path.append('D:/PythonData/nltk_data')

weakness = wn.synsets('weakness')
atrophy = wn.synsets('atrophy')

dist = weakness[0].path_similarity(atrophy[0])

print()