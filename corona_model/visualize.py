import networkx as nx
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def makeGraph(vertices, vertexLabels, edges, buildings, buildingRoom, roomDict, directed=False):
    """
        get the partitions and their adjacency list to create a graph
        The graph will show the label of partitions that have more edges than the threshold 
    """
    theshold = 10 # rooms
    # flip the direction of the building to room, to rooms to building
    roomsToBuilding = dict((roomId, buildingId) for buildingId, rooms in buildingRoom.items() for roomId in rooms)
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(vertices) #G.nodes()
    G.add_edges_from(edges)

    # this part dictates the size and color
    sizeList, colorList, labelList = [], [], dict()
    lables = False
    colorbar = False
    colors = dict((key, index/len(buildings)) for index, key in enumerate(buildingRoom.keys()))
    typeName = set(bType.building_type for bType in buildings.values())
    typeCount = len(typeName)
    
    typeColor = dict((key, index/typeCount) for index, key in enumerate(sorted(typeName)))
    basedOnType = True
    cmap = mpl.cm.get_cmap("gist_rainbow")
    for node in nx.nodes(G):
        connection = len(list(nx.neighbors(G, node)))
        if roomDict[node].capacity > 5000:
            sizeList.append(300)
        else:
            coeff = 2 if connection < 20 else 1 
            sizeList.append(int((coeff*connection*6000)/len(vertices)))
        building = roomsToBuilding[node]
        if lables:
            labelList[node] = "" if connection < theshold else buildings[building].building_name+" :\n " +vertexLabels[node]
        else: 
            labelList[node] = ""
        if basedOnType:
            colorList.append(typeColor[buildings[building].building_type])
        else:
            colorList.append(colors[building])
    
    pos = nx.spring_layout(G,k=0.05,  scale = 2)
    print(nx.info(G))
    print("labels for vertices:", [names for names in labelList.values() if names != ""])
    f = plt.figure(1)
    ax = f.add_subplot(1, 1, 1)
    handleList = []
    for key, colorVal in sorted(typeColor.items()):
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

def timeSeriesGraph(timeIntervals, xLim, yLim, data, linestyle = ["r-", "b.", "g--"]):
    fig, ax= plt.subplots(figsize = (10, 5))
    plt.xlim(xLim[0], xLim[1])
    plt.ylim(yLim[0], yLim[1])
    animateData = [[] for _ in data.items()]
    for index, (name, dataList) in enumerate(data.items()):
        print(index, name, data)
        animateData[index] = dataList
        plt.plot(timeIntervals, dataList, label=name)
    plt.xlabel("Time")
    plt.ylabel("Agent's conditions")
    plt.title("Agent's state over time")
    leg = ax.legend()
    # show static graph
    plt.show()    
    # show animated graph
    showAnimation(timeIntervals, animateData[0], animateData[1], xLim, yLim, len(timeIntervals))

def showAnimation(timeList, list_1, list_2, xLim, yLim, frames):   
    fig = plt.figure()
    ax1 = plt.axes(xlim=xLim, ylim=yLim)
    line = ax1.plot([], [], lw=2)
    plt.xlabel("time")
    plt.ylabel("# of agents")
    plotColor, lines = ["red", "blue"], []
    for i in range(2):
        lobj = ax1.plot([], [], lw=2, color=plotColor[i])[0]
        lines.append(lobj)

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def animate(i):
        xList = [timeList[:i], timeList[:i]]
        yList = [list_1[:i], list_2[:i]]
        for lNum, line in enumerate(lines):
            line.set_data(xList[lNum], yList[lNum])
        return lines
        
    ani = animation.FuncAnimation(fig, animate, init_func=init, frames = frames, interval = 200)
    plt.show()

def main():
    pass


if __name__ == "__main__":
    main()