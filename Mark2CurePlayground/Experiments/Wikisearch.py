from wikiapi import WikiApi
wiki = WikiApi()
wiki = WikiApi({ 'locale' : 'es'}) # to specify your locale, 'en' is default

wiki.options

results = wiki.find('hereditary myopathies')
print()