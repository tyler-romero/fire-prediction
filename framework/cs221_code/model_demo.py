from framework import *
import models


truckRange = (3, 6)
truckVec = []
for i in xrange(truckRange[0], truckRange[1]):
	truckVec.append(i)

qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.05, numActions = 20, discount = 0.6)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(10), i, verbose = True)
	dd1.dispenseData(qlearningModel)
	qLearningTimes.append(dd1.averageResponseTime)
print qLearningTimes



