import geocoder
import time

year = '2009'
filename = 'incidents'+year+'.csv'
newFileName = 'newincidents'+year+'.csv'
failedFileName = 'failincidents'+year+'.csv'
f = open(filename,'rU')
failed = open(failedFileName,'w')

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

total = 0
totalWorked = 0
just_failed = 0
newDataFile = open(newFileName,'w')
allLines = []
for line in f:
	allLines.append(line)
for i in xrange(0,len(allLines)):
	line = allLines[i]
	if len(splitComma(line)) != 11:
		print 'fail'
	splitList = splitComma(line)
	s = splitList[4] + " San Diego, CA"
	g = geocoder.google(s)
	if len(g.latlng)==2:
		totalWorked+=1
	else:
		if just_failed == 1:
			just_failed = 0
			print g.latlng
			print s
			total+=1
			failed.write(line)
			continue
		else:
			just_failed = 1
			time.sleep(.5)
			i-=1
			continue

	total+=1
	print float(totalWorked)/float(total)
	latlngString = str(g.latlng[0])+ str(g.latlng[1])
	newDataString = ''
	count = 0
	for el in splitList:
		if count == 4:
			newDataString += latlngString + ','
		else:
			newDataString += el + ','
		count += 1
	newDataString = newDataString[:-1]
	newDataFile.write(newDataString)






