import networkx as nx
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def makeGraph(vertices, edges, vertices2Cluster, cluster2Vertices,clusterName, roomCapacity, directed=False):
    """
        get the partitions and their adjacency list to create a graph
        The graph will show the label of partitions that have more edges than the threshold 
    """
    theshold = 10 # rooms
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(vertices) #G.nodes()
    G.add_edges_from(edges)
  
    # this part dictates the size and color
    sizeList, colorList, labelList = [], [], dict()
    lables, colorbar = False, False
    #colors = dict((key, index/len(buildings)) for index, key in enumerate(buildingRoom.keys()))
    colors = dict((buildingId, index/len(cluster)) for index ,(buildingId, cluster) in enumerate(cluster2Vertices.items()))
    #typeName = set(bType.building_type for bType in buildings.values())
    #taken care by clusterName

    clusters = set(clusterName.values())
    groupColor = dict((key,index/len(clusters)) for index, key in enumerate(sorted(clusters)))
    groupColor["dorm"], groupColor["transit"], groupColor["library"] = groupColor["library"], groupColor["dorm"], groupColor["transit"] 
    
    print(groupColor.items())
    basedOnType = True
    cmap = mpl.cm.get_cmap("gist_rainbow")
    for node in nx.nodes(G):
        connection = len(list(nx.neighbors(G, node)))
        buildingId = vertices2Cluster[node]
        if roomCapacity[node] > 5000:
            sizeList.append(300)
        else:
            coeff = 2 if connection < 20 else 1 
            sizeList.append(int((coeff*connection*6000)/len(vertices)))
        
        if lables: # ignore
            labelList[node] = "" if connection < theshold else clusterName[buildingId]+" :\n " +vertexLabels[node]
        else: # no labels
            labelList[node] = ""
        if basedOnType: # here
            colorList.append(groupColor[clusterName[buildingId]]-1)
        else:
            colorList.append(colors[building])
  
    pos = nx.spring_layout(G,k=0.05,  scale = 2)
    print(nx.info(G))
    print("labels for vertices:", [names for names in labelList.values() if names != ""])
    f = plt.figure(1)
    ax = f.add_subplot(1, 1, 1)
    handleList = []
    for key, colorVal in sorted(groupColor.items()):
        ax.plot([0], [0], color=cmap(colorVal), label=key)
        a = mpl.patches.Patch(color=cmap(colorVal), label=key)
        handleList.append(a)
    
    ec = nx.draw_networkx_edges(G, pos, alpha=0.2)
    nc = nx.draw_networkx_nodes(G, pos, with_labels=True, node_size=sizeList, 
                node_color=np.array(colorList), alpha=0.7,  cmap="gist_rainbow")
    lc = nx.draw_networkx_labels(G, pos, labels=labelList, font_size= 10)
    if colorbar: 
        plt.colorbar(nc)
    plt.axis("off")
    plt.legend(handles=handleList)
    plt.tight_layout()
    plt.show()

def timeSeriesGraph(timeIntervals, xLim, yLim, data, linestyle = ["r-", "b.", "g--"], savePlt=False, saveName="defaultImage.png", animatePlt=True):
    fig, ax= plt.subplots(figsize = (10, 5))
    plt.xlim(xLim[0], xLim[1])
    plt.ylim(yLim[0], yLim[1])
    animateData = [[] for _ in data.items()]
    for index, (name, dataList) in enumerate(data.items()):
        animateData[index] = dataList
        plt.plot(timeIntervals, dataList, label=name)
    plt.xlabel("Time (Hours)")
    plt.ylabel("# of Agents")
    plt.title("Agent's State over Time")
    leg = ax.legend()
    # show static graph
    if savePlt:
        print("image saved as", saveName)
        plt.savefig(saveName)
    else:
        plt.show()    
    # show animated graph
    if animatePlt:
        showAnimation(timeIntervals, animateData, xLim, yLim, len(timeIntervals))

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)

def showAnimation(timeList, dataList, xLim, yLim, frames):   
    fig = plt.figure()
    ax1 = plt.axes(xlim=xLim, ylim=yLim)
    # plot parameter is dimension x dimension2 # position of plot, and linewidth
    line = ax1.plot(len(dataList), 1, 1, lw=2)
    #line = ax1.plot([], [], lw=2)
    plt.xlabel("time")
    plt.ylabel("# of agents")
    dataSize = len(dataList)
    cmap = get_cmap(dataSize+1)
    lines = []
    
    for i in range(dataSize):
        lobj = ax1.plot([], [], lw=2, c=cmap(i))[0]
        lines.append(lobj)

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def animate(i):
        xList = [timeList[:i] for _ in range(dataSize)]
        yList = [list_1[:i] for list_1 in dataList]
        for lNum, line in enumerate(lines):
            line.set_data(xList[lNum], yList[lNum])
        return lines
        
    ani = animation.FuncAnimation(fig, animate, init_func=init, frames = frames, interval = 200)
    plt.show()


def main():
    pass


if __name__ == "__main__":
    main()