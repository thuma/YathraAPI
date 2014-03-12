from bs4 import BeautifulSoup
import re


datafile = open('hlt.html','r')
data = datafile.read()
bs = BeautifulSoup(data)
#print bs .findAll('div', id=lambda x: x and x.startswith('result-')
print bs.findAll('div', id=re.compile('^result-'))

