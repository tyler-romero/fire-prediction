f = open('addresses/just_address_data/small_matched.csv','rU')

def splitComma(myStr):
	#necessary because data has form _one,_two,"three, three continued", four
	returnList = []
	previous = 0
	inquotes = 0
	for i in xrange(0,len(myStr)):
		if myStr[i] == '"':
			if inquotes == 1:
				inquotes = 0
			else:
				inquotes = 1
		if myStr[i] == ",":
			if inquotes == 0:
				returnList.append(myStr[previous:i])
				previous = i+1
	returnList.append(myStr[previous:len(myStr)])
	return returnList

addressDict = {}

for line in f:
	split = splitComma(line)
	add = split[1].strip()
	lat = split[19].strip()
	lng = split[20].strip()
	addressDict[add] = (lat,lng)

filenames = [\
'incidents2009.csv',\
'incidents2010.csv',\
'incidents2011.csv',\
'incidents2012.csv',\
'incidents2013.csv',\
'incidents2014.csv',\
'incidents2015.csv',\
'incidents2016.csv'\
]

missed = 0

for name in filenames:
	print name
	fl = open(name,'rU')
	outFileName = 'new_data/new_' + name
	out = open(outFileName,'w')
	first = 1
	for line in fl:
		if first == 1:
			first = 0
			continue
		split = splitComma(line)
		address = split[4].strip()
		if address not in addressDict:
			missed +=1
			continue
		s = ''
		count = 0
		for el in split:
			if count == 4:
				s += addressDict[address][0] + '_' + addressDict[address][1] + ','
			else:
				s += el.strip() + ','
			count += 1
		s += address + '\n'
		out.write(s)

print missed





















