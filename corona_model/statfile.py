import statistics as stat
import numpy as np
import matplotlib.pyplot as plt
# this file is used for analyzing the data and providing insights

def analyzeModel(simulationData):
    """
        the only function that is not stand alone, 
        requires data from model_framework

        Parameters:
        - list of list that stores the time series of one variable
            Ex: [
                [number of infected for each time slice for simulation 1],
                [number of infected for each time slice for simulation 2],
                ...,
                [number of infected for each time slice for simulation n]
            ]
    """
    infoList = []
    changes = []
    changeInfo = []
    for row in simulationData:
        infoList.append(analyzeData(row))
        dxdt = changeOverUnitTime(row)
        changes.append(dxdt)
        changeInfo.append(analyzeData(dxdt))
    
    filteredInfo = []
    filteredChange = []
    filteredChangeInfo = []
    # this filters zeros and empty values
    for row in simulationData:
        row = filterZeros(row)
        filteredInfo.append(analyzeData(row))
        dxdt = changeOverUnitTime(row)
        filteredChange.append(dxdt)
        filteredChangeInfo.append(analyzeData(dxdt))

    simulationAverages = [a[0] for a in infoList]
    simulationDx = [a[0] for a in filteredChangeInfo]


    return (simulationAverages, simulationDx)

def plotBoxAverageAndDx(simulationDatas, labels=[]):
    average = []
    dx = []
    for simulationData in simulationDatas:
        dataTup = analyzeModel(simulationData)
        average.append(dataTup[0])
        dx.append(dataTup[1])
    boxplot(average, "averages", "models", "infected #", labels=labels)
    #boxplot(dx, "averageChanges", "models", "d(infected)/dt #", labels=labels)


def boxplot(data, oneD=True, pltTitle="Some Title", xlabel="Default X", ylabel="Default Y", labels=[], showplt=True, saveplt=False):
    # nice example of boxplots:
    # https://matplotlib.org/2.0.1/examples/statistics/boxplot_color_demo.html
    fig1, ax1 = plt.subplots()
    ax1.set_title(pltTitle)
    ax1.boxplot(data, vert=True)
    ax1.yaxis.grid(True)
    xticks = [a+1 for a in range(len(data))]
    ax1.set_xticks(xticks)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    """
    if oneD:
        plt.xlim(-2, 2)
    else:
        plt.xlim(-2, len(data)+2+2)
    """
    if labels != [] and len(labels) == len(data):
        plt.setp(ax1, xticks=xticks, xticklabels=labels)
    plt.show()

def changeOverUnitTime(listData):
    """
        return a list of size n-1 which stores the chnages that occured over each entry
    """
    newData = np.array(listData)
    shfitedOriginal = newData[:-1]
    shiftedData = newData[1:]
    return shiftedData-shfitedOriginal 

def filterZeros(listData):
    "return a list with continuous zeros removed"
    tempList = [a for i, a in enumerate(listData) if not (0.0001 > a > -0.0001) or (i == 0 or not (0.0001>listData[i-1] > -0.0001))]
    return tempList

def analyzeData(ListData):
    """
    simple function that returns mean, median, mode, stdDev as a tuple
    """
    # convert to numpy array
    newData = np.array(ListData)
    # numpy's statistic functions
    rangeVal = np.ptp(newData)
    median = np.median(newData)
    npMean = np.mean(newData)
    stdev = np.std(newData)

    # non numpy function
    #geo_mean = geometric_mean(ListData)
    
    return (npMean, stdev, rangeVal, median)

def geometric_mean(listData):
    """
        this function is created in python's statistics library from 3.8
        since I, the user, am using python 3.7, I made this function to fill my need

        if you're running python >= 3.8, make sure to call statistics.geometric_mean() instead of this one
    """

    # geometric mean = n-th root of (X1*X2*...*Xn)
    # log (geometric mean)  = 1/n * (log(X1)+log(X2)+...+log(Xn))
    # to return it to the geometric mean, take both side to the power of e
    npData = np.array(listData)
    if min(listData) == 0:
        # add a very small value to the data to allow log
        npData += np.full(len(npData), 0.00001)
    elif min(listData)<0: # geometric mean doesnt work with negative
        return 0
   
    logData = np.log(npData)
    logSum = np.sum(logData)
    return np.exp((1/len(logData)) * logSum)
 


def main():
    data = [10, 10, 10, 11, 12,41,71,1,1,12,3,56, 0,5,75,4, 0, 0, 0]
    print(changeOverUnitTime(data))
    print(filterZeros(data))
    analyzeModel([data])
    boxplot([data for _ in range(3)])

if __name__ == "__main__":
    main()