import numpy as np
import matplotlib.pyplot as plt
# the code works but a bit slow, so open for change


def createSchedule(numOfAgents,agentArchetypes,classrooms, capacity, classAllowedTypeDict=None, modulo=24):
    """
        create a list of schedules for each agents, 
        agent_archetype dictates the distribution and types of random values to fill the empty slots after assigning the static portion
    """
    # the key is the name of the schedule, the value is a list of tuples (duration, starting time, end time), 
    # if the duration is less than the total interval, then it will choose a starting and end time inside the interval
    # for now the time is in hours so everything is mod 24.  (24 hours in a day)
    # initialization of parameters
    staticSchedule = {
        "sleep": [(8, 22, 8)],
        "classes": [(2, 10, 12), (2, 12,14), (2,14, 16),(2,16,18)],
        "eating": [(1, 8, 10), (1, 12, 15), (1, 18, 21)]
    }

    # define the parameters relating to choosing classes
    
    OE_slots = 4 # both odd and even slots are 4
    totalClassSlots = 8
    timeslotsPerDay = 24 # 24 hours in a day
    # define the number and name of unique schedules
    # change to ["mon", "tues", ..." sunday"] to create differnt schedules for a week, this can be expanded
    scheduleType = ["Odd", "Even", "Weekends"] 
    # define the priorities of assigning a schedules for odd days, even days, and weekends
    OEW_priority = [["sleep", "eating"], ["sleep", "eating"],  ["sleep", "eating"]]
    # dynamic schedules are types of schedules that will be used to fill empty slots in the schedules
    dynamicSchedule = ["study", "gym", "off_campus"]
    dynamicProbabilites = {
        "stem" : [0.5, 0.2, 0.3],
        "athletes" : [0.1, 0.5, 0.4],
        "party": [0.1, 0.2, 0.7],
        "other" : [1/3 for _ in range(3)]
    }
    
    listOfScedules = []
    classList = [classrooms[index] for index, val in enumerate(capacity) for _ in range(int(val))]
    masks = createMask(numOfAgents)
    maskSum = np.sum(masks, axis=0, dtype=int)

    maskCurrIndex = np.zeros(maskSum.shape, dtype = int)
    x, y = maskSum.shape
    classes = [[np.random.permutation(classList) for _ in range(y)] for _ in range(x)]
  
    for index in range(numOfAgents): # iterate over each agents
        # create a mask that splits the classes into odd and even schedules
        # NoteToSelf: put classPerAgent and totalClassStots inside the loop for randomization 
        agentSchedule = [[0 for _ in range(timeslotsPerDay)] for _ in range(len(scheduleType))]
        agentSchedule = assignClasses(agentSchedule, masks[index], classes, maskCurrIndex)
        maskCurrIndex+=masks[index]

        # check if the agent's type is defined or not
        archetype = agentArchetypes[index]
        if archetype not in dynamicProbabilites.keys():
            archetype = "other"
        
        # assign a schedule for each unique schedule
        for i, routineName in enumerate(scheduleType): # odd, even, weekends
            agentSchedule[i] = chooseStatic(agentSchedule[i], staticSchedule, OEW_priority[i])
            # fill the empty slots with random values with some distribution
            agentSchedule[i] = fillRandomWithCDF(agentSchedule[i], 0, dynamicSchedule, dynamicProbabilites[archetype])
                
        # add i-th agent's schedule to the schedule list
        listOfScedules.append(agentSchedule)
    return listOfScedules

def chooseStatic(schedule, staticDict, priorityQueue, modulo=24,className=None,spKey=None, spDict=None,archetype=None ,mask=None):
    """
        given a scheudule and a priority queue, 
        it takes the next highest priority item and checks for conflicts and the event is added to the schedule only if there's no confict
        if the duration of the event is less than the time interval, 
        then the event is placed at a random time such that its between the interval and end before or at the end time
        note: this isnt a greedy schedule, it just assign an event if time is available. 
    """
    # iterate in highest priority to lowest priority
    for priorityItem in priorityQueue:
        staticList = staticDict[priorityItem]
        if mask != None:
            # mask for this scheduling exists, so apply the mask to get the new list
            if priorityItem in mask.keys():
                staticList = [val for index, val in enumerate(staticList) if index in mask[priorityItem]]
        # go over the time interval(s) for the event
        for index, tup in enumerate(staticList):
            duration, start, end = tup 
            # take a slice of the schedule and cut it so its [start, ...., end], since index is time, theres cases where the index wraps around due to modulo
            timeslot = (schedule[start:] + schedule[:end]) if start > end else schedule[start:end]
            # get the possible starting possitions
            availability = getAvailability(timeslot, duration)
            if availability != []:
                # choose a random starting possition and assign the event for the duration of the event 
                x = np.random.choice(availability)
                itemName = className[index] if spKey == priorityItem else priorityItem
                for i in range(duration):
                        schedule[(start+x+i)%modulo] = itemName
    return schedule
            
def fillRandomWithCDF(scheduleList, replaceVal, randomValues, associatedProbabilities = []):
    """
        fill the empty slots with values provided, you can also provide the distribution of those values being selected
        if no probability list is given, then everything will have uniform probability
    """
    # get a random list that is the size of the empty slots
    numRandom = scheduleList.count(replaceVal)
    if associatedProbabilities == [] and len(randomValues) > 0:
        size = len(randomValues)
        associatedProbabilities = [1/size]*size
    distributedSchedule = np.random.choice(randomValues, size= numRandom, p=associatedProbabilities)
    i = 0
    # fill the empty slots with the random value
    for index in range(len(scheduleList)):
        if scheduleList[index] == replaceVal:
            scheduleList[index] = distributedSchedule[i]
            i+=1
    return scheduleList          

def getAvailability(partialInterval, duration):
    """
        returns the starting index of a semi-random scheduler
        if the intervals are | 1 | 2 | 3 |, and the duration is 2, 
        then it will return  [0, 1], because they're the corresponding zero based index when the event can start
        if a slot contains a value that doesnt evaluate to False when evaluated as a bool, then that slot is deemed taken 
    """
    a=np.zeros(len(partialInterval), dtype=int)
    for i in range(len(a)):
        # the value at that index is not filled
        if not (partialInterval[i] or a[i-1] > duration): # used De Morgans to simplify logic
            # if the value is not yet equal to the required duration
            a[i] = a[i-1]+1
        # else is that the value of a at that index stays 0
    return [time-duration+1 for time, val in enumerate(a) if val >= duration]

def countSchedule(schedule, countParam):
    storingList = [0 for _ in countParam]
    for agent_schedule in schedule:
        for daily_schedule in agent_schedule:
            for activity in daily_schedule:
                if activity in countParam:
                    storingList[countParam.index(activity)]+=1
    return storingList

def createMask(agentNumber, schedulePerAgent = 2):
    """return a 3d object in np"""
    mask = np.concatenate([np.ones(4, dtype=bool), np.zeros(4, dtype=bool)])
    newmask = np.array([np.random.permutation(mask).reshape(2,-1) for _ in range(agentNumber)], dtype=bool)
    return newmask

def assignClasses(agentSchedule, masks, classes, indexMatrix):
    """ assign classes to a schedule"""
    durr = 2
    base = 10
    for index in range(len(masks)): # odd vs even
        chair = classes[index]
        maskRow = indexMatrix[index]
        for i, val in enumerate(masks[index]):
            if val:
                indexVal = maskRow[i]
                for k in range(durr):
                    agentSchedule[index][base+(2*i)+k] = chair[i][indexVal]
    return agentSchedule

def main():
    # test schedule parameters for this file
    agentTypes = ["athletes", "stem", "party", "introverts", "terminators", "aliens", "other"]
    numAgent = 2000
    modTime = 24
    randomizedAgents = np.random.choice(agentTypes, size=numAgent, replace=True)
    # 150 classrooms with 20~50 agent capacity
    classrooms = [a for a in range(0, 150)]
    classCapacity = np.random.choice(range(20, 50), size=len(classrooms), replace=True)
    classEnrollment = np.zeros(shape=np.shape(classCapacity))
    # create schedules

    classDict = dict()
    for key in agentTypes:
        classDict[key] = {classKey: [cap, enrollment] for (classKey, cap, enrollment) in zip(classrooms, classCapacity, classEnrollment)}
    
    schedule = createSchedule(numAgent, randomizedAgents, classrooms, classCapacity, classDict, modulo=modTime)

    # print the first 5 agent's schedule for n unique days
    print(schedule[:5])

    createMask(numAgent)

if __name__ == "__main__":
    main()