import datetime
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import math



class gridDispenser():
	def __init__(self,day,timerange,dataFileNames= \
		[\
		'data/new_data/new_incidents2009.csv',\
		'data/new_data/new_incidents2010.csv',\
		'data/new_data/new_incidents2011.csv',\
		'data/new_data/new_incidents2012.csv',\
		'data/new_data/new_incidents2013.csv',\
		'data/new_data/new_incidents2014.csv',\
		'data/new_data/new_incidents2015.csv',\
		'data/new_data/new_incidents2016.csv',\
		]):
		#Emergency Medical Response,FS09000001,San Diego,Stabbing/Gunshot (L1),2800 BROADWAY,28TH ST/29TH ST,SAN DIEGO,92102,1/1/09 0:05:49,1/1/09 0:08:08,0:02:19
		self.data = []
		self.dataLength = []
		self.gridHorizontalGranularity = 20
		self.corners = [(33.112853, -117.358872), (32.644608, -116.883714)]
		ratio = (self.corners[0][0]-self.corners[1][0])/(self.corners[1][1]-self.corners[0][1])
		self.gridVerticleGranularity = int(ratio * self.gridHorizontalGranularity)
		self.grid = self.getGrid()
		self.start = day
		self.end = day+timerange
		print self.start, self.end

		#self.data is a list with 8 elements: the lists of data for each year
		for fileName in dataFileNames:
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
		self.grid_mapper = self.grid_map_data()
		self.heat_map()

	def heat_map(self):
		grid_mapper_lengths = []
		for r in xrange(0,self.gridVerticleGranularity):
			tempRow = []
			for c in xrange(0,self.gridHorizontalGranularity):
				tempRow.append(math.log(len(self.grid_mapper[r][c])+1))
			grid_mapper_lengths.append(tempRow)
		plt.imshow(grid_mapper_lengths, cmap='hot', interpolation='nearest')
		plt.show()
		hour_by_hour = []
		for i in xrange(0,24):
			tempGrid = []
			for r in xrange(0,self.gridVerticleGranularity):
				tempRow = []
				for c in xrange(0,self.gridHorizontalGranularity):
					tempRow.append(0)
				tempGrid.append(tempRow)
			hour_by_hour.append(tempGrid)
		for r in xrange(0,self.gridVerticleGranularity):
			for c in xrange(0,self.gridHorizontalGranularity):
				for el in self.grid_mapper[r][c]:
					hour_by_hour[el[0].hour][r][c] += 1
		for i in xrange(0,24):
			for r in xrange(0,self.gridVerticleGranularity):
				for c in xrange(0,self.gridHorizontalGranularity):
					hour_by_hour[i][r][c] = math.log(hour_by_hour[i][r][c]+1)

		for i in xrange(0,24):
			plt.imshow(hour_by_hour[i], cmap='hot', interpolation='nearest')
			plt.show()

	def getGrid(self):
		#grid[0][0] is the northwest corner of sanDiego and grid[n][m] is the southeast.
		#This means that the latitude  at grid[0][0] is greater than the latitude  at grid[n][m]
		#and 			 the longitude at grid[0][0] is less    than the longitude at grid[n][m]
		vertSteps = self.gridVerticleGranularity
		horizontalSteps = self.gridHorizontalGranularity
		deltaLat = abs(self.corners[0][0]-self.corners[1][0]) 
		deltaLong = abs(self.corners[0][1]-self.corners[1][1]) 
		grid = []
		for r in xrange(0,self.gridVerticleGranularity):
			tempRow = []
			for c in xrange(0,self.gridHorizontalGranularity):
				curLat = self.corners[0][0] - r*(deltaLat/(self.gridVerticleGranularity))
				curLong = self.corners[0][1] + c*(deltaLong/(self.gridHorizontalGranularity))
				tempRow.append((curLat,curLong))
			grid.append(tempRow)
		return grid

	def whereOnGrid(self,lat,longd):
		if lat > self.corners[0][0] or lat < self.corners[1][0]:
			return None
		if longd < self.corners[0][1] or longd > self.corners[1][1]:
			return None

		curRow = 0
		curCol = 0
		while curRow < self.gridVerticleGranularity-1:
			if self.grid[curRow+1][0][0] < lat:
				break
			curRow += 1
		while curCol < self.gridHorizontalGranularity-1:
			if self.grid[0][curCol+1][1] > longd:
				break
			curCol += 1

		return (curRow,curCol)



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

	def getDateTime(self,timeString):
		#year, month, day, hour*24*60 + minute*60 + second
		#example:   11/23/09 20:42:52
		myList = timeString.strip().split()[0].split('/')
		timeList = timeString.strip().split()[1].split(':')
		myDateTime = datetime.datetime(int(myList[2]),int(myList[0]),int(myList[1]),int(timeList[0]),int(timeList[1]),int(timeList[2]))
		return myDateTime

	def grid_map_data(self):
		gridMapper = [[[] for i in xrange(0,self.gridHorizontalGranularity)] for j in xrange(0,self.gridVerticleGranularity)]
		total = 0
		totalIN = 0
		for datapoint in self.data:
			lati = float(datapoint[1][4].split('_')[0])
			lond = float(datapoint[1][4].split('_')[1])
			location = self.whereOnGrid(lati, lond)
			total += 1
			if location == None:
				continue
			totalIN += 1
			gridMapper[location[0]][location[1]].append(datapoint)
		print float(totalIN)/float(total)
		return gridMapper

myGridDispenser = gridDispenser(datetime.datetime(9,1,1), datetime.timedelta(10000))
