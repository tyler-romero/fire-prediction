import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense,Activation


size_of_y_grid = (20,20)


x_train_temp = open('data/x_train.txt','r')
x_train_points = 0
for line in x_train_temp:
	if line.strip() == 'NEW_POINT':
		x_train_points += 1
x_train_temp.close()

x_valid_temp = open('data/x_valid.txt','r')
x_valid_points = 0
for line in x_valid_temp:
	if line.strip() == 'NEW_POINT':
		x_valid_points += 1
x_valid_temp.close()

x_test_temp = open('data/x_test.txt','r')
x_test_points = 0
for line in x_test_temp:
	if line.strip() == 'NEW_POINT':
		x_test_points += 1
x_test_temp.close()

x_train = open('data/x_train.txt','r')
print 1
y_train = open('data/y_train.txt','r')
print 2
x_valid = open('data/x_valid.txt','r')
print 3
y_valid = open('data/y_valid.txt','r')
print 4
x_test = open('data/x_test.txt','r')
print 5
y_test = open('data/y_test.txt','r')
print 6

def return_npArray_x(f,size):
	prevLine = None
	a = np.zeros((size,67))
	count = 0
	for line in f:
		if count % 10000 == 0:
			print count
		if line == '':
			continue
		if line.strip() == 'NEW_POINT':
			myList = prevLine.strip().split()
#			added = np.array([[float(myList[2]),float(myList[2]),float(myList[2]),float(myList[2]),float(myList[3]),float(myList[3]),float(myList[3]),float(myList[3]),float(myList[4]),float(myList[4]),float(myList[4]),float(myList[4])]])
			added = np.zeros((1,67))
			added[0][int(myList[2])] = 1
			ind = 23+int(myList[4])
			added[0][ind] = 1
			added[0][35+int(myList[3])] = 1
			a[count] = added
			count +=1 
		else:
			prevLine = line

	return a

def return_npArray_y(f,size_1,size_2):
	grid = None
	totArr = np.zeros((int(size_1),int(size_2)))
	count = 0
	currentLine = 0
	for line in f:
		count +=1 
		if count % 10000 == 0:
			print count
		if line == '':
			continue
		if line.strip() == 'NEW_POINT':
			totArr[currentLine] = grid
			currentLine+=1
			grid = None
		else:
			myList = line.strip().split()
			a = []
			for el in myList:
				a.append(float(el))
			if grid == None:
				grid = np.array([a])
			else:
				grid = np.append(grid,[a])
	return totArr


ys = size_of_y_grid[0]*size_of_y_grid[1]

x_train_arr = return_npArray_x(x_train,x_train_points)
print np.shape(x_train_arr)
y_train_arr = return_npArray_y(y_train, np.shape(x_train_arr)[0], ys)
print np.shape(y_train_arr)
x_valid_arr = return_npArray_x(x_valid,x_valid_points)
print np.shape(x_valid_arr)
y_valid_arr = return_npArray_y(y_valid, np.shape(x_valid_arr)[0], ys)
print np.shape(y_valid_arr)
x_test_arr = return_npArray_x(x_test,x_test_points)
print np.shape(x_test_arr)
y_test_arr = return_npArray_y(y_test, np.shape(x_test_arr)[0], ys)
print np.shape(y_test_arr)

model = Sequential()
model.add(Dense(input_dim=67, output_dim=ys, activation='linear'))
model.add(Dense(input_dim=ys, output_dim=ys, activation='linear'))
model.add(Dense(input_dim=ys, output_dim=ys, activation='linear'))

#model.add(Dense(input_dim=9, output_dim=3*3))
#model.add(Dense(input_dim=3*3, output_dim=19*20))
#model.add(Dense(input_dim=19*20, output_dim=19*20))
model.add(Activation('relu'))
model.compile(loss='mean_squared_error', optimizer='adagrad')
single_y_train = y_train_arr
single_y_valid = y_valid_arr
model.fit(x_train_arr, single_y_train, batch_size=100, nb_epoch=5, shuffle=True, validation_data=(x_valid_arr, single_y_valid))

single_y_test = y_test_arr
tresults = model.evaluate(x_test_arr, single_y_test)

print tresults

y = model.predict(x_test_arr, verbose=1)


average_y_train = np.average(single_y_test,axis=0)
total_sum=0
total = 0 
for i in xrange(0,np.shape(single_y_test)[0]):
	total += 1
	total_sum += np.linalg.norm(average_y_train-single_y_test[i])
total_sum_2 = 0
total_2 = 0
for i in xrange(0,np.shape(y)[0]):
	total_2 += 1
	total_sum_2  += np.linalg.norm(y[i]-single_y_test[i])

print 'mean_squared_error ', float(total_sum)/float(total)
print 'net_squared_error', float(total_sum_2)/float(total_2)

