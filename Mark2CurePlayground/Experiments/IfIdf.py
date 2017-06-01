#https://stats.stackexchange.com/questions/73908/search-in-tf-idf

from sklearn.feature_extraction.text import TfidfVectorizer
#import numpy as np

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
vectorizer = TfidfVectorizer(min_df=1, stop_words='english')
all_phrases = phrase + my_phrases
my_features = vectorizer.fit_transform(all_phrases)

print()
#scores = (my_features[0, :] * my_features[1:, :].T).A[0]
#best_score = np.argmax(scores)
#answer = my_phrases[best_score]