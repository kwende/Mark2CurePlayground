import pickle

class Entry:
    
    def __init__(self, text):
       self.Text = text

class Term:

    def __init__(self):
        self.Main = None
        self.Synonyms = []


def Save():
    term = Term()
    term.Main = Entry("Dog")
    term.Synonyms.append(Entry("Canine"))
    term.Synonyms.append(Entry("Pursue"))
    term.Synonyms.append(Entry("Follow"))
    term.Synonyms.append(Entry("Plague"))

    terms = []
    terms.append(term)

    with open('output.pickle', 'wb') as p:
        pickle.dump(terms, p)

def Load():
    loadedTerms = []

    with open('output.pickle', 'rb') as p:
        loadedTerms = pickle.load(p)

    return loadedTerms


#Save()
terms = Load()
