import os
import random
import pandas as pd
import pickle
import file_related as flr
import numpy as np

def convert_to_min(time_str):
    """convert time represnted in the following forms to minutes in a day
        1.) military time, xx:xx
        2.) AM/PM, xx:xxAM or xx:xxPM
    """
    minutes = 0
    time_symbol = time_str[-2:]
    if time_symbol in ["AM", "PM"]:
        time_str = time_str[:-2]
    time_split = time_str.strip().split(":")
    if time_symbol == "PM":
            minutes += 60*12
            time_split[0] = int(time_split[0])%12
    print(time_split)
    minutes+= int(time_split[0])*60 + int(time_split[1])%61
    return minutes
    

class agent:
    def __init__(self, rand_bool, name = "SE_lain", age = 22, immunity = 0.1, curr_location = "dorm", infected = False, archetype = "introvert"):
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

    def assign_schedule(self, archetype_dict, schedule = []):
        schedule_size = len(archetype_dict[self.archetype])
        if schedule_size < len(schedule):
            schedule = [1/schedule_size for _ in range(schedule_size)]
        self.schedule = schedule

    def update_agents(self, curr_time, adj_list):
        threshhold = 0.2
        # if we waited in the room long enough then the agent will move
        if self.state == "stationary" and curr_time < self.minimum_waiting_time + self.arrival_time:
            if random.random() < threshhold:
                self.state = "moving"
                rooms = adj_list[self.curr_location]
                self.move(adj_rooms)
                   
        if self.state == "moving":
            rooms = adj_list[self.curr_location]
            self.move(rooms)
            if self.curr_location == self.desitination:
                self.desitination = None
                self.state = "stationary"
                self.arrival_time = curr_time
                self.minimum_waiting_time = 5
    
    def move_to(self, connected_rooms):
        if self.desitination in connected_rooms:
            self.curr_location = self.destination
            self.destination = None
            print(f"locations {self.curr_location}, {self.desitination}")
        else:
            self.curr_location = random.choice(connected_rooms)


class rooms:
    def __init__(self, id_num, room_name = "unnamed_room", capacity = 20, default_agents = []):
        self.id_num = id_num
        self.room_name = room_name
        self.capacity = capacity
        self.agents_in_room = default_agents

    def enter_room(self, id):
        self.agents_in_room.append(id)

    def leave_room(self, id):
        if id in self.agents_in_room:
            self.agents_in_room.remove(id)

    def update(self, agent_dict):
        for agent in self.agents_in_room:
            pass

class disease_model:
    def __init__(self, building_info = "building_info.csv", room_info = "room_info.csv", agent_info = "people_info.csv"):
        """start a new infection model, the model will load the data from the csv files in the configuration folder
            if there's a different csv that you're trying to load, then modify the name of the file that is being passed
        """
        # make panda dataframe from the given csv file
        self.agent_df = self.make_df(agent_info) 
        self.building_df = self.make_df(building_info)
        self.room_df = self.make_df(room_info)
        # make an adjacency list from the room_df
        
        self.adjacency_list = self.make_adj_list()
        self.adjacency_list_checker()
        self.cached_shortestpath = None # coming soon
        
        self.rooms = self.initialize_rooms()
        self.building_room_list = self.make_building_room()
        self.agents = self.initilize_agents()
        self.room_people_dict = self.initialize_room_people()
        self.time = 0
    
    def initialize_room_people(self):
        temp_dict = dict((room_name, []) for room_name in self.adjacency_list.keys())
        for index, agent in self.agents.items():
            temp_dict[agent.curr_location].append(index)
        print(temp_dict.keys())
        print(temp_dict.values())
        print("*"*20)
        return temp_dict
        
    def make_building_room(self):
        temp_dict = dict((building_name, []) for building_name in list(self.building_df["building_name"]))
        print(temp_dict.items())
        for index, room_info in self.room_df.iterrows():
            temp_dict[room_info["located building"]].append(self.rooms[index])
        return temp_dict

    def initialize_rooms(self):
        temp_dict = dict()
        for index, row in self.room_df.iterrows():
            temp_dict[index] = row["room_name"]
        return temp_dict

    def make_adj_list(self):
        adj_dict = dict()
        for _, row in self.room_df.iterrows():
            room = row["room_name"]
            adj_room = row["connected to"]
            travel_time  =  row["travel time"]
            adj_dict[room] = adj_dict.get(room, []) + [(adj_room, travel_time)]
            adj_dict[adj_room] = adj_dict.get(adj_room,[]) + [(room, travel_time)]
        return adj_dict

    def adjacency_list_checker(self):
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
        for t in range(steps):
            self.update_time()
            self.update_agents()
            self.infection_rule()  
    
    def update_agents(self):
        for k, agents in self.agents.items():
            agents.update_agents(self.time, self.adjacency_list)

    def infection_rule(self):
        for agent in self.agents.values():
            if random.random()> 0.5:
                agent.infected = "True"


    def update_time(self, time_step = 1):
        self.time+=time_step

    def initilize_agents(self):
        print("*"*20)
        building_list = list(self.building_df["building_name"])
        print(building_list)
        temp_dict = dict()
        for index, agent_row in self.agent_df.iterrows():
            curr_location = agent_row["initial condition"]
            temp_dict[index] = agent(*list(agent_row))
            if temp_dict[index].curr_location in building_list:
                temp_dict[index].change_curr_location(random.choice(self.building_room_list[curr_location]))
        return temp_dict

    def make_df(self, file_name):
        a = flr.format_data(file_name)
        print("this is a preview of the data that you're loading:")
        print(a.head(3))
        return a
    
    def print_relevant_info(self):
        total_infected = 0
        for agent in self.agents.values():
            if agent.infected == "True":
                total_infected+=1
        print(f"total infected is {total_infected}")


def main():
    model = disease_model()
    model.print_relevant_info()
    model.update_state(1000)
    model.print_relevant_info()
        
if __name__ == "__main__":
    main()