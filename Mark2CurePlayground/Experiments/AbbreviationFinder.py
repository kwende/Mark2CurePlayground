import re

txt = "blah b lah blah blah blah ddkdfdk Congenital disorders of glycosylation (CDG) are a growing group of inherited metabolic disorders where enzymatic defects in the formation or processing of glycolipids and/or glycoproteins lead to variety of different diseases. The deficiency of GDP-Man:GlcNAc2-PP-dolichol mannosyltransferase, encoded by the human ortholog of ALG1 from yeast, is known as ALG1-CDG (CDG-Ik). The phenotypical, molecular and biochemical analysis of a severely affected ALG1-CDG patient is the focus of this paper. The patient's main symptoms were feeding problems and diarrhea, profound hypoproteinemia with massive ascites, muscular hypertonia, seizures refractory to treatment, recurrent episodes of apnoea, cardiac and hepatic involvement and coagulation anomalies. Compound heterozygosity for the mutations c.1145T>C (M382T) and c.1312C>T (R438W) was detected in the patient's ALG1-coding sequence. In contrast to a previously reported speculation on R438W we confirmed both mutations as disease-causing in ALG1-CDG."
abbreviation = "CDG"

match = re.search(r"\( ?[A-Z]* ?\)", txt)

if match:
    str = match.group(0).replace(")","").replace("(","").strip()
    strAsCharsReversed = list(reversed(list(str.lower())))
    strIndex = txt.index(str)
    curIndex = strIndex -1
    failureCount = 0
    indices = []
    stillGood = True

    for char in strAsCharsReversed:

        for i in reversed(range(curIndex)):
            if txt[i].lower() == char and i>0 and txt[i-1] == ' ':
                failureCount = 0
                indices.append(i)
                curIndex = i
                break
            elif txt[i] == ' ':
                failureCount = failureCount + 1

            if failureCount >= 3:
                stillGood = False
                break

        if not stillGood:
            break

    if stillGood:
        possiblePhrase = txt[indices[len(indices)-1]:strIndex-1].strip()
        print(possiblePhrase)
    else:
        print("not found.")