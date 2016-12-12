from framework import *
import models
import matplotlib.pyplot as plt


truckRange = (3, 8)
truckVec = []
for i in xrange(truckRange[0], truckRange[1]):
	truckVec.append(i)

'''
oracleTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Oracle Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	oracleModel = models.Oracle()
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(100), i)
	dd1.dispenseData(oracleModel)
	oracleTimes.append(dd1.averageResponseTime)
print oracleTimes

greedyTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Greedy Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	greedymodel = models.GreedyAssignmentModel()
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(100), i)
	dd1.dispenseData(greedymodel)
	greedyTimes.append(dd1.averageResponseTime)
print greedyTimes
'''

qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.05, numActions = 10, discount = 0.4)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(1), i)
	dd1.dispenseData(qlearningModel)
	qLearningTimes.append(dd1.averageResponseTime)
print qLearningTimes

qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.05, numActions = 10, discount = 0.4)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(5), i)
	dd1.dispenseData(qlearningModel)
	qLearningTimes.append(dd1.averageResponseTime)
print qLearningTimes

qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.05, numActions = 10, discount = 0.4)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(20), i)
	dd1.dispenseData(qlearningModel)
	qLearningTimes.append(dd1.averageResponseTime)
print qLearningTimes

qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.05, numActions = 10, discount = 0.4)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(100), i)
	dd1.dispenseData(qlearningModel)
	qLearningTimes.append(dd1.averageResponseTime)
print qLearningTimes


'''
naiveQLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Naive Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	naiveQModel = models.NaiveQlearningModel(explorationProb = 0.2, numActions = 1)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(20), i)
	dd1.dispenseData(naiveQModel)
	naiveQLearningTimes.append(dd1.averageResponseTime)
print naiveQLearningTimes
'''

#plt.plot(truckVec, qLearningTimes)
#plt.show()

#Discount doesnt matter much as long as its in the middle
#For the current featuers, explorationProb doesnt make much of a difference

#Goal: Develop features that will actually give us an improvement
