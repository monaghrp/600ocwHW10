# Problem Set 10
# Name:
# Collaborators:
# Time:

#Code shared across examples
import pylab, random, string, copy, math

class Point(object):
    def __init__(self, name, originalAttrs, normalizedAttrs = None):
        """normalizedAttrs and originalAttrs are both arrays"""
        self.name = name
        self.unNormalized = originalAttrs
        self.attrs = normalizedAttrs
    def dimensionality(self):
        return len(self.attrs)
    def getAttrs(self):
        return self.attrs
    def getOriginalAttrs(self):
        return self.unNormalized
    def distance(self, other):
        #Euclidean distance metric
        difference = self.attrs - other.attrs
        return sum(difference * difference) ** 0.5
    def getName(self):
        return self.name
    def toStr(self):
        return self.name + str(self.attrs)
    def __str__(self):
        return self.name

class County(Point):
    ##weights = pylab.array([1.0] * 14)
    ##poverty set to 0
    ##weights = pylab.array([1.0,1.0,0.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0])
    weights = pylab.array([1.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0])
    
    # Override Point.distance to use County.weights to decide the
    # significance of each dimension
    def distance(self, other):
        difference = self.getAttrs() - other.getAttrs()
        return sum(County.weights * difference * difference) ** 0.5
    
class Cluster(object):
    def __init__(self, points, pointType):
        self.points = points
        self.pointType = pointType
        self.centroid = self.computeCentroid()
    def getCentroid(self):
        return self.centroid
    def computeCentroid(self):
        dim = self.points[0].dimensionality()
        totVals = pylab.array([0.0]*dim)
        for p in self.points:
            totVals += p.getAttrs()
        meanPoint = self.pointType('mean',
                                   totVals/float(len(self.points)),
                                   totVals/float(len(self.points)))
        return meanPoint
    def update(self, points):
        oldCentroid = self.centroid
        self.points = points
        if len(points) > 0:
            self.centroid = self.computeCentroid()
            return oldCentroid.distance(self.centroid)
        else:
            return 0.0
    def getPoints(self):
        return self.points
    def contains(self, name):
        for p in self.points:
            if p.getName() == name:
                return True
        return False
    def toStr(self):
        result = ''
        for p in self.points:
            result = result + p.toStr() + ', '
        return result[:-2]
    def __str__(self):
        result = ''
        for p in self.points:
            result = result + str(p) + ', '
        return result[:-2]
        

    
def kmeans(points, k, cutoff, pointType, minIters = 3, maxIters = 100, toPrint = False):
    """ Returns (Cluster list, max dist of any point to its cluster) """
    #Uses random initial centroids
    initialCentroids = random.sample(points,k)
    clusters = []
    for p in initialCentroids:
        clusters.append(Cluster([p], pointType))
    numIters = 0
    biggestChange = cutoff
    while (biggestChange >= cutoff and numIters < maxIters) or numIters < minIters:
        ##print "Starting iteration " + str(numIters)
        newClusters = []
        for c in clusters:
            newClusters.append([])
        for p in points:
            smallestDistance = p.distance(clusters[0].getCentroid())
            index = 0
            for i in range(len(clusters)):
                distance = p.distance(clusters[i].getCentroid())
                if distance < smallestDistance:
                    smallestDistance = distance
                    index = i
            newClusters[index].append(p)
        biggestChange = 0.0
        for i in range(len(clusters)):
            change = clusters[i].update(newClusters[i])
            #print "Cluster " + str(i) + ": " + str(len(clusters[i].points))
            biggestChange = max(biggestChange, change)
        numIters += 1
        if toPrint:
            ##print 'Iteration count =', numIters
            pass
    maxDist = 0.0
    for c in clusters:
        for p in c.getPoints():
            if p.distance(c.getCentroid()) > maxDist:
                maxDist = p.distance(c.getCentroid())
    ##print 'Total Number of iterations =', numIters, 'Max Diameter =', maxDist
    ##print biggestChange
    return clusters, maxDist

#US Counties example
def readCountyData(fName, numEntries = 14):
    dataFile = open(fName, 'r')
    dataList = []
    nameList = []
    maxVals = pylab.array([0.0]*numEntries)
    #Build unnormalized feature vector
    for line in dataFile:
        if len(line) == 0 or line[0] == '#':
            continue
        dataLine = string.split(line)
        name = dataLine[0] + dataLine[1]
        features = []
        #Build vector with numEntries features
        for f in dataLine[2:]:
            try:
                f = float(f)
                features.append(f)
                if f > maxVals[len(features)-1]:
                    maxVals[len(features)-1] = f
            except ValueError:
                name = name + f
        if len(features) != numEntries:
            continue
        dataList.append(features)
        nameList.append(name)
    return nameList, dataList, maxVals
    
def buildCountyPoints(fName):
    """
    Given an input filename, reads County values from the file and returns
    them all in a list.
    """
    nameList, featureList, maxVals = readCountyData(fName)
    points = []
    for i in range(len(nameList)):
        originalAttrs = pylab.array(featureList[i])
        normalizedAttrs = originalAttrs/pylab.array(maxVals)
        points.append(County(nameList[i], originalAttrs, normalizedAttrs))
    return points

def randomPartition(l, p):
    """
    Splits the input list into two partitions, where each element of l is
    in the first partition with probability p and the second one with
    probability (1.0 - p).
    
    l: The list to split
    p: The probability that an element of l will be in the first partition
    
    Returns: a tuple of lists, containing the elements of the first and
    second partitions.
    """
    l1 = []
    l2 = []
    for x in l:
        if random.random() < p:
            l1.append(x)
        else:
            l2.append(x)
    return (l1,l2)

def getAveIncome(cluster):
    """
    Given a Cluster object, finds the average income field over the members
    of that cluster.
    
    cluster: the Cluster object to check
    
    Returns: a float representing the computed average income value
    """
    tot = 0.0
    numElems = 0
    for c in cluster.getPoints():
        tot += c.getOriginalAttrs()[1]

    return float(tot) / len(cluster.getPoints())


def test(points, k = 200, cutoff = 0.1):
    """
    A sample function to show you how to do a simple kmeans run and graph
    the results.
    """
    incomes = []
    print ''
    clusters, maxSmallest = kmeans(points, k, cutoff, County)

    for i in range(len(clusters)):
        if len(clusters[i].points) == 0: continue
        incomes.append(getAveIncome(clusters[i]))

    pylab.hist(incomes)
    pylab.xlabel('Ave. Income')
    pylab.ylabel('Number of Clusters')
    pylab.show()

        
points = buildCountyPoints('counties.txt')
##random.seed(123)
testPoints = random.sample(points, len(points)/10)


    
    
def graphRemovedErr(points, kvals = [25, 50, 75, 100, 125, 150], cutoff = 0.1):
##def graphRemovedErr(points, kvals = [10, 20, 30, 40, 50, 60], cutoff = 0.1):
    """
    Should produce graphs of the error in training and holdout point sets, and
    the ratio of the error of the points, after clustering for the given values of k.
    For details see Problem 1.
    """

    # Your Code Here
    holdOutSet,trainingSet=randomPartition(points,.2)
    ##print 'trainingSet: ' +str(trainingSet)
    trainingSetErr=[]
    holdOutSetErr=[]
    
    for i in xrange(0,len(kvals)):
        [clusters,maxDist]=kmeans(trainingSet, kvals[i], cutoff, County)
        ##increment over every cluster and every point in each cluster
        tempErr=0
        for j in xrange(0,len(clusters)):
            points=clusters[j].getPoints()
            clusters[j].computeCentroid()
            centroid=clusters[j].getCentroid()
            for k in xrange(0,len(points)):
                tempErr+=(points[k].distance(centroid))**2
        trainingSetErr.append(tempErr)
        
        ##increment through each point in the hold out set
        tempErr=0
        for j in xrange(len(holdOutSet)):
            distCheck=999
            ##increment through each cluster
            for k in xrange(0,len(clusters)):
                centroid=clusters[k].getCentroid()
                ##check distance between point and cluster center
                ##update if necessary
                if holdOutSet[j].distance(centroid)<distCheck:
                    distCheck=holdOutSet[j].distance(centroid)
            tempErr+=distCheck**2
        holdOutSetErr.append(tempErr)
    pylab.plot(kvals,trainingSetErr,label = "Training Set Error")
    pylab.plot(kvals,holdOutSetErr, label = "Holding Set Error")
    pylab.xlabel('K')
    pylab.ylabel('Error')
    pylab.legend(loc = "best")
    pylab.show()
    ratioErr=[]
    for i in xrange(0,len(trainingSetErr)):
        ratioErr.append(holdOutSetErr[i]/trainingSetErr[i])
    pylab.plot(kvals,ratioErr,label="Hold/Training Set Error Ratio")
    pylab.xlabel('K')
    pylab.ylabel('Error')
    pylab.legend(loc = "best")
    pylab.show()
            
##foo=buildCountyPoints('counties.txt')
##graphRemovedErr(foo)

def problem2():
    foo=buildCountyPoints('counties.txt')
    [clusters,maxDist]=kmeans(foo, 50, 0.1, County)
    for i in xrange(0,len(clusters)):
        points=clusters[i].getPoints()
        for j in xrange(0,len(points)):
            name=points[j].getName()
            if name=="WAKing":
                print 'Found it in cluster :' + str(i)
                for k in xrange(0,len(points)):
                    print str(points[k].getName())

##problem2()
##problem2()
##problem2()                    
##def graphPredictionErr(points, dimension, kvals = [25, 50, 75, 100, 125, 150], cutoff = 0.1):
def graphPredictionErr(points, kvals = [5,10,15,25,30], cutoff = 0.1):
    """
    Given input points and a dimension to predict, should cluster on the
    appropriate values of k and graph the error in the resulting predictions,
    as described in Problem 3.
    """

	# Your Code Here
    holdOutSet,trainingSet,=randomPartition(points,.2)
    poverty=[]
    for i in xrange(0,len(kvals)):
        [clusters,maxDist]=kmeans(trainingSet, kvals[i], cutoff, County)
        ##cycle through every point in the holdout set
        povErr=0
        for j in xrange(0,len(holdOutSet)):
            distCheck=999
            ##increment through each cluster
            for k in xrange(0,len(clusters)):
                clusters[k].computeCentroid()
                centroid=clusters[k].getCentroid()
                ##check distance between point and cluster center
                ##update if necessary
                if holdOutSet[j].distance(centroid)<distCheck:
                    distCheck=holdOutSet[j].distance(centroid)
                    index=k
            ##compute average value of poverty in associated cluster
            points=clusters[index].getPoints()
            povAvg=0
            for k in xrange(0,len(points)):
                povAvg+=points[k].getOriginalAttrs()[2]
            povAvg/=len(points)
            povErr+=(holdOutSet[j].getOriginalAttrs()[2]-povAvg)**2
        poverty.append(povErr)
    pylab.plot(kvals,poverty,label = "Poverty Error")
    pylab.xlabel('K')
    pylab.ylabel('Error')
    pylab.legend(loc = "best")
    pylab.show()       
                

foo=buildCountyPoints('counties.txt')
graphPredictionErr(foo)
