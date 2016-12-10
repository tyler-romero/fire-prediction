import utilities
import models
import datetime
import random
import math
import copy
import sys
import simulation



class dataDispenser():
	def __init__(self,day,timerange,ts=4,dataFileNames=['data/new_data/new_incidents2009.csv']):
		#,'incidents2010.csv',\
		#'incidents2011.csv','incidents2012.csv','incidents2013.csv','incidents2014.csv',\
		#'incidents2015.csv','incidents2016.csv']):
		#Emergency Medical Response,FS09000001,San Diego,Stabbing/Gunshot (L1),2800 BROADWAY,28TH ST/29TH ST,SAN DIEGO,92102,1/1/09 0:05:49,1/1/09 0:08:08,0:02:19
		self.data = []
		self.dataLength = []
		self.start = day
		self.end = day+timerange
		self.averageResponseTime = None
		self.ts =ts

		#self.data is a list with 8 elements: the lists of data for each year
		for fileName in dataFileNames:
			self.timeStep = 60
			self.dataFile = open(fileName,'rU')
			first = 1
			for line in self.dataFile:
				if first == 1:
					first = 0
					continue
				splitList = self.splitComma(line.strip())
				dateTime = self.getDateTime(splitList[8])
				if splitList[4] == '0_0':
					continue
				#splitList = self.fixLatLong(splitList)
				if len(splitList) != 11 and len(splitList) != 12:
					print splitList
					raise Exception('Data is not proper number of fields')
				if dateTime >= self.start and dateTime <= self.end:
					self.data.append([dateTime, splitList])
			self.dataLength = len(self.data)


	def splitComma(self,myStr):
		#necessary because data has form _one,_two,"three, three continued", four
		returnList = []
		previous = 0
		inquotes = 0
		for i in xrange(0,len(myStr)):
			if myStr[i] == '"':
				if inquotes == 1:
					inquotes = 0
				else:
					inquotes = 1
			if myStr[i] == ",":
				if inquotes == 0:
					returnList.append(myStr[previous:i])
					previous = i+1
		returnList.append(myStr[previous:len(myStr)])
		return returnList


	def fixLatLong(self,myList):
		myList[4] = myList[4].split('-')[0]+'_-'+myList[4].split('-')[1]
		return myList


	def getDateTime(self,timeString):
		#year, month, day, hour*24*60 + minute*60 + second
		#example:   11/23/09 20:42:52
		myList = timeString.strip().split()[0].split('/')
		timeList = timeString.strip().split()[1].split(':')
		myDateTime = datetime.datetime(int(myList[2]),int(myList[0]),int(myList[1]),int(timeList[0]),int(timeList[1]),int(timeList[2]))
		return myDateTime

	def giveOracleData(self,model):
		startTime = self.data[0][0]
		currentTime = startTime
		endTime = self.data[-1][0]
		timeStep = datetime.timedelta(0,self.timeStep)
		currentElement = 0
		currentTime = currentTime - timeStep
		dataMapper = []
		timeStepNumber = 0 
		while currentTime < endTime:
			while self.data[currentElement][0] < currentTime:
				currentElement+=1
				dataMapper.append(timeStepNumber)
				#maps each piece of data to a time step number
				if currentElement >= self.dataLength:
					break
			currentTime = currentTime +timeStep
			timeStepNumber += 1

		returnList = []
		timeStepNumber = 0
		i = 0
		while i < len(dataMapper):
			passList = []
			while dataMapper[i] <= timeStepNumber:
				passList.append(self.data[i][1])
				i+=1
				if i == len(dataMapper):
					break
			returnList.append(passList)
			timeStepNumber+=1

		model.accept_data(returnList)

	def dispenseData(self, model):
		if model.oracle == 1:
			self.giveOracleData(model)
		startTime = self.data[0][0]
		currentTime = startTime
		endTime = self.data[-1][0]
		timeStep = datetime.timedelta(0,self.timeStep)
		currentElement = 0
		currentTime = currentTime - timeStep
		dataMapper = []
		timeStepNumber = 0 
		while currentTime < endTime:
			while self.data[currentElement][0] < currentTime:
				currentElement+=1
				dataMapper.append(timeStepNumber)
				#maps each piece of data to a time step number
				if currentElement >= self.dataLength:
					break
			currentTime = currentTime +timeStep
			timeStepNumber += 1

		simulationInstance = simulation.Simulation(model, timeStepNumber, self.ts)
		timeStepNumber = 0
		i = 0
		while i < len(dataMapper):
			passList = []
			while dataMapper[i] <= timeStepNumber:
				passList.append(self.data[i][1])
				i+=1
				if i == len(dataMapper):
					break
			simulationInstance.executeTimestep(passList, timeStepNumber)
			timeStepNumber+=1
		
		self.averageResponseTime = simulationInstance.compileResults()




