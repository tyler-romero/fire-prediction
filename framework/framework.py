import datetime
import random
import geocoder
import mdp
import math
import sys



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
		self.numTrucks = 5  # must be >= 1
		self.stepSize = 5
		self.truckPos = []
		self.ongoingIncidents = {}
		self.allIncidents = {}
		self.resolvedIncidents = {}
		self.gridHorizontalGranularity = 100 # must be > 1
		self.gridVerticleGranularity = 100 # must be > 1
		self.grid = self.getGrid()
		self.totalError = 0
		self.currentTime = -1
		self.qlearn = mdp.QLearningAlgorithm(self.generateActions, 1, self.featureExtractor)
		for i in xrange(0,self.numTrucks):
			gridRow = random.randint(0,len(self.grid))
			gridCol = random.randint(0,len(self.grid[0]))
			self.truckPos.append((gridRow,gridCol))


	class State():
		def __init__(self, col, row, tPos, iPos):
			self.cols = col
			self.rows = row
			self.truckPos = tPos
			self.incidentPos = iPos


	#Returns the current state. Which is just a compact representation of the model
	def generateCurrentState(self):
		return self.State(self.gridHorizontalGranularity, self.gridVerticleGranularity, self.truckPos, self.ongoingIncidents)


	#returns a list of actions based on the current state
	#	We discussed doing this by:
	#		- (randomly sampling and assigning each truck to the nearest sampled location)*1000
	#		- Including the previous best action
	#		- (Randomly assigning each truck to an incident)*1000
	def generateActions(self, state):
		thresh = 0.3	#Chance of inserting an incident
		masterList = []
		for _ in range(100):
			#For each truck, insert a point
			point_list = []
			for truck in self.truckPos:
				if random.random() > thresh or len(self.ongoingIncidents) is 0:
					rrow = random.randint(0,self.gridVerticleGranularity-1)
					point_list.append((rrow, rcol))
				else:
					rIndex = random.randint(0, len(self.ongoingIncidents))
					rincident = self.ongoingIncidents.values()[rIndex]
					point_list.append(rincident)

			#Greedily assign each point to the nearest truck
			assignment_list = [-1]*len(self.truckPos)
			for j, point in enumerate(point_list):
				minDist = sys.maxint
				minIndex = 0
				tempTruckList = self.truckPos
				for i, truck in enumerate(tempTruckList):
					dist = manhattanDistance(truck, point):
					if dist < minDist:
						minDist = dist
						minIndex = i
				assignment_list[minIndex] = point
				del tempTruckList[minIndex]
			masterList.append(assignment_list)
		return masterList
				




	#Take an action and move the trucks accordingly
	def updateTruckLocations(self, truckDirectives):
		#Action should be a list of tuples where action[i] = (ith truck directive x, ith truck directive y)
        for i, (t_row, t_col) in enumerate(self.truckPos):
            (directive_row, directive_col) = truckDirectives[i]
            dy = directive_row - t_row
            dx = directive_col - t_col
            if (dx == 0 and dy == 0):
                # "do nothing" 
                return (t_row, t_col)
            if dx >= 0:
                if(-.5*dx <= dy and dy <= .5*dx):
                    # "move right"
                    self.truckPos[i] =(t_row, t_col +1)
                elif(-2*dx <= dy and dy <= -.5*dx):
                    # "move right and up"
                    self.truckPos[i] = (t_row-1, t_col+1)
                elif(.5*dx <= dy and dy <= 2*dx):
                    # "move right and down"
                    self.truckPos[i] = (t_row+1, t_col+1)
                elif(2*dx >= dy):
                    # "move up"
                    self.truckPos[i] = (t_row-1, t_col)
                elif(dy >= -2*dx):
                    # "move down"
                    self.truckPos[i] = (t_row+1, t_col)
            if dx <= 0:
                if(-.5*dx >= dy and dy >= .5*dx):
                    # "move left"
                    self.truckPos[i] = (t_row, t_col -1)
                elif(.5*dx >= dy and dy >= 2*dx):
                    # "move left and up"
                    self.truckPos[i] = (t_row-1, t_col-1)
                elif(-2*dx >= dy and dy >= -.5*dx):
                    # "move left and down"
                    self.truckPos[i] = (t_row+1, t_col-1)
                elif(2*dx <= dy):
                    # "move up"
                    self.truckPos[i] = (t_row-1, t_col)
                elif(dy <= -2*dx):
                    # "move down"
                    self.truckPos[i] = (t_row+1, t_col)

	#Resolve and update incidents
	def resolveIncidents(self):
		for incident_key, incident_location in dict(self.ongoingIncidents).iteritems():
			for truck in self.truckPos:
				if incident_location == truck:
					del self.ongoingIncidents[incident_key]
					self.resolvedIncidents[incident_key] = (self.currentTime, incident_location)


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


	def baselineMoveTrucks(self, listOfData):
		for i in xrange(0,self.numTrucks):
			newGridRow = self.truckPos[i][0] + random.randint(-self.stepSize,self.stepSize)
			newGridCol = self.truckPos[i][1] + random.randint(-self.stepSize,self.stepSize)
			self.truckPos[i] = (newGridRow, newGridCol)


	def featureExtractor(self):
		#The way I am doing this is, instead of how in blackjack where we did (state,action) pairs
		#as the feature key, now I am doing (1, some_helpful_value) -- the one so that it is included
		#for every state no matter what's happening, and the value to hopefully kind of represent
		#the action? I could be doing this wrong but I think this is right
		results = []
		#sum of distance from truck to nearest truck
		totalMin = 0
		for truck in xrange(0,self.numTrucks):
			myMin = self.gridHorizontalGranularity+self.gridVerticleGranularity
			minPos = -1
			for other_truck in xrange(0,self.numTrucks):
				if truck == other_truck:
					continue
				if self.manhattanDistance(self.truckPos[truck],self.truckPos[other_truck]) < myMin:
					myMin = self.manhattanDistance(self.truckPos[truck],self.truckPos[other_truck])
					minPos = other_truck
			totalMin += myMin
		keyTuple = (1,('truck',totalMin/float(self.numTrucks)))
		results.append((keyTuple,1))

		#sum of distances from incidents to nearest truck
		totalMin = 0
		numIncidents = len(self.ongoingIncidents)
		for incident in xrange(0,numIncidents):
			myMin = self.gridHorizontalGranularity+self.gridVerticleGranularity
			minPos = -1
			for truck in xrange(0,self.numTrucks):
				if self.manhattanDistance(self.truckPos[truck],self.ongoingIncidents[incident]) < myMin:
					myMin = self.manhattanDistance(self.truckPos[truck],self.ongoingIncidents[incident])
					minPos = other_truck
			totalMin += myMin
		if numIncidents == 0:
			keyTuple = (1,('incident',0))
			results.append((keyTuple,1))
		else:
			keyTuple = (1,('incident',int(totalMin/float(numIncidents))))
			results.append((keyTuple,1))


		return results

	def rewardFuntion(self, oldState, newState):
		#TODO: Does reward have to have something to do with the random nature of changing states? This is deterministic.
		#probably should be a function of time as well (we want to incentivize quick action)
		return len(oldState.incidentPos) - len(newState.incidentPos)


	def qlearnMoveTrucks(self, listOfData):
		currentState = self.generateCurrentState()
		action = self.qlearn.getAction(currentState)
		self.updateTruckLocations(action)
		self.resolveIncidents()

		for i in xrange(0,self.numTrucks):
			newGridRow = self.truckPos[i][0] + random.randint(-self.stepSize,self.stepSize)
			newGridCol = self.truckPos[i][1] + random.randint(-self.stepSize,self.stepSize)
			self.truckPos[i] = (newGridRow, newGridCol)
		
		newState = generateCurrentState()
		reward = rewardFuntion(currentState, newState)
		self.qlearn.incorporateFeedback(currentState, action, reward, newState)


	def manhattanDistance(self, x1, x2):
		return abs(x1[0]-x2[0]) + abs(x1[1]-x2[1])
 

	def minDistFromIncident(self, listOfData):
		totalNum = len(listOfData)
		totalDist = 0
		for i in xrange(0,totalNum):
			latLong = []
			latLong.append(float(listOfData[i][4].split('-')[0]))
			latLong.append(float(listOfData[i][4].split('-')[1]))
			dataPosition = None
			dataPosition = latLong
			minTruck = 0
			minDist = self.manhattanDistance(self.truckPos[0], dataPosition)
			for truck in xrange(0,self.numTrucks):
				myDist = self.manhattanDistance(self.truckPos[truck], dataPosition) #two tuples
				if myDist < minDist:
					minDist = myDist
					minTruck = truck
			totalDist += minDist
		return totalDist


	def updateModel(self, listOfData, timestep):
		#self.totalError += self.minDistFromIncident(listOfData)
		self.currentTime = timestep
		for datapoint in listOfData:
			incident_key = datapoint[2]
			lati = float(datapoint[4].split('_')[0])
			lond = float(datapoint[4].split('_')[1])
			location = whereOnGrid(lati, lond)
			self.ongoingIncidents[incident_key] = location
			self.allIncidents[incident_key] = (self.currentTime, location)

	def printModel(self):
		baseString = "O"*self.gridVerticleGranularity
		stringModel = [baseString for i in range(self.gridHorizontalGranularity)]
		for i,(t_row,t_col) in enumerate(self.truckPos):
			stringModel[t_row][t_col] = str(i)
		for (i_row,i_col) in self.ongoingIncidents.values():
			stringModel[i_row][i_col] = "X"
		for i in range(len(stringModel)):
			print stringModel[i]


	#Recieve Data, Move Trucks
	def receiveNextData(self, listOfData, timestep):
		self.updateModel(listOfData, timestep)
		self.qlearnMoveTrucks(listOfData)
		self.printModel()
		
	

class dataDispenser():
	def __init__(self,day,timerange,dataFileNames=['data/i2009.csv']):

		#,'incidents2010.csv',\
		#'incidents2011.csv','incidents2012.csv','incidents2013.csv','incidents2014.csv',\
		#'incidents2015.csv','incidents2016.csv']):
		#Emergency Medical Response,FS09000001,San Diego,Stabbing/Gunshot (L1),2800 BROADWAY,28TH ST/29TH ST,SAN DIEGO,92102,1/1/09 0:05:49,1/1/09 0:08:08,0:02:19
		self.data = []
		self.dataLength = []
		self.start = day
		self.end = day+timerange
		#self.data is a list with 8 elements: the lists of data for each year
		for fileName in dataFileNames:
			self.timeStep = 60
			self.dataFile = open(fileName,'rU')
			first = 1
			for line in self.dataFile:
				if first == 1:
					first = 0
					continue
				splitList = self.splitComma(line.strip())
				dateTime = self.getDateTime(splitList[8])
				splitList = self.fixLatLong(splitList)
				if len(splitList) != 11:
					print splitList
					raise Exception('Data is not proper number of fields')
				if dateTime >= self.start and dateTime <= self.end:
					self.data.append([dateTime, splitList])
			self.dataLength = len(self.data)

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


	def fixLatLong(self,myList):
		#sorry about this, latLong was formatted as 'lat-long', needs to be 'lat_-long'
		myList[4] = myList[4].split('-')[0]+'_-'+myList[4].split('-')[1]
		return myList


	def getDateTime(self,timeString):
		#year, month, day, hour*24*60 + minute*60 + second
		#example:   11/23/09 20:42:52
		myList = timeString.strip().split()[0].split('/')
		timeList = timeString.strip().split()[1].split(':')
		myDateTime = datetime.datetime(int(myList[2]),int(myList[0]),int(myList[1]),int(timeList[0]),int(timeList[1]),int(timeList[2]))
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
				#maps each piece of data to a time step number
				if currentElement >= self.dataLength:
					break
			currentTime = currentTime +timeStep
			timeStepNumber += 1

		modelInstance = Model()
		timeStepNumber = 0
		i=0

		while i < len(dataMapper):
			passList = []
			while dataMapper[i] <= timeStepNumber:
				passList.append(self.data[i][1])
				print i
				i+=1
				if i == len(dataMapper):
					break

			modelInstance.receiveNextData(passList, timeStepNumber)
			timeStepNumber+=1
		print modelInstance.totalError


dd = dataDispenser(datetime.datetime(9,1,1),datetime.timedelta(1))
dd.dispenseData()
