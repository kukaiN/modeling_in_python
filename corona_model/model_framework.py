import os
import random
import pandas as pd
import pickle

import numpy as np

#mport schedule
import time
import copy
import itertools
# the following are .py files
import fileRelated as flr
import statfile
import visualize as vs
import modifyDf as mod_df
import schedule_students
import schedule_faculty
# for speed tests/debug
import functools

def clock(func): # version 2, page 203 - 205
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        arg_lst = [] #name = func.__name__
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ["%s=%r" % (k,w) for k, w in sorted(kwargs.items())]
            arg_lst.append(", ".join(pairs))
        arg_str = ", ".join(arg_lst)
        print("[%0.8fs] %s(%s) -> %r " % (elapsed, func.__name__, arg_str, result))
        return result
    return clocked

def convertToMin(timeStr):
    """convert time represnted in the following forms to minutes in a day, 
        this function is used to decode the schedule in terms of minutes
        1.) military time, xx:xx
        2.) time with Meridiem Indicator (AM/PM), xx:xxAM or xx:xxPM
    """
    meridiemIndicator = timeStr[-2:]
    if meridiemIndicator in ["AM", "PM"]: # check if Meridiem Indicator is included
        timeStr = timeStr[:-2]
    hours, minutes = [int(a) for a in timeStr.strip().split(":")]
    if meridiemIndicator == "PM": # if the period is PM, then add 12 hours to the time
            minutes += 60*12
    minutes+= hours*60
    return minutes

def findInTuple(val, itemList, index):
    """ iterate over the item_list and returns the first tuple with the same value"""
    for tup in itemList:
        if tup[index] == val: return tup
    return None

def runSimulation(pickleName, simulationN= 10, runtime = 200):
    print(f"starting {simulationN} simulation for {runtime} steps")
    infA0, infA1, infS = "infected Asymptomatic0", "infected Asymptomatic1" ,"infected Symptomatic"
    simulationOutcome = []
    for _ in range(simulationN):
        model = flr.loadUsingDill(pickleName)
        print("loaded pickled object successfully")
        model.configureDebug(False)
        model.startInfectionAndSchedule()
        model.initializeStoringParameter([infA0, infA1, infS], steps=1)
        model.updateSteps(runtime)
        # end of simulation
        
        # retrieve the time series data
        dataDict = model.returnStoredInfo()
        # look at total infected over time, 
        arr1 = np.array(dataDict[infA0])
        arr2 = np.array(dataDict[infA1])
        arr3 = np.array(dataDict[infS])
        infected_numbers = arr1+arr2+arr3
        simulationOutcome.append(infected_numbers)
    return simulationOutcome

def simulateAndPlot(pickleNames, simulationN=10, runtime=200):
    outcomes = []
    totalcases = len(pickleNames)
    t0 = time.time()
    for i, name in enumerate(pickleNames):
        print("*"*20)
        print(f"{(i+1)/totalcases*100}% cases finished")
        outcomes.append(runSimulation(name,simulationN, runtime))
        print((f"took {time.time()-t0} time to finish{(i+1)/totalcases*100}%"))
    print(f"took {time.time()-t0} time to run {totalcases*simulationN} simulations")
    statfile.plotBoxAverageAndDx(outcomes)

def initializeSimulations(simulationControls, modelConfig, debug=True, pickleBaseName="pickleModel_"):
    """
        create the initialized model for each controlled experiment
    """
    createdNames = []
    for i, independentVariables in enumerate(simulationControls):
        pickleName = pickleBaseName+str(i)
        pickleName = flr.fullPath(pickleName+".pkl", "picklefile")
        if independentVariables[0][0] == None: # base model
            model = createModel(modelConfig, debug)
        else: # modify the data
            # the following copy of the model config is a shallow copy, 
            # if you want to modify a dict in the config, then use deep copy 
            configCopy = dict(modelConfig)
            for variableTup in independentVariables:
                configCopy[variableTup[0]] = variableTup[1]
            model = createModel(configCopy, debug)
        flr.saveUsingDill(pickleName, model)
        createdNames.append(pickleName)
    print("copy the following list and put in in as a parameter")
    print(createdNames)
    return createdNames

def createModel(modelConfig, debug=False):
    model = AgentBasedModel()
    model.addKeys(modelConfig)
    model.loadBuilder("newBuilding.csv")
    model.loadAgent("newAgent.csv")
    model.generateAgentFromDf()
    model.initializeWorld()
    model.initializeAgents()
    model.startLog()
    model.configureDebug(debug)
    model.agentAssignBool(0.2, attrName="compliance")
    model.agentAssignBool(0.2, attrName="officeAttendee")
    model.agentAssignBool(0.5, attrName="gathering")
    #model.agentAssignBool(0, attrName="gathering")
    return model

def simpleCheck(modelConfig, days=100, visuals=True):
    loadDill = False
    saveDill = False
    pickleName = flr.fullPath("coronaModel.pkl", "picklefile")
    if not loadDill:
        model = createModel(modelConfig)
        if saveDill:
            flr.saveUsingDill(pickleName, model)
            # save an instance for faster loading
            return 0
    else:
        model = flr.loadUsingDill(pickleName)
        print("loaded pickled object successfully")
    model.configureDebug(False)
    # make schedules for each agents, outside of pickle for testing and for randomization
    model.startInfectionAndSchedule()
    model.initializeStoringParameter(["susceptible","exposed", "infected Asymptomatic0", "infected Asymptomatic1" ,"infected Symptomatic", "recovered", "quarantined"], 
                                        steps=1)
    model.printRelevantInfo()
    for _ in range(days):
        model.updateSteps(24)
        model.printRelevantInfo()
    model.final_check()
    model.printLog()
    if visuals:
        model.visualOverTime()
    #model.visualizeBuildings()

def R0_simulation(modelConfig, R0Control, simulationN=10, debug=False):
    infA0 = "infected Asymptomatic0"
    infA1, infS, rec = "infected Asymptomatic1", "infected Symptomatic", "recovered"
    R0List = []
    configCopy = dict(modelConfig)
    for variableTup in R0Control:
        configCopy[variableTup[0]] = variableTup[1]
    # base model
    model = createModel(configCopy)
    model.configureDebug(debug)
    if debug:
        model.startLog()
        max_limits = dict()
    
    days = 50
    for i in range(simulationN):
        print("*"*20)
        new_model = copy.deepcopy(model)    
        new_model.startInfectionAndSchedule()
        new_model.findR0()
        new_model.initializeStoringParameter([infA0, infA1, infS, rec], steps=1)
        print("starting model")
        for _ in range(days):
            new_model.updateSteps(24)
        if debug:
            logDataDict = new_model.printLog()
            for key, value in logDataDict.items():
                max_limits[key] = max_limits.get(key, []) + [value]
        sampleR0 = new_model.returnR0()
        R0List.append(sampleR0)
        print(f"finished {(i+1)/simulationN*100}% of cases")
    if debug:
        for key, value in max_limits.items():
            print(key, "max is the following:", value)
    print("R0 is", R0List)
    data = statfile.analyzeData(R0List)
    #pickleName = flr.fullPath("R0Data.pkl", "picklefile")
    # save the data just in case
    #flr.saveUsingDill(pickleName, R0List)
    print(data)
    print("(npMean, stdev, rangeVal, median)")
    statfile.boxplot(R0List,True, "R0 simulation", "cases", "infected people (R0)", ["base model"])
    new_model.visualOverTime()


def main():
    """ the main function that starts the model"""
    # the "config" and "info" are different, config tells the code what values/range are allowed for a variable.
    # the info are the specific data for a specific instance of the class
    sus = "susceptible"
    exp = "exposed"
    infA0 = "infected Asymptomatic0"
    infA1 = "infected Asymptomatic1"
    infS = "infected Symptomatic"
    rec = "recovered"
    qua = "quarantined"

    modelConfig = {
        # time intervals
        "unitTime" : "hour",

        # rewrite this for speed up
        "qua" : "quarantined",
        "sus" : "susceptible",
        "exp" : "exposed",
        "infA0" : "infected Asymptomatic0",
        "infA1" : "infected Asymptomatic1",
        "infS" : "infected Symptomatic",
        "rec" : "recovered",

        # AGENTS
        "AgentPossibleStates": {
            "neutral" : ["susceptible", "exposed", "quarantined"],
            "infected" : ["infected Asymptomatic0", "infected Asymptomatic1", "infected Symptomatic"],  
            "recovered" : ["recovered"],
            },


        # these are parameters, that are assigned later or is ok to be initialized with default value 0
        "extraParam": {
            "Agents": ["agentId","path", "destination", "currLocation",
                        "statePersistance","lastUpdate", "personality", 
                        "arrivalTime", "schedule", "travelTime", "compliance", 
                        "officeAttendee", "gathering"],
            "Rooms":  ["roomId","agentsInside","oddCap", "evenCap", "classname"],
            "Buildings": ["buildingId","roomsInside"],
        },
        "extraZipParam": {
            "Agents" : [("motion", "stationary"), ("infected", False)],
        },
        # 0.05-->R0 is [9, 8, 5, 0, 7]
        #(5.8, 3.1874754901018454, 9, 7.0)
        # INFECTION parameter
        # 0.025 --> R0 is 3.8, (3.84, 2.257077756746541, 10, 3.5)
        # going with 2.5
        # base p of 0.025
        "baseP" : 0.01,
        "infectionSeedNumber": 10,
        "infectionSeedState": "exposed",
        "infectionContribution":{
            "infected Asymptomatic0":0.5,
            "infected Asymptomatic1":0.5,
            "infected Symptomatic":1,
        },
        # INFECTION STATE
        "transitionTime" : {
            "susceptible":-1,
            "exposed":2*23,
            "infected Asymptomatic0":2*24,
            "infected Asymptomatic1":10*24,
            "infected Symptomatic":10*24,
            "recovered":-1,
            "quarantined":24*14,
            "ghost": -1,
        },
        
        "transitionProbability" : {
            "susceptible": [("exposed", 1)],
            "exposed": [("infected Asymptomatic0", 0.85), ("infected Asymptomatic1", 1)],
            "infected Asymptomatic1": [("recovered", 1)],
            "infected Asymptomatic0": [("infected Symptomatic", 1)],
            "infected Symptomatic": [("recovered", 1)],
            "quarantined":[("susceptible", 1)],
            "recovered":[("susceptible", 0.5), ("recovered", 1)],
            # the probability og ghost is not required but its safe to put it in
            "ghost": [("ghost", 1)],
        },

        # QUARANTINE
        "quarantineSamplingProbability" : 0,
        "walkinProbability":0,#0.90,
        "quarantineSampleSize" : 200,
        "quarantineSamplePopulationSize":0.10,
        "quarantineRandomSubGroup": True,
        "closedBuildings": ["eating", "gym", "study"],
        "quarantineOffset": 1*24+9,
        "quarantineInterval": 24*1,
        "falsePositive":0.01,
        "falseNegative":0.10,
        
        # OTHER parameters
        "transitName": "transit_space_hub",
        # change back to 0.001
        "offCampusInfectionP":0.125/700,
        "trackLocation" : ["_hub"],
        "interventions":[3],
    }
    # you can control for multiple interventions by adding a case:
    #  [(modified attr1, newVal), (modified attr2, newVal), ...]
    simulationControls = [
        [(None, None)], # base case
        [("quarantineSamplingProbability", 0.03)], # case 1
        [("quarantineSamplingProbability", 0.1)],
        [("quarantineSamplingProbability", 0.5)],
    ]
    R0_controls = [("infectionSeedNumber", 10),("quarantineSamplingProbability", 0),
                    ("walkinProbability", 0),("quarantineOffset", 20*24), ("interventions", [])]
    simpleCheck(modelConfig, days=100, visuals=True)
    #R0_simulation(modelConfig, R0_controls,1, debug=True)
    return
    
    #createdFiles = initializeSimulations(simulationControls, modelConfig, True)
    #simulateAndPlot(createdFiles, 5, 800)
  

def agentFactory(agent_df, slotVal):
    """
        factory function used to dynamically assign __slots__, creates agents from the given df
        the values stored in __slots__ are the column of the df and some additional parameters that deals with relatinships and membership

        Parameters:
        - agent_df: a panda dataframe with each row corresponding to an agent's initial value
        - slotVal: the column values of the dataframe
    
    """
    class Agents:
        """
            creates an agent that moves between rooms and interacts with each other (indirectly)
        """
        #__slot__ = ["name", "age", "gender", "immunity", "curr_location", "state", "archetype", "personality"]
        __slots__ = slotVal
        def __init__(self, agentParam):
            for slot, value in zip(self.__slots__, agentParam):
                self.__setattr__(slot, value)

        def updateLoc(self, currTime, adjDict):
            """
                change agent's state, either moving or stationary,
                look at adjacent rooms and move to one of the connected rooms

                Parameters:
                currTime: the current time
                adjDict: the adjacency dictionary, (key: roomId, value: list of roomsId of rooms connected to the key)    
            """
            curr_room = self.currLocation
            
            if self.motion == "stationary" and currTime >= self.arrivalTime:
                
                if True: #purly deterministic 
                    self.destination = self.checkschedule(currTime)
                    
                    nextNode,lastNode  = adjDict[curr_room][0][0], adjDict[self.destination][0][0] 
                 
                    if curr_room == self.destination:
                        self.path = []
                    elif nextNode == lastNode: # moving between the same superstructure
                        self.path = [nextNode]
                    else: # required to move across the transit hub
                        self.path = [lastNode, self.transit, nextNode] 
                    
                    self.move(adjDict)
            elif self.motion == "moving" and currTime >= self.travelTime + self.arrivalTime:
                
                self.move(adjDict)
                self.arrivalTime = currTime
            else: 
                
                return (self.currLocation, self.currLocation)
            return (curr_room, self.currLocation)

        def checkschedule(self, currTime):
            """
                check the current time and return the value stored in the shcedule

                Parameters:
                - currTime: current time, used to find the schedule item
            
            """
            # there are 24*7 hours in a week
            # currTime%24*7 will give you the time in terms of week, then // 24 give you days
            # if the value is greater than 5, then its a weekday
            # if currTime is odd, then its a odd day and vise versa with even days

        
            dayOfWeek = (currTime%(24*7))//24
            hourOfDay = currTime%24
            if self.state == "quarantined":
                return self.initial_location
            if dayOfWeek > 5: # its a weekend
                return self.schedule[2][hourOfDay]
            elif dayOfWeek & 1: # bit and, its an odd day
                return self.schedule[1][hourOfDay]
            else: # its an even day
  
                return self.schedule[0][hourOfDay]

        def move(self, adjDict):
            """
                chooses the random room and moves the agent inside
            """
            pastLocation = self.currLocation
            if self.destination in [a[0] for a in adjDict[self.currLocation]]:
                # the agent reached it's destination, takes a rest
                
                self.currLocation = self.destination
                self.destination = None
                self.path = []
                self.motion = "stationary"
            elif self.path == []:
                pass #no change
            else: #the path array is not empty, the agent is still moving
                self.motion = "moving"
                self.currLocation = self.path.pop()
                self.travelTime = 0
            return (pastLocation, self.currLocation)
   
        def changeState(self, updateTime, stateName, durration):
            """
                Change the state of the agents, all states have a minimum waiting time,
                and changing state durring that waiting period is not recommended, because it defeats the purpose
            
                If the current state can evolve unexpectedly, then set durration to 0 and use a random value to determine if the state should change.
                Negative value for durration means the state will persist on to infinity
            
                Parameters:
                - updateTime: the time when the state was updated
                - stateName: the name of the start to transition to 
                - infected: bool that tells if the agent was infected or not
                - durration: the minimum time required to wait until having the choice of chnaging states
            """
            self.lastUpdate = updateTime
            self.statePersistance = durration
            self.state = stateName
            if stateName in ["exposed", "infected Asymptomatic0", "infected Asymptomatic1", "infected Symptomatic"]:

                self.infected = True
        
        def transitionTime(self):
            """
                return the time that that the agent can change state,
                since the agent is looking at his "clock", the returned time could be off from the global time, can be used for comas (if those states are implimented)
            """
            return self.lastUpdate + self.statePersistance

        def __repr__(self):
            repr_list = [val for val in self.__slots__]
            return repr_list.join() 
        
        def __str__(self):
            repr_list = [val for val in self.__slots__]
            return repr_list.join() 

    # creates the agents and put them in a dictionary
    tempDict = dict()
    for index, row in agent_df.iterrows():
        tempDict[index] = Agents(row.values.tolist())
    return tempDict

def SuperStructBuilder():
    pass

def roomFactory(room_df, slotVal):
    """
        meta function used to dynamically assign __slots__

        Parameters:
        - agent_df: a panda dataframe with each row corresponding to a room's initial value
        - slotVal: the column values of the dataframe
    """
    class Partitions:
        __slots__ = slotVal
        def __init__(self, roomParam):
            for slot, value in zip(self.__slots__, roomParam):
                self.__setattr__(slot, value)

        def enter(self, agentId):
            """ a put the id of the agent that entered the room"""
            if self.checkCapacity():
                self.agentsInside.append(agentId)

        def checkCapacity(self):
            """return a boolean, return True if theres capacity for one more agent, False if the room is at max capacity 
            """
            
            if len(self.agentsInside) < int(self.capacity):
                return True
            return False
    
        def leave(self, agentId):
            """ remove the id of the agent that exited the room"""
            if agentId in self.agentsInside:
                self.agentsInside.remove(agentId)
        
    tempDict = dict()
    for index, row in room_df.iterrows():
        tempDict[index] = Partitions(row.values.tolist())
    return tempDict
    
def superStrucFactory(struc_df, slotVal):
    """
        creates and returns a dictionary that keeps the building class
    
        Parameters:
        - agent_df: a panda dataframe with each row corresponding to an buildings's initial value
        - slotVal: the column values of the dataframe
    """
    class Superstructure: # buildings
        __slots__ = slotVal
        def __init__(self, strucParam):
            for slot, value in zip(self.__slots__, strucParam):
                self.__setattr__(slot, value)

    temp_dict = dict()
    for index, row in struc_df.iterrows():
        temp_dict[index] = Superstructure(row.values.tolist())
    return temp_dict
        
class AgentBasedModel:
    def __init__(self):
        """
        starts an instance of an agent based model,
        agents and a network is not added at this point
        """
        self.time = 0
        self.storeVal = False
        self.directedGraph = False
        self.randSchedule = False
        self.intervention1 = False
        self.hybridIntervention = False
        self.quarantineIntervention = False
        self.closedLocation = []
        self.buildingClosure = False
        self.officeHours = True
        self.debug=True
        self.R0 = False
        self.R0_agentId = -1
   
    def configureDebug(self, debugBool):
        self.debug=debugBool
        
    def loadAgent(self, fileName, folderName="configuration"):
        self.agent_df = flr.make_df(folderName, fileName)
    
    def loadBuilder(self, filename, folderName="configuration"):
        """use a builder to make the dataframe for the buiulding and rooms"""
        self.building_df, self.room_df = mod_df.mod_building(filename, folderName)
    
    
    
    # takes 4 seconds
    def studentFacultySchedule(self):
        schedules, onVsOffCampus = schedule_students.scheduleCreator()
        fac_schedule = schedule_faculty.scheduleCreator()
        roomIds = self.findMatchingRooms("building_type", "classroom")
        
        # replace entries like (48, 1) --> 48
        for index, faculty_sche in enumerate(fac_schedule):
            fac_schedule[index] = [[roomIds[a] if isinstance(a, int) else a for a in row] for row in faculty_sche]
        
        for index, student_schedule in enumerate(schedules):
            schedules[index] = [[roomIds[a[0]] if isinstance(a[0], int) else a for a in row] for row in student_schedule]
       

        onCampusIndex = 0
        offCampusIndex = 0
        facultyIndex = 0
        offCampusSchedule = [] 
        onCampusSchedule = []
        for schedule, onOffDistinction in zip(schedules, onVsOffCampus):
            if onOffDistinction == "Off":
                offCampusSchedule.append(schedule)
            else:
                onCampusSchedule.append(schedule)
        for agentId, agent in self.agents.items():
            if agent.archetype == "student": # needs to be for students
                if agent.Agent_type == "onCampus":
                    agent.schedule = onCampusSchedule[onCampusIndex]
                    onCampusIndex+=1
                else:
                    agent.schedule = offCampusSchedule[offCampusIndex]
                    offCampusIndex+=1
            else:# this is for faculty
                agent.schedule = fac_schedule[facultyIndex] 
                facultyIndex+=1
        #print(f"there are {len(schedules)} agent's schedule with {num_of_entry} entries")
        # finished assigning schedule to each agent
        self.replaceScheduleEntry("sleep") # this gets rid of "sleep"
        self.replaceScheduleEntry("Off") #this gets rid of "off"
        self.replaceScheduleEntry("dorm")
        self.replaceByType(partitionTypes=["library", "dining","gym", "office", "social"])
        
   
    def replaceByType(self, agentParam=None, agentParamValue=None, partitionTypes=None):
        """
        go over the schedules of the agents of a specific type and convert entries in their schedules

        Parameters:
        - agentParam: a string of the attribute name
        - agentParamValue: the value of the agentParam attribute, filter agents with this value and apply the replace function
        - SuperStrucType: a string to replace 
        """
        # filter rooms with specific value for building_type, returned roomIds dont include hub ids
        index = 0
        if not isinstance(partitionTypes, list): # if only one value is passed\
            if agentParam != None and agentParamValue != None:
                filteredId = [agentId for agentId, agent in self.agents.items() if getattr(agent, agentParam) == agentParamValue]
            else: filteredId = list(self.agents.keys())
            roomIds = self.findMatchingRooms("building_type", partitionTypes) 
            randomVec = np.random.choice(roomIds, size=len(self.agents), replace=True)
            for agentId in filteredId:
                for i, row in enumerate(self.agents[agentId].schedule):
                    for j, item in enumerate(row):
                        if item == partitionTypes:
                            self.agents[agentId].schedule[i][j] = randomVec[index]
                index +=1
        else: # if a list of values is passed
            print("here")
            def indexVal(listObj, obj):
                try:
                    return listObj.index(obj)
                except ValueError:
                    return -1
            if agentParam != None and agentParamValue != None:
                filteredId = [agentId for agentId, agent in self.agents.items() if getattr(agent, agentParam) == agentParamValue]
            else: filteredId = list(self.agents.keys())
            
            partitionIds = [self.findMatchingRooms("building_type", partitionType)  for partitionType in partitionTypes]
            agentCount = len(self.agents)
            randRoomIds = [np.random.choice(idList, size=agentCount, replace=True) for idList in partitionIds]

            for agentId in filteredId:
                for i, row in enumerate(self.agents[agentId].schedule):
                    for j, item in enumerate(row):
                        indx = indexVal(partitionTypes, item) 
                        if  indx != -1:
                            self.agents[agentId].schedule[i][j] = randRoomIds[indx][index]
                
                index+=1
        
    def replaceScheduleEntry(self, antecedent):
        for agentId, agent in self.agents.items():
            agent.schedule = [[a if a != antecedent else agent.initial_location for a in row] for row in agent.schedule] 

   
    def initializeWorld(self):
        """
            initialize the world with default value, 
            also unpacks dataframe and make the classes 
        """
        # add a column to store the id of agents or rooms inside the strucuture
        
        # these are required values added to the df so that they can be used to store information and relationships 
        self.addToDf()
        print("*"*20)
        
        self.adjacencyDict = self.makeAdjDict()
        self.buildings = self.makeClass(self.building_df, superStrucFactory)
        self.rooms = self.makeClass(self.room_df, roomFactory)
        # a dictionary (key: buildingID, value: [roomID in the building])
        self.roomsInBuilding = dict((buildingId, []) for buildingId in self.buildings.keys())
        # a dictionary (key: buildingName, value: building ID)
        self.buildingNameId = dict((getattr(building, "building_name"), buildingId) for buildingId, building in self.buildings.items())
        # a dictionary (key: roomName, value: room ID)
        self.roomNameId = dict((getattr(room, "room_name"), roomId) for roomId, room in self.rooms.items())
        # initialize a transit hub
        self.setTransitHub()
        self.configureOffcampus()
        # add rooms to buildings 
        self.addRoomsToBuildings()
        # create agents
        self.agents = self.makeClass(self.agent_df, agentFactory)
      
        for agentId, agent in self.agents.items():
            agent.agentId = agentId
        

    def addToDf(self):
        """add columns to dataframe before object creation, mainly because objects in this code use __slots__,
         __slots__ prevents the addition of attributes after instance creation, hence required to define them before creation"""
        keyList = list(self.config["extraParam"].keys())
        keyZipList = list(self.config["extraZipParam"].keys())
        for dfRef, keyStr in zip([self.agent_df, self.room_df, self.building_df], ["Agents", "Rooms", "Buildings"]):
            # assign 0 as default value:
            if keyStr in keyList:
                for attrName in self.config["extraParam"][keyStr]:
                    dfRef[attrName] = 0
            # assigned default value
            if keyStr in keyZipList:
                for (attrName, attrVal) in self.config["extraZipParam"][keyStr]:
                    dfRef[attrName] = attrVal

    def startInfectionAndSchedule(self):
        self.initialize_infection()
        self.studentFacultySchedule()
        self.InitializeIntervention(self.config["interventions"])


    def configureOffcampus(self):
        offcampus = self.roomNameId["offCampus_hub"] 
        
        self.offCampusHub = offcampus
   
    def setTransitHub(self):
        """
        fix a transit hub, used for inter-building travel
        """
        transitId = self.roomNameId[self.config["transitName"]]
        self.transitHub = transitId
        self.agent_df["transit"] = transitId

    def agentAssignBool(self, percent = 0, attrName="officeAttendee", replacement=False):
        """Assign True or false to Agent's office attend boolean value """
        # check if its a decimal or probability
        if percent > 1: percent/=100
        size = int(len(self.agents) * percent)
        sample = np.random.choice(list(self.agents.keys()), size=size, replace=replacement)
        sample_compliment = list(set(self.agents.keys()) - set(sample))
        for index in sample:
            setattr(self.agents[index], attrName,True)
        for index in sample_compliment:
            setattr(self.agents[index], attrName, False)

    def addRoomsToBuildings(self):
        """add room_id to associated buildings"""
        for roomId, rooms in self.rooms.items():
            self.roomsInBuilding[self.buildingNameId[rooms.located_building]].append(roomId)      

    def generateAgentFromDf(self, counterColumn="totalCount"):
        """
        use this to multiple the number of agents, multiplies by looking at the counterColumn
        Expand the dataframe along the counterColumn 

        """
        slotVal = self.agent_df.columns.values.tolist()
        if counterColumn in slotVal:
            slotVal.remove(counterColumn)
        tempList = []
        for _, row in self.agent_df.iterrows():
            counter = row[counterColumn]
            rowCopy = row.drop(counterColumn).to_dict()
            tempList+=[rowCopy for _ in range(counter)]
        self.agent_df = pd.DataFrame(tempList)     
        
    def findR0(self):
        self.R0 = True
        self.R0_agentId = [agentId for agentId, agent in self.agents.items() if agent.state != "susceptible"][0]
        print("running R0 calculation")
        self.R0_counter = 0
        self.uniqueIds = set()
    
    def returnR0(self):
        print("*"*20, "total", len(self.uniqueIds), self.uniqueIds)
        return self.R0_counter

    def R0Increase(self, roomId, totalInfection):
        room = self.rooms[roomId]
        #print(f"at time {self.time}, in {(roomId, room.room_name)}, 1 got infected by the comparison randomValue < {totalInfection}. Kv is {room.Kv}, limit is {room.limit},  {len(room.agentsInside)} people in room ")
        self.R0_counter+=1

    def initializeAgents(self):
        """
            change the agent's current location to match the initial condition
        """
        # convert agent's location to the corresponding room_id and add the agent's id to the room member
        # initialize
        print("*"*20)
        for rooms in self.rooms.values():
            rooms.agentsInside = []
        # building_type
        bType_RoomId_Dict = dict()
        for buildingId, building in self.buildings.items():
            # get all rooms that dont end with "_hub"
            buildingType_roomId = [roomId for roomId in self.roomsInBuilding[buildingId] if not self.rooms[roomId].room_name.endswith("_hub")]
            bType_RoomId_Dict[building.building_type] = bType_RoomId_Dict.get(building.building_type, []) + buildingType_roomId

        for agentId, agent in self.agents.items():
            initialLoc = getattr(agent, "initial_location")
            if initialLoc in self.roomNameId.keys(): # if the room is specified
                # convert the location name to the corresponding id
                location = self.roomNameId[initialLoc]
            elif initialLoc in self.buildingNameId.keys(): # if location is under building name
                # randomly choose rooms from the a building
                possibleRoomsIds = self.roomsInBuilding[self.buildingNameId[initialLoc]]
                possibleRooms = [roomId for roomId in possibleRoomsIds if self.rooms[roomId].checkCapacity() and not self.rooms[roomId].room_name.endswith("_hub")]
                location = np.random.choice(possibleRooms)
            elif initialLoc in bType_RoomId_Dict.keys(): # if location is under building type
                possibleRooms = [roomId for roomId in bType_RoomId_Dict[initialLoc] if self.rooms[roomId].checkCapacity()]
                location = np.random.choice(possibleRooms)
            else:
                print("something wrong")
                # either the name isnt properly defined or the room_id was given
                pass
            agent.currLocation = location
            agent.initial_location = location
            self.rooms[location].agentsInside.append(agentId)
    
    def extraInitialization(self):
        self.globalCounter = 0
        self.R0_interactions = 0
        self.R0_visits = []

    def makeSchedule(self):
        """
            part 1, dedicate a class to rooms
            create schedules for each agents
        """
        
        self.numAgent = len(self.agents.items())
        archetypeList = [agent.archetypes for agent in self.agents.values()]
        classIds = list(roomId for roomId, room in self.rooms.items() if room.building_type == "classroom" and not room.room_name.endswith("hub"))
        capacities = list(self.rooms[classId].limit for classId in classIds)
        self.scheduleList = schedule.createSchedule(self.numAgent, archetypeList,classIds,capacities)
        self.replaceStaticEntries("sleep")

    def checkFaculty(self):
        """
        an abstract reprsentation of professors meeting with students,
        People meet with proffesors and the pair might get infected 
        """
        for roomId, room in self.rooms.items():
            # this only happens in classrooms
            if len(self.rooms[roomId].agentsInside) > 0 and room.building_type == "classroom":
                # get the ids of faculty
                faculty = [agentId for agentId in self.rooms[roomId].agentsInside 
                        if "faculty" in self.agents[agentId].Agent_type] 
                # if faculty are in the system(partition)
                if len(faculty) > 0:
                    non_faculty = [agentId for agentId in self.rooms[roomId].agentsInside 
                                    if self.agents[agentId].officeAttendee and agentId not in faculty]
                    # setting up the infection 
                    officeHourAgents = non_faculty+faculty
                    agentsOnsite = len(officeHourAgents)
                    baseP = self.config["baseP"]
                    randVec = np.random.random(len(faculty)*len(non_faculty))
                    # pairwise infection happening
                    for i, tup in enumerate(itertools.product(faculty, non_faculty)):
                        contribution = self.infectionWithinPopulation(tup)
                        if randVec[i] < (3*baseP*contribution)/agentsOnsite:
                            for agentId in tup:
                                if self.agents[agentId].state == self.config["sus"]:
                                    self.agents[agentId].changeState(self.time, self.config["exp"], self.config["transitionTime"]["exposed"])
    
    def printAgent(self):
        if self.agents[self.R0_agentId].state != "recovered":
            agentId = self.R0_agentId
            if self.agents[agentId].destination != None and self.agents[agentId].destination != 0:
                print(f"{self.time}: {self.agents[agentId].state} ({self.rooms[self.agents[agentId].currLocation].room_name} --> {self.rooms[self.agents[agentId].destination].room_name})")
            else:
                print(f"{self.time}:{self.agents[agentId].state} ({self.rooms[self.agents[agentId].currLocation].room_name} --> NA)")          
            
    def makeAdjDict(self):
        """
            creates an adjacency list implimented with a dictionary

            Parameters (implicit):
            - room's "connected_to" parameters
        """
        self.specialId = False
        adjDict = dict()
        for roomId, row in self.room_df.iterrows():
            adjRoom = self.room_df.index[self.room_df["room_name"] == row["connected_to"]].tolist()[0]
            travelTime = row["travel_time"]
            adjDict[roomId] = adjDict.get(roomId, []) + [(adjRoom, travelTime)]
            if not self.directedGraph:
                adjDict[adjRoom] = adjDict.get(adjRoom,[]) + [(roomId, travelTime)]
        return adjDict
    
    def makeClass(self, dfRef, func):
        """
        returns a dictionary with ID as Keys and values as the class object
        
        Parameters:
        - dfRef: the dataframe object
        - func: a referenece to the function used to create the class object 
        """
        slotVal = dfRef.columns.values.tolist()
        tempDict = func(dfRef, slotVal)
        numObj, objVal = len(tempDict), list(tempDict.values())
        className = objVal[0].__class__.__name__ if numObj > 0 else "" 
        if self.debug:
            print(f"creating {numObj} {className} class objects, each obj will have __slots__ = {slotVal}")
        return tempDict

    def findMatchingRooms(self, partitionAttr, attrVal=None, strType=False):
        """
            returns a list of room IDs that have a specific value for the roomAttr of its parameter
        
            Parameters:
            - roomParam: the attribute name
            - roomVal: the attribute value, if None, returns all room

            Parameters(might be removed):
            - strType (= False): if the value is a string or not, 
        """
        if attrVal==None: # return rooms without filters
            return [roomId for roomId, room in self.rooms.items() if not getattr(room, "room_name").endswith("hub")]
        if strType: # case insensitive
            return [roomId for roomId, room in self.rooms.items() if getattr(room, partitionAttr).strip().lower() == attrVal.strip().lower() and not getattr(room, "room_name").endswith("hub")]
        else:
            return [roomId for roomId, room in self.rooms.items() if getattr(room, partitionAttr) == attrVal and not getattr(room, "room_name").endswith("hub")]

    def convertToRoomName(self, idList):
        """
            for debugging/output purpose
            get a single row of 24 hour schedule and convert the ids to the corresponding room name 

            Parameters:
            - idList: a list that stores room ids
        """
        return [[self.rooms[roomId].room_name for roomId in row] for row in idList]
        
    def updateSteps(self, step = 1):
        
        for _ in range(step):
            self.time+=1
            # assign renewed schedule after specific time 
            #if self.time % (24*100) == 0:
            #    self.replaceScheduleValues()
            if  23 > self.time%24 > 6: 
                # update 4 times to move the agents to their final destination
                # 4 is the max number of updates required for moving the agents from room --> building_hub --> transit_hub --> building_hub --> room
                for _ in range(4):
                    self.updateAgent()
                    self.infection()
                self.infection()
                if self.officeHours: # remove office hours
                    self.checkFaculty()
            self.big_gathering()
            
            self.checkForWalkin()
            self.quarantine()
            
            self.storeInformation()
            self.logData()
            
    def big_gathering(self):
        
        if self.time%(24*7) == 0: # big gathering at sunday midnight
            
            agentIds = [agentId for agentId, agent in self.agents.items() if agent.gathering]
            if len(agentIds) < 50:
                return
            subsetA = np.random.choice(agentIds, size=random.randint(20,81), replace=False)
            subsetB = np.random.choice(agentIds, size=random.randint(20,81), replace=False)
            subsetC = np.random.choice(agentIds, size=random.randint(20,81), replace=False)
            totalSubset = list(set(list(subsetA)+list(subsetB)+list(subsetC)))
            transition = self.config["transitionTime"]
            transitionProbability = self.config["transitionProbability"]
            newly_infected = 0
            for subset in [subsetA, subsetB, subsetC]:
                randVec = np.random.random(len(subset))
                totalInfection = self.gathering_infection(subset)
                for index, agentId in enumerate(subset):
                    state = self.agents[agentId].state
                    if state == "susceptible" and randVec[index] < totalInfection: 
                        print("infected at aprty")
                        self.agents[agentId].changeState(self.time, "exposed", transition["exposed"])
                        newly_infected+=1

                        if self.R0: # if infection occured
                            self.R0Increase(roomId, totalInfection)
            counter = self.countWithinAgents(totalSubset, "susceptible")
            print(f"big gathering at day {self.time/24}, at the gathering there were {counter} healthy out of {len(totalSubset)} and {newly_infected} additionally infected agents,", totalInfection)

    def gathering_infection(self, subset):
        contribution = self.infectionWithinPopulation(subset)
        cummulativeFunc = (self.config["baseP"]*3*contribution)/len(subset)
        return cummulativeFunc

    def addKeys(self, tempDict):
         self.config = tempDict

    def startLog(self):
        """
            initialize the log, building, room and people in rooms
        """
        self.building_log = dict((key,[]) for key in self.buildings.keys())
        self.room_log = dict((key,[]) for key in self.rooms.keys())
        self.room_cap_log = dict((key,[]) for key in self.rooms.keys())

    def logData(self):
        # find total infected and add them to the room_log
        for roomId, room in self.rooms.items():
            total_infected = sum(self.countWithinAgents(room.agentsInside, stateName) for stateName in self.config["AgentPossibleStates"]["infected"])
            self.room_log[roomId].append(total_infected)
        
        # this is the total number of agents in the room
        for roomId, room in self.rooms.items():
            self.room_cap_log[roomId].append(len(room.agentsInside))

    def printLog(self):
        """
            print the logs, only for debug purpose
        """
        
        stationary = self.countAgents("stationary", attrName="motion")
        motion = self.countAgents("motion", attrName="motion")
        if self.debug:
            print(f"stationary: {stationary}, motion: motion {motion}")
        # print the schedule of agents with IDs 1~9
        
        # convert the log to 24 hour bits and get the daily activity
        timeInterval = 24
        maxDict = dict()
        scheduleDict = dict()
        for key, value in self.room_cap_log.items():
            buildingType = self.rooms[key].building_type 

            if len(value)%timeInterval !=0:
                remainder = len(value)%timeInterval
                value+=[0 for _ in range(timeInterval - remainder)]
            
            a = np.array(value).reshape((-1,timeInterval))
            maxDict[buildingType] = max(maxDict.get(buildingType, 0), max(value))
            scheduleDict[self.rooms[key].room_name] = a
        nodes = ["gym", "library", "offCampus", "social"]
        for node in nodes:
            if self.debug:
                for index, (key, value) in enumerate(scheduleDict.items()):
                    if node in key and not key.endswith("_hub") and index < 5:
                        print(key, value)
                for key, value in maxDict.items():
                    if node in key and not key.endswith("_hub"):
                        print(key, value)
        return maxDict
                
    def getRoomNames(self, listOfRoomsId):
        """ probably a duplicate function"""
        return list(self.rooms[roomId].room_name for roomId in listOfRoomsId)

    def updateAgent(self):
        """call the update function on each person"""
       
        # change location if the old and new location is different
        transit, offcampus = self.transitHub, self.offCampusHub
        offCampusNumber = len(self.rooms[self.offCampusHub].agentsInside)
        if offCampusNumber>0:
            infectedNumber = int(self.config["offCampusInfectionP"]*offCampusNumber) 
            infectedMask = np.concatenate([np.ones(infectedNumber, dtype=bool), np.zeros(offCampusNumber-infectedNumber, dtype=bool)])
            np.random.shuffle(infectedMask)
            infectedIndex = 0 
        for agentId, agent in self.agents.items():
            loc = agent.updateLoc(self.time, self.adjacencyDict)
            if loc[0] != loc[1]:
                if loc[0] == offcampus and loc[1] == transit:
                    if infectedMask[infectedIndex]:
                        agent.changeState(self.time, self.config["exp"],self.config["transitionTime"]["exposed"] )
                    infectedIndex+=1
                self.rooms[loc[0]].leave(agentId)
                self.rooms[loc[1]].enter(agentId)
                
    def initialize_infection(self):
        """
            iniitilize the infection, start people off as susceptible
        """
        for agent in self.agents.values():
            # negative value for durration means the state will persist on to infinity
            agent.changeState(self.time, self.config["sus"], -1)
        seedNumber = self.config["infectionSeedNumber"]
        seededState = self.config["infectionSeedState"]
        infectedAgentIds = np.random.choice(list(self.agents.keys()),size=seedNumber)
        for agentId in infectedAgentIds:
            #print("agent infected")
            self.agents[agentId].changeState(self.time, seededState, self.config["transitionTime"][seededState])
        debugTempDict = dict()
        for agentId in infectedAgentIds:
            debugTempDict[self.agents[agentId].Agent_type] = debugTempDict.get(self.agents[agentId].Agent_type, 0) + 1
        print(f"{seedNumber} seeds starting off with {seededState}, {debugTempDict.keys()}")
        

    def infection(self):
        """
            the actual function that takes care of the infection
            goes over rooms and check if an infected person is inside and others were infected
        """
        # time it takes to transition states, negative means, states doesnt change
        if 23 > self.time%24 > 7:
            transition = self.config["transitionTime"]
            transitionProbability = self.config["transitionProbability"]
            randVec = np.random.random(len(self.agents))
            
            for roomId, room in self.rooms.items():
                if room.building_type != "offCampus":
                    totalInfection = self.infectionInRoom(roomId)
                    for index, agentId in enumerate(room.agentsInside):
                        state = self.agents[agentId].state
                        if self.R0 and agentId == self.R0_agentId:
                            if not room.room_name.endswith("_hub") and room.building_type != "dining":
                                old_sets = set(self.uniqueIds)
                                for ids in room.agentsInside:
                                    self.uniqueIds.add(ids)
                                if old_sets != self.uniqueIds:
                                    print("*"*20, room.room_name, len(room.agentsInside))
                    
                        if state == "susceptible" and randVec[index] < totalInfection: 
                            self.agents[agentId].changeState(self.time, "exposed", transition["exposed"])
                            #print(f"at time {self.time}, in {(roomId, room.room_name)}, 1 got infected by the comparison randomValue < {totalInfection}. Kv is {room.Kv}, limit is {room.limit},  {len(room.agentsInside)} people in room ")
                            if self.R0: # if infection occured
                                self.R0Increase(roomId, totalInfection)
                        elif self.agents[agentId].transitionTime() < self.time and state == "quarantined" and not self.agents[agentId].infected:
                            # go back to the susceptible state, because the agent was never infected, just self isolated
                            print("quar to susc")
                            self.agents[agentId].changeState(self.time, "susceptible", transition["susceptible"])     
                        elif self.agents[agentId].transitionTime() < self.time and state != "quarantined" and state != "susceptible" and transition[state] > 0:
                            # the agent can change state
                            cdf = 0
                            if self.R0_agentId == agentId and self.agents[agentId].state == "exposed":
                                tup = transitionProbability[state][0]
                                self.agents[agentId].changeState(self.time,tup[0] ,transition[tup[0]] )
                            else:
                                for tup in transitionProbability[state]:
                                    if tup[1] > randVec[index] > cdf:
                                        cdf+=tup[1]
                                        nextState = tup[0]
                                self.agents[agentId].changeState(self.time, nextState, transition[nextState])
                             

    def infectionInRoom(self, roomId):
        contribution = self.infectionWithinPopulation(self.rooms[roomId].agentsInside)
        if self.rooms[roomId].building_type == "social": # check fo rdivision by zero
            if len(self.rooms[roomId].agentsInside) == 0:
                return 0
            cummulativeFunc = (self.config["baseP"]*self.rooms[roomId].Kv*contribution)/len(self.rooms[roomId].agentsInside)
        else:
            cummulativeFunc = (self.config["baseP"]*self.rooms[roomId].Kv*contribution)/self.rooms[roomId].limit
        return cummulativeFunc

    def infectionWithinPopulation(self, agentIds):
        contribution = 0
        for agentId in agentIds:
            lastUpdate = self.agents[agentId].lastUpdate
            compliance = self.agents[agentId].compliance
            contribution+= self.infectionContribution(agentId, lastUpdate)
            if compliance and self.intervention1 and self.time > self.intervention1_startTime:
                contribution*= self.maskP
        return contribution

    def infectionContribution(self, agentId, lastUpdate):
        if (not self.R0) or (self.R0 and agentId == self.R0_agentId): 
            return self.config["infectionContribution"].get(self.agents[agentId].state, 0)
        return 0

    def countWithinAgents(self, agentList, stateVal, attrName="state"):
        return len(list(filter(lambda x: getattr(x, attrName) == stateVal, [self.agents[val] for val in agentList]))) 

    def countAgents(self, stateVal, attrName="state"):
        return len(list(filter(lambda x: getattr(x, attrName) == stateVal, self.agents.values() )))

    def printRelevantInfo(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this functio n will be converted to the proper format using __repr__"""
        stateList = ["susceptible", "exposed", "infected Asymptomatic0", "infected Asymptomatic1", "infected Symptomatic", "recovered", "quarantined"]
        num = [self.countAgents(state) for state in stateList]
        print(f"time: {self.time}, Sus {num[0]} E: {num[1]}, I Asympto: {num[2]}, IAsym: {num[3]}, I Sympto: {num[4]}, rec: {num[5]}, quar: {num[6]}, total states{sum(num)}")
    
    def initializeStoringParameter(self, listOfStatus, steps=10):
        """
            tell the code which values to keep track of. 
            t defines the frequency of keeping track of the information
        """
        self.storeVal = True
        self.timeIncrement = steps 
        self.parameters = dict((param, []) for param in listOfStatus)
        self.timeSeries = []

    def storeInformation(self):
        if self.storeVal and self.time%self.timeIncrement == 0:
            self.timeSeries.append(self.time)
            for param in self.parameters.keys():
                self.parameters[param].append(self.countAgents(param, attrName="state"))

    def returnStoredInfo(self):
        return self.parameters

    def visualOverTime(self):
        vs.timeSeriesGraph(self.timeSeries, (0, self.time+1), (0,len(self.agents)), self.parameters)
    
    def visualizeBuildings(self):
        pairs = [(room, adjRoom[0]) for room, adjRooms in self.adjacencyDict.items() for adjRoom in adjRooms]
        nameDict = dict((roomId, room.room_name) for roomId, room in self.rooms.items())
        vs.makeGraph(self.rooms.keys(), nameDict, pairs, self.buildings, self.roomsInBuilding, self.rooms)

    def getBuilding(self, buildingAttribute, attributeVal):
        return [buildingId for buildingId, building in self.buildings.items() if getattr(building, buildingAttribute) == attributeVal]

    def replaceScheduleVal(self, originalSchedule, changeVals, newVal, num):
        """takes in a list for changeVals"""
        new_schedule = [[item if item not in changeVals else newVal for item in rows] for rows in originalSchedule]
        return new_schedule

    def InitializeIntervention(self, InterventionId):
        for i in InterventionId:
            if i == 1:
                # face mask
                self.maskP = 0.8
                self.facemaskIntervention = True
                self.facemask_startTime = 0
            elif i == 2:
                # hybrid courses
                self.hybridIntervention = True
                self.initializeHybridClasses()
            elif i == 3:
                # test for covid and quarantine
                self.quarantineIntervention = True
                self.quarantineInterval = self.config["quarantineInterval"]
                self.startQuarantineGroup()
            elif i == 4:
                self.buildingClosure = True
                self.closedLocation = self.config["closedBuildings"]
            elif i == 5:
                self.officeHours = False

    def initializeHybridClasses(self):
        """ hybrid courses"""
        hybridprobabilities = [0.5, 0.5, 0.5]
        listOfAcademicBuilding = self.getBuilding("building_type", "classroom")
        
        sizeList = ["small", "medium", "large"]
        sizeRooms = [[] for _ in sizeList]
        for i, sizeStr in enumerate(sizeList):
            for buildingId in listOfAcademicBuilding:
                if self.buildings[buildingId].building_size == sizeStr:
                    sizeRooms[i]+=self.roomsInBuilding[buildingId]

        sample_size = [10, 10, 10]
        (small, medium, large) = sizeRooms
        changeVals = small + medium + large
        changeVals = list(set(changeVals))
        for agentId, agent in self.agents.items():
            agentHome = agent.initial_location
            agent.schedule = self.replaceScheduleVal(agent.schedule, changeVals, agentHome, agentId)

    def startQuarantineGroup(self):
        if self.config["quarantineRandomSubGroup"]: # do nothing if quarantine screening is with random samples from the population
            pass
        else: # the population is split in smaller groups and after every interval we cycle through the groups in order and screen each member in the group
            
            totalIds = set(self.agents.keys())
            size = len(self.agents)
            # the size of the group, if there's a remainder, then they all get grouped together
            QuarantineGroupSize = self.config["quarantineSampleSize"]
           
            self.groupIds = []
            while len(totalIds) > 0:
                sampleMinSize = min(len(totalIds), QuarantineGroupSize)
                if sampleMinSize < QuarantineGroupSize:
                    print("is smaller", sampleMinSize, QuarantineGroupSize)
                sampledIds = np.random.choice(list(totalIds), size=sampleMinSize,replace=False)
                totalIds -= set(sampledIds)
                self.groupIds.append(list(sampledIds))
            print(len(self.groupIds))
            self.quarantineGroupNumber = len(self.groupIds)
            self.quarantineGroupIndex = 0
    
    def final_check(self):
        spAgent = [agentId for agentId, agent in self.agents.items() if agent.state == "quarantined"]
        printArr = [self.agents[agentId].transitionTime for agentId in spAgent]
        for i, obj in enumerate(printArr):
            if i < 100:
                print(obj)

    def quarantine(self):
        if self.quarantineIntervention and self.time%self.quarantineInterval == 0 and self.time > self.config["quarantineOffset"]: 
            if self.config["quarantineRandomSubGroup"]: # if random
                print("cycle1")
                listOfId = np.random.choice(list(self.agents.keys()), size=self.config["quarantineSampleSize"], replace=False)
                size = len(listOfId)
            else: # we cycle through groups to check infected
                print("cycle2")
                listOfId = self.groupIds[self.quarantineGroupIndex]
                self.quarantineGroupIndex = (self.quarantineGroupIndex+1)% self.quarantineGroupNumber
                size = len(listOfId)
          
            fpCounter = 0
            quarCounter = 0
            transition = self.config["transitionTime"]
            

            falsePositiveMask = np.random.random(len(listOfId))
            falsePositive = [agentId for agentId, prob in zip(listOfId, falsePositiveMask) if prob < self.config["falsePositive"]]
            normalScreeningId = list(set(listOfId) - set(falsePositive))
            if self.R0 and self.R0_agentId in listOfId:
                    for ids in listOfId:
                        self.uniqueIds.add(ids)
                    print("*"*20, "social gathering", len(listOfId))
            # these people had false positive results and are quarantined
            for agentId in falsePositive:
                fpCounter+=1
                self.agents[agentId].changeState(self.time,self.config["qua"],transition["quarantined"] )
            falseNegVec = np.random.random(len(normalScreeningId))
            # these are people who are normally screened
            for i, agentId in enumerate(normalScreeningId):
                # if infected
                if self.agents[agentId].state in self.config["AgentPossibleStates"]["infected"]:
                    if falseNegVec[i] > self.config["falseNegative"]:
                        quarCounter+=1
                        self.agents[agentId].changeState(self.time, self.config["qua"], transition["quarantined"])
            #print("quararntined", quarCounter, "out of", len(normalScreeningId),"quarantined", fpCounter, "false positive results")

    def checkForWalkin(self):
        if self.time%24 == 10 and False:
            for agentId, agent in self.agents.items():
                if agent.state == "infected Symptomatic" and agent.lastUpdate+25 > self.time:
                    # with some probability the agent will walkin
                    tupP = np.random.random(3) # (P of walking in, P for false neg, P for false Pos)
                    if tupP[0] < self.config["walkinProbability"]: # walkin
                        if tupP[1] < self.config["falseNegative"]:
                            pass
                        # theres no false negative because we assume all walkins are infected
                        elif tupP[2] < self.config["falsePositive"]:
                            agent.changeState(self.time, self.config["qua"], self.config["transitionTime"]["quarantined"])
                        else:
                            agent.changeState(self.time, self.config["qua"], self.config["transitionTime"]["quarantined"])

if __name__ == "__main__":
    main()    


