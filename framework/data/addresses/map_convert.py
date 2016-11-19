import time
import geocoder
import requests

year = '2009'
filename = 'just_address_data/addresses'+year+'.txt'
outFile = 'mapQuestConverted/address-latlong'+year+'.txt'
f = open(filename,'rU')
write = open(outFile,'r')
currentLine = 0
for line in write:
	currentLine+=1
write.close()
w = open(outFile,'a')
lineNumber = 0
currentBatch = 0
currentBatchList = []
for line in f:
	print 'here'
	if lineNumber < currentLine:
		lineNumber+=1
		continue
	if currentBatch < 99:
		currentBatchList.append(line.strip())
		currentBatch += 1
		continue
	currentBatch = 0
	params = {'key':'AnBHFbwUqomjtakPpX83E0tZxfzGDrYz','location':currentBatchList}
	url = 'http://www.mapquestapi.com/geocoding/v1/batch'
	r = requests.get(url,params=params)
	print r.content
	j = r.json()

	for i in xrange(0,len(currentBatchList)):
		lat = None
		lng = None
		try:
			lat = j['results'][i]['locations'][0]['latLng']['lat']
			lng = j['results'][i]['locations'][0]['latLng']['lng']		
		except:
			nothing = 0




		s = currentBatchList[i].strip() + '__delimeter__'
		if lat == None or lng == None:
			s += 'FAIL' + '\n'
		else:
			latlngString = str(lat)+ ',' + str(lng)
			s += latlngString + '\n'
		w.write(s)

	del currentBatchList[:]
