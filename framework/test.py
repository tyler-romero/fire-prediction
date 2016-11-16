f = open('incidents2016.csv','rU')

'''
import csv
with open('incidents2009.csv', 'rU') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        print ', '.join(row)

'''
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

for line in f:
	if len(splitComma(line)) != 11:
		print 'fail'







