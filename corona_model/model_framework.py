import os
import random
import pandas as pd
import pickle
import fileRelated as flr
import numpy as np
import bisect
import numpy as np
import visualize as vs
import modifyDf as mod_df
import schedule
import time
import copy
import itertools
import statfile

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
    for n in range(simulationN):
        model = flr.loadUsingDill(pickleName)
        print("loaded pickled object successfully")
        model.configureDebug(False)
        model.initilize_infection()
        model.makeSchedule()
        model.initializeRandomSchedule()
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
        print(f"{i/totalcases*100}% cases finished")
        outcomes.append(runSimulation(name,simulationN, runtime))
        print((f"took {time.time()-t0} time to finish{(i+1)/totalcases*100}%"))
    print(f"took {time.time()-t0} time to run {totalcases*simulationN} simulations")
    statfile.plotBoxAverageAndDx(outcomes)

def initializeSimulations(simulationControls, modelConfig, fileLoc, pickleBaseName="pickleModel_"):
    """
        create the initialized model for each controlled experiment
    """
    createdNames = []
    for i, independentVariables in enumerate(simulationControls):
        pickleName = pickleBaseName+str(i)
        pickleName = flr.fullPath(pickleName+".pkl", "picklefile")
        if independentVariables[0][0] == None: # base model
            model = createModel(modelConfig, fileLoc)
        else: # modify the data
            # the following copy of the model config is a shallow copy, 
            # if you want to modify a dict in the config, then use deep copy 
            configCopy = dict(modelConfig)
            for variableTup in independentVariables:
                configCopy[variableTup[0]] = variableTup[1]
            model = createModel(configCopy, fileLoc)
        flr.saveUsingDill(pickleName, model)
        createdNames.append(pickleName)
    print("copy the following list and put in in as a parameter")
    print(createdNames)
    return createdNames

def createModel(modelConfig, fileLoc):
    model = AgentBasedModel()
    model.addKeys(modelConfig)
    model.loadDefaultData(fileLoc)
    model.loadBuilder("newBuilding.csv")
    model.loadAgent("newAgent.csv")
    model.generateAgentFromDf()
    model.initializeWorld()
    model.startLog()
    model.initializeAgents()
    model.agentAssignBool(0.2, attrName="compliance")
    model.agentAssignBool(0.2, attrName="officeAttendee")
    
    return model

def simpleCheck(modelConfig, fileLoc):
    loadDill = False
    saveDill = False
    pickleName = flr.fullPath("coronaModel.pkl", "picklefile")
    if not loadDill:
        model = createModel(modelConfig, fileLoc)
        if saveDill:
            flr.saveUsingDill(pickleName, model)
            # save an instance for faster loading
            return 0
    else:
        model = flr.loadUsingDill(pickleName)
        print("loaded pickled object successfully")
    model.configureDebug(False)
    model.initilize_infection()
    # make schedules for each agents, outside of pickle for testing and for randomization
    model.makeSchedule()
    model.initializeRandomSchedule()
    
    #model.onetime_check()
    #model.start_intervention([1, 2, 3])
    model.initializeStoringParameter(["susceptible","exposed", "infected Asymptomatic0", "infected Asymptomatic1" ,"infected Symptomatic", "recovered", "quarantined"], 
                                        steps=1)
    model.printRelevantInfo()
    
    #return 
    for i in range(10):
        model.updateSteps(10)
        model.printRelevantInfo()
    model.printLog()
    
    model.visualOverTime()
    #model.visualizeBuildings()

def R0_simulation(modelConfig, fileLoc, R0Control, simulationN=10):
    infA0 = "infected Asymptomatic0"
    infA1, infS, rec = "infected Asymptomatic1", "infected Symptomatic", "recovered"
    R0List = []
    configCopy = dict(modelConfig)
    for variableTup in R0Control:
        configCopy[variableTup[0]] = variableTup[1]
    # base model
    model = createModel(configCopy, fileLoc)
    model.configureDebug(False)
    model.initilize_infection()
    model.findR0()
    days = 20
    for i in range(simulationN):
        new_model = copy.deepcopy(model)    
        new_model.makeSchedule()
        new_model.initializeRandomSchedule()
        new_model.initializeStoringParameter([infA0, infA1, infS, rec], steps=1)
        print("starting model")
        for _ in range(days):
            new_model.updateSteps(24)
        sampleR0 = new_model.returnR0()
        R0List.append(sampleR0)
        print(f"finished {i/simulationN*100}% of cases")
    print("R0 is", R0List)
    data = statfile.analyzeData(R0List)
    pickleName = flr.fullPath("R0Data.pkl", "picklefile")
    # save the data just in case
    flr.saveUsingDill(pickleName, R0List)
    print(data)
    print("(npMean, stdev, rangeVal, median)")
    statfile.boxplot(R0List,True, "R0 simulation", "cases", "infected people (R0)", ["base model"])
    


def main():
    """ the main function that starts the model"""
    # the "config" and "info" are different, config tells the code what values/range are allowed for a variable.
    # the info are the specific data for a specific instance of the class
    
    fileLoc = {
        "config_folder"     : "txt_config",
        "agent_config"      : "agent_config.txt",
        "room_config"       : "room_config.txt",
        "building_config"   : "building_config.txt",
        "schedule_config"   : "schedule_config.txt",
        
        "info_folder"       : "configuration",
        "agent_info"        : "agents.csv",
        "room_info"         : "rooms.csv",
        "building_info"     : "buildings.csv",
        "schedule_info"     : "schedules.csv",
    }

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
            "Agents": ["archetypes","path", "destination", "currLocation",
                        "statePersistance","lastUpdate", "personality", 
                        "arrivalTime", "schedule", "travelTime", "compliance", 
                        "officeAttendee"],
            "Rooms":  ["agentsInside", "oddCap", "evenCap", "classname"],
            "Buildings": ["roomsInside"],
        },
        "extraZipParam": {
            "Agents" : [("motion", "stationary")],
        },

        # INFECTION parameter
        "infectionSeedNumber": 20,
        # tested 1
        "baseP" : 4,
        "infectionSeedState": "exposed",
        "infectionContribution":{
            "infected Asymptomatic0":0.5,
            "infected Asymptomatic1":0.5,
            "infected Symptomatic":1,
        },
        "transitionTime" : {
            exp:2*24,
            infA0:2*24,
            infA1:8*24,
            infS:10*24,
            rec:-1,
            qua:24*14
        },
        "transitionProbability" : {
            exp: [(infA0, 0.75), (infA1, 1)],
            infA1: [(rec, 1)],
            infA0: [(infS, 1)],
            infS: [(rec, 1)],
            qua:[(sus, 1)],
            rec:[(sus, 0.5), (rec, 1)]
        },

        # QUARANTINE
        "quarantineSamplingProbability" : 0,
        "walkinProbability":0.95,
        "closedBuildings": ["eating", "gym", "study"],
        "quarantineOffset": 0*24,
        "quarantineInterval": 24*5,
        "falsePositive":0.01,
        "falseNegative":0.01,
        
        # OTHER parameters
        "transitName": "transit_space_hub",
        "offCampusInfectionP":0.01,
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
    R0_controls = [("infectionSeedNumber", 1),("quarantineSamplingProbability", 0),
                    ("walkinProbability", 0),("quarantineOffset", 20*24), ("interventions", [])]
    #simpleCheck(modelConfig, fileLoc)
    R0_simulation(modelConfig, fileLoc, R0_controls, 200)
    return
    createdFiles = initializeSimulations(simulationControls, modelConfig, fileLoc)
    
    #createdFiles = ['c:\\Projects\\modeling_in_python\\corona_model\\picklefile\\pickleModel_0.pkl', 'c:\\Projects\\modeling_in_python\\corona_model\\picklefile\\pickleModel_1.pkl', 
    #'c:\\Projects\\modeling_in_python\\corona_model\\picklefile\\pickleModel_2.pkl', 'c:\\Projects\\modeling_in_python\\corona_model\\picklefile\\pickleModel_3.pkl']
   
    simulateAndPlot(createdFiles, 2)

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
                        self.path = [nextNode, self.transit, lastNode] 
                    
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
                pass
                self.motion = "stationary"
            else: # the agent is still moving
                self.motion = "moving"
                self.currLocation = self.path.pop()
                self.travelTime = 0
            return (pastLocation, self.currLocation)
   
        def changeState(self, updateTime, stateName,durration):
            """
                Change the state of the agents, all states have a minimum waiting time,
                and changing state durring that waiting period is not recommended, because it defeats the purpose
            
                If the current state can evolve unexpectedly, then set durration to 0 and use a random value to determine if the state should change.
                Negative value for durration means the state will persist on to infinity
            
                Parameters:
                - updateTime: the time when the state was updated
                - stateName: the name of the start to transition to 
                - durration: the minimum time required to wait until having the choice of chnaging states
            """
            self.lastUpdate = updateTime
            self.statePersistance = durration
            self.state = stateName
        
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
            if len(self.agentsInside) < self.capacity:
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
        self.intervention2 = False
        self.intervention3 = False
        self.closedLocation = []
        self.buildingClosure = False
        self.officeHours = True
        self.debug=True
        self.R0 = False
        self.R0_agentId = -1
   
    def configureDebug(self, debugBool):
        self.debug=debugBool

    # initialization
    def loadDefaultData(self, files):
        """load the data in a csv and load it as a panda dataframe"""    
        self.building_df = flr.make_df(files["info_folder"], files["building_info"]) 
        self.room_df = flr.make_df(files["info_folder"], files["room_info"]) 
        self.agent_df = flr.make_df(files["info_folder"], files["agent_info"]) 
        self.schedule_df = flr.make_df(files["info_folder"], files["schedule_info"]) 
        # get the config of the individual components
    
    def loadDefaultConfig(self, files):
        """
        there is no use for this right now
        """
        self.agent_config = flr.loadConfig(files["config_folder"], files["agent_config"])
        self.room_config = flr.loadConfig(files["config_folder"], files["room_config"])
        self.building_config = flr.loadConfig(files["config_folder"], files["building_config"])
        self.schedule_config = flr.loadConfig(files["config_folder"], files["schedule_config"])
        
    def loadAgent(self, fileName, folderName="configuration"):
        self.agent_df = flr.make_df(folderName, fileName)
    
    def loadBuilder(self, filename, folderName="configuration"):
        """use a builder to make the dataframe for the buiulding and rooms"""
        self.building_df, self.room_df = mod_df.mod_building(filename, folderName)
    
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
    
     
    def initializeWorld(self):
        """
            initialize the world with default value, 
            also unpacks dataframe and make the classes 
        """
        # add a column to store the id of agents or rooms inside the strucuture
        
        # these are required values added to the df so that they can be used to store information and relationships 
        self.addToDf()
        print("*"*20)
        self.start_intervention(self.config["interventions"])
        self.adjacencyDict = self.makeAdjDict()
        self.buildings = self.makeClass(self.building_df, superStrucFactory)
        self.rooms = self.makeClass(self.room_df, roomFactory)
        # a dictionary (key: buildingID, value: [roomID in the building])
        self.roomsInBuilding = dict((buildingId, []) for buildingId in self.buildings.keys())
        # a dictionary (key: buildingName, value: building ID)
        self.buildingNameId = dict((getattr(building, "building_name"), buildingId) for buildingId, building in self.buildings.items())
        # a dictionary (key: buildingType, value: [Building ID of specific type])
        self.buildingTypeId = dict((getattr(building, "building_type"), buildingId) for buildingId, building in self.buildings.items())
        # a dictionary (key: roomName, value: room ID)
        self.roomNameId = dict((getattr(room, "room_name"), roomId) for roomId, room in self.rooms.items())
        # initialize a transit hub
        self.setTransitHub()
        self.configureOffcampus()
        # add rooms to buildings 
        self.addRoomsToBuildings()
        # create agents
        self.agents = self.makeClass(self.agent_df, agentFactory)
        # not used, but assign random personality to agents
        #self.randomPersonality()

    def configureOffcampus(self):
        offcampus = self.roomNameId["offCampus_hub"] 
        
        self.offCampusHub = offcampus
   

    def setTransitHub(self):
        """
        fix a transit hub, used for inter-building travel
        """
        transitId = self.roomNameId[self.config["transitName"]]
        self.transitHub = transitId

        #print("adj", self.adjacencyDict[transit_id])
        self.agent_df["transit"] = transitId

    def randomPersonality(self):
        """
            randomly assign a major and personality to the agents
        """

        personalities = ["athletic", "introvert", "party people", "people", "terminators", "aliens"]
        majors = ["math", "stem", "english", "humanities", "philosophy", "sleeping"]
        numAgent = len(self.agents)
        randPersonalities = np.random.choice(personalities, numAgent)
        randMajors = np.random.choice(majors, numAgent)
        for index, agent in enumerate(self.agents.values()):
            agent.personality = randPersonalities[index]
            agent.archetypes = randMajors[index]

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
        self.R0_counter = 0
    
    def returnR0(self):
        return self.R0_counter

    def initializeAgents(self):
        """
            change the agent's current location to match the initial condition
        """
        # convert agent's location to the corresponding room_id and add the agent's id to the room member
        capacity = 0
        for rooms in self.rooms.values():
            rooms.agentsInside = []
        
        tempList = []
      
        for agentId, agent in self.agents.items():
            
            initialLoc = getattr(agent, "initial_location")
            if initialLoc in self.roomNameId.keys(): # if the room is specified
                # convert the location name to the corresponding id
                location = self.roomNameId[initialLoc]
            elif initialLoc in self.buildingNameId.keys(): # if location is under building name
                # randomly choose rooms from the a building
                possibleRoomsIds = self.roomsInBuilding[self.buildingNameId[initialLoc]]
                possibleRooms = [roomId for roomId in possibleRoomsIds if self.rooms[roomId].checkCapacity()] #and not self.rooms[roomId].room_name.endswith("_hub")]
                location = np.random.choice(possibleRooms)
            elif initialLoc in self.buildingTypeId.keys(): # if location is under building type
                
                possibleRoomsIds = self.roomsInBuilding[self.buildingTypeId[initialLoc]]
                possibleRooms = [roomId for roomId in possibleRoomsIds if self.rooms[roomId].checkCapacity()] #and not self.rooms[roomId].room_name.endswith("_hub")]
              
                location = np.random.choice(possibleRooms)
           
            else:
                print("something wrong")
                # either the name isnt properly defined or the room_id was given
                pass
            agent.currLocation = location
            agent.initial_location = location
            self.rooms[location].agentsInside.append(agentId)
    
    def makeSchedule(self):
        """
            part 1, dedicate a class to rooms
            create schedules for each agents
        """
        
        self.numAgent = len(self.agents.items())
        archetypeList = [agent.archetypes for agent in self.agents.values()]
        classIds = list(roomId for roomId, room in self.rooms.items() if room.building_type == "classroom" and not room.room_name.endswith("hub"))
        capacities = list(self.rooms[classId].limit for classId in classIds)
        #classTypes = list(self.rooms[classId].ClassType for classId in classIds)
        # modify the following to blacklist or whitelist agents from rooms, then pass it to create scheudule
        """
        classDict = dict()
        for key in agentTypes:
            classDict[key] = {classKey: [cap, enrollment] for (classKey, cap, enrollment) in zip(classrooms, classCapacity, classEnrollment)}
        """
        # print class names
        #print([self.rooms[classId].room_name for classId in classIds])
        self.scheduleList = schedule.createSchedule(self.numAgent, archetypeList,classIds,capacities)
        self.replaceStaticEntries()
    
    def onetime_check(self):
        if self.debug:
            classList = []
            agentList = []
            for roomId, room in self.rooms.items():
                if room.building_type == "classroom":
                    classList.append(roomId)
            for agentId, agent in self.agents.items():
                if agent.Agent_type == "faculty":
                    agentList.append(agentId)
            print("classroom", classList)
            print("faculty", agentList)
            for i in range(2100, 2110):
                print(self.convertToRoomName(self.agents[i].schedule))
            mkey = max(self.agents.keys())
            print(self.convertToRoomName(self.agents[mkey].schedule))

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

    def replaceStaticEntries(self):
        """
        part 2
        replaces the static locations with the corresponding Ids
        """
        for i, agent in enumerate(self.agents.values()):
            self.scheduleList[i] = self.replaceEntry(self.scheduleList[i], "sleep", getattr(agent, "currLocation"))

    def initializeRandomSchedule(self,t=-1, agentTypes=[]):
        """
        random schedule part 1
        
        convert the entries that are not ids to locations that matches the id
        if t is negative then the randomization only happens once 
        """
        print("new scheduling")
        self.randSchedule = True if t < 0 else False 
        self.activityList = ["eating", "gym", "study", "off_campus"]
        self.buildingList = ["dining_hall", "gym", "library", "offCampus"]
        self.activityCount = schedule.countSchedule(self.scheduleList, self.activityList)
        self.activityLocList = [self.findMatchingRooms("building_type", loc) for loc in self.buildingList]
        self.randomSchedule = [np.random.choice(possibleLoc, size=self.activityCount[i], replace=True) 
                                for i, possibleLoc in enumerate(self.activityLocList)]
        self.agentTypeCount = dict()
        for agentType in agentTypes:
            self.agentTypeCount[agentType] = self.countAgents(agentType, "type")
        
        self.replaceScheduleValues()

    def replaceScheduleValues(self, agentTypes = []):
        """
            random schedule part 2
            if t = -1, then the scheudule doesnt change, 
            if t is greater than 0, then the schedule changes with that frequency 
        """
        self.randomSchedule = [np.random.choice(possibleLoc, size=self.activityCount[i], replace=True) 
                                for i, possibleLoc in enumerate(self.activityLocList)]
        indices = [0 for _ in range(len(self.activityLocList))]
        for scheduleIndex, agent in enumerate(self.agents.values()):
            scheduleChart = self.scheduleList[scheduleIndex]
            
            loc = agent.initial_location
            if self.buildingClosure: # takes care of 4.3
                for closedSpace in self.closedLocation:
                    scheduleChart = self.replaceEntry(scheduleChart, closedSpace, loc)
            # definitly rewrite
            # replace and randomize the rest
            for index, location in enumerate(self.randomSchedule):
                for i, row in enumerate(scheduleChart):
                    for j, item in enumerate(row):
                        if item == self.activityList[index]:
                            scheduleChart[i][j] = location[indices[index]]
                            indices[index]+=1
            
            agent.schedule = scheduleChart
            

    def replaceEntry(self, schedule, antecedent, replacement):
        """
            replace entry with a different value convert all antecedent to replacement
        
            Parameters:
            - schedule: the whole schedule( include A, B, W)
            - antecedent: the value to convert
            - replacement: the value to be converted to

        """
        return [[a if a != antecedent else replacement for a in row] for row in schedule]

    def makeAdjDict(self):
        """
            creates an adjacency list implimented with a dictionary

            Parameters (implicit):
            - room's "connected_to" parameters
        """
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

    def findMatchingRooms(self, roomParam, roomVal, strType=False):
        """
            returns a list of room IDs that have a specific value for one of its parameter
        
            Parameters:
            - roomParam: the attribute name
            - roomVal: the attribute value

            Parameters(might be removed):
            - strType (= False): if the value is a string or not, 
        """
        if strType: # case insensitive
            return [roomId for roomId, room in self.rooms.items() if getattr(room, roomParam).strip().lower() == roomVal.strip().lower() and not getattr(room, "room_name").endswith("hub")]
        else:
            return [roomId for roomId, room in self.rooms.items() if getattr(room, roomParam) == roomVal and not getattr(room, "room_name").endswith("hub")]

    def convertToRoomName(self, idList):
        """
            for debugging/output purpose
            get a single row of 24 hour schedule and convert the ids to the corresponding room name 

            Parameters:
            - idList: a list that stores room ids
        """
        return [[self.rooms[roomId].room_name for roomId in row] for row in idList]
        
    # update functions
    def updateSteps(self, step = 1):
        """ 
        a function that updates the time and calls other update functions, 
        you can also set how many steps to update
        
        paramters:
        - step: the number of steps to update states 
        """
        for _ in range(step):
            # add 1 to time
            self.time+=1
            # assign renewed schedule after specific time 
            if self.time % (24*100) == 0:
                self.replaceScheduleValues()
            # update 4 times to move the agents to their final destination
            # 4 is the max number of updates required for moving the agents from room --> building_hub --> transit_hub --> building_hub --> room
            
            
            for _ in range(4):
                self.updateAgent()
                if 22 > self.time%24 > 8:
                    self.infection()
                    
            # infection occurs between 8AM and 10PM
            if 22 > self.time%24 > 8:
                self.infection()
                if self.officeHours: # remove office hours
                    self.checkFaculty()
            if self.time%24 == 10:
                self.checkForWalkin()
            # store values with some increment
            if self.storeVal and self.time%self.timeIncrement == 0:
                self.storeInformation()

            # random quarantining if intervention is in place
            if self.intervention3 and self.time%self.intervention3_timeInterval == 0: 
                self.quarantine()

            # save the data at a specific time
            self.logData()

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
        """
           append the new values to the log table
        """
        """
            agent archetype:
            stem, humanities, art
            class: distribution 2 for sure, 2 left over
            
            1-1094 dorm
            1326 social_space_hub
            1327 transit_space
            1328 transit_space_hub
            1329 parking
            1330 offCampus_hub
            1206 dining_hall
            1207 dining_hall_hub
            1208-1215 library
            1216 library_hub
            1217-1224 gym
            1225 gym_hub
        """
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
        for i in range(1, 5):
            sche = self.agents[i].schedule
            for row in sche:
                if self.debug:
                    print(self.getRoomNames(row))
        
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
        if self.debug:
            for key, value in scheduleDict.items():
                if "gym" in key:
                    print(key, value)
            for key, value in maxDict.items():
                if "gym" in key:
                    print(key, value)
            
    def getRoomNames(self, listOfRoomsId):
        """ probably a duplicate function"""
        return list(self.rooms[roomId].room_name for roomId in listOfRoomsId)

    def updateAgent(self):
        """call the update function on each person"""
        count = 0
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
                    if infectedNumber[infectedIndex]:
                        agent.changeState(self.time, self.config["exp"],self.config["transitionTime"]["exposed"] )
                    infectedIndex+=1
                self.rooms[loc[0]].leave(agentId)
                self.rooms[loc[1]].enter(agentId)
                count+=1
    
    def checkAdj(self, loc):
        temp = False
        doubleTemp = False
        if loc[1] in [a[0] for a in self.adjacencyDict[loc[0]]]:
            temp=True
        if loc[0] in [a[0] for a in self.adjacencyDict[loc[1]]]:
            if temp:
                doubleTemp = True
            temp = True
        print(doubleTemp, self.rooms[loc[0]].room_name, self.rooms[loc[1]].room_name)
   
    def initilize_infection(self):
        """
            iniitilize the infection, start people off as susceptible
        """
        for agent in self.agents.values():
            # negative value for durration means the state will persist on to infinity
            agent.changeState(self.time, self.config["sus"], -1)
        seedNumber = self.config["infectionSeedNumber"]
        seededState = self.config["infectionSeedState"]
        for agentId in np.random.choice(list(self.agents.keys()),size=seedNumber):
            self.agents[agentId].changeState(self.time, seededState, self.config["transitionTime"][seededState])
    
    def infection(self):
        """
            the actual function that takes care of the infection
            goes over rooms and check if an infected person is inside and others were infected
        """
        sus, exp, qua = "susceptible", "exposed", "quarantined"
        # time it takes to transition states, negative means, states doesnt change
        transition = self.config["transitionTime"]
        transitionProbability = self.config["transitionProbability"]
        baseP = self.config["baseP"]
        randVec = np.random.random(len(self.agents))
       
        for roomId, room in self.rooms.items():
            totalInfected = self.infectionInRoom(roomId)
            if totalInfected > 0:
                print(totalInfected)
            for index, agentId in enumerate(room.agentsInside):
                if self.agents[agentId].state == sus and randVec[index] < (baseP*room.Kv*totalInfected)/room.limit: 
                    self.agents[agentId].changeState(self.time, exp, transition[exp])
                    if self.R0:
                        print(roomId, room.room_name, room.Kv, "agents inside", len(room.agentsInside), randVec[index] ,"<",(baseP*room.Kv*totalInfected)/room.limit, room.limit, totalInfected)
                        self.R0_counter+=1
                else:
                    state = self.agents[agentId].state
                    if state == qua or state == sus:
                        pass 
                    elif self.agents[agentId].transitionTime() > self.time and transition[state] > 0:
                        cdf = 0
                        for tup in transitionProbability[state]:
                            if tup[1] > randVec[index] >= cdf:
                                cdf+=tup[1]
                                nextState = tup[0]
                        self.agents[agentId].changeState(self.time, nextState, transition[state])

    def infectionInRoom(self, roomId):
        contribution = self.infectionWithinPopulation(self.rooms[roomId].agentsInside)
        return contribution

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
        print(f"time: {self.time}, Sus {num[0]} E: {num[1]}, I Asympto: {num[2]}, IAsym: {num[3]}, I Sympto: {num[4]}, rec: {num[5]}, quar: {num[6]}")
    
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

    def start_intervention(self, InterventionId):
        for i in InterventionId:
            if i == 1:
                # face mask
                self.maskP = 0.8
                self.intervention1 = True
                self.intervention1_startTime = 0
            elif i == 2:
                # hybrid courses
                self.intervention2 = True
                self.start_intervention2()
            elif i == 3:
                # test for covid and quarantine
                self.intervention3 = True
                self.intervention3_timeInterval = 100
            elif i == 4:
                self.buildingClosure = True
                self.closedLocation = self.config["closedBuildings"]
            elif i == 5:
                self.officeHours = False


    def start_intervention2(self):
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
        small = sizeRooms[0]
        medium = sizeRooms[1]
        large = sizeRooms[2]
        changeVals = small + medium + large
        changeVals = list(set(changeVals))
        for agentId, agent in self.agents.items():
            agentHome = agent.initial_location
            agent.schedule = self.replaceScheduleVal(agent.schedule, changeVals, agentHome, agentId)
            
    def quarantine(self):
        if self.time > self.config["quarantineOffset"] and self.time%self.config["quarantineInterval"]:
            self.quarantineCycle = None 
            listOfId = list(self.agents.keys())
            probability = self.config["quarantineSamplingProbability"]
            size = len(listOfId)
            falsePositive = np.random.choice(listOfId, size=int(size*self.config["falsePositive"]), replace=False)
            normalScreeningId = list(set(listOfId) - set(falsePositive))
            # these people had false positive results and are quarantined
            for agentId in falsePositive: 
                self.agents[agentId].state = self.config["qua"]
            falseNegVec = np.random.random(len(normalScreeningId))
            for i, agentId in enumerate(normalScreeningId):
                if self.agents[agentId].state in self.config["AgentPossibleStates"]["infected"]:
                    falseNegVec[i] < self.config["false"]
                    self.agents[agentId].changeState(self.time, self.config["qua", 24*14])

    def checkForWalkin(self):
        for agentId, agent in self.agents.items():
            if agent.state == "infected Symptomatic" and agent.lastUpdate+25 > self.time:
                # with some probability the agent will walkin
                tupP = np.random.random(3) # (P of walking in, P for false neg, P for false Pos)
                if tupP[0] < self.config["walkinProbability"]: # walkin
                    if tupP[1] < self.config["falseNegative"]:
                        pass
                    elif tupP[2] < self.config["falsePositive"]:
                        agent.changeState(self.time, self.config["qua"], self.config["transitionTime"]["quarantined"])
                    else:
                        agent.changeState(self.time, self.config["qua"], self.config["transitionTime"]["quarantined"])

if __name__ == "__main__":
    main()    


