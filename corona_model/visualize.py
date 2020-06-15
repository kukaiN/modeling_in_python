import networkx as nx
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as plt_ani

def make_graph(vertices, vertices_label, edges, buildings, building_room, directed=False):
    print(vertices)
    print(edges)
    # flip the direction of the building to room, to rooms to building
    print(building_room.values())
    print(building_room.keys())
    rooms_to_building = dict((room_id, building_id) for building_id, rooms in building_room.items() for room_id in rooms)
    print(rooms_to_building.values())
    if directed: G=nx.DiGraph()
    else: G = nx.Graph()
    G.add_nodes_from(vertices)
    #G.nodes()

    print(rooms_to_building.items())
    G.add_edges_from(edges)
    size_list, label_list, color_list = [], dict(), []
    colors = dict((key, index/len(buildings)) for index, key in enumerate(building_room.keys()))
    theshold = 5 # rooms
    for node in nx.nodes(G):
        connection = len(list(nx.neighbors(G, node)))
        size_list.append(int((connection*4000)/len(vertices)))
        label_list[node] = "" if connection < theshold else buildings[rooms_to_building[node]].building_name+" :\n " +vertices_label[node]
        building = rooms_to_building[node]
        color_list.append(colors[building])
    print(label_list)
    # convert color list to numpy array
    color_list = np.array(color_list)
    print(nx.info(G))
    pos = nx.spring_layout(G)
    #nx.draw(G, node_size=size_list, with_labels=True, labels=label_list, node_color =color_list, edge_color="b")
    ec = nx.draw_networkx_edges(G, pos, alpha=0.2)
    nc = nx.draw_networkx_nodes(G, pos, with_labels=True, node_size=size_list, node_color=color_list, alpha=0.7,  cmap="gist_rainbow")
    lc = nx.draw_networkx_labels(G, pos, labels=label_list, font_size= 16)
    plt.colorbar(nc)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)


def draw_timeseries(time_intervals, x_lim, y_lim, data, linestyle = ["r-", "b.", "g--"]):
    fig, ax= plt.subplots(figsize = (10, 5))
    plt.xlim(x_lim[0], x_lim[1])
    plt.ylim(y_lim[0], y_lim[1])
    for entry_name, data_list in data.items():
        plt.plot(time_intervals, data_list, label = entry_name)
    plt.xlabel("Time")
    plt.ylabel("Agent's conditions")
    plt.title("Agent's state over time")
    le = ax.legend()
    plt.show()


    

def show_animation(time_list, list_1, list_2, x_lim, y_lim, frame_num):
    fig = plt.figure()
    ax1 = plt.axes(xlim=x_lim, ylim=y_lim)
    line = ax1.plot([], [], lw=2)
    plt.xlabel("time")
    plt.ylabel("# of agents")
    lines = []
    plot_color = ["red", "blue"]
    for index in range(2):
        lobj = ax1.plot([], [], lw=2, color=plot_color[index])[0]
        lines.append(lobj)

    def init():
        for line in lines:
            line.set_data([], [])
    def animate(i):
        x_list = [time_list[:i], time_list[:i]]
        y_list = [list_1[:i], list_2[:i]]
        for lnum, line in enumerate(lines):
            line.set_data(xlist[lnum], ylist[lnum])
        return lines

    ani = plt_ani.animations.FuncAnimation(fig, animate, init_func=init, frames = frame_num, interval = 10, blit=True)
    plt.show()


def main():
    pass



if __name__ == "__main__":
    main()