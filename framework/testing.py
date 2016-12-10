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
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(50), i)
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


qLearningTimes = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	qlearningModel = models.QlearningModel(explorationProb = 0.2)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(10), i)
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

a = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Naive Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	naiveQModel = models.NaiveQlearningModel(explorationProb = 0.2, numActions = 5)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(20), i)
	dd1.dispenseData(naiveQModel)
	a.append(dd1.averageResponseTime)
print a

b = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Naive Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	naiveQModel = models.NaiveQlearningModel(explorationProb = 0.2, numActions = 10)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(20), i)
	dd1.dispenseData(naiveQModel)
	b.append(dd1.averageResponseTime)
print b

c = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Naive Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	naiveQModel = models.NaiveQlearningModel(explorationProb = 0.2, numActions = 50)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(20), i)
	dd1.dispenseData(naiveQModel)
	c.append(dd1.averageResponseTime)
print c

d = []
for i in xrange(truckRange[0], truckRange[1]):
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	print "Naive Qlearning Model: ", i
	print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	naiveQModel = models.NaiveQlearningModel(explorationProb = 0.2, numActions = 100)
	dd1 = dataDispenser(datetime.datetime(9,1,1), datetime.timedelta(20), i)
	dd1.dispenseData(naiveQModel)
	d.append(dd1.averageResponseTime)
print d



plt.plot(truckVec, naiveQLearningTimes, truckVec, a, truckVec, b, truckVec, c, truckVec, d)
plt.show()




#Qlearning is better than Greedy for any value of exploration prob
#NaiveQlearning is the same for any value of exploration prob
#Qlearning is the same as Greedy when numActions = 1
#!!! More actions makes NaiveQlearning better???

#[12.064388311045072, 7.031863959055638, 5.127125639755655, 4.076770678553739, 3.328875681030213]
#[9.346706290242695, 5.293379560838699, 3.81954763084035, 2.9552583787353477, 2.463760937757966]
#[8.829288426613836, 4.920600858369099, 3.614000330196467, 2.7515681743149556, 2.2471112578408716]
#[9.002476473501734, 5.120026415717351, 3.568268119531121, 2.692091794617798, 2.1475978207033184]
#[9.027575957727873, 4.9940564635958395, 3.4106965995378014, 2.537890044576523, 1.9333003136866436]