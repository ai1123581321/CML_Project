import numpy as np
import sys
from sklearn import datasets

max_iter = 50
data = datasets.load_iris().data
randomSeed = 10161990
rnd = np.random.RandomState(randomSeed)

def calDistance(vecX, vecY):
    # Calculate the distance between two vectors
    sumV = 0
    for i in xrange(0, len(vecX)):
        sumV += (vecX[i] - vecY[i]) ** 2
    return sumV

def findCloestCentroid(x, k_centroids):
    # For a vector x, and k clusters, calculate the distance between x and 
    # each centroid and also return the closest centroid index to x
    minDis = sys.maxint
    index = 0
    for i in xrange(len(k_centroids)):
        dis = calDistance(x, k_centroids[i])
        if dis < minDis:
            minDis = dis
            index = i
    return (index, minDis)

def updateCentroid(k_clusters, label_count):
    # Takes a tuple of size k, each element is a tuple of vector
    # Return a tuple of k vector as the new centroid  
    new_centroid = []
    for cluster in k_clusters:
        centroid = [0] * label_count
        if len(cluster) > 0:
            for x in cluster:
                for i in xrange(0, label_count):
                    centroid[i] += x[i]
            for j in xrange(0, label_count):
                centroid[j] = centroid[j] / len(cluster)
        new_centroid.append(centroid)
    return new_centroid   

def rndCluster(data, k):
    rnd_index = rnd.randint(low=0, high=len(data), size=k)
    # print rnd_index
    return data[rnd_index]
    
def computeTtlDistortion(data, k_centroid, centroid_index_list):
    # Calculate the total distance by adding the distance between each x 
    # and the prototype it belongs to, i.e. via the findCloestCentroid
    total_dis = 0
    for x in xrange(0, len(centroid_index_list)):
        index = centroid_index_list[x]
        total_dis += calDistance(data[x], k_centroid[index])
    return total_dis
    

def mykmeans(data, k, max_iter=max_iter, init_centorid=None):
    k_centroid = rndCluster(data, k) if init_centorid is None else init_centorid
    label_count = len(data[0])
    centroid_index_list = []
    index_set = set([])
    for i in xrange(max_iter):
        new_clusters = [[] for j in xrange(k)]
        index = 0
        for x in data:
            index = findCloestCentroid(x, k_centroid)[0]
            new_clusters[index].append(x)
            index_set.add(index)
            if i == max_iter - 1:
                centroid_index_list.append(index)
        new_centroid = updateCentroid(new_clusters, label_count)
        k_centroid = new_centroid
    return (k_centroid, centroid_index_list)


def mykmeans_multi(data, run, k, max_iter=max_iter, init_centorid=None):
    min_dist = sys.maxint
    min_final_centroid = None
    min_init_centroid = None
    for i in xrange(run):
        # Each time choose different random centroid
        init_centorid = rndCluster(data, k) if init_centorid is None else init_centorid
        # Find the corresponding k_centroid by mykmeans
        k_centroid, centroid_index_list = mykmeans(data=data, k=k,
                                            max_iter=max_iter, init_centorid=init_centorid)
        total_dis = computeTtlDistortion(data, k_centroid, centroid_index_list)
        if total_dis < min_dist:
            min_dist = total_dis
            min_final_centroid = k_centroid
            min_init_centroid = init_centorid
    return (min_init_centroid, min_final_centroid)
    
def mykmeans_plus(data, k, max_iter=max_iter):
    init_centorid = rndCluster(data, 1).tolist()
    while len(init_centorid) < k:
        dis_array = []
        for x in data:
            dis_array.append(findCloestCentroid(x, init_centorid)[1])
        rnd = np.random.randint(0, sum(dis_array))
        i = 0
        while rnd > 0 and i < len(dis_array):
        # Data point with larger distortion value has more chance of being selected
            rnd -= dis_array[i]
            i += 1
        if i == len(dis_array):
            i -= 1
        init_centorid.append(data[i])
    return mykmeans(data, k, init_centorid=init_centorid)
