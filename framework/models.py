import utilities
import mdp
import random
import copy
import sys
import simulation


class genericModel:
	def __init__(self):
		self.oracle = 0 #Set this to one if you want dataDispenser to give all data to your model. This is for the oracle
		#Returns the action dictated by the model at this time
		self.future_data = None

	def chooseAction(self, state):
		raise("Override Me")

	#Option to incorporate feedback
	def witnessResult(self, state):
		pass

	def accept_data(self, data):
		self.future_data = data

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
		
class Oracle(genericModel):
	def __init__(self):
		self.oracle = 1
		self.currentTimeStep = 0
		self.sim = simulation.Simulation(None,0) #using this for whereOnGrid functionality

	def chooseAction(self,state):
		actionList = []
		point_list = []
		#Randomly get an assigment list, with greedy assignment of trucks to incidents
		ongoingList = state.incidentPos.keys()
		tempTime = self.currentTimeStep+1
		tempPoint = 0
		for i in xrange(0,len(state.truckPos)):
			if len(ongoingList) > i:
				point_list.append(state.incidentPos[ongoingList[i]])
			else:
				found = 0
				while tempTime < len(self.future_data):
					if len(self.future_data[tempTime]) > tempPoint:
						lat = float(self.future_data[tempTime][tempPoint][4].split('_')[0])
						lng = float(self.future_data[tempTime][tempPoint][4].split('_')[1])
						loc = self.sim.whereOnGrid(lat,lng)
						point_list.append(loc)
						tempPoint+=1
						found = 1
						break
					else:
						tempPoint = 0
						tempTime += 1
				if found == 0:
					rrow = random.randint(0,self.nrow-1)
					rcol = random.randint(0,self.ncol-1)
					point_list.append((rrow, rcol))

		assignment_list = [-1]*len(state.truckPos)
		tempTruckList = copy.deepcopy(state.truckPos)
		for j, point in enumerate(point_list):
			minDist = sys.maxint
			minIndex = -1
			for i, truck in enumerate(tempTruckList):
				if truck is None:
					continue
				dist = utilities.manhattanDistance(truck, point)
				if dist < minDist:
					minDist = dist
					minIndex = i
			assignment_list[minIndex] = point
			tempTruckList[minIndex] = None
		self.currentTimeStep+=1
		return assignment_list



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



#Qlearning model, without any features or rewards.
#WHY DOES THIS WORK THE BEST?
class NaiveQlearningModel(genericModel):
	def __init__(self):
		self.trainingOrTesting = 'training'
		self.qlearn = mdp.QLearningAlgorithm(self.generateActions, 0.7, self.featureExtractor)
		self.mostRecentState = None
		self.mostRecentAction = None
		self.numActions = 50	#Number of actions to generate each state
		self.oracle = 0

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

	def featureExtractor(self,state,action):
		return []

	##--------------- Reward Functions ------------------------
	def dumbReward(self):
		return 0

	##---------------------------------------------------------

	def chooseAction(self, currentState):
		self.mostRecentState = currentState
		action = self.qlearn.getAction(currentState)
		self.mostRecentAction = action
		return action

	def witnessResult(self, newState):
		reward = self.dumbReward()
		self.qlearn.incorporateFeedback(self.mostRecentState, self.mostRecentAction, reward, newState)
		if newState.timestep > self.expectedTimeSteps/2:
			self.trainingOrTesting = 'testing'
			self.qlearn.explorationProb = 0



# OUR ACTUAL MODEL
class QlearningModel(genericModel):
	def __init__(self):
		self.trainingOrTesting = 'training'
		self.qlearn = mdp.QLearningAlgorithm(self.generateActions, 0.7, self.featureExtractor)
		self.mostRecentState = None
		self.mostRecentAction = None
		self.numActions = 50	#Number of actions to generate each state
		self.oracle = 0

	def generateActions(self, state):
		masterList = []
		for actionNum in range(self.numActions):
			#For each truck, insert a point into point_list
			point_list = []

			#Heuristic to only include points directing trucks to nearby incidents
			#TODO: what if two incidents at same location?
			incidentList = state.incidentPos.keys()

			#TODO: This is unintelligent if there are more incidents than trucks
			for i in xrange(0,len(state.truckPos)):
				if len(incidentList) > i:
					point_list.append(state.incidentPos[incidentList[i]])
				else:
					rrow = random.randint(0, self.nrow-1)
					rcol = random.randint(0, self.ncol-1)
					point_list.append((rrow, rcol))

			#Greedily assign each point to the nearest truck
			#This isnt the worst thing ever
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
		for i, (t_row, t_col) in enumerate(newState.truckPos):
			(directive_row, directive_col) = action[i]
			dy = directive_row - t_row
			dx = directive_col - t_col
			if abs(dy) > abs(dx):
				move_y = utilities.sign(dy)
				newState.truckPos[i] = (t_row + move_y, t_col)
			else:
				move_x = utilities.sign(dx)
				newState.truckPos[i] = (t_row, t_col + move_x)
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
		truckDistKey = ('truckDist',round(totalMin/float(numTrucks)))
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

		incidentKey = ('incidentDist', 0 if numIncidents == 0 else round(totalMin/float(numIncidents)))
		results.append((incidentKey,1))

		#TODO: Include time of day as a feature?
		#TODO: Include average horizontal and average vertical position of trucks as features?
		return results


	##--------------- Reward Functions ------------------------
	#Reward given at each state for minimizing squared distance to NEW Incidents
	def newIncidentAppearsReward(self, newState):
		if len(newState.newIncidents) is not 0:
			totalDist = sum( min(utilities.manhattanDistance(tPos, iPos) for tPos in newState.truckPos) for incident, iPos in newState.newIncidents.iteritems())	#This could double count some trucks
			return 1000/(totalDist**2 + 1)	#No dividing by infinity
		else:
			return 0
	##---------------------------------------------------------


	def chooseAction(self, currentState):
		self.mostRecentState = currentState
		action = self.qlearn.getAction(currentState)
		self.mostRecentAction = action
		return action

	def witnessResult(self, newState):
		#reward = self.incidentsResolvedReward(newState)
		reward = self.newIncidentAppearsReward(newState)
		self.qlearn.incorporateFeedback(self.mostRecentState, self.mostRecentAction, reward, newState)
		if newState.timestep > self.expectedTimeSteps/2:
			self.trainingOrTesting = 'testing'
			self.qlearn.explorationProb = 0