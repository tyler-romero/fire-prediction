import datetime
import random

class Model():
	'''

	The model gets instantiated by a data dispenser, which dispenses data to it at a fixed timestep.
	The model's job is to hold information about where trucks are, and decide where to send each truck
	at each timestep. 

	The way I have structured the model is by using a grid of longitude/latitude data. the granularity
	of the grid can be set in the initialization function. Each truck is at a certain point, and can
	travel one grid space per timestep (this is a simplifying assumption that isn't necessarily close
	to reality but we can change this as we work on the project).

	Baseline: The baseline is simple: it chooses a random step for each truck at each timestep, no matter
	what the data says. The baseline should have a lot of loss.

	Oracle: The oracle knows everything, and will make sure a truck is at each location of each incident
	at the correct timestep. Therefore the oracle should have 0 loss.


	'''
	def __init__(self,data, dataMapper):
		self.data = data #For oracle's eyes only
		self.dataMapper = dataMapper #Also for oracle's eyes only
		self.setup = 0
		self.numTrucks = 5  # must be >= 1
		self.stepSize = 5
		self.truckPos = []
		self.gridHorizontalGranularity = 100 # must be > 1
		self.gridVerticleGranularity = 100 # must be > 1
		self.grid = self.getGrid()
		self.totalError = 0
		self.missingZip = {}
		for i in xrange(0,self.numTrucks):
			gridRow = random.randint(0,len(self.grid))
			gridCol = random.randint(0,len(self.grid[0]))
			self.truckPos.append((gridRow,gridCol))
		#self.oracleMoves = self.getOracleMoves()
		self.zipCodeLocs = self.getZipCodeLocs()



	def getGrid(self):
		#grid[0][0] is the northwest corner of sanDiego and grid[n][m] is the southeast.
		#This means that the latitude  at grid[0][0] is greater than the latitude  at grid[n][m]
		#and 			 the longitude at grid[0][0] is less    than the longitude at grid[n][m]

		corners = [(32.981625, -117.270982), (32.692295, -117.009370)]

		vertSteps = self.gridVerticleGranularity
		horizontalSteps = self.gridHorizontalGranularity
		deltaLat = abs(corners[0][0]-corners[1][0]) / vertSteps
		deltaLong = abs(corners[0][1]-corners[1][1]) / horizontalSteps
		grid = []
		curLat = corners[0][0]
		while curLat > corners[1][0]:
			curLong = corners[0][1]
			tempRow = []
			while curLong < corners[1][1]:
				tempRow.append((curLat,curLong))
				curLong += deltaLong
			curLat -= deltaLat
			grid.append(tempRow)
		return grid

	def whereOnGrid(self,lat,longd):
		curRow = 0
		curCol = 0
		if lat < self.grid[len(self.grid)-1][curCol]:
			curRow = len(self.grid)-1
		else:
			while lat < self.grid[curRow][curCol]:
				curRow += 1
		if longd > self.grid[curRow][len(self.grid[curRow])-1]:
			curCol = len(self.grid[curRow])-1
		else:
			while longd > self.grid[curRow][curCol]:
				curCol += 1
		return (curRow,curCol)

	def getZipCodeLocs(self):
		f = open('zipcode.txt')
		coordinate = None
		zipDict = {}
		for line in f:
			if coordinate == None:
				coordinate = line.strip()
			else:
				zipDict[int(line.strip())] = self.whereOnGrid(float(coordinate.split(',')[0].strip()),float(coordinate.split(',')[1].strip()))
				coordinate = None
		return zipDict


	def baselineMoveTrucks(self, listOfData):
		for i in xrange(0,self.numTrucks):
			newGridRow = self.truckPos[i][0] + random.randint(-self.stepSize,self.stepSize)
			newGridCol = self.truckPos[i][1] + random.randint(-self.stepSize,self.stepSize)
			self.truckPos[i] = (newGridRow, newGridCol)

	def getOracleMoves(self):
		truckAssignment = []
		truckMoves = []
		for i in xrange(0,len(self.data)):
			truckAssignment.append(-1)
		for truck in xrange(0,self.numTrucks):
			print truck
			curTime = 0
			currentLocation = self.truckPos[truck]
			for i in xrange(0,len(self.data)):
				if self.dataMapper[i] > curTime and truckAssignment[i] == -1:
					dataPosition = None
					zipCode = int(self.data[i][1][-1])
					if zipCode not in self.zipCodeLocs:
						dataPosition = (0,0)
					else:
						dataPosition = self.zipCodeLocs[zipCode]
					numMovesPossible = self.stepSize(self.dataMapper[i] - curTime)
					if numMovesPossible >= abs(dataPosition[0] - currentLocation[0]):
						if numMovesPossible >= abs(dataPosition[1]-currentLocation[1]):
							truckAssignment[i] = truck
							currentLocation = dataPosition
		print truckAssignment
		self.oracleMoves = truckAssignment

	#def oracleMoveTrucks(self, listOfData):


	def manhattanDistance(self, x1, x2):
		return abs(x1[0]-x2[0]) + abs(x1[1]-x2[1])

	def minDistFromIncident(self, listOfData):
		totalNum = len(listOfData)
		totalDist = 0
		for i in xrange(0,totalNum):
			zipCode = int(listOfData[i][len(listOfData[i])-1])
			dataPosition = None
			if zipCode not in self.zipCodeLocs:
				if zipCode not in self.missingZip:
					self.missingZip[zipCode] = 0
				self.missingZip[zipCode] += 1
				dataPosition = (0,0)
			else:
				dataPosition = self.zipCodeLocs[int(listOfData[i][len(listOfData[i])-1])] #zip
			minTruck = 0
			minDist = self.manhattanDistance(self.truckPos[0], dataPosition)
			for truck in xrange(0,self.numTrucks):
				myDist = self.manhattanDistance(self.truckPos[truck], dataPosition) #two tuples
				if myDist < minDist:
					minDist = myDist
					minTruck = truck
			totalDist += minDist
		return totalDist

	def receiveNextData(self, listOfData):
		self.totalError += self.minDistFromIncident(listOfData)
		#print self.totalError
		self.baselineMoveTrucks(listOfData)


class dataDispenser():
	def __init__(self,dataFileName='fd_incidents_past_12_mo_datasd.csv'):
		self.timeStep = 60
		self.dataFile = open(dataFileName,'r')
		self.data = []
		for line in self.dataFile:
			splitList = self.splitComma(line.strip())
			dateTime = self.getDateTime(splitList[6])
			if len(splitList[-1]) < 5:
				continue
			self.data.append([dateTime, splitList])
		self.data.reverse()
		self.dataLength = len(self.data)
		self.dispenseData()

	def splitComma(self,myStr):
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


	def getDateTime(self,timeString):
		#year, month, day, hour*24*60 + minute*60 + second
		myList = timeString.strip().split('T')[0].split('-')
		timeList = timeString.strip().split('T')[1].split(':')
		myDateTime = datetime.datetime(int(myList[0]),int(myList[1]),int(myList[2]),int(timeList[0]),int(timeList[1]),int(timeList[2]))
		return myDateTime

	def dispenseData(self):
		startTime = self.data[0][0]
		currentTime = startTime
		endTime = self.data[-1][0]
		timeStep = datetime.timedelta(0,self.timeStep)
		currentElement = 0
		currentTime = currentTime - timeStep
		dataMapper = []
		timeStepNumber = 0 
		while currentTime < endTime:
			while self.data[currentElement][0] < currentTime:
				currentElement+=1
				dataMapper.append(timeStepNumber)
				if currentElement >= self.dataLength:
					break
			currentTime = currentTime +timeStep
			timeStepNumber += 1




		modelInstance = Model(self.data,dataMapper)
		currentElement = 0
		currentTime = currentTime - timeStep
		dataMapper = []
		while currentTime < endTime:
			print currentTime, endTime, modelInstance.totalError

			passList = []
			while self.data[currentElement][0] < currentTime:
				passList.append(self.data[currentElement][1])
				currentElement+=1
				dataMapper.append(timeStepNumber)
				if currentElement >= self.dataLength:
					break

			modelInstance.receiveNextData(passList)

			currentTime = currentTime +timeStep
			timeStepNumber += 1
		print modelInstance.totalError
#		for el in modelInstance.missingZip.keys():
#			print el,modelInstance.missingZip[el]

dd = dataDispenser()
dd.dispenseData()

#33575059
#183960899


