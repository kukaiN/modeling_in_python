import os
import random
import pandas as pd
import pickle
import file_related as flr
import numpy as np
import bisect
import visualize as vs
import modify_df as mod_df

def convert_to_min(time_str):
    """convert time represnted in the following forms to minutes in a day, 
        this function is used to decode the schedule in terms of minutes
        1.) military time, xx:xx
        2.) time with Meridiem Indicator (AM/PM), xx:xxAM or xx:xxPM
    """
    meridiem_indicator = time_str[-2:]
    if meridiem_indicator in ["AM", "PM"]: # check if Meridiem Indicator is included
        time_str = time_str[:-2]
    hours, minutes = [int(a) for a in time_str.strip().split(":")]
    if meridiem_indicator == "PM": # if the period is PM, then add 12 hours to the time
            minutes += 60*12
    minutes+= hours*60
    return minutes

def find_tuple(val, item_list, index):
    """ iterate over the item_list and returns the first tuple with the same value"""
    for tup in item_list:
        if tup[index] == val: return tup
    return None

def main():
    """ the main function that starts the model"""
    # the "config" and "info" are different in that config tells the code what values/range are allowed for a variable.
    # the info are the specific data for a specific instance of the class
    
    file_loc = {
        "config_folder"     : "txt_config",
        "agent_config"      : "agent_config.txt",
        "room_config"       : "room_config.txt",
        "building_config"   : "building_config.txt",
        "schedule_config"   : "schedule_config.txt",
        
        "info_folder"       : "configuration",
        "agent_info"        : "agents.csv",
        "room_info"         : "rooms.csv",
        "building_info"     : "buildings.csv",
        "schedule_info"     : "schedules.csv"
    }
    foldername, filename = "configuration", "new_building.csv"
    model = Agent_based_model()
    model.loadData(file_loc, True, foldername, filename)
    model.initialize_agents()
    model.initialize_storing_parameter(["healthy", "infected", "recovered"])
    model.print_relevant_info()
    
    for i in range(10):
        model.update_time(10)
        model.print_relevant_info()
        model.store_information()
    #model.visual_over_time()
    model.visualize_buildings()
    #model.print_relevant_info()
    #if str(input("does all the information look correct?")) in ["T", "t", "y", "Y", "Yes"]:
    #    pass
    

def agent_class(agent_df, slot_val =  ["name", "age", "gender", "immunity", "curr_location", "motion" "health_state", "archetype", "personality", "arrival_time", "path_to_dest", "waiting_time"]):
    """
        meta function used to dynamically assign __slots__,
        creates agents from the given df
    """
    class Agents:
        """
            creates an agent that moves between rooms and interacts with each other (indirectly)
            (1) Room limits
            (2) State transition times
            (3) What questions do we want to answer?
            (a) reduced classroom capacity (b) facemasks (c) building closures (gyms, libraries) (d) no large classes
            (e) physical distancing
            (f) movement restrictions
            (g) quarantine space
            (h) enhanced detection
            (i) contact tracing

        """
        #__slot__ = ["name", "age", "gender", "immunity", "curr_location", "state", "archetype", "personality"]
        __slots__ = slot_val
        def __init__(self, values_in_rows):
            for slot, value in zip(self.__slots__, values_in_rows):
                self.__setattr__(slot, value)

        def update_loc(self, curr_time, adj_dict):
            """
                change agent's state, either moving or stationary,
                look at adjacent rooms and move to one of the connected rooms    
            """
            threshold = 0.4
            if self.motion == "stationary" and curr_time > self.arrival_time:
                if random.random() < threshold:
                    rooms = list(adj_dict.keys())
                    self.destination =  np.random.choice(rooms, 1)
                    self.move_to(adj_dict)
            elif self.motion == "moving" and curr_time > self.travel_time + self.arrival_time:
                self.move_to(adj_dict)
                self.arrival_time = curr_time
            else: 
                return (self.curr_location, self.curr_location)

        def move_to(self, adj_dict):
            """
                chooses the random room and moves the agent inside
            """
            past_location = self.curr_location
            if find_tuple(self.destination, adj_dict[self.curr_location], 1) != None:
                # the agent reached it's destination, takes a rest
                self.curr_location = self.destination
                self.destination = None
                self.motion = "stationary"
            else: # the agent is still moving
                self.motion = "moving"
                # choose a random room and go to it
                next_partition = np.random.choice(adj_dict[self.curr_location])
                self.travel_time = next_partition[1]
                self.curr_location = next_partition[0]
            return (past_location, self.curr_location)

        def make_schedule(self, schedule_list):
            a = self.personality
            b = self.archetypes

    # creates the agents and put them in a dictionary
    temp_dict = dict()
    for index, row in agent_df.iterrows():
        temp_dict[index] = Agents(row.values.tolist())
    return temp_dict

def room_class(room_df, slot_val):
    """
        meta function used to dynamically assign __slots__
    """
    class Partitions:
        __slots__ = slot_val
        def __init__(self, param):
            for slot, value in zip(self.__slots__, param):
                self.__setattr__(slot, value)

        def enter(self, agent_id):
            """ a put the id of the agent that entered the room"""
            if self.check_capacity():
                self.agents_in_room.append(agent_id)

        def check_capacity(self):
            """return a boolean, return True if theres capacity for one more agent, False if the room is at max capacity 
            """
            if len(self.agents_in_room) < self.capacity:
                return True
            return False
    
        def leave(self, agent_id):
            """ remove the id of the agent that exited the room"""
            if agent_id in self.agents_in_room:
                self.agents_in_room.remove(agent_id)
        
    temp_dict = dict()
    for index, row in room_df.iterrows():
        temp_dict[index] = Partitions(row.values.tolist())
    return temp_dict
    
def superstruc_class(struc_df, slot_val):
    """
        creates and returns a dictionary that keeps the building class
    """
    class Superstructure: # buildings
        __slots__ = slot_val
        def __init__(self, struc_param):
            for slot, value in zip(self.__slots__, struc_param):
                self.__setattr__(slot, value)

    temp_dict = dict()
    for index, row in struc_df.iterrows():
        temp_dict[index] = Superstructure(row.values.tolist())
    return temp_dict
        
class Agent_based_model:
    def __init__(self):
        # get the dataframe of individual components
        self.time = 0
        self.graph_type = "undirected"

    def loadData(self, files, onefile=False, filename="configuration", folder="new_building.csv"):
        if onefile:
            self.building_df, self.room_df = mod_df.mod_building() 
        else:
            self.building_df = flr.make_df(files["info_folder"], files["building_info"]) 
            self.room_df = flr.make_df(files["info_folder"], files["room_info"]) 
        self.agent_df = flr.make_df(files["info_folder"], files["agent_info"]) 
        self.schedule_df = flr.make_df(files["info_folder"], files["schedule_info"]) 
        # get the config of the individual components
        self.agent_config = flr.load_config(files["config_folder"], files["agent_config"])
        self.room_config = flr.load_config(files["config_folder"], files["room_config"])
        self.building_config = flr.load_config(files["config_folder"], files["building_config"])
        self.schedule_config = flr.load_config(files["config_folder"], files["schedule_config"])
        self.initialize()


    def initialize(self):
        # add a column to store the id of agents or rooms inside the strucuture
        self.agent_df["curr_location"] = 0
        self.agent_df["motion"] = 0
        self.agent_df["personality"] = 0
        self.agent_df["arrival_time"] = 0
        self.agent_df["schedule"] = 0
        self.agent_df["travel_time"] = 0
        self.building_df["rooms_inside"] = 0
        self.room_df["agents_inside"] = 0
        self.room_df["odd_cap"] = 0
        self.room_df["even_cap"] = 0 
        self.room_df["limit"] = [int(x*0.8 + 0.5) for x in self.room_df["capacity"]] # 80% limit
        self.room_df["classname"] = 0
        print("*"*20)
        self.
        self.adjacency_dict = self.make_adj_dict()
        self.buildings = self.make_class(self.building_df, superstruc_class)
        self.rooms = self.make_class(self.room_df, room_class)
        self.agents = self.make_class(self.agent_df, agent_class)
        self.random_personality()
        self.make_schedule()
        #self.make_schedule_part2()
        self.rooms_in_building = dict((building_id, []) for building_id in self.buildings.keys())
        self.building_name_id = dict((getattr(building, "building_name"), building_id) for building_id, building in self.buildings.items())
        self.room_name_id = dict((getattr(room, "room_name"), room_id) for room_id, room in self.rooms.items())
        self.add_rooms_to_buildings()

    def random_personality(self):
        """
            randomly assign a major and personality to the agents
        """

        personalities = ["athletic", "introvert", "party people", "people", "terminators", "aliens"]
        majors = ["math", "stem", "english", "humanities", "philosophy", "sleeping"]
        num_agent = len(self.agents)
        rand_personalities = np.random.choice(personalities, num_agent)
        rand_majors = np.random.choice(majors, num_agent)
        for index, agent in enumerate(self.agents.values()):
            agent.personality = rand_personalities[index]
            agent.archetypes = rand_majors[index]

    def make_schedule(self):
        """dedicate a class to rooms"""
        self.schedule_chart = ["math", "stem", "english", "humanities", "philosophy", "sleeping"]
        self.schedule_dict = dict((key, []) for key in self.schedule_chart)
        classrooms_count = len(self.room_df[self.room_df["building_type"] == "classroom"])
        print(classrooms_count)
        self.random_class = np.random.choice(self.schedule_chart, classrooms_count)
        index = 0
        for room_id, room in self.rooms.items():
            if room.building_type == "classroom":
                room.classname = self.random_class[index]
                self.schedule_dict[room.classname].append(room_id) 
                index +=1

    def make_schedule_part2(self):
        print("*"*20)
        for classes in self.schedule_chart:
            print(classes)
            class_probability = [(room.limit, room_id) for room_id, room in self.rooms.items() if room.classname == classes]
            class_sum = sum([a[0] for a in class_probability])
            class_room = [a[1] for a in class_probability]
            class_probability = [a[0]/class_sum for a in class_probability]
            for key, agent in self.agents.items():
                if agent.archetypes == classes:
                    x = np.random.choice(class_room, size = 4, replace=False, p = class_probability)
                    print(sc_A, sc_B)
                    # A is odd
                    # B is even
                    agent.schedule = x
                    for room_id in sc_A:
                        if self.rooms[room_id].odd_capa < self.rooms[room_id].capacity:
                            self.rooms[room_id].odd_capa +=1
                        else:
                            new_room = np.random.choice(class_room, p=class_probability)
                            while not self.rooms[room_id].odd_capa < self.rooms[room_id].capacity:
                                new_room = np.random.choice(class_room, p=class_probability)
                            self.rooms[room_id].opp_capa += 1

                    for room_id in sc_B:
                        if self.rooms[room_id].even_capa < self.rooms[room_id].capacity:
                            self.rooms[room_id].even_capa +=1
                             
                    #print(x)
           

    def add_rooms_to_buildings(self):
        """add room_id to associated buildings"""
        for room_id, rooms in self.rooms.items():
            self.rooms_in_building[self.building_name_id[rooms.located_building]].append(room_id) 

    def initialize_agents(self):
        # convert agent's location to the corresponding room_id and add the agent's id to the room member
        for rooms in self.rooms.values():
            rooms.agents_inside = []
        num_of_rooms = len(self.rooms)
        for agent_id, agents in self.agents.items():
            initial_location = getattr(agents, "initial_location")
            if initial_location in self.building_name_id.keys():
                # randomly choose rooms from the a building
                possible_rooms = self.rooms_in_building[self.building_name_id[initial_location]]
                location = np.random.choice(possible_rooms)
            elif initial_location in self.room_name_id.keys():
                # convert the location name to the corresponding id
                location = self.room_name_id[initial_location]
            else:
                # either the name isnt properly defined or the room_id was given
                location = initial_location
                location = random.randint(0, num_of_rooms-1)
            agents.curr_location = location
            self.rooms[location].agents_inside.append(agent_id)

    def make_adj_dict(self):
        """ creates an adjacency list implimented with a dictionary"""
        adj_dict = dict()
        for room_id, row in self.room_df.iterrows():
            #print(row["connected_to"])
            adj_room = self.room_df.index[self.room_df["room_name"] == row["connected_to"]].tolist()[0]
            travel_time = row["travel_time"]
            adj_dict[room_id] = adj_dict.get(room_id, []) + [(adj_room, travel_time)]
            if self.graph_type == "undirected": 
                adj_dict[adj_room] = adj_dict.get(adj_room,[]) + [(room_id, travel_time)]
        return adj_dict
    
    def make_class(self, df_ref, func):
        slot_val = df_ref.columns.values.tolist()
        temp_dict = func(df_ref, slot_val)
        num_obj, obj_val = len(temp_dict), list(temp_dict.values())
        class_name = obj_val[0].__class__.__name__ if num_obj > 0 else "" 
        print(f"creating {num_obj} {class_name} class objects, each obj will have __slots__ = {slot_val}")
        return temp_dict

    def update_time(self, step = 1):
        """ 
        a function that updates the time and calls other update functions, 
        you can also set how many steps to update"""
        for t in range(step):
            self.time+=1
            self.update_agent()
            self.infection()

    def update_agent(self):
        """call the update function on each person"""
        for agent_id, agent in self.agents.items():
            loc = agent.update_loc(self.time, self.adjacency_dict)
            if loc[0] != loc[1]:
                self.rooms[loc[0]].leave(agent_id)
                self.rooms[loc[1]].enter(agent_id)

    def count_within_agents(self, agent_list, state_name):
        return len(list(filter(lambda x: x.state == state_name, [self.agents[val] for val in agent_list]))) 

    def count_agents(self, state_name):
        return len(list(filter(lambda x: x.state == state_name, self.agents.values() )))

    def print_relevant_info(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this functio n will be converted to the proper format using __repr__"""
        infected = self.count_agents("infected")
        carrier = self.count_agents("carrier")
        dead = self.count_agents("dead")
        healthy = self.count_agents("healthy")
        recovered = self.count_agents("recovered")
        print(f"time: {self.time} total healthy {healthy} infected: {infected}, carrier: {carrier}, dead: {dead}, recovered: {recovered}")
        #print(f" agent's locations is {list(room.agents_in_room for room in self.room_dict.values())}")
        #print(f"agent's location is {self.room_agent_dict}")
    
    def initialize_storing_parameter(self, list_of_status):
        self.parameters = dict((param, []) for param in list_of_status)
        self.timeseries = []

    def store_information(self):
        self.timeseries.append(self.time)
        for param in self.parameters.keys():
            self.parameters[param].append(self.count_agents(param))

    def visual_over_time(self):
        vs.draw_timeseries(self.timeseries, (0, self.time+1), (0,len(self.agents)), self.parameters)
    
    def visualize_buildings(self):
        if True:
            pairs = [(room, adj_room[0]) for room, adj_rooms in self.adjacency_dict.items() for adj_room in adj_rooms]
            name_dict = dict((room_id, room.room_name) for room_id, room in self.rooms.items())
            vs.make_graph(self.rooms.keys(), name_dict, pairs, self.buildings, self.rooms_in_building, self.rooms)
        

    def infection(self):
        base_p = 0.01 # 0.01
        rand_vect = np.random.random(len(self.agents))
        index = 0
        for room in self.rooms.values():
            total_infected = self.count_within_agents(room.agents_inside, "infected")
            for agent_id in room.agents_inside:
                #print(base_p*total_infected/room.limit)
                if self.agents[agent_id].state == "healthy" and rand_vect[index] < base_p*total_infected/room.limit: 
                    self.agents[agent_id].state = "infected"
                else:
                    state = self.agents[agent_id].state
                    if state == "infected":
                        if rand_vect[index] < 0.05:
                            self.agents[agent_id].state = "recovered"

                index +=1    

    def MMs_queueing_model(self, lambda_val, mean):
        pass

if __name__ == "__main__":
    main()    
