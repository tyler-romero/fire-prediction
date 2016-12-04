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
	def __init__(self, model, timeStepsIncoming,ts=4):
		self.model = model	#The model we are simulating
		self.expectedTimeSteps = timeStepsIncoming #Added this to change the exploration prob halfway through
		self.numTrucks = ts  # must be >= 1
		self.stepSize = 1
		self.truckPos = []
		self.recentlyResolved = 0
		self.ongoingIncidents = {}
		self.allIncidents = {}
		self.resolvedIncidents = {}
		self.gridHorizontalGranularity = 100 # must be > 1
		self.gridVerticleGranularity = 100 # must be > 1
		self.grid = self.getGrid()
		self.currentTime = -1
		for i in xrange(0,self.numTrucks):
			gridRow = random.randint(0,len(self.grid)-1)
			gridCol = random.randint(0,len(self.grid[0])-1)
			self.truckPos.append((gridRow,gridCol))
		if model != None:
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
		print "=============== TOTAL RESULTS ================="
		print "Average Response Time: ", sum(response_times) / float(len(response_times))
		print "Max Response Time: ", max(response_times)
		print "Min Response Time: ", min(response_times)
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
  		return sum(response_times) / float(len(response_times))
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
		
		
		
	
