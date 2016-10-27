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
	def __init__(self):
		self.setup = 0
		self.numTrucks = 5
		self.truckPos = []
		self.gridHorizontalGranularity = 100
		self.gridVerticleGranularity = 100
		self.grid = self.getGrid()
		for i in xrange(0,self.numTrucks):
			gridRow = random.randint(0,len(grid))
			gridCol = random.randint(0,len(grid[0]))
			self.truckPos.append((gridRow,gridCol))
		self.zipCodeLocs = self.getZipCodeLocs()



	def getGrid(self):
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

	def getZipCodeLocs(self):
		f = open('zipcode.txt')
		coordinate = None
		for line in f:
			if 

	def baselineMoveTrucks(self, listOfData):
		for i in xrange(0,self.numTrucks):
			newGridRow = self.truckPos[i][0] + random.randint(-1,1)
			newGridCol = self.truckPos[i][1] + random.randint(-1,1)
			self.truckPos[i] = (newGridRow, newGridCol)

	def minDistFromIncident(self, listOfData):
		totalNum = len(listOfData)
		totalDist = 0
		for i in xrange(0,totalNum):
			minTruck = 0
			for truck in xrange(0,self.numTrucks):


	def receiveNextData(self, listOfData):
		baselineMoveTrucks(listOfData)


class dataDispenser():
	def __init__(self,dataFileName='fd_incidents_past_12_mo_datasd.csv'):
		self.timeStep = 60
		self.dataFile = open(dataFileName,'r')
		self.data = []
		for line in self.dataFile:
			splitList = self.splitComma(line.strip())
			dateTime = self.getDateTime(splitList[6])
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
		modelInstance = Model()
		currentElement = 0
		currentTime = currentTime - timeStep
		while currentTime < endTime:
			print currentTime
			passList = []
			while self.data[currentElement][0] < currentTime:
				passList.append(self.data[currentElement][1])
				currentElement+=1
				if currentElement >= self.dataLength:
					break

			modelInstance.receiveNextData(passList)

			currentTime = currentTime +timeStep

dataDispenser()




