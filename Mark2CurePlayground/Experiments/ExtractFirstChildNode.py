import lxml.etree

tree = lxml.etree.parse('C:/Users/Ben\Desktop/BioNLP/supp2017.xml')

node = tree.xpath("/descendant::SupplementalRecord[1]")

content = (lxml.etree.tostring(node[0], pretty_print=True))

with open('c:/users/ben/desktop/supplementalrecord.xml', 'w+') as w:
    w.write(content.decode('utf8'))

print()
