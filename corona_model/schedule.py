import numpy as np
import matplotlib.pyplot as plt
# the code works but a bit slow, so open for change


def create_schedule(number_of_agents,agent_archetypes,classrooms, capacity, class_dict, modulo=24):
    """
        create a list of schedules for each agents, 
        agent_archetype dictates the distribution and types of random values to fill the empty slots after assigning the static portion
    """
    # the key is the name of the schedule, the value is a list of tuples (duration, starting time, end time), 
    # if the duration is less than the total interval, then it will choose a starting and end time inside the interval
    # for now the time is in hours so everything is mod 24.  (24 hours in a day)
    # initialization of parameters
    static_schedule = {
        "sleep": [(8, 22, 8)],
        "classes": [(2, 10, 12), (2, 12,14), (2,14, 16),(2,16,18)],
        "eating": [(1, 8, 10), (1, 12, 15), (1, 18, 21)]
    }

    # define the parameters relating to choosing classes
    class_per_agent = 4
    OE_slots = 4 # both odd and even slots are 4
    total_class_slots = 8
    possible_classes = np.array(range(1, total_class_slots + 1), dtype=int)
    timeslots_per_day = 24 # 24 hours in a day
    # define the number and name of unique schedules
    # change to ["mon", "tues", ..." sunday"] to create differnt schedules for a week, this can be expanded
    schedule_type = ["Odd", "Even", "Weekends"] 
    # define the priorities of assigning a schedules
    odd_priorities = ["sleep", "classes", "eating"]
    even_priorities = ["sleep", "classes", "eating"]
    weekend_priority = ["sleep", "eating"]
    # dynamic schedules are types of schedules that will be used to fill empty slots in the schedules
    dynamic_schedule = ["study", "gym", "off_campus"]
    dynamic_probabilites = {
        "stem" : [0.5, 0.2, 0.3],
        "athletes" : [0.1, 0.5, 0.4],
        "party": [0.1, 0.2, 0.7],
        "other" : [1/3 for _ in range(3)]
    }
    
    list_of_scedules = []
    class_list = [classrooms[index] for index, val in enumerate(capacity) for _ in range(int(val))]
    odd_class_list = class_list[:]
    np.random.shuffle(odd_class_list)
    even_class_list =  class_list[:]
    np.random.shuffle(even_class_list)

    odd_index = 0
    odd_jump = 0
    even_index = 0
    even_jump = 0

    for agent_index in range(number_of_agents): # iterate over each agents
        # create a mask that splits the classes into odd and even schedules
        mask = np.concatenate([np.ones(class_per_agent, dtype=bool), np.zeros(total_class_slots-class_per_agent, dtype=bool)])
        np.random.shuffle(mask)
        classes = possible_classes[mask]
        odd_classes, even_classes = [a%OE_slots for a in classes if a <= OE_slots], [b%OE_slots for b in classes if b > OE_slots]
        # check if the agent's type is defined or not
        agent_archetype = agent_archetypes[agent_index]
        if agent_archetype not in dynamic_probabilites.keys():
            agent_archetype = "other"
        # each agent will have a 24 hour schedule and is initially empty
        agent_schedule = [[0 for _ in range(timeslots_per_day)] for _ in range(len(schedule_type))]
        # assign a schedule for each unique schedule
        for i, sched_type in enumerate(schedule_type):
            if sched_type in ["Odd","O"]: # creates the odd day schedule
                odd_mask = {"classes" : odd_classes}
                odd_jump = len(odd_classes)
                odd_class = odd_class_list[odd_index:odd_index+odd_jump]
                odd_index+=odd_jump
                agent_schedule[i] = choose_static(agent_schedule[i], static_schedule, odd_priorities, class_name=odd_class, archetype=agent_archetype , sp_key="classes", sp_dict=class_dict, mask=odd_mask)
                
            elif sched_type in ["Even", "E"]: # create the even days
                even_mask = {"classes" : even_classes}
                even_jump = len(even_classes)
                even_class = even_class_list[even_index:even_index+even_jump]
                even_index+=even_jump
                agent_schedule[i] = choose_static(agent_schedule[i], static_schedule, even_priorities, class_name=even_class, archetype=agent_archetype,sp_key="classes", sp_dict=class_dict, mask=even_mask)
                
            else: # this takes care of the weekend schedule
                agent_schedule[i] = choose_static(agent_schedule[i], static_schedule, weekend_priority)
            print(agent_schedule)
            # fill the empty slots with random values with some distribution
            agent_schedule[i] = fill_random_with_CDF(agent_schedule[i], 0, dynamic_schedule, dynamic_probabilites[agent_archetype])
                
        # add i-th agent's schedule to the schedule list
        list_of_scedules.append(agent_schedule)
        break
    return list_of_scedules

def choose_static(schedule, static_dictionary, priority_queue, modulo=24,class_name=None,sp_key=None, sp_dict=None,archetype=None ,mask=None):
    """
        given a scheudule and a priority queue, 
        it takes the next highest priority item and checks for conflicts and the event is added to the schedule only if there's no confict
        if the duration of the event is less than the time interval, 
        then the evnt is placed at a random time such that its between the interval and end before or at the end time
        note: this isnt a greedy schedule, it just assign an event if time is available. 
    """
    # iterate in highest priority to lowest priority
    
    
    
    for priority_item in priority_queue:
        static_list = static_dictionary[priority_item]
        if mask != None:
            # mask for this scheduling exists, so apply the mask to get the new list
            if priority_item in mask.keys():
                static_list = [val for index, val in enumerate(static_list) if index in mask[priority_item]]
        # go over the time interval(s) for the event
        for index, tup in enumerate(static_list):
            duration, start, end = tup 
            # take a slice of the schedule and cut it so its [start, ...., end], since index is time, theres cases where the index wraps around due to modulo
            timeslot = (schedule[start:] + schedule[:end]) if start > end else schedule[start:end]
            # get the possible starting possitions
            availability = get_availability(timeslot, duration)
            if availability != []:
                # choose a random starting possition and assign the event for the duration of the event 
                x = np.random.choice(availability)
                if sp_key == None:
                    for i in range(duration):
                        schedule[(start+x+i)%modulo] = priority_item
                elif sp_key == priority_item:
                    # we need to rename what ever this event is by checking into a room with enrollment < capacity
                    # value is a tuple :(capacity, curr_enrollment)
                    #available = [key for key, value in sp_dict[archetype].items() if value[0] > value[1]]
                    #class_key = np.random.choice(available)
                    # increase enrollment by 1
                    #sp_dict[archetype][class_key][1] = sp_dict[archetype][class_key][1] + 1  
                    for i in range(duration):
                        if index >= len(class_name):
                            print(static_list)
                            print(duration, sp_key, archetype, schedule)
                            print(priority_item, index, tup, class_name)
                            print(index, class_name)
                        a = class_name[index]
                        schedule[(start+x+i)%modulo] = a
    return schedule
            
def fill_random_with_CDF(schedule_list, replace_val, random_values, associated_probabilities = []):
    """
        fill the empty slots with values provided, you can also provide the distribution of those values being selected
        if no probability list is given, then everything will have uniform probability
    """
    # get a random list that is the size of the empty slots
    num_random = schedule_list.count(replace_val)
    if associated_probabilities == [] and len(random_values) > 0:
        size = len(random_values)
        associated_probabilities = [1/size]*size
    distributed_schedule = np.random.choice(random_values, size= num_random, p=associated_probabilities)
    i = 0
    # fill the empty slots with the random value
    for index in range(len(schedule_list)):
        if schedule_list[index] == replace_val:
            schedule_list[index] = distributed_schedule[i]
            i+=1
    return schedule_list          

def get_availability(partial_interval, duration):
    """
        returns the starting index of a semi-random scheduler
        if the intervals are | 1 | 2 | 3 |, and the duration is 2, 
        then it will return  [0, 1], because they're the corresponding zero based index when the event can start
        if a slot contains a value that doesnt evaluate to False when evaluated as a bool, then that slot is deemed taken 
    """
    
    a=np.zeros(len(partial_interval), dtype=int)
    for i in range(len(a)):
        # the value at that index is not filled
        if not (partial_interval[i] or a[i-1] > duration): # used De Morgans to simplify logic
            # if the value is not yet equal to the required duration
            a[i] = a[i-1]+1
        # else is that the value of a at that index stays 0
    return [time-duration+1 for time, val in enumerate(a) if val >= duration]

def aperature()



def main():
    # test schedule parameters for this file
    agent_types = ["athletes", "stem", "party", "introverts", "terminators", "aliens", "other"]
    num_agent = 2000
    mod_time = 24
    randomized_agents = np.random.choice(agent_types, size=num_agent, replace=True)
    # 150 classrooms with 20~50 agent capacity
    classrooms = [a for a in range(0, 150)]
    classroom_capacity = np.random.choice(range(20, 50), size=len(classrooms), replace=True)
    classroom_enrollment = np.zeros(shape=np.shape(classroom_capacity))
    # create schedules
    
    
    class_dict = dict()
    for key in agent_types:
        class_dict[key] = {class_key: [cap, enrollment] for (class_key, cap, enrollment) in zip(classrooms, classroom_capacity, classroom_enrollment)}
    
    schedule = create_schedule(num_agent, randomized_agents, classrooms, classroom_capacity, class_dict, modulo=mod_time)

    # print the first 5 agent's schedule for n unique days
    print(schedule[:5])

if __name__ == "__main__":
    main()