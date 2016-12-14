from framework import *
import models
import matplotlib.pyplot as plt


truckRange = (3, 8)
truckVec = []
for i in xrange(truckRange[0], truckRange[1]):
	truckVec.append(i)


oracleTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Oracle Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	oracleModel = models.Oracle()
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(10), i)
	dd1.dispenseData(oracleModel)
	oracleTimes.append(dd1.averageResponseTime)
print oracleTimes

greedyTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Greedy Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	greedymodel = models.GreedyAssignmentModel()
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(10), i)
	dd1.dispenseData(greedymodel)
	greedyTimes.append(dd1.averageResponseTime)
print greedyTimes

qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.05, numActions = 10, discount = 0.6)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(10), i)
	dd1.dispenseData(qlearningModel)
	qLearningTimes.append(dd1.averageResponseTime)
print qLearningTimes


plt.plot(truckVec, oracleTimes, truckVec, greedyTimes, truckVec, qLearningTimes)
plt.show()

