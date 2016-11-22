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

	def setSimulationParameters(self, expTimeSteps, nrow, ncol):
		self.expectedTimeSteps = expTimeSteps
		self.nrow = nrow
		self.ncol = ncol



class RandomModel(genericModel):
	def chooseAction(self, state):
		actionList = []
		for i in xrange(0,len(state.truckPos)):
			r = random.randint(0,self.ncol-1)
			c = random.randint(0,self.nrow-1)
			actionList.append((r,c))
		return actionList



class GreedyAssignmentModel(genericModel):
	def chooseAction(self, state):
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
				rrow = random.randint(0,self.nrow-1)
				rcol = random.randint(0,self.ncol-1)
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


class QlearningModel(genericModel):
	def __init__(self):
		self.trainingOrTesting = 'training'
		self.qlearn = mdp.QLearningAlgorithm(self.generateActions, 1, self.featureExtractor)
		self.mostRecentState = None
		self.mostRecentAction = None
		self.numActions = 50	#Number of actions to generate each state

	def generateActions(self, state):
		masterList = []
		for actionNum in range(self.numActions):
			#For each truck, insert a point into point_list
			point_list = []

			#Heuristic to only include points directing trucks to nearby incidents
			#TODO: what if two incidents at same location?
			incidentList = state.incidentPos.keys()
			for i in xrange(0,len(state.truckPos)):
				if len(incidentList) > i:
					point_list.append(state.incidentPos[incidentList[i]])
				else:
					rrow = random.randint(0, self.nrow-1)
					rcol = random.randint(0, self.ncol-1)
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

		return masterList

	def simulateAction(self, state, action):
		newState = copy.deepcopy(state)
		for i, (t_row, t_col) in enumerate(state.truckPos):
			(directive_row, directive_col) = action[i]
			dy = directive_row - t_row
			dx = directive_col - t_col
			move_x = utilities.sign(dx)
			move_y = utilities.sign(dy)
			newState.truckPos[i] = (t_row + move_y, t_col + move_x)
		return newState


	def featureExtractor(self,state,action):
		#The way I am doing this is, instead of how in blackjack where we did (state,action) pairs
		#as the feature key, now I am doing (1, some_helpful_value) -- the one so that it is included
		#for every state no matter what's happening, and the value to hopefully kind of represent
		#the action? I could be doing this wrong but I think this is right
		results = []

		#Features should help to distinguish between actions!
		#Every action has the same state, soley state based features
		#cause every action to have the same weight, and its essentially
		#random choice! By evaluating potential future states, we get a better
		#distinction between actions
		newState = self.simulateAction(state,action)

		#sum of distance from truck to nearest truck
		totalMin = 0
		numTrucks = len(newState.truckPos)
		for truck in xrange(0,numTrucks):
			myMin = self.nrow + self.ncol
			minPos = -1
			for other_truck in xrange(0,numTrucks):
				if truck == other_truck:
					continue
				#print truck, other_truck, self.truckPos, self.numTrucks
				if utilities.manhattanDistance(newState.truckPos[truck],newState.truckPos[other_truck]) < myMin:
					myMin = utilities.manhattanDistance(newState.truckPos[truck],newState.truckPos[other_truck])
					minPos = other_truck
			totalMin += myMin
		truckDistKey = ('truckDist',totalMin/float(numTrucks))
		results.append((truckDistKey,1))

		#sum of distances from incidents to nearest truck
		totalMin = 0
		numIncidents = len(newState.incidentPos)
		for key, incident in newState.incidentPos.iteritems():
			myMin = self.nrow + self.ncol
			minPos = -1
			for truck in xrange(0, numTrucks):
				if utilities.manhattanDistance(newState.truckPos[truck], incident) < myMin:
					myMin = utilities.manhattanDistance(newState.truckPos[truck], incident)
					minPos = other_truck
			totalMin += myMin

		for truck in newState.truckPos:
			xtotal = truck[0]
			ytotal = truck[1]
		truckDistKey = ('aveTruckX', round(xtotal/len(newState.truckPos)))
		results.append((truckDistKey,1))
		truckDistKey = ('aveTruckY', round(ytotal/len(newState.truckPos)))
		results.append((truckDistKey,1))

		incidentKey = ('incident', 0 if numIncidents == 0 else int(totalMin/float(numIncidents)))
		results.append((incidentKey,1))

		#TODO: Include time of day as a feature?
		#TODO: Include average horizontal and average vertical position of trucks as features?
		return results


	##--------------- Reward Functions ------------------------
	#TODO: for the old reward function to be viable, more info needs to be passed into witness results
	#However, I dont think that this is a good reward function, as it doesnt have a lot to do with
	#what we are trying to optimize for, which is time
	def incidentsResolvedReward(self, oldState, newState):
		return newState.recentlyResolved

	# Sum of distances from trucks to incidents in a given state
	def sumOfIncidentDistances(state):
		for incident in state.incidentPos:
			for truck in state.truckPos:
				pass
				#TODO: finish implementing this

	#Reward given at each state for distance to events
	def normailizedIncidentDistanceReward(self, oldState, newState):
		return 100 - sumOfIncidentDistances(oldState)
	##---------------------------------------------------------


	def chooseAction(self, currentState):
		self.mostRecentState = currentState
		action = self.qlearn.getAction(currentState)
		self.mostRecentAction = action
		return action

	def witnessResult(self, newState):
		reward = self.incidentsResolvedReward(self.mostRecentState, newState)
		#reward = self.normailizedIncidentDistanceReward(self.mostRecentState, newState)
		self.qlearn.incorporateFeedback(self.mostRecentState, self.mostRecentAction, reward, newState)
		if newState.timestep > self.expectedTimeSteps/2:
			self.trainingOrTesting = 'testing'
			self.qlearn.explorationProb = 0