import numpy as np




def create_schedule(number_of_agents,agent_archetypes, classes, class_capacity):
    
    # the key is the name of the schedule, the value is a list of tuples (duration, starting time, end time), 
    # if the duration is less than the total interval, then it will choose a starting and end time inside the interval
    # for now the time is in hours so everything is mod 24.  (24 hours in a day)
    static_schedule = {
        "sleep": [(10, 22, 8)]
        "classes": [(2, 10, 12), (2, 12,14), (2,14, 16),(2,16,18)]
        "eating": [(1, 8, 10), (1, 12, 3), (1, 6, 9)]
    }
    static_assignment_order = ["sleep", "class", "eating"]
    dynamic_schedule = ["study", "gym", "off_campus"]
    dynamic_probabilites = {
        "stem" : [0.5, 0.2, 0.3]
        "athletes" : [0.1, 0.5, 0.4]
        "party": [0.1, 0.3, 0.7]
        "other" : "random"
    }
    schedule_type = ["Odd", "Even", "Weekends"]
    list_of_scedules = []

    for agent_index in range(number_of_agents):
        agent_archetype = agent_archetypes[agent_index]
        agent_schedule = [["a" for _ in range(24)] for _ in range(3)]
        for i, sched_type in enumerate(schedule_type):
            static = choose_static(static_schedule, static_assignment_order)
            agent_schedule[i][]



        list_of_scedules.append(agent_schedule)

def choose_static(static_dictionary, static_order):
    for order_str in static_order:
        static_list = static_dictionary(order_str)
        for tup in static_dictionary
            durration, start_time
def main():
    agent_types = ["athletes", "stem", "party", "introverts", "terminators", "aliens"]
    num_agent = 2000
    random_people = np.random.choice(agent_types, size=num_agent, replace=True)
    classrooms = [a for a in range(0, 150)]
    classroom_capacity = np.random.choice(range(20, 50), size=len(classrooms), replace=True)


    schedule = create_schedule(num_agent, random_people, classrooms, class_capacity)
    print(schedule[0])

if __name__ == "__main__":
    main()