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
my_phrases = ["Diabetes Mellitus, Insulin-Dependent, 22",
              "Dipsogenic Diabetes Insipidus",
              "Mitochondrial Myopathy with Diabetes",
              "adenovirus type-2 vaccine (canine)",
              "Diabetes Mellitus, Type 2"]

#  and you want to find the most similar document
#  to this document             
phrase = ["type-2 diabetes"]

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

print(answer)

# i bet it reduces to the words in the matrx (the vocabulary on which it was trained)
#output = vectorizer.transform(["boring answer dog"])
#result = (output * my_features[1:,:].T).A[0]
#best_score = np.argmax(result)
#answer = my_phrases[best_score]

print()