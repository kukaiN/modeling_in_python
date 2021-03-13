import statistics as stat
import numpy as np
import platform
import matplotlib.pyplot as plt
import fileRelated as flr
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
        #dxdt = changeOverUnitTime(row)
        #changes.append(dxdt)
        #changeInfo.append(analyzeData(dxdt))
    """
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
    """
    simulationAverages = [a[0] for a in infoList]
    simulationDx = [0]#[a[0] for a in filteredChangeInfo]


    return (simulationAverages, simulationDx)

def plotBoxAverageAndDx(simulationDatas, pltTitle="some Title", xlabel="models", ylabel="infected #",labels=[], showPlt=False, savePlt=False, saveName="defaultimage.png"):
    """
    run simple analysis on the given data and plot a box and whiskers graph

    Parameters:
    - simulationDatas: the data to plot
    - pltTitle: title for the generated plot
    - xlabel: label for the x axis
    - ylabel: label for the y axis
    - labels: the labels for each B&W plot
    - showplt: boolean, show the plot or not
    - savePlt: boolean, save the plot with the given filename or not
    - saveName: string, ends with .png or some file format, save the plot with this name

    """

    averages = []
    dx = []
    for simulationData in simulationDatas:
        dataTup = analyzeModel(simulationData)
        averages.append(dataTup[0])
        dx.append(dataTup[1])
    boxplot(averages, True, pltTitle=pltTitle, xlabel=xlabel, ylabel=ylabel, labels=labels, showPlt=showPlt, savePlt=savePlt, saveName=saveName)
    #boxplot(dx, "averageChanges", "models", "d(infected)/dt #", labels=labels)


def boxplot(data, oneD=False, pltTitle="Some Title", xlabel="Default X", ylabel="Default Y", labels=[], showPlt=True, savePlt=False, saveName="defaultimage.png", outputDir="outputs"):
    """
    Parameters:
    - data: the data to plot, can be a one or two dimentional list, if a 2D list is passed, each row is going to be a data for a separate box plot
    - oneD:  bool to tell if "data" is one dimentional or not
    - pltTitle: the title of the plot
    - xlabel: label for the x axis
    - ylabel: label for the y axis
    - labels: labels for each box plot, pass a list with one entry if there's one B&W, and a list filled with entries for multiple B&W
    - showPlt: boolean, show the plot or not
    - savePlt: boolean, save the plot with the given filename or not
    - saveName: string, ends with .png o some file format, save the plot with this name

    """
    # nice example of boxplots:
    # https://matplotlib.org/2.0.1/examples/statistics/boxplot_color_demo.html
    fig1, ax1 = plt.subplots()
    ax1.set_title(pltTitle)
    ax1.boxplot(data, vert=True)
    ax1.yaxis.grid(True)
    if oneD:
        xticks = [1]
    else:
        xticks = [a+ 1 for a in range(len(data))]
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(labels)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)


    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    #if labels != [] and len(labels) == len(data):
    #    #plt.setp(ax1, xticks=xticks, xticklabels=labels)
    #    #ax1.set_xticklabels(labels, rotation=45, ha="right")
    plt.tight_layout()
    if savePlt:
        if not saveName.endswith(".png"):
            saveName+=".png"
        print("image saved as", saveName)
        plt.savefig(flr.fullPath(saveName, outputDir))
    else:
        plt.show()
    plt.close()

def barChart(data, oneD=False, pltTitle="Some Title", xlabel="Default X", ylabel="Default Y", labels=[], showPlt=True, savePlt=False, saveName="defaultimage.png"):
    fig1, ax1 = plt.subplots()
    ax1.set_title(pltTitle)
    if oneD:
        mean, _, _, standardDev = analyzeData(data)
        barLoc = [1]
        width=0.05
    else:
        # each entry looks like (mean, median, mode, stdDev)
        dataList = [analyzeData(simData) for simData in data]
        mean = [int(a[0]*10)/10 for a in dataList]
        standardDev = [a[3] for a in dataList]
        barLoc = np.arange( len(data))
        width = 0.4
    barObject = ax1.bar(barLoc, mean, width, yerr=standardDev)
    #ax1.yaxis.grid(True)
    ax1.set_xticks(barLoc)
    ax1.set_xticklabels(labels, rotation=45, ha="right")
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    for bar in barObject:
        height = bar.get_height()
        ax1.annotate('{}'.format(height), xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points", ha='center', va='bottom')

    plt.tight_layout()
    if savePlt:
        if not saveName.endswith(".png"):
            saveName+=".png"
        plt.savefig(flr.fullPath(saveName, "outputs"))
    else:
        plt.show()
    plt.close()

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

def comparingBoxPlots(dictObj, plottedData="R0", saveName="default", outputDir="outputs"):
    osName = platform.system()
    files = "images\\" if osName.lower() == "windows" else "images/"
    osExtension = "win" if osName.lower() == "windows" else "Linux"
    print("this is it")
    print(dictObj)
    if plottedData == "R0":
        if len(dictObj) > 0:
            und_labels = []
            und_R0data = []
            #R0AnalyzedData = []
            reg_labels = []
            reg_R0data = []
            for key, value in dictObj.items():
                #if ("NC_" in key or "VC_" in key or "SC_" in key) and isinstance(value[0], float):
                #    und_labels.append(key)
                #    und_R0data.append(value[0])
                #else:
                reg_labels.append(key)
                reg_R0data.append(value[0])

                #R0AnalyzedData.append(value[1])
            flr.saveObjUsingPickle(flr.fullPath("R0"+osExtension+ saveName, "picklefile")+".pkl", dictObj)
            #boxplot(und_R0data,oneD=False, pltTitle="R0 Comparison (box)", xlabel="Model Name",
            #    ylabel="Infected Agents (R0)", labels=und_labels, savePlt=True, saveName=osExtension+"9R0_box_"+saveName, outputDir=outputDir)
            #statfile.barChart(und_R0data, oneD=False, pltTitle="R0 Comparison (bar)", xlabel="Model Name",
            #    ylabel="Infected Agents (R0)", labels=und_labels, savePlt=True, saveName=osExtension+"9R0_bar_"+saveName)
            boxplot(reg_R0data,oneD=False, pltTitle="R0 Comparison (box)", xlabel="Model Name",
                ylabel="Infected people (R0)", labels=reg_labels, savePlt=True, saveName=osExtension+"restR0_box_"+saveName,  outputDir=outputDir)
            #statfile.barChart(reg_R0data, oneD=False, pltTitle="R0 Comparison (bar)", xlabel="Model Name",
            #    ylabel="Infected Agents (R0)", labels=reg_labels, savePlt=True, saveName=osExtension+"restR0_bar_"+saveName)
    elif plottedData in ["inf", "double"]:
        if len(dictObj) > 0:
            labels = []
            infectedCounts = []
            labels1 = []
            infectedCounts1 = []
            for key, value in dictObj.items():#InfectedCountDict.items():
                #if "NC_" in key or "VC_" in key or "SC_" in key:
                #    labels.append(key)
                #    infectedCounts.append(value)
                #else:
                labels1.append(key)
                infectedCounts1.append(value)
            print(labels, labels1)
            flr.saveObjUsingPickle(flr.fullPath("infectedCount"+osExtension+saveName, "picklefile")+".pkl", dictObj)
            title = "Infection Comparison"
            xlabels = "Model Name"
            ylabels = "Total # of Infected Agents"
            if plottedData =="double":
                xlabels = "number infected, n"
                ylabels = "time, t"
                title = "doubling time"
            if len(infectedCounts) > 0:
                boxplot(infectedCounts,oneD=False, pltTitle=title, xlabel=xlabels,
                    ylabel=ylabels, labels=labels, savePlt=True, saveName=osExtension+"9infe_box_"+saveName,  outputDir=outputDir)
                #statfile.barChart(infectedCounts, oneD=False, pltTitle="Infection Comparison (bar)", xlabel="Model Name",
                #    ylabel="Total Infected Agents", labels=labels, savePlt=True, saveName=osExtension+"9infe_bar_"+saveName)

            if len(infectedCounts1) > 0:
                boxplot(infectedCounts1,oneD=False, pltTitle=title, xlabel=xlabels,
                    ylabel=ylabels, labels=labels1, savePlt=True, saveName=osExtension+"rest_infe_box_"+saveName,  outputDir=outputDir)
                #statfile.barChart(infectedCounts1, oneD=False, pltTitle="Infection Comparison (bar)", xlabel="Model Name",
                #    ylabel="Total Infected Agents", labels=labels1, savePlt=True, saveName=osExtension+"rest_infe_bar_"+saveName)

def generateVisualByLoading(fileNames, plottedData="inf", saveName='default'):
    # get all csv in filenames and create the visuals for it
    nameList = list(fileNames.keys())
    fileList = [name+".csv" for name in nameList]
    dataDict = dict()
    for name, fileName in zip(nameList, fileList):
        val = flr.openCsv(flr.fullPath(fileName, folder="outputs"))
        print(val)
        break
        dataDict[name] = val
    comparingBoxPlots(dataDict, plottedData=plottedData, saveName=saveName)

def main():
    data = [10, 10, 10, 11, 12,41,71,1,1,12,3,56, 0,5,75,4, 0, 0, 0]
    print(changeOverUnitTime(data))
    print(filterZeros(data))
    analyzeModel([data])
    #boxplot([data for _ in range(3)])

    data2 =[[1,1,1,1,1,1,1,14,6,7,7,4,3,12,3,4], [6,4,32,2,43], [1,1,1,1]]
    data3=data2[0]
    label = ["base case", "case 2", "case 3"]
    barChart(data2, labels=label)
    #barChart(data3,oneD=True, labels=["a"])
    boxplot(data2,  labels=label)
if __name__ == "__main__":
    main()