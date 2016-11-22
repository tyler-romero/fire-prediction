import utilities
import models
import datetime
import random
import math
import copy
import sys



class State():
	def __init__(self, tm, tPos, iPos, rRes):
		self.timestep = tm
		self.truckPos = tPos
		self.incidentPos = iPos
		self.recentlyResolved = rRes
		


class Simulation():
	'''
	The simulation gets instantiated by a data dispenser, which dispenses data to it at a fixed timestep.
	The simulation's job is to hold information about where trucks are, and decide where to send each truck
	at each timestep. 

	The way I have structured the simulation is by using a grid of longitude/latitude data. the granularity
	of the grid can be set in the initialization function. Each truck is at a certain point, and can
	travel one grid space per timestep (this is a simplifying assumption that isn't necessarily close
	to reality but we can change this as we work on the project).

	Baseline: The baseline is simple: it chooses a random step for each truck at each timestep, no matter
	what the data says. The baseline should have a lot of loss.

	Oracle: The oracle knows everything, and will make sure a truck is at each location of each incident
	at the correct timestep. Therefore the oracle should have 0 loss.
	'''
	def __init__(self, model, timeStepsIncoming):
		self.model = model	#The model we are simulating
		self.expectedTimeSteps = timeStepsIncoming #Added this to change the exploration prob halfway through
		self.numTrucks = 3  # must be >= 1
		self.stepSize = 1
		self.truckPos = []
		self.recentlyResolved = 0
		self.ongoingIncidents = {}
		self.allIncidents = {}
		self.resolvedIncidents = {}
		self.gridHorizontalGranularity = 20 # must be > 1
		self.gridVerticleGranularity = 20 # must be > 1
		self.grid = self.getGrid()
		self.currentTime = -1
		for i in xrange(0,self.numTrucks):
			gridRow = random.randint(0,len(self.grid)-1)
			gridCol = random.randint(0,len(self.grid[0])-1)
			self.truckPos.append((gridRow,gridCol))
		self.model.setSimulationParameters(self.expectedTimeSteps, self.gridVerticleGranularity, self.gridHorizontalGranularity)
		self.incidentCounter = []
		for i in range(self.gridVerticleGranularity):
			temp = [0]*self.gridHorizontalGranularity
			self.incidentCounter.append(temp)

	#Returns the current state. Which is just a compact representation of the model
	def generateCurrentState(self):
		return State(self.currentTime, self.truckPos, self.ongoingIncidents, self.recentlyResolved)


	def getGrid(self):
		#grid[0][0] is the northwest corner of sanDiego and grid[n][m] is the southeast.
		#This means that the latitude  at grid[0][0] is greater than the latitude  at grid[n][m]
		#and 			 the longitude at grid[0][0] is less    than the longitude at grid[n][m]
		corners = [(32.981625, -117.270982), (32.692295, -117.009370)]
		vertSteps = self.gridVerticleGranularity
		horizontalSteps = self.gridHorizontalGranularity
		deltaLat = abs(corners[0][0]-corners[1][0]) 
		deltaLong = abs(corners[0][1]-corners[1][1]) 
		grid = []
		for r in xrange(0,self.gridVerticleGranularity):
			tempRow = []
			for c in xrange(0,self.gridHorizontalGranularity):
				curLat = corners[0][0] - r*(deltaLat/(self.gridVerticleGranularity-1))
				curLong = corners[0][1] + c*(deltaLong/(self.gridHorizontalGranularity-1))
				tempRow.append((curLat,curLong))
			grid.append(tempRow)
		return grid


	def whereOnGrid(self,lat,longd):
		(curRow, curCol) = (0, 0)
		if lat < self.grid[len(self.grid)-1][curCol][0]:
			curRow = len(self.grid)-1
		else:
			while lat < self.grid[curRow][curCol][0]:
				curRow += 1
		if longd > self.grid[curRow][len(self.grid[curRow])-1][1]:
			curCol = len(self.grid[curRow])-1
		else:
			while longd > self.grid[curRow][curCol][1]:
				curCol += 1
		return (curRow,curCol)


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
			minDist = utilities.manhattanDistance(self.truckPos[0], dataPosition)
			for truck in xrange(0,self.numTrucks):
				myDist = utilities.manhattanDistance(self.truckPos[truck], dataPosition) #two tuples
				if myDist < minDist:
					minDist = myDist
					minTruck = truck
			totalDist += minDist
		return totalDist


	#Take an action and move the trucks accordingly
	def updateTruckLocations(self, truckDirectives):
		#Action should be a list of tuples where action[i] = (ith truck directive x, ith truck directive y)
		for i, (t_row, t_col) in enumerate(self.truckPos):
			(directive_row, directive_col) = truckDirectives[i]
			dy = directive_row - t_row
			dx = directive_col - t_col
			move_x = utilities.sign(dx)
			move_y = utilities.sign(dy)
			self.truckPos[i] = (t_row + move_y, t_col + move_x)


	#Resolve and update incidents
	def resolveIncidents(self):
		self.recentlyResolved = 0
		for incident_key, incident_location in dict(self.ongoingIncidents).iteritems():
			for truck in self.truckPos:
				if incident_location == truck:
					if self.ongoingIncidents.has_key(incident_key):
						del self.ongoingIncidents[incident_key]
						self.resolvedIncidents[incident_key] = (self.currentTime, incident_location)
						self.recentlyResolved += 1


	def updateSimulation(self, listOfData, timestep):
		self.currentTime = timestep
		for datapoint in listOfData:
			incident_key = datapoint[1]
			lati = float(datapoint[4].split('_')[0])
			lond = float(datapoint[4].split('_')[1])
			location = self.whereOnGrid(lati, lond)
			x, y = location
			self.incidentCounter[x][y] += 1
			self.ongoingIncidents[incident_key] = location
			self.allIncidents[incident_key] = (self.currentTime, location)


	def printSimulation(self):
		stringModel = [["_"  for i in range(self.gridHorizontalGranularity)] for j in range(self.gridVerticleGranularity)]
		for i,(t_row,t_col) in enumerate(self.truckPos):
			stringModel[t_row][t_col] = str(i+1)
		for (i_row,i_col) in self.ongoingIncidents.values():
			stringModel[i_row][i_col] = "X"
		for i in range(len(stringModel)):
			print stringModel[i]
		print "Ongoing Incidents: ", len(self.ongoingIncidents), "Resolved Incidents: ", len(self.resolvedIncidents), "\n"
		


	def compileResults(self):
		#Calculate Average Response Time
		total = 0
		response_times = []
		response_times1 = []
		response_times2 = []
		myLength = len(self.resolvedIncidents)/2.0
		count = 0
		for incident_key, (t1, loc1) in self.resolvedIncidents.iteritems():
			count += 1
			t2, loc2 = self.allIncidents[incident_key]
			respTime = t1-t2
			response_times.append(respTime)
			if t1 < self.expectedTimeSteps/2:
				response_times1.append(respTime)
			else:
				response_times2.append(respTime)

		#THIS BREAKDOWN IS INHERANTLY BIASED, The second half is more difficult
		print "============= FIRST HALF RESULTS =============="
		print "Average Response Time: ", sum(response_times1) / float(len(response_times1))
		print "Max Response Time: ", max(response_times1)
		print "Min Response Time: ", min(response_times1)
		print "============= SECOND HALF RESULTS ============="
		print "Average Response Time: ", sum(response_times2) / float(len(response_times2))
		print "Max Response Time: ", max(response_times2)
		print "Min Response Time: ", min(response_times2)
		respTimes = open('responseTimes.txt', 'w')
		for item in response_times:
  			respTimes.write("%s\n" % item)
  		#Where the incidents actually occur
  		#print "Incident Locations:"
		#for li in self.incidentCounter:
		#	print li


	#Recieve Data, Move Trucks
	#I changed the order of some things here to allow us to be more true to
	#the actual Qlearning model. Namely that witnessResult needs to come after
	#the next state is fully updated:
	#(state s) -> trucks moved -> incidents resolved -> new incidents added -> (state s')
	def executeTimestep(self, listOfData, timestep):
		self.updateSimulation(listOfData, timestep)

		if timestep != 0:
			newState = self.generateCurrentState()
			self.model.witnessResult(newState)

		sys.stdout.write("Timestep: %d  \r" % (timestep) )
		sys.stdout.flush()
		#self.printSimulation()

		currentState = self.generateCurrentState()
  		action = self.model.chooseAction(currentState)
  		self.updateTruckLocations(action)
		self.resolveIncidents()
		
		
		
	

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
		myList[4] = myList[4].split('-')[0]+'_-'+myList[4].split('-')[1]
		return myList


	def getDateTime(self,timeString):
		#year, month, day, hour*24*60 + minute*60 + second
		#example:   11/23/09 20:42:52
		myList = timeString.strip().split()[0].split('/')
		timeList = timeString.strip().split()[1].split(':')
		myDateTime = datetime.datetime(int(myList[2]),int(myList[0]),int(myList[1]),int(timeList[0]),int(timeList[1]),int(timeList[2]))
		return myDateTime


	def dispenseData(self, model):
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

		simulationInstance = Simulation(model, timeStepNumber)
		timeStepNumber = 0
		i = 0
		while i < len(dataMapper):
			passList = []
			while dataMapper[i] <= timeStepNumber:
				passList.append(self.data[i][1])
				i+=1
				if i == len(dataMapper):
					break
			simulationInstance.executeTimestep(passList, timeStepNumber)
			timeStepNumber+=1
		simulationInstance.compileResults()


#randmodel = models.RandomModel()
qlearnmodel = models.QlearningModel()
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "Qlearning Model"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5))
dd1.dispenseData(qlearnmodel)
dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5))
dd1.dispenseData(qlearnmodel)
dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5))
dd1.dispenseData(qlearnmodel)


print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "Greedy Model"
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
greedymodel = models.GreedyAssignmentModel()
dd2 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5))
dd2.dispenseData(greedymodel)
dd2 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5))
dd2.dispenseData(greedymodel)
dd2 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5))
dd2.dispenseData(greedymodel)
