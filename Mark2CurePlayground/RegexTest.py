import re

line = "Content Management System"

match = re.fullmatch(r'\b[A-Z]', line)
        
if match:
    self.Abbreviation = line
else:
    abbreviation = ''.join([w[0].upper() for w in line.split()])
    print(abbreviation)