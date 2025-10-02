import re

source_code = '''name { "Snake the game" }
version { 0.1 }
'''
pos = 0

rex1 = re.compile(r'\b(?!\d)\w+\b')
nlmatch = rex1.match(source_code, pos)

print(nlmatch)

if nlmatch:
    pos = nlmatch.end(0)
    #print(source_code[pos])
else: 
    print("no new line found. error")