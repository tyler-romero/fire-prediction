file_list = ['2009','2010','2011','2012','2013','2014','2015','2016']

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

o = open('all_addresses','w')


for year in file_list:
	fileName = '../incidents' + year + '.csv'
	f = open(fileName,'rU')
	first = 1
	for line in f:
		if first == 1:
			first = 0
			continue
		splitList = splitComma(line)
		if splitList[4] == '':
			continue
		else:
			s = splitList[4].strip() + ' San Diego, CA'
			o.write(s)
			o.write('\n')












