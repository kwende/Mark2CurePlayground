import csv

causeResults = {}
diagnosis = {}

with open('c:/users/brush/desktop/survey/survey.csv', 'r') as csvFile:
    csvReader = csv.reader(csvFile)

    readHeader = False
    for row in csvReader:
        if readHeader:
            startedWith = row[1]
            diagRow = row[4].lower()
            bits = startedWith.split(";")
            for bit in bits:
                if not bit in causeResults:
                    causeResults[bit] = 1
                else:
                    causeResults[bit] = causeResults[bit] + 1
            if not diagRow in diagnosis:
                diagnosis[diagRow] = 1
            else:
                diagnosis[diagRow] = diagnosis[diagRow] + 1
        else:
            readHeader = True

#with open('c:/users/brush/desktop/results.csv', 'w+') as fout:
    
#    for k,v in causeResults.items():
#        k = k.replace('"', '')
#        fout.write('"' + k + '",' + str(v) + "\n")
#        fout.flush()


with open('c:/users/brush/desktop/diagnosis.csv', 'w+') as fout:
    
    for k,v in diagnosis.items():
        k = k.replace('"', '')
        fout.write('"' + k + '",' + str(v) + "\n")
        fout.flush()

