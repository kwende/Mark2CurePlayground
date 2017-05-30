import lxml.etree

descTree = lxml.etree.parse('C:/Users/Ben/Desktop/BioNLP/desc2017.xml')

count = descTree.xpath(".//DescriptorRecord/DescriptorName")
#p =
#descTree.xpath('.//DescriptorRecord/DescriptorName/String[translate(text(),
#"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="amyotrophic
#lateral sclerosis"]')
qualifiersAndCount = {}

phrases = open('c:/users/ben/desktop/bionlp/threeormore.txt', 'r').readlines()
toMatchEntries = []
phrases = [p.replace('\n','') for p in phrases]
phraseCount = len(phrases)
for phrase in phrases:
    print("Looking for " + phrase.lower())
    path = './/DescriptorRecord/DescriptorName/String[translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="' + phrase.lower() + '"]'
    descriptor = descTree.xpath(path)
    if not descriptor:
        path = './/DescriptorRecord/ConceptList/Concept/ConceptName/String[translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="' + phrase.lower() + '"]'
        descriptor = descTree.xpath(path)
        path = path + "/../../../../AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName/String/text()"
    else:
        path = path + "/../../AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName/String/text()"

    if descriptor:
        
        allQualifiersForDescriptor = descTree.xpath(path)
        for qualifier in allQualifiersForDescriptor:
            if qualifier not in qualifiersAndCount:
                qualifiersAndCount[qualifier] = 1
            else:
                qualifiersAndCount[qualifier] = qualifiersAndCount[qualifier] + 1

with open("c:/users/ben/desktop/results99.csv", "w+") as f:
    for k,v in qualifiersAndCount.items():
        num = descTree.xpath('.//DescriptorRecord/AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName/String[translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="' + k.lower() + '"]')
        f.write(k + ", " + str(v) + "," + str(len(num)) + "\n")

