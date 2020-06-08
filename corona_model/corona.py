import os
import random
import pandas as pd
import pickle
import file_related as flr
import numpy as np

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
    

class agent:
    """make an agent that can interact with the room class
    """
    def __init__(self, rand_bool, name = "SE_lain", age = 22, immunity = 0.1, curr_location = "dorm", infected = False, archetype = "introvert"):
        """takes in the initial parameters"""
        self.name = name
        self.age = age
        self.immunity = immunity
        self.infected = False
        self.archetype = archetype
        self.curr_location = curr_location

        # the states below are used to tell if the agent is moving or not
        self.state = "stationary"
        self.arrival_time = 0
        self.minimum_waiting_time = 0
        self.desitination = None

    def change_curr_location(self, location):
        self.curr_location = location

    def random_schedule(self, archetype_dict = []):
        """ creates a plausable schedule that matches with the agent's archetype"""
        pass

    def update_agents(self, room_dict, room_sp_dict, curr_time, adj_list):
        """function that update the time and the state of the agent, for now the agent is either moving or at rest"""
        threshhold = 0.9
        #print("called1")
        # if we waited in the room long enough then the agent will move
        if self.state == "stationary" and curr_time > self.minimum_waiting_time + self.arrival_time:
            if random.random() < threshhold: # with a certain probabilty the agent will start moving again
                self.state = "moving"
           
                self.destination = random.choice(list(adj_list.keys()))
                adj_rooms = adj_list[room_dict[self.curr_location]]
                self.move_to(room_sp_dict, adj_rooms)
                   
        if self.state == "moving": # if the agent is moving, then it will keep on moving until it reaches its destination
            adj_rooms = adj_list[room_dict[self.curr_location]]
            self.move_to(room_sp_dict, adj_rooms)
            if self.curr_location == self.desitination:
                self.desitination = None
                self.state = "stationary"
                self.arrival_time = curr_time
                self.minimum_waiting_time = 5
    
    def move_to(self, room_name_dict, connected_rooms):
        """moves the agent to rooms thats adjacent to the current room"""
        
        if self.desitination in connected_rooms:
            self.curr_location = self.destination
            self.destination = None
            print(f"locations {self.curr_location}, {self.desitination}")
        else:
            
            random_room = random.choice(connected_rooms)[0]
            print(f"{self.name} moved to {random_room}")
            self.curr_location = room_name_dict[random_room]


class rooms:
    def __init__(self, room_name = "unnamed_room", capacity = 20, default_agents = []):
        """initailize the room"""
        self.room_name = room_name
        self.capacity = capacity
        self.agents_in_room = default_agents

    def enter_room(self, id):
        """ a put the id of the agent that entered the room"""
        if self.check_capacity():
            self.agents_in_room.append(id)

    def check_capacity(self):
        """return a boolean, return True if theres capacity for one more agent, False if the room is at max capacity 
        """
        if len(self.agents_in_room) < self.capacity:
            return True
        return False
    
    
    def leave_room(self, id):
        """ remove the id of the agent that exited the room"""
        if id in self.agents_in_room:
            self.agents_in_room.remove(id)

    def update(self, agent_dict):
        """update the room state if needed"""
        for agent in self.agents_in_room:
            pass

class disease_model:
    def __init__(self, building_info = "buildings.csv", room_info = "rooms.csv", agent_info = "agents.csv", schedule_info = "schedules.csv"):
        """
        start a new infection model, the model will load the data from the csv files in the configuration folder
        if there's a different csv that you're trying to load, then modify the name of the file that is being passed
        """
        # make panda dataframe from the given csv file
        self.agent_df = self.make_df(agent_info) 
        self.building_df = self.make_df(building_info)
        self.room_df = self.make_df(room_info)
        self.schedule_df = self.make_df(schedule_info)
    

        print("*"*20)
        # make an adjacency list from the room_df
        self.adjacency_list = self.make_adj_list()
        self.adjacency_list_checker()
        self.cached_shortestpath = None # coming soon
        
        # make lists and dictionaries that stores refrences to the room or agent objects
        self.rooms = self.initialize_rooms()
        self.name_to_room_id = {value:key for key, value in self.rooms.items()}
        self.room_dict = self.initialize_room_dict()
        self.building_room_list = self.make_building_room()
        self.agents = self.initilize_agents()
        self.room_agent_dict = self.initialize_room_agent()
        self.time = 0
        self.schedule_dict = self.make_schedule_chart()
    
    def initialize_room_agent(self):
        """ creates a dictionary with the following:
            keys: room id
            values: agents' id that corresponds to the agents in the room
        """ 
        print(self.name_to_room_id)
        temp_dict = dict((self.name_to_room_id[room_name], []) for room_name in self.adjacency_list.keys())
        for index, agent in self.agents.items():
            temp_dict[agent.curr_location].append(index)
        print(temp_dict.keys())
        print(temp_dict.values())
        print("*"*20)
        return temp_dict
     
    def make_schedule_chart(self):
        """ make a dictionary(key: archetype of agent) --> value: list of ["name of room", [list of time (xx:xxAM, xx:xxAM)] ]"""
        temp_dict = dict()
        for _ , schedule in self.schedule_df.iterrows():
            temp_val = temp_dict.get(schedule["type"], [])
            time_periods = list(filter(None, schedule["time interval"].replace(")", "").replace("(", "").split(";")))
            temp_val.append([schedule["room name"], [tuple(a for a in val.split("|"))  for val in time_periods]])
            temp_dict[schedule["type"]] = temp_val
        return temp_dict


    def make_building_room(self):
        """make a dictionary of the following:
            keys: building name
            values: rooms located in that building
        """
        temp_dict = dict((building_name, []) for building_name in list(self.building_df["building_name"]))
        print(temp_dict.items())
        for index, room_info in self.room_df.iterrows():
            temp_dict[room_info["located building"]].append(self.rooms[index])
        return temp_dict

    def initialize_rooms(self):
        """creates a dictionary where the key is the unique room id and the value is the name of the room,
        help when looking up names"""
        temp_dict = dict()
        for index, row in self.room_df.iterrows():
            temp_dict[index] = row["room_name"]
        return temp_dict

    def initialize_room_dict(self):
        temp_dict = dict()
        for index, row in self.room_df.iterrows():
            temp_dict[index] = rooms(room_name=row["room_name"], capacity=row["capacity"])
        return temp_dict

    def make_adj_list(self):
        """ creates an adjacency list of rooms that are in the csv file"""
        adj_dict = dict()
        for _, row in self.room_df.iterrows():
            room = row["room_name"]
            adj_room = row["connected to"]
            travel_time  =  row["travel time"]
            adj_dict[room] = adj_dict.get(room, []) + [(adj_room, travel_time)]
            adj_dict[adj_room] = adj_dict.get(adj_room,[]) + [(room, travel_time)]
        return adj_dict

    def adjacency_list_checker(self):
        """simple checker, that outputs the inconsistencies in the csv files, if any inconsistency exists"""
        global_print = True
        for key, value in self.adjacency_list.items():
            count_dict = dict()
            print_bool = False
            locations = [val[0] for val in value]
            for location_name in locations:
                get_val = count_dict.get(location_name, 0)
                if get_val == 1:
                    print_bool = True
                count_dict[location_name]= get_val + 1
            if print_bool:
                global_print = False
                print(f"for the key: {key}, you have these overlapping locations: {[key for key, value in count_dict.items() if value > 1]}")
        if global_print:
            print("good, no overlapping locations in the adjacency dict")

    def update_state(self, steps = 5):
        """ 
        a function that updates the time and calls other update functions, 
        you can also set how many steps to update"""
        for t in range(steps):
            self.update_time()
            self.update_agents()
            self.infection_rule()  
    
    def update_agents(self):
        """function that calls the agents to update its state"""
        for k, agents in self.agents.items():
            agents.update_agents(self.rooms, self.name_to_room_id, self.time, self.adjacency_list)

    def infection_rule(self):
        """ this function determines how the infection will spread and how strong the infection is,
        the function can be modified to make new rules for infection"""
        for agent in self.agents.values():
            if random.random()> 0.5:
                agent.infected = "True"


    def update_time(self, time_step = 1):
        """ updates time passed in the model"""
        self.time+=time_step

    def initilize_agents(self):
        """ creates the agents and make a dictionary with agent_id as keys and the agent object is the value"""
        print("*"*20)
        building_list = list(self.building_df["building_name"])
        print(building_list)
        temp_dict = dict()
        for index, agent_row in self.agent_df.iterrows(): # go through all rows and make agent objects
            curr_location = agent_row["initial condition"]
            temp_dict[index] = agent(*list(agent_row))
            
            if curr_location in building_list:
                temp_dict[index].change_curr_location(self.name_to_room_id[random.choice(self.building_room_list[curr_location])])
            else:
                temp_dict[index].change_curr_location(self.name_to_room_id[curr_location])
        return temp_dict

    def make_df(self, file_name):
        """ creates a panda dataframe from the content in a csv file"""
        a = flr.format_data(file_name)
        print("this is a preview of the data that you're loading:")
        print(a.head(3))
        return a
    
    def print_relevant_info(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this function will be converted to the proper format using __repr__"""
        total_infected = sum([1 for agent in self.agents.values() if agent.infected == "True"])
        print(f"total infected is {total_infected}")
        print(f" agent's locations is {list(room.agents_in_room for room in self.room_dict.values())}")


def main():
    """start a new disease model"""
    
    model = disease_model()
    model.print_relevant_info()
    model.update_state(10)
    model.print_relevant_info()
        
if __name__ == "__main__":
    main()