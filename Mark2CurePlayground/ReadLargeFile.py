#!/usr/bin/env python3
import mmap

with open('C:/Users/Ben/Desktop/BioNLP/supp2017.xml', 'rb', 0) as file, \
     mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
    i = 0
    while True:
        i = s.find(b'ALG1', i+1) #do another find, loop over all
        if i != -1:
            part = s[i-20:i+20]
            print(part)
        else:
            break
