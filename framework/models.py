import utilities
import mdp
import random
import copy
import sys

#Since our "Model" (Aka now Simulation) was beginning to contain multiple models, 
#I thought it was best to make our code more modular, so that it is more simple
#to work with existing models and to add new ones

class genericModel:
	#Returns the action dictated by the model at this time
	def chooseAction(self, state):
		raise("Override Me")

	#Option to incorporate feedback
	def witnessResult(self, state):
		pass


class GreedyAssignmentModel(genericModel):

	def chooseAction(self, state):
		'''
		action = self.baselineGetAction(currentState)
		for i in xrange(0,self.numTrucks):
			newGridRow = self.truckPos[i][0] + random.randint(-self.stepSize,self.stepSize)
			newGridCol = self.truckPos[i][1] + random.randint(-self.stepSize,self.stepSize)
			newGridRow = min(self.gridHorizontalGranularity-1, max(0,newGridRow))
			newGridCol = min(self.gridVerticleGranularity-1, max(0,newGridCol))
			self.truckPos[i] = (newGridRow, newGridCol)
		'''
		action = self.generateAction(state)
		return action


	def generateAction(self, state):
		point_list = []

		#Randomly get an assigment list, with greedy assignment of trucks to incidents
		ongoingList = state.incidentPos.keys()
		for i in xrange(0,len(state.truckPos)):
			if len(ongoingList) > i:
				point_list.append(state.incidentPos[ongoingList[i]])
			else:
				rrow = random.randint(0,state.nrow-1)
				rcol = random.randint(0,state.ncol-1)
				point_list.append((rrow, rcol))
		assignment_list = [-1]*len(state.truckPos)
		tempTruckList = copy.deepcopy(state.truckPos)
		for j, point in enumerate(point_list):
			minDist = sys.maxint
			minIndex = 0
			for i, truck in enumerate(tempTruckList):
				if truck is None:
					continue
				dist = utilities.manhattanDistance(truck, point)
				if dist < minDist:
					minDist = dist
					minIndex = i
			assignment_list[minIndex] = point
			tempTruckList[minIndex] = None
		return assignment_list
		'''
		actionList = []
		for i in xrange(0,len(currentState.truckPos)):
			if len(currentState.incidentPos.keys()) > i:
				#print currentState.incidentPos[currentState.incidentPos.keys()[i]]
				actionList.append(currentState.incidentPos[currentState.incidentPos.keys()[i]])
			else:
				r = random.randint(0,self.gridHorizontalGranularity-1)
				c = random.randint(0,self.gridVerticleGranularity-1)
				actionList.append((r,c))
		return tuple(actionList)
		'''



class QlearningModel(genericModel):
	def __init__(self):
		self.trainingOrTesting = 'training'
		self.qlearn = mdp.QLearningAlgorithm(self.generateActions, 1, self.featureExtractor)
		self.mostRecentState = None
		self.mostRecentAction = None
		self.numActions = 50	#Number of actions to generate each state


	def generateActions(self, state):
		thresh = 0.4	#Chance of inserting an incident
		masterList = []
		for _ in range(self.numActions):
			#For each truck, insert a point into point_list
			point_list = []

			#Heuristic to only include points directing trucks to nearby incidents
			incidentList = state.incidentPos.keys()
			for i in xrange(0,len(state.truckPos)):
				if len(incidentList
					) > i:
					point_list.append(state.incidentPos[incidentList[i]])
				else:
					rrow = random.randint(0, state.nrow-1)
					rcol = random.randint(0, state.ncol-1)
					point_list.append((rrow, rcol))

			#Greedily assign each point to the nearest truck
			assignment_list = [-1]*len(state.truckPos)
			tempTruckList = copy.deepcopy(state.truckPos)
			for point in point_list:
				minDist = sys.maxint
				minIndex = 0
				for i, truck in enumerate(tempTruckList):
					if truck is None:
						continue
					dist = utilities.manhattanDistance(truck, point)
					if dist < minDist:
						minDist = dist
						minIndex = i
				assignment_list[minIndex] = point
				tempTruckList[minIndex] = None
			masterList.append(assignment_list)
		
		#Append action where trucks do not move:
		#masterList.append(state.truckPos)

		#TODO: Append action same as last turn
		return masterList


	def featureExtractor(self,state,action):
		#The way I am doing this is, instead of how in blackjack where we did (state,action) pairs
		#as the feature key, now I am doing (1, some_helpful_value) -- the one so that it is included
		#for every state no matter what's happening, and the value to hopefully kind of represent
		#the action? I could be doing this wrong but I think this is right
		results = []

		#TODO: Include time of day as a feature

		#sum of distance from truck to nearest truck
		totalMin = 0
		numTrucks = len(state.truckPos)
		for truck in xrange(0,numTrucks):
			myMin = state.nrow + state.ncol
			minPos = -1
			for other_truck in xrange(0,numTrucks):
				if truck == other_truck:
					continue
				#print truck, other_truck, self.truckPos, self.numTrucks
				if utilities.manhattanDistance(state.truckPos[truck],state.truckPos[other_truck]) < myMin:
					myMin = utilities.manhattanDistance(state.truckPos[truck],state.truckPos[other_truck])
					minPos = other_truck
			totalMin += myMin
		keyTuple = (1,('truck',totalMin/float(numTrucks)))
		results.append((keyTuple,1))

		#sum of distances from incidents to nearest truck
		totalMin = 0
		numIncidents = len(state.incidentPos)
		for key, incident in state.incidentPos.iteritems():
			myMin = state.nrow + state.ncol
			minPos = -1
			for truck in xrange(0, numTrucks):
				if utilities.manhattanDistance(state.truckPos[truck], incident) < myMin:
					myMin = utilities.manhattanDistance(state.truckPos[truck], incident)
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


	def chooseAction(self, currentState):
		self.mostRecentState = currentState
		action = self.qlearn.getAction(currentState)
		self.mostRecentAction = action
		return action


	def witnessResult(self, newState):
		reward = self.rewardFuntion(self.mostRecentState, newState)
		self.qlearn.incorporateFeedback(self.mostRecentState, self.mostRecentAction, reward, newState)
		#if ntimestep > self.expectedTimeSteps/2:
		#	self.trainingOrTesting = 'testing'
		#	self.qlearn.explorationProb = 0