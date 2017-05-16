import os
import lxml.etree

phrases = {}
#tree = lxml.etree.parse('C:/Users/ben/desktop/group 25.xml')
tree = lxml.etree.parse('D:/BioNLP/group 25.xml')
for atext in tree.xpath(".//document/passage/annotation/infon[@key='type' and text() = 'disease']/../text"):
    phrase = atext.text
    if phrase in phrases:
        phrases[phrase] = phrases[phrase] + 1
    else:
        phrases[phrase] = 1

f = open('c:/users/brush/desktop/threeormore.txt', 'w+')
for k,v in phrases.items():
    if v > 3:
        f.write(k + "\n")
f.close()