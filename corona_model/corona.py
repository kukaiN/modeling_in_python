import os
import random
import pandas as pd
import pickle
import file_related as flr
import numpy as np
import bisect

def convert_to_min(time_str):
    """convert time represnted in the following forms to minutes in a day, 
        this function is used to decode the schedule in terms of minutes
        1.) military time, xx:xx
        2.) time with Meridiem Indicator (AM/PM), xx:xxAM or xx:xxPM
    """
    meridiem_indicator = time_str[-R2:]
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
    def __init__(self, rand_bool, name = "SE_lain", age = 22, immunity = 0.1, curr_location = "dorm", state = "healthy", archetype = "introvert"):
        """takes in the initial parameters"""
        self.name = name
        self.age = age
        self.immunity = immunity
        self.state = state #this defines the infection state
        self.archetype = archetype
        self.curr_location = curr_location

        # the states below are used to tell if the agent is moving or not
        self.motion = "stationary"
        self.arrival_time = 0
        self.minimum_waiting_time = 0
        self.desitination = None

    def random_schedule(self, archetype_dict = []):
        """ creates a plausable schedule that matches with the agent's archetype"""
        pass

    def update_loc(self, curr_time, adj_list):
        """function that update the time and the state of the agent, for now the agent is either moving or at rest"""
        threshhold = 0.5
        # if we waited in the room long enough then the agent will move
        if self.motion == "stationary" and curr_time > self.minimum_waiting_time + self.arrival_time:
            if random.random() < threshhold: # with a certain probabilty the agent will start moving again
                self.motion = "moving"

                self.destination = random.choice(list(adj_list.keys()))
                self.travel_time = 5
                adj_rooms = adj_list[self.curr_location]
                loc = self.move_to(adj_rooms)
                return loc
        if self.motion == "moving" and curr_time > self.travel_time: # if the agent is moving, then it will keep on moving until it reaches its destination
            adj_rooms = adj_list[self.curr_location]
            loc = self.move_to(adj_rooms)
            if self.curr_location == self.desitination:
                self.desitination = None
                self.motion = "stationary"
                self.arrival_time = curr_time
                self.minimum_waiting_time = 45
            return loc
        loc = (self.curr_location, self.curr_location)
        return loc

    def move_to(self,  adj_list):
        """moves the agent to rooms thats adjacent to the current room"""
        past_location = self.curr_location
        if self.desitination in adj_list:
            self.curr_location = self.destination
            self.destination = None
            #print(f"locations {self.curr_location}, {self.desitination}")
        else:
            random_room = random.choice(adj_list)
            #print(f"{self.name} moved to {random_room}")
            self.curr_location = random_room[0]
        #print("this, ", (past_location, self.curr_location))
        return (past_location, self.curr_location)


class rooms:
    def __init__(self, room_name = "unnamed_room", capacity = 20, default_agents = []):
        """initailize the room"""
        self.room_name = room_name
        self.capacity = capacity
        self.agents_in_room = default_agents

    def enter_room(self, agent_id):
        """ a put the id of the agent that entered the room"""
        if self.check_capacity():
            self.agents_in_room.append(agent_id)

    def check_capacity(self):
        """return a boolean, return True if theres capacity for one more agent, False if the room is at max capacity 
        """
        if len(self.agents_in_room) < self.capacity:
            return True
        return False
    
    
    def leave_room(self, agent_id):
        """ remove the id of the agent that exited the room"""
        if id in self.agents_in_room:
            self.agents_in_room.remove(agent_id)

    def update(self, agent_dict):
        """update the room state if needed"""
        for agent in self.agents_in_room:
            pass

class disease_model:
    def __init__(self, config_folder = "configuration", building_info = "buildings.csv", room_info = "rooms.csv", agent_info = "agents.csv", schedule_info = "schedules.csv"):
        
        """
        start a new infection model, the model will load the data from the csv files in the configuration folder
        if there's a different csv that you're trying to load, then modify the name of the file that is being passed
        """
        # this is a markov chain represented as a dictionary
        # key = "name of state", value = list of possible states and the associated probability
        self.default_agent_state = "healthy"
        # if you have a probability of staying on the same state, then make that state, the first entry in the list
        self.agent_markov_states = {
            "healthy": [(0.9995, "healthy"), (0.00025, "carrier"), (0.00025, "infected")],
            "carrier": [(0.995, "carrier"), (0.0049, "recovered"), (0.0005, "healthy"), (0.0005, "infected") ],
            "infected" : [(0.999, "infected"), (0.00099, "recovered"), (0.00001, "dead")], 
            "dead" : [(1, "dead")],
            "recovered" : [(0.999, "recovered"), (0.001, "healthy")]
        }
        self.check_markov_chain()
        self.markov_cdf = self.make_markov_to_cdf()
        # make panda dataframe from the given csv file
        self.config_folder_name = config_folder
        self.agent_df = self.make_df(agent_info) 
        self.building_df = self.make_df(building_info)
        self.room_df = self.make_df(room_info)
        self.schedule_df = self.make_df(schedule_info)


        print("*"*20)
        # make an adjacency list from the room_df, although it's called list by convention
        # the adjacency list is implimented as a dictionary
        self.adjacency_list = self.make_adj_list()
        self.check_adjacency_list()
        self.cached_shortestpath = None # coming soon
        
        # make lists and dictionaries that stores refrences to the room or agent objects
        self.id_to_rooms = self.initialize_rooms()
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
        temp_dict = dict((room_id, []) for room_id in self.adjacency_list.keys())
        for index, agent in self.agents.items():

            temp_dict[agent.curr_location].append(index)
        print(temp_dict.keys())
        print(temp_dict.values())
        print("*"*20)
        return temp_dict

    def make_markov_to_cdf(self, key_loc = 0):
        temp_dict = dict()
        for key, value in self.agent_markov_states.items():
            cdf = [value[0][key_loc]]
            for ind in range(1, len(value)):
                cdf.append(cdf[-1] + value[ind][key_loc])
            temp_dict[key] = cdf
        print(temp_dict.values())
        return temp_dict
        

    def check_markov_chain(self):
        for _, markov_row in self.agent_markov_states.items():
            probability_space = sum(markov_state[0] for markov_state in markov_row)
            if probability_space < 1:
                print("row of markov matrix doesnt sum to 1")
                markov_row.append((1-probability_space, self.default_agent_state))

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
            temp_dict[room_info["located building"]].append(index)
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
        for room_id, row in self.room_df.iterrows():
            # since the index is the unique id, we find the id of the FIRST room with the same name
            adj_room = self.room_df.index[self.room_df["room_name"] == row["connected to"]].tolist()[0]
            travel_time  =  row["travel time"]
            adj_dict[room_id] = adj_dict.get(room_id, []) + [(adj_room, travel_time)]
            adj_dict[adj_room] = adj_dict.get(adj_room,[]) + [(room_id, travel_time)]
        return adj_dict

    def check_adjacency_list(self):
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
            if t%10 == 0:
                self.infection_rule()  
    
    def update_agents(self):
        """function that calls the agents to update its state"""
        for index, agents in self.agents.items():
            loc = agents.update_loc(self.time, self.adjacency_list)
            if loc[0] != loc[1]:
                self.room_agent_dict[loc[0]].remove(index)
                self.room_agent_dict[loc[1]].append(index)

    def infection_rule(self):
        """ this function determines how the infection will spread and how strong the infection is,
        the function can be modified to make new rules for infection"""
        rand_vect = np.random.random(len(self.agents))
        update_dict = dict([(keys, []) for keys in self.agent_markov_states.keys()])
        for index, agent in enumerate(self.agents.values()):
            agent_list = self.room_agent_dict[agent.curr_location]
            # get the number of infected vs not infected
            infected, population = self.count_within_agents(agent_list, "infected"), len(agent_list)
            agents_infected = infected/population
            if agent.state == "healthy" and agents_infected > 0:
                # add a buff to infection if theres more infected agents in the same room
                possible_states = self.agent_markov_states[agent.state]
                random_val = rand_vect[index] #* (1-agent.immunity)
                ind = bisect.bisect(self.markov_cdf[agent.state], random_val)
                update_dict[possible_states[ind][1]].append(index)
                #agent.state = possible_states[ind][1]
                #print(random_val, 1-agent.immunity)
                #print(possible_states, random_val, ind, agent.state)
            else: 
                possible_states = self.agent_markov_states[agent.state]
                random_val = rand_vect[index]
                ind = bisect.bisect(self.markov_cdf[agent.state], random_val)
                if ind+1 > len(possible_states): ind = -1
                update_dict[possible_states[ind][1]].append(index)
                #agent.state = possible_states[ind][1]
                #print(possible_states, random_val, ind, agent.state)
        #print(update_dict.keys())
        #print(update_dict.values())
        for key,  value in update_dict.items():
            for agent_id in value:
                self.agents[agent_id+1].state = key
            

    def update_time(self, time_step = 1):
        """ updates time passed in the model"""
        self.time+=time_step

    def initilize_agents(self):
        """ creates the agents and make a dictionary with agent_id as keys and the agent object is the value"""
        print("*"*20)
        building_list = list(self.building_df["building_name"])
        print(building_list)
        agent_dict = dict()
        for index, agent_row in self.agent_df.iterrows(): # go through all rows and make agent objects
            curr_location = agent_row["initial condition"]
            agent_dict[index] = agent(*list(agent_row))
            if curr_location in building_list:
                agent_dict[index].curr_location = random.choice(self.building_room_list[curr_location])
            else:
                adj_room = self.room_df.index[self.room_df["room_name"] == row["connected to"]].tolist()[0]
                a = self.room_df[self.room_df["room_name"] == curr_location].to_list()
                print(a)
                agent_dict[index].curr_location = a
        return agent_dict

    def make_df(self, file_name):
        """ creates a panda dataframe from the content in a csv file"""
        a = flr.format_data(self.config_folder_name, file_name)
        print("this is a preview of the data that you're loading:")
        print(a.head(3))
        return a
    
    def count_within_agents(self, agent_list, state_name):
        return len(list(filter(lambda x: x.state == state_name, [self.agents[val] for val in agent_list]))) 

    def count_agent(self, state_name):
        return len(list(filter(lambda x: x.state == state_name, self.agents.values() )))

    def print_relevant_info(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this functio n will be converted to the proper format using __repr__"""
        infected = self.count_agent("infected")
        carrier = self.count_agent("carrier")
        dead = self.count_agent("dead")
        healthy = self.count_agent("healthy")
        recovered = self.count_agent("recovered")
        print(f"time: {self.time} total healthy {healthy} infected: {infected}, carrier: {carrier}, dead: {dead}, recovered: {recovered}")
        #print(f" agent's locations is {list(room.agents_in_room for room in self.room_dict.values())}")
        #print(f"agent's location is {self.room_agent_dict}")

def main():
    """start a new disease model"""
    # supceptable, exposed, infected, recovered, dead
    #

    model = disease_model()
    model.print_relevant_info()
    days = 10
    time_interval_in_min = 60
    for day in range(days):
        #model.print_relevant_info()
        #model.update_state(int(24*60/time_interval_in_min))
        model.print_relevant_info()
           
if __name__ == "__main__":
    main()