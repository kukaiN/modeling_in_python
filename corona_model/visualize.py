import networkx as nx
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as plt_ani

def make_graph(vertices, vertices_label, edges, buildings, building_room, room_dict, directed=False):
    """
        get the partitions and their adjacency list to create a graph
        The graph will show the label of partitions that have more edges than the threshold 
    """
    theshold = 10 # rooms
    # flip the direction of the building to room, to rooms to building
    rooms_to_building = dict((room_id, building_id) for building_id, rooms in building_room.items() for room_id in rooms)
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(vertices) #G.nodes()
    G.add_edges_from(edges)

    # this part dictates the size and color
    size_list, label_list, color_list = [], dict(), []
    lables = True
    colorbar = False
    colors = dict((key, index/len(buildings)) for index, key in enumerate(building_room.keys()))
    type_name = set(b_type.building_type for b_type in buildings.values())
    type_count = len(type_name)
    
    type_color = dict((key, index/type_count) for index, key in enumerate(sorted(type_name)))
    based_on_type = True
    cmap = mpl.cm.get_cmap("gist_rainbow")
    for node in nx.nodes(G):
        connection = len(list(nx.neighbors(G, node)))
        if room_dict[node].capacity > 5000:
            size_list.append(300)
        else:
            coeff = 1
            if connection < 20:
                coeff = 2
            size_list.append(int((coeff*connection*6000)/len(vertices)))
        building = rooms_to_building[node]
        if lables:
            label_list[node] = "" if connection < theshold else buildings[building].building_name+" :\n " +vertices_label[node]
        else: 
            label_list[node] = ""
        if based_on_type:
            color_list.append(type_color[buildings[building].building_type])
        else:
            color_list.append(colors[building])
    
    pos = nx.spring_layout(G,k=0.05,  scale = 2)
    print(nx.info(G))
    print("labels for vertices:", [names for names in label_list.values() if names != ""])
    f = plt.figure(1)
    ax = f.add_subplot(1, 1, 1)
    handle_list = []
    for key, color_val in sorted(type_color.items()):
        ax.plot([0], [0], color=cmap(color_val), label=key)
        a = mpl.patches.Patch(color=cmap(color_val), label=key)
        handle_list.append(a)
    
    ec = nx.draw_networkx_edges(G, pos, alpha=0.2)
    nc = nx.draw_networkx_nodes(G, pos, with_labels=True, node_size=size_list, node_color=np.array(color_list), alpha=0.7,  cmap="gist_rainbow")
    lc = nx.draw_networkx_labels(G, pos, labels=label_list, font_size= 10)
    if colorbar: 
        plt.colorbar(nc)
    plt.axis("off")
    plt.legend(handles=handle_list)
    plt.tight_layout()
    plt.show()

def draw_timeseries(time_intervals, x_lim, y_lim, data, linestyle = ["r-", "b.", "g--"]):
    fig, ax= plt.subplots(figsize = (10, 5))
    plt.xlim(x_lim[0], x_lim[1])
    plt.ylim(y_lim[0], y_lim[1])
    for entry_name, data_list in data.items():
        plt.plot(time_intervals, data_list, label = entry_name)
    plt.xlabel("Time")
    plt.ylabel("Agent's conditions")
    plt.title("Agent's state over time")
    leg = ax.legend()
    plt.show()    
    new_data = [[], []]
    for index, (entry_name, data_list) in enumerate(data.items()):
        if index == 2: break
        new_data[index] = data_list
    
    show_animation(time_intervals, new_data[0], new_data[1], x_lim, y_lim, len(time_intervals))

def show_animation(time_list, list_1, list_2, x_lim, y_lim, frame_num):
    # dont know how the funcAnimation works, so ill cite the documents latter
    fig = plt.figure()
    ax1 = plt.axes(xlim=x_lim, ylim=y_lim)
    line = ax1.plot([], [], lw=2)
    plt.xlabel("time")
    plt.ylabel("# of agents")
    plot_color, lines = ["red", "blue"], []
    for index in range(2):
        lobj = ax1.plot([], [], lw=2, color=plot_color[index])[0]
        lines.append(lobj)

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def animate(i):
        x_list = [time_list[:i], time_list[:i]]
        y_list = [list_1[:i], list_2[:i]]
        for lnum, line in enumerate(lines):
            line.set_data(x_list[lnum], y_list[lnum])
        return lines
        

    ani = plt_ani.FuncAnimation(fig, animate, init_func=init, frames = frame_num, interval = 200)
    plt.show()

def main():
    pass


if __name__ == "__main__":
    main()