import time
import geocoder

year = '2009'
filename = 'just_address_data/addresses'+year+'.txt'
outFile = 'converted/address-latlong'+year+'.txt'
f = open(filename,'rU')
write = open(outFile,'r')
currentLine = 0
for line in write:
	currentLine+=1
write.close()
w = open(outFile,'a')
lineNumber = 0
for line in f:
	print 'here'
	if lineNumber < currentLine:
		lineNumber+=1
		continue
	s = line.strip() + '__delimeter__'
	g = geocoder.google(line)
	if len(g.latlng)!=2:
		s += 'FAIL' + '\n'
	else:
		latlngString = str(g.latlng[0])+ str(g.latlng[1])
		s += latlngString + '\n'
	w.write(s)
