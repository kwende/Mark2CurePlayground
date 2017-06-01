#https://stats.stackexchange.com/questions/73908/search-in-tf-idf

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
import numpy as np
from nltk.stem import *
import nltk
from nltk import word_tokenize

def TfidTokenizer(text):
    stemmer = PorterStemmer()
    tokens = nltk.word_tokenize(text)
    stems = []
    for token in tokens:
        stems.append(stemmer.stem(token))

nltk.data.path.append('D:/PythonData/nltk_data')

# each phrase here could be document in your list 
# of documents
my_phrases = ["boring answer phrase",
              "exciting phrase",
              "phrase on stackoverflow",
              "answer on stackoverflow"]

#  and you want to find the most similar document
#  to this document             
phrase = ["stackoverflow answer"]

# You could do it like this:
vectorizer = TfidfVectorizer(stop_words='english')
all_phrases = phrase + my_phrases
my_features = vectorizer.fit_transform(all_phrases)

#interesting. this computes the dot product for all the vectors against the 
#first vector. and then returns the results as an array, which can have argmax 
#ran over it. 
scores = (my_features[0, :] * my_features[1:, :].T).A[0]
best_score = np.argmax(scores)
answer = my_phrases[best_score]

# i bet it reduces to the words in the matrx (the vocabulary on which it was trained)
output = vectorizer.transform(["boring answer dog"])
result = (output * my_features[1:,:].T).A[0]
best_score = np.argmax(result)
answer = my_phrases[best_score]

print()