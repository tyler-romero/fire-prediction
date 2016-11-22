filenames = [\
'addresses2009.txt', \
'addresses2010.txt', \
'addresses2011.txt', \
'addresses2012.txt', \
'addresses2013.txt', \
'addresses2014.txt', \
'addresses2015.txt', \
'addresses2016.txt', \
]

out = open('small.txt','w')

count = 0
addressDict = {}
for n in filenames:
	print n
	f = open(n,'rU')
	for line in f:
		if line.strip() not in addressDict:
			addressDict[line.strip()] = 1
		else:
			addressDict[line.strip()] += 1

count = 0
for el in addressDict.keys():
	count += 1
	out.write(el)
	out.write('\n')

print count