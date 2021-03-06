import utilities
import qlearning as mdp
import random
import copy
import sys


class genericModel:
	def __init__(self):
		raise("Override Me")

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
		


class Oracle(genericModel):
	def __init__(self):
		self.oracle = 1
		self.currentTimeStep = 0

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
						point_list.append(self.future_data[tempTime][tempPoint][4])
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

	def accept_data(self, data):
		self.future_data = data


#Our Baseline Model
class GreedyAssignmentModel(genericModel):
	def __init__(self):
		self.oracle = 0

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



# OUR ACTUAL MODEL
class QlearningModel(genericModel):
	def __init__(self, discount = 0.5, explorationProb = 0.2, numActions = 100):
		self.qlearn = mdp.QLearningAlgorithm(self.generateActions, discount, self.featureExtractor, explorationProb)
		self.mostRecentState = None
		self.mostRecentAction = None
		self.numActions = numActions	#Number of actions to generate in each state
		self.oracle = 0

	def generateActions(self, state):
		masterList = []
		for actionNum in range(self.numActions):
			#For each truck, insert a point into point_list
			point_list = []

			#Include points directing trucks to nearby incidents
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
		results = []

		#Features should help to distinguish between actions!
		#This allows us to evaluate the truck locations after an action has taken place
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
				if utilities.manhattanDistance(newState.truckPos[truck],newState.truckPos[other_truck]) < myMin:
					myMin = utilities.manhattanDistance(newState.truckPos[truck],newState.truckPos[other_truck])
					minPos = other_truck
			totalMin += myMin
		truckDistKey = ('truckDist',round(totalMin/float(numTrucks)))
		results.append((truckDistKey,1))

		#Indicators on general position of trucks
		#Essentially this "reduces" the grainularity of the grid from the perspective of Qlearning
		granularityScale = 3	# Use 2 or 3
		for truck in newState.truckPos:
			xpos, ypos = truck
			ysection = ypos / granularityScale
			xsection = xpos / granularityScale
			sectionIndiator = ('SectionIndicator', (xsection, ysection))
			columnIndicator = ('ColIndicator', ysection)
			rowIndicator = ('RowIndicator', xsection)
			if sectionIndiator not in results:
				results.append((sectionIndiator,1))
			if columnIndicator not in results:
				results.append((columnIndicator,1))
			if rowIndicator not in results:
				results.append((rowIndicator,1))

		return results


	##--------------- Reward Functions ------------------------
	def newIncidentAppearsReward(self, newState):
		if len(newState.newIncidents) is not 0:
			totalDist = sum( min(utilities.manhattanDistance(tPos, iPos) for tPos in newState.truckPos) for incident, iPos in newState.newIncidents.iteritems())	#This could double count some trucks
			return -1*totalDist
		else:
			return 0
	##---------------------------------------------------------


	def chooseAction(self, currentState):
		self.mostRecentState = currentState
		action = self.qlearn.getAction(currentState)
		self.mostRecentAction = action
		return action

	def witnessResult(self, newState):
		reward = self.newIncidentAppearsReward(newState)
		self.qlearn.incorporateFeedback(self.mostRecentState, self.mostRecentAction, reward, newState)
