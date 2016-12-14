def manhattanDistance(x1, x2):
	return abs(x1[0]-x2[0]) + abs(x1[1]-x2[1])

def sign(x):
	return (x>0) - (x<0)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)