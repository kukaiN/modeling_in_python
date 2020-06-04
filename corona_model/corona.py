import os
import random
import pandas as pd
import pickle
import file_related as flr
import numpy as np
class people:
    def __init__(self, name = "SE_lain", age = 22, immunity = 0.1, infected = False, archetype = "introvert", curr_location):
        self.name = name
        self.age = age
        self.immunity = immunity
        self.infected = False
        self.archetype = archetype
        self.curr_location = curr_location

    def assign_schedule(self, archetype_dict, schedule = []):
        schedule_size = len(archetype_dict[self.archetype])
        if schedule_size < len(schedule):
            schedule = [1/schedule_size for _ in range(schedule_size)]
        self.schedule = schedule


    def move_to(self, destination):
        self.destination = destination

    def update_t():

class disease_model:
    def __init__(self, building_info = "building_info.csv", room_info = "room_info.csv", people_info = "people_info.csv"):
        self.people_df = self.make_df(people_info) 
        self.building_df = self.make_df(building_info)
        self.room_df = self.make_df(room_info)
        self.cached_shortestpath = None # coming soon
        print("*"*20)
        #print(self.people_df.loc[1])
        # dictionary: keys are the building name, values are the rooms that are located in it
        self.building_room_dict = dict((building_name, []) for building_name in self.building_df["building_name"])
        for index, room in self.room_df.iterrows():
            self.building_room_dict[room["located building"]].append(room["room_name"])
        
        self.room_people_dict = dict((room_name, []) for room_name in self.room_df["room_name"])
        
        print(self.room_people_dict.keys())
        building_list = list(self.building_df["building_name"])
        print(building_list)
        for index, people in self.people_df.iterrows():
            if people["initial condition"] in building_list:
                random_room = random.choice(self.building_room_dict[people["initial condition"]])
                self.room_people_dict[random_room].append(index)
            else:
                self.room_people_dict[people["initial condition"]].append(index)
        print(self.room_people_dict.keys())
        print(self.room_people_dict.values())
  
    

    def update_state(self, steps = 5):
        # update t time steps
        def infection_rule(num_of_infected, population, list_of_id):
            infected_ratio = num_of_infected/population
            rng = np.random.default_rng()
            x = rng.random((population,))
            
            return [id_num for index, id_num in enumerate(list_of_id) if x[index] < infected_ratio]

        for t in range(steps):
            print("*"*20)
            for room, list_of_people in self.room_people_dict.items():
                if list_of_people != []:
                    print(room, list_of_people)
                    num_of_infected = sum([1 for people_id in list_of_people if self.people_df.loc[people_id]["infected"] == "True"])
                    num_not_infected = len(list_of_people) - num_of_infected
                    population = len(list_of_people)
                    print("# infected", num_of_infected, num_not_infected)
                    if 0 < num_of_infected < population:
                        newly_infected = infection_rule(num_of_infected, population, list_of_people)
                        for infected_id in newly_infected:
                            self.people_df.loc[infected_id]["infected"] = "True"
            print(t, "num_infected =", (self.people_df.infected.values == "True").sum())    
        
    def make_df(self, file_name):
        a = flr.format_data(file_name)
        print("this is a part of the data that you're loading")
        print(a.head())
        return a
    
def main():
    model = disease_model()
    model.update_state()
    
if __name__ == "__main__":
    main()