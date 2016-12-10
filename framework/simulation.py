import utilities
import models
import datetime
import random
import math
import copy
import sys
import time


class State():
	def __init__(self, tm, tPos, iPos, rRes, newInc):
		self.timestep = tm
		self.truckPos = tPos
		self.incidentPos = iPos
		self.recentlyResolved = rRes
		self.newIncidents = newInc
		

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
	def __init__(self, model, timeStepsIncoming, grid, ts=4):
		self.model = model	#The model we are simulating
		self.expectedTimeSteps = timeStepsIncoming #Added this to change the exploration prob halfway through
		self.numTrucks = ts  # must be >= 1
		self.stepSize = 1
		self.truckPos = []
		self.recentlyResolved = 0
		self.ongoingIncidents = {}
		self.allIncidents = {}
		self.newIncidents = {}	#Only incidents apperaing in the most recent timestep
		self.resolvedIncidents = {}
		self.grid = grid
		self.gridVerticleGranularity = len(grid)
		self.gridHorizontalGranularity = len(grid[0])
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
		return State(self.currentTime, self.truckPos, self.ongoingIncidents, self.recentlyResolved, self.newIncidents)


	#Take an action and move the trucks accordingly
	#Trucks now only move up, down, left, or right
	def updateTruckLocations(self, truckDirectives):
		#Action should be a list of tuples where action[i] = (ith truck directive x, ith truck directive y)
		for i, (t_row, t_col) in enumerate(self.truckPos):
			(directive_row, directive_col) = truckDirectives[i]
			dy = directive_row - t_row
			dx = directive_col - t_col
			if abs(dy) > abs(dx):
				move_y = utilities.sign(dy)
				self.truckPos[i] = (t_row + move_y, t_col)
			else:
				move_x = utilities.sign(dx)
				self.truckPos[i] = (t_row, t_col + move_x)
			

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
		self.newIncidents.clear()
		for datapoint in listOfData:
			incident_key = datapoint[1]
			location = datapoint[4]
			x, y = location
			self.incidentCounter[x][y] += 1
			self.ongoingIncidents[incident_key] = location
			self.newIncidents[incident_key] = location
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
		#Calculate Average Squared Response Time
		response_times = []
		myLength = len(self.resolvedIncidents)/2.0
		count = 0
		for incident_key, (t1, loc1) in self.resolvedIncidents.iteritems():
			count += 1
			t2, loc2 = self.allIncidents[incident_key]
			respTime = t1-t2
			response_times.append(respTime)

		#SWICHED TO AVERAGE SQUARED RESPONSE TIME
		print "=============== TOTAL RESULTS ================="
		print "Average Squared Response Time: ", sum(time**2 for time in response_times) / float(len(response_times))
		print "Max Response Time: ", max(response_times)
		print "Min Response Time: ", min(response_times)

  		return sum(time**2 for time in response_times) / float(len(response_times))


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