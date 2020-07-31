import os
import random
import pandas as pd
import pickle
import numpy as np
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
# for speed tests/debug and memoization
import functools
import cProfile

def clock(func): # from version 2, page 203 - 205 of Fluent Python by Luciano Ramalho
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

def multiSimulation(simulationCount, modelConfig, days, debug, modelName):
    """
        run multiple simulations and return the location where the infection occured, the total number infected, and the max infected 
    """
    multiResults = {} # dictionary that will be converted to a dataframe
    infectionData = [] # list that will contain multiple time series dictionary 
    totalInfected = []
    for i in range(simulationCount):
        result = simpleCheck(modelConfig, days=days, visuals=False, debug=debug, modelName=modelName+"_"+str(i))
        for individualResult in result[:2]:
            for (k, v) in individualResult.items():
                multiResults[k] = multiResults.get(k, []) + [v]
            dfobj = pd.DataFrame.from_dict(multiResults, orient="index")
            flr.save_df_to_csv(flr.fullPath(modelName+".csv", "outputs"), dfobj)
        infectionData.append(result[3])
    print(infectionData)   
    return infectionData

def simpleCheck(modelConfig, days=100, visuals=True, debug=False, modelName="default"):
    """
        runs one simulatons with the given config and showcase the number of infection and the graph
    """
    loadDill, saveDill = False, False
    pickleName = flr.fullPath("coronaModel.pkl", "picklefile")
    if not loadDill:
        model = createModel(modelConfig, debug=debug)
        if saveDill:
            flr.saveUsingDill(pickleName, model)
            # save an instance for faster loading
            return 0
    else:
        model = flr.loadUsingDill(pickleName)
        print("loaded pickled object successfully")
    
    model.initializeStoringParameter(
        ["susceptible","exposed", "infected Asymptomatic", 
        "infected Asymptomatic Fixed" ,"infected Symptomatic Mild", 
        "infected Symptomatic Severe", "recovered", "quarantined"])
    model.printRelevantInfo()
    for _ in range(days):
        model.updateSteps(24)
        if debug:
            model.printRelevantInfo()
    model.final_check()
    model.printRoomLog()
    #tup = model.findDoubleTime()
    #for description, tupVal in zip(("doublingTime", "doublingInterval", "doublingValue"), tup):
    #    print(description, tupVal)
    if visuals:
        fileformat = ".png"
        model.visualOverTime(False, True, flr.fullPath(modelName+fileformat, "outputs"))
        modelName+="_total"
        model.visualOverTime(True, True, flr.fullPath(modelName+fileformat, "outputs"))
    #model.visualizeBuildings()
    # return (newdata, otherData, data, totalExposed)
    return model.outputs()

def R0_simulation(modelConfig, R0Control, simulationN=100, debug=False, timeSeriesVisual=False, R0Visuals=False, modelName="default"):
    R0Values = []
    configCopy = dict(modelConfig)
    for variableTup in R0Control:
        configCopy[variableTup[0]] = variableTup[1]
    # base model
    model = createModel(configCopy, debug=debug, R0=True)
    if debug:
        max_limits = dict()
    days=20
    t1 = time.time()
    for i in range(simulationN):
        print("*"*20, "starting model")
        new_model = copy.deepcopy(model)    
        new_model.initializeR0()
        new_model.initializeStoringParameter(
            ["susceptible","exposed", "infected Asymptomatic", 
        "infected Asymptomatic Fixed" ,"infected Symptomatic Mild", 
        "infected Symptomatic Severe", "recovered", "quarantined"])
        for _ in range(days):
            if debug:
                new_model.printRelevantInfo()
            new_model.updateSteps(24)
        if debug:
            logDataDict = new_model.printRoomLog()
            for key, value in logDataDict.items():
                max_limits[key] = max_limits.get(key, []) + [value]
        R0Values.append(new_model.returnR0())
        print(f"finished {(i+1)/simulationN*100}% of cases")
    if debug:
        for key, value in max_limits.items():
            print(key, "max is the following:", value)
    print("R0 is", R0Values)
    if timeSeriesVisual:
        new_model.visualOverTime()
    print("time:", time.time()-t1)
    data = statfile.analyzeData(R0Values)
    pickleName = flr.fullPath(modelName+"R0Data.pkl", "picklefile")
    # save the data just in case
    flr.saveUsingDill(pickleName, R0Values)
    print(data)
    print("(npMean, stdev, rangeVal, median)")
    if R0Visuals:
        statfile.boxplot(R0Values,oneD=True, pltTitle="R0 Simulation (box)", xlabel="Model Name",
             ylabel="Infected people (R0)", labels=[modelName], savePlt=True, saveName=modelName)
        statfile.boxplot(R0Values, oneD=True, pltTitle="R0 Simulation (bar)", xlabel="Model Name", 
            ylabel="Infected Agents (R0", labels=[modelName], savePlt=True, saveName=modelName)
    return (R0Values, ("(npMean, stdev, rangeVal, median)", data))

def createModel(modelConfig, debug=False, R0=False):
    """
        calls the required function(s) to properly initialize the model and returns it

        Parameters:
        - modelConfig: a dictionary with  the attribute/property name and the value associated with it
    """
    model = AgentBasedModel()
    # loading data
    model.addKeys(modelConfig)
    model.configureDebug(debug)
    if R0:
        model.initializeR0()
    model.initializeInterventionsAndPermittedActions()
    model.loadBuilder("newBuilding.csv")
    model.loadAgent("newAgent.csv")
    model.generateAgentDfFromDf()
    # object creation
    
    model.createWorld()
    # start initialization and configuration
    model.intializeAndConfigureObjects()
    
    model.startRoomLog()
    
    return model
   
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
        __slots__ = slotVal
        def __init__(self, agentParam):
            for slot, value in zip(self.__slots__, agentParam):
                self.__setattr__(slot, value)

        def updateLoc(self, currTime, adjDict):
            """
                change agent's state, either moving or stationary,
                look at adjacent rooms and move to one of the connected rooms

                Parameters:
                - currTime: the current time
                - adjDict: the adjacency dictionary, (key: roomId, value: list of roomsId of rooms connected to the key)    
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
            elif self.motion == "moving" and currTime >= self.arrivalTime:
                # the agent is still moving across
                self.move(adjDict)
                self.arrivalTime = currTime
            else: # the agent doesnt need to move
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
            elif self.state == "infected Symptomatic Severe" and currTime>self.lastUpdate+120:
                return self.initial_location
            if dayOfWeek > 3: # its a weekend
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
                #self.travelTime = 0
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
            if stateName in ["exposed", "infected Asymptomatic", "infected Asymptomatic Fixed", "infected Symptomatic Mild", "infected Symptomatic Severe"]:
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

def roomFactory(room_df, slotVal):
    """
        factory function used to dynamically assign __slots__

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
                self.agentsInside.add(agentId)

        def checkCapacity(self):
            """return a boolean, return True if theres capacity for one more agent, False if the room is at max capacity 
            """
            
            if len(self.agentsInside) < int(self.capacity):
                return True
            return False
    
        def leave(self, agentId):
            """ remove the id of the agent that exited the room"""
            if agentId in self.agentsInside:
                self.agentsInside.discard(agentId)
        
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
        self.date = 0
        self.dateDescriptor = "E" # can be "E": even, "O": odd, or "W": weelend
        self.storeVal = False
        self._debug = False
        self.directedGraph = False
        self.R0Calculation = False
        self.R0_agentIds = []
        self.largeGathering = True
        # rename in the future, used to cache informstion to reduce the number of filtering thats happening in the future run
        self.state2IdDict=dict()
        self.gathering_count = 0

    def addKeys(self, tempDict):
        """
        create a reference to the passed config dictionary
        The dictionary should contain all the elements that will be in use for that specific simulation, or else there will be a key not found error
        """
        self.config = tempDict

    def initializeInterventionsAndPermittedActions(self):
        """
        Assign True or False to the intervention checklist, and turn it on or off.  
        the actual ineterventions are not implimented in this function.  this function just tells the rest of the code whether it needs to deviate and run the interventions
        """
        def inInterventions(interventionName):
            return True if interventionName.lower() in [intervention.lower() for intervention in self.config["World"]["TurnedOnInterventions"]] else False
    
        self.faceMask_intervention = inInterventions("FaceMasks")
        self.walkIn = True if "walkin" in self.config["World"]["permittedAction"] else False
        self.quarantine_intervention = inInterventions("Quarantine")
        self.closedBuilding_intervention = inInterventions("ClosingBuildings")
        self.hybridClass_intervention = inInterventions("HybridClasses")
        self.lessSocial_intervention = inInterventions("LessSocial")
        self.largeGathering = self.config["World"]["LargeGathering"]
        print("the following interventions are turned on/off:")
        print(f" (Facemask, {self.faceMask_intervention}), (Quarantine, {self.quarantine_intervention}), (Closed,  {self.closedBuilding_intervention}), (Hybrid, {self.hybridClass_intervention}), (Less Social, {self.lessSocial_intervention})")

    def configureDebug(self, debugBool):
        """
            set debug equal to True or False,
            this enables or disables most of the messages in the console.  
            turn this off when you want to run it a bit faster, turn it on if you need to observe the innerplay of the simulation
        """
        self._debug=debugBool

    def loadAgent(self, fileName, folderName="configuration"):
        """
        load the agent dataframe
        """
        self.agent_df = flr.make_df(folderName, fileName, debug=self._debug)
    
    def loadBuilder(self, filename, folderName="configuration"):
        """use a builder to make the dataframe for the buiulding and rooms"""
        self.building_df, self.room_df = mod_df.mod_building(filename, folderName, debug=self._debug)
    
    def generateAgentDfFromDf(self, counterColumn="totalCount"):
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

    def createWorld(self):
        """
            initialize the world with default value, 
            also unpacks dataframe and make the classes 
        """
        # add a column to store the id of agents or rooms inside the strucuture
        # these are required values added to the df so that they can be used to store information and relationships 
        self.addAttrToDf()
        self.add_Id_to_Df()
      
        
        self.adjacencyDict = self.makeAdjacencyDict()
        self.buildings = self.createObject(self.building_df, superStrucFactory)
        self.rooms = self.createObject(self.room_df, roomFactory)
        
        # a dictionary for both rooms and buildings (key: buildingName, value: building ID)
        self.buildingNameId = dict((getattr(building, "building_name"), buildingId) for buildingId, building in self.buildings.items())
        self.roomNameId = dict((getattr(room, "room_name"), roomId) for roomId, room in self.rooms.items())
        # initialize a transit hub
        self.agent_df["transit"] = self.roomNameId[self.config["World"]["transitName"]]
        # add rooms to buildings, because up to this point the rooms and the buildings are separate Objects and we need buildings to store references(IDs) to rooms
        self.addRoomsToBuildings()
        # create agent object, dict(key: agentId --> value: agent object)
        self.agents = self.createObject(self.agent_df, agentFactory)
        
    def addAttrToDf(self):
        """
            add columns to dataframe before object creation, mainly because objects in this code use __slots__,
            __slots__ prevents the addition of attributes after instance creation, hence required to define them before creation
        """
        for dfRef, descriptor in zip([self.agent_df, self.room_df, self.building_df], ["Agents", "Rooms", "Buildings"]):
            if "ExtraParameters" in self.config[descriptor].keys():
                # assign default value of 0
                for attrName in self.config[descriptor]["ExtraParameters"]:
                    dfRef[attrName] = 0
            if "ExtraZipParameters" in self.config[descriptor].keys():
                # assign a default value
                for (attrName, attrVal) in self.config[descriptor]["ExtraZipParameters"]:
                    dfRef[attrName] = attrVal
    
    def makeAdjacencyDict(self):
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
    
    def add_Id_to_Df(self):
        for dfRef, dfEntry in zip([self.agent_df, self.room_df, self.building_df], ["agentId", "roomId", "buildingId"]):
            if dfEntry in dfRef.columns.values.tolist():
                dfRef[dfEntry] = dfRef.index # gets the first column (the Id column)

    def createObject(self, dfRef, func):
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
        if self._debug:
            print(f"creating {numObj} {className} class objects, each obj will have {len(slotVal)} attributes, __slots__ = {slotVal}")
        return tempDict
 
    def addRoomsToBuildings(self):
        """add room_id to associated buildings"""
        for buildingId, building in self.buildings.items():
            building.roomsInside = []   
        for roomId, room in self.rooms.items():
            self.buildings[self.buildingNameId[room.located_building]].roomsInside = self.buildings[self.buildingNameId[room.located_building]].roomsInside + [roomId] 
    
    def booleanAssignment(self):
        """
        go through the agent's attributes that are True or False and assign a default value based on randomness
        """
        for (VarName ,p_val) in self.config["Agents"]["booleanAssignment"]:
            self.agentAssignBool(p_val, VarName, replacement=False)  
    
    def agentAssignBool(self, percent = 0, attrName="officeAttendee", replacement=False):
        """Assign True or false to Agent's office attend boolean value """
        # check if its a decimal or probability
        if percent > 1: percent/=100
        size = int(len(self.agents) * percent)
        sample = np.concatenate((np.ones(size), np.zeros(len(self.agents)-size)), axis=0)
        np.random.shuffle(sample)
        for index, agent in enumerate(self.agents.values()):
            if sample[index]:
                setattr(agent, attrName,True)
            else:
                setattr(agent, attrName,False)

    def intializeAndConfigureObjects(self):
        # # build a dictionary, key: state --> value: list of agentIds
        # initialize state2IdDict
        for stateList in self.config["Agents"]["PossibleStates"].values():
            for stateName in stateList:
                self.state2IdDict[stateName] = set()

        # initialize agentsInside
        for rooms in self.rooms.values():
            rooms.agentsInside = set()
      
        self.transitionDict = self.config["Infection"]["TransitionTime"]

        # make schedules for each agents, outside of pickle for testing and for randomization
        self.booleanAssignment()
        self.initializeHybridClasses()
        self.initializeAgentsLocation()
        # start these two intervention after initializing agent's location, cause we remove agents from dorms
        # put agents in the right position
        
        self.studentFacultySchedule() # have hybrid,closing
        # agents dont change after this so we can get the offCampus students
        self.initialize_infection()
        self.initializeFaceMask()
        self.initializeTestingAndQuarantine()

    def initializeHybridClasses(self):
        onCampusIds = self.getAgents("onCampus", "Agent_type")
        offCampusIds = self.getAgents("offCampus", "Agent_type")
        facultyIds = self.getAgents("faculty", "Agent_type")
        
        onCampusCount = len(onCampusIds)
        offCampusCount = len(offCampusIds)
        facultyCount =  len(facultyIds)
        offCampusLeaf = self.findMatchingRooms("building_type","offCampus")[0]

        if self.hybridClass_intervention:
          
           
            hybridDict = self.config["HybridClass"]
            self.largeGathering = not hybridDict["TurnOffLargeGathering"]
            # these are the number of agents we need to convert
            remoteStudentCount = min(onCampusCount, hybridDict["RemoteStudentCount"])
            remoteFacultyCount = min(facultyCount, hybridDict["RemoteFacultyCount"])
            remoteOffCampusCount = min(offCampusCount, hybridDict["OffCampusCount"])

            self.remoteCount = remoteStudentCount + remoteFacultyCount
            if self._debug:
                print(f"HybridClass in effect, {remoteStudentCount} many agents are re-configured (onCampus --> OffCampus), and {remoteFacultyCount} faculty are remote")
            self.remoteStudentIds = set(np.random.choice(onCampusIds, size=remoteStudentCount, replace=False))            
            self.remoteFacultyIds = set(np.random.choice(facultyIds, size=remoteFacultyCount, replace=False))
            self.remoteOffCampusIds = set(np.random.choice(offCampusIds, size=remoteOffCampusCount, replace=False))
            self.rooms[offCampusLeaf].limit+=self.remoteCount
            self.rooms[offCampusLeaf].capacity+= self.remoteCount
     

            for agentId, agent in self.agents.items():
                if agentId in self.remoteStudentIds:
                    
                    agent.initial_location = "offCampus"
                elif agentId in self.remoteFacultyIds:
                    agent.initial_location = "offCampus"


        else:
            self.remoteStudentIds, self.remoteFacultyIds = {}, {}
            self.remoteOffCampusIds = {}

    def initializeAgentsLocation(self):
        """
            change the agent's current location to match the initial condition
        """
        # convert agent's location to the corresponding room_id and add the agent's id to the room member
        # initialize
        print("*"*20, "intializing Agents")
        possibleBType = {building.building_type for building in self.buildings.values()}
        counter = [0, 0, 0]
        if self.hybridClass_intervention:
            dorms = self.findMatchingRooms("building_type", "dorm")
            doubleRooms = [roomId for roomId in dorms if self.rooms[roomId].capacity == 2]
            convertCount = min(len(doubleRooms), self.config["HybridClass"]["RemovedDoubleCount"])
            print(f"{len(dorms) -len(doubleRooms)} single dorms and {len(doubleRooms)} doubles")
            for roomId in np.random.choice(doubleRooms, size=convertCount, replace=False):
                self.rooms[roomId].capacity = 1
            print("NewCap", sum(self.rooms[roomId].capacity for roomId in dorms) ,"and we have", self.countAgents("onCampus", "Agent_type"), 'oncampusStudents but', self.countAgents("dorm", "initial_location"), "in dorm")
        dormRoom = self.findMatchingRooms("building_type", "dorm")

        for agentId, agent in self.agents.items():
            initialLoc = getattr(agent, "initial_location")
            if initialLoc in self.roomNameId.keys(): # if the room is specified
                # convert the location name to the corresponding id
                location = self.roomNameId[initialLoc]
                counter[0]+=1
            elif initialLoc in self.buildingNameId.keys(): # if location is under building name
                # randomly choose rooms from the a building that doesnt end in "_hub" and is empty
                possibleRooms = [roomId for roomId in self.buildings[self.buildingNameId[initialLoc]].roomsInside 
                                if not self.rooms[roomId].room_name.endswith("_hub") and self.rooms[roomId].checkCapacity()]
                location = np.random.choice(possibleRooms)
                counter[1]+=1
            elif initialLoc in possibleBType: # if location is under building type
                possibleRooms = [roomId for roomId in self.findMatchingRooms("building_type", initialLoc) if self.rooms[roomId].checkCapacity()]
                location = np.random.choice(possibleRooms)
                counter[2]+=1
            else:
                print("something wrong, possibly there are agents that dont have a valid spawn point, maybe increase capacity for some nodes?")
                # either the name isnt properly defined or the room_id was given
                pass
            agent.currLocation = location
            agent.initial_location = location
            self.rooms[location].agentsInside.add(agentId)
        if self._debug:
            print(f"the agents we initialized using values (specific, buildingName, buildingType) --> {counter}")
        spCounter = [0,0,0]
        for room in self.findMatchingRooms("building_type", "dorm"):
            if len(self.rooms[room].agentsInside) > 1:
                spCounter[0]+=1
            elif len(self.rooms[room].agentsInside) == 1:
                spCounter[1]+=1
            else:
                spCounter[2]+=1
        print("# of rooms filled with [2 people, 1 , 0]", spCounter)    

        
    #@functools.lru_cache(maxsize=128)
    def findMatchingRooms(self, partitionAttr, attrVal=None, strType=False):
        """
            returns a list of room IDs that matches the criterion: if object.attrVal == partitionAttr
        
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

    def startRoomLog(self):
        """
            initialize the log, building, room and people in rooms
        """
        self.room_cap_log = dict((key,[]) for key in self.rooms.keys())

    def logRoomData(self):
        # this is the total number of agents in the room, only need to be called for a week
        for roomId, room in self.rooms.items():
            self.room_cap_log[roomId].append(len(room.agentsInside))

    def printRoomLog(self):
        """
            print the logs, only for debug purpose
        """ 
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
            if self._debug:
                for index, (key, value) in enumerate(scheduleDict.items()):
                    if node in key and not key.endswith("_hub") and index < 5:
                        print(key, value)
                for key, value in maxDict.items():
                    if node in key and not key.endswith("_hub"):
                        print(key, value)
        return maxDict

    def initialize_infection(self):
        """
            iniitilize the infection, start people off as susceptible
        """
        for agentId in self.agents.keys():
            # negative value for durration means the state will persist on to infinity
            self.changeStateDict(agentId, "susceptible", "susceptible")
        
        if self.hybridClass_intervention:
            seedNumber = self.config["HybridClass"]["ChangedSeedNumber"]
        else:
            seedNumber = self.config["Infection"]["SeedNumber"]
        seedState = self.config["Infection"]["SeedState"]
        onCampusIds = [agentId for agentId, agent in self.agents.items() if agent.Agent_type == "onCampus"]
        

        if len(onCampusIds) < seedNumber:
            print("not enough agents to satisfy initial # of seed, taking the minimum")
        infectedAgentIds = np.random.choice(onCampusIds,size=min(len(onCampusIds), seedNumber), replace=False)
        for agentId in infectedAgentIds:
            self.changeStateDict(agentId, "susceptible",seedState)
        debugTempDict = dict()
        for agentId in infectedAgentIds:
            debugTempDict[self.agents[agentId].Agent_type] = debugTempDict.get(self.agents[agentId].Agent_type, 0) + 1
        if self.R0Calculation:
            self.R0_agentIds = infectedAgentIds

        print(f"{seedNumber} seeds starting off with {seedState}, {debugTempDict.keys()}")

        self.baseP = self.config["Infection"]["baseP"]

    def initializeFaceMask(self):
        
        self.maskP = self.config["FaceMasks"]["MaskInfectivity"]
        self.maskB = self.config["FaceMasks"]["MaskBlock"]
        self.nonCompliantLeaf = set(self.config["FaceMasks"]["NonCompliantLeaf"] + self.config["FaceMasks"]["NonCompliantBuilding"])
        self.compliantZone = set(self.config["FaceMasks"]["CompliantHub"])
        self.nonCompliantZone = set(self.config["FaceMasks"]["NonCompliantBuilding"])
        
        maskNumber = int(self.config["World"]["complianceRatio"]*len(self.agents))
        maskVec = np.concatenate((np.zeros(maskNumber),np.ones(len(self.agents)-maskNumber)))
        np.random.shuffle(maskVec)
        for i, agent in enumerate(self.agents.values()):
            if maskVec[i] > 0:
                agent.compliance = True
            else:
                agent.compliance = False 

    def initializeTestingAndQuarantine(self):
        self.quarantineInterval = self.config["Quarantine"]["checkupFrequency"] 
        self.quarantineOffset =  self.config["Quarantine"]["offset"]
        self.falsePositiveList = []
        self.quarantineList = []
        self.screeningTime = []
        if self.config["Quarantine"]["RandomSampling"]: # do nothing if quarantine screening is with random samples from the population
            self.groupIds = [agentId for agentId, agent in self.agents.items() if agent.Agent_type != "faculty"]
        else: # the population is split in smaller groups and after every interval we cycle through the groups in order and screen each member in the group
            totalIds = set([agentId for agentId, agent in self.agents.items() if agent.archetype == "student"])
            size = len(self.agents)
            # the size of the group, if there's a remainder, then they all get grouped together
            
            self.groupIds = []
            while len(totalIds) > 0:
                sampledIds = np.random.choice(list(totalIds), size=min(len(totalIds), self.config["Quarantine"]["BatchSize"]),replace=False)
                totalIds -= set(sampledIds)
                self.groupIds.append(list(sampledIds))
      
            self.quarantineGroupNumber, self.quarantineGroupIndex = len(self.groupIds), 0

    def initializeClosingBuilding(self):
        """
        "ClosedBuilding_LeafKv=0" : [],
            # close buildings in the list(remove them from the schedule), and go home or go to social spaces 
            "ClosedBuilding_ByType" : ["gym", "library"],
            "GoingHomeP": 0.5,
            # the building in the list will be removed with probability and replaced with going home, otherwise it stays
            "Exception_SemiClosedBuilding": [],
            "Exception_GoingHomeP":0.5,
            
        },"""
        closedBuilding =  self.config["ClosingBuildings"]["ClosedBuilding_ByType"]
        closedBuildingId = [roomId for bType in closedBuilding for roomId in self.findMatchingRooms("building_type", bType)]
        closedLeafOpenHub = [roomId for bType in self.config["ClosingBuildings"]["ClosedBuildingOpenHub"] for roomId in self.findMatchingRooms("building_type", bType)]
        semiClosedBuilding = [roomId for bType in self.config["ClosingBuildings"]["Exception_SemiClosedBuilding"] for roomId in self.findMatchingRooms("building_type", bType)]
        for roomId in closedLeafOpenHub:
            self.rooms[roomId].Kv = 0
        self.homeP = self.config["ClosingBuildings"]["GoingHomeP"]
        self.e_homeP = self.config["ClosingBuildings"]["Exception_GoingHomeP"]
        return closedBuilding, semiClosedBuilding

    def getAgentsInGroup(self, agentIds, attrVal, attrName="state"):
        return [agentId for agentId in agentIds if getattr(self.agents[agentId], attrName) == attrVal]

    def getAgents(self, attrVal, attrName="state"):
        return [agentId for agentId, agent in self.agents.items() if getattr(agent, attrName) == attrVal]

    def countAgentsInGroup(self, agentIds, attrVal, attrName="state"):
        return len(self.getAgentsInGroup(agentIds, attrVal, attrName))

    def countAgents(self, attrVal, attrName="state"):
        return len(self.getAgents(attrVal, attrName))

    def changeStateDict(self, agentId, previousState, newState):
        """
            modifies the dictionary, state2IdDict, when an agent change states, 
            takes care of removal and addition to the appropriate dictionary value, and modifies the agent's attribute

            Parameters:
            - agentId: the agent's key/Id value 
            - previousState: the state of the agent, better to be a parameter because checks occurs before the function is called
            - newState: the state name to transition into
        """
        self.state2IdDict[previousState].discard(agentId)# remove the agent from the state list
        if previousState == "quarantined" and not self.agents[agentId].infected:
            self.state2IdDict["falsePositive"].discard(agentId)
        self.state2IdDict[newState].add(agentId)# then add them to the new state list
        self.agents[agentId].changeState(self.time, newState, self.transitionDict[newState])
    

     # takes 4 seconds
    
    def setOffCampus(self, agentId, offCampusLeaf,  scheduleTemp):
            self.agents[agentId].schedule = scheduleTemp
            self.agents[agentId].Agent_type = "offCampus"
            initalLoc = self.agents[agentId].currLocation
            self.rooms[initalLoc].agentsInside.discard(agentId)
            self.agents[agentId].currLocation = offCampusLeaf
            self.agents[agentId].initial_location = offCampusLeaf
            self.rooms[offCampusLeaf].agentsInside.add(agentId)

    def setToRemote(self, agentId, offCampusLeaf,  scheduleTemp):
            self.agents[agentId].schedule = scheduleTemp
            initalLoc = self.agents[agentId].currLocation
            self.rooms[initalLoc].agentsInside.discard(agentId)
            self.agents[agentId].currLocation = offCampusLeaf
            self.agents[agentId].initial_location = offCampusLeaf
            self.rooms[offCampusLeaf].agentsInside.add(agentId)

    def studentFacultySchedule(self):
        """
            calls the schedule creator and replace general notion of locations with specific location Id,
            for example if the string "dorm" is in the schedule, it will be replaced by a room located in a building with "building_type" equal to "dorm"
        """
        self.lazySunday = self.config["World"]["LazySunday"]
        onCampusCount = self.countAgents("onCampus","Agent_type")
        offCampusCount = self.countAgents("offCampus","Agent_type")
        facultyCount = self.countAgents("faculty", "Agent_type")
        offCampusLeaf = self.findMatchingRooms("building_type","offCampus")[0]
       
        socialP = self.config["World"]["socialInteraction"]
        if self.lessSocial_intervention:
            socialP *= (1-self.config["LessSocializing"]["StayingHome"])
            print("social p", socialP)
        schedules, onVsOffCampus = schedule_students.scheduleCreator(socialP)
        fac_schedule, randomizedFac = schedule_faculty.scheduleCreator()
        classrooms = self.findMatchingRooms("building_type", "classroom")
        stem = self.findMatchingRooms("located_building", "STEM_office")
        art = self.findMatchingRooms("located_building", "HUM_office")
        hum = self.findMatchingRooms("located_building", "ART_office") 
        if self.closedBuilding_intervention:
            closedBuilding, semiClosed = self.initializeClosingBuilding()
            closedBuilding, semiClosed = set(closedBuilding), set(semiClosed)
            

            for index, schedule in enumerate(schedules):
                for i, row in enumerate(schedule):
                    for j, item in enumerate(row):
                        if item in closedBuilding:
                            if random.random() < self.homeP:
                                schedules[index][i][j] = "sleep"
                            else:
                                schedules[index][i][j] = "social"
                        elif item in semiClosed:
                            if random.random() < self.homeP:
                                schedules[index][i][j] = "sleep" 
            #schedules = [
            #    [[item if item not in closedBuilding else ("sleep" if random.random() < self.homeP else "social") for item in row]
            #     for row in uniqueSchedule] for uniqueSchedule in schedules]# ("sleep" if random.random() < 0.5 else "social")
            fac_schedule = [
                [[item if item not in closedBuilding else "Off" for item in row] for row in uniqueSchedule] 
                    for uniqueSchedule in fac_schedule]
        
        
        # assign one dining room as faculty only
        facultyDiningRoom = self.findMatchingRooms("building_type", "dining")[0]
        self.rooms[facultyDiningRoom].room_name = "faculty_dining_room"
        self.rooms[facultyDiningRoom].building_type = "faculty_dining_room"
        
        # sample faculty schedule ["Off", "Off", "dining", 45, "Off", ...]
        offCampusScheduleTemplate = [[offCampusLeaf for _ in range(24)] for _ in range(3)]
        for index, (facSche, randFac) in enumerate(zip(fac_schedule, randomizedFac)):
            replacement = stem if randFac == "S" else (art if randFac == "A" else hum)
            
            favoriteOffice = np.random.choice(replacement)
            
            for i, row in enumerate(facSche):
                for j, item in enumerate(row):
                    if item == "office": # choose a random office within their department
                        if self.closedBuilding_intervention and "office" in closedBuilding:
                            fac_schedule[index][i][j] = "Off"
                        else:    
                            fac_schedule[index][i][j] = favoriteOffice
                    elif item == "dining": # convert to faculty dining to restict area to faculty only space
                        fac_schedule[index][i][j] = "faculty_dining_room"
                    elif isinstance(item, int): # maps the nth class to the right classroom Id
                        fac_schedule[index][i][j] = classrooms[item]
                    elif isinstance(item[0], int):
                        fac_schedule[index][i][j] = classrooms[item[0]]

        # replace entries like (48, 1) --> 48, tuple extractor
        schedules = [[[classrooms[a[0]] if isinstance(a[0], int) else a for a in row] for row in student_schedule] for student_schedule in schedules]

        onCampusIndex, offCampusIndex, facultyIndex = 0, 0, 0
        offCampusSchedule, onCampusSchedule = [], [] 
        
        # map the schedules to oncampus and offcampus students
        for schedule, onOffDistinction in zip(schedules, onVsOffCampus):
            if onOffDistinction == "Off": offCampusSchedule.append(schedule)
            else: onCampusSchedule.append(schedule)
        

        # assign the schedule to the correct agent
        for agentId, agent in self.agents.items():
            if agent.Agent_type == "onCampus": # oncampus
                if agentId in self.remoteStudentIds: # this student is learning remote
                    self.setOffCampus(agentId, offCampusLeaf,offCampusScheduleTemplate)
                else:
                    agent.schedule = onCampusSchedule[onCampusIndex]
                onCampusIndex+=1
            elif agent.Agent_type == "offCampus": # offcampus
                if agentId in self.remoteOffCampusIds:
                    self.setOffCampus(agentId, offCampusLeaf, offCampusScheduleTemplate)
                else:
                    agent.schedule = offCampusSchedule[offCampusIndex]
                offCampusIndex+=1
            else:# faculty
                if agentId in self.remoteFacultyIds: # this faculty is teaching remote
                    self.setToRemote(agentId,offCampusLeaf, offCampusScheduleTemplate)
                else:
                    agent.schedule = fac_schedule[facultyIndex] 
                facultyIndex+=1
        
        # this gets rid of "sleep", "Off", "dorm" and replace it with one of the leaf Ids
        for entry in ["sleep", "Off", "dorm"]:
            self.replaceScheduleEntry(entry)
        self.replaceByType(agentParam="Agent_type", agentParamValue="faculty", partitionTypes="faculty_dining_room", perEntry=False)
        self.replaceByType(partitionTypes=["library", "dining","gym", "office"])
        students = [agentId for agentId, agent in self.agents.items() if agent.archetype == "student"]
        self.replacewithTwo(students)
        print("finished assigning schedules")
        
        """
        # print sample faculty schedules
        for agentId, agent in self.agents.items():
            
            if agentId%10 == 0 and agentId > 2000:
                print("below", "*"*20, agent.Agent_type)
                #print(agent.schedule[:2])
                print(self.convertScheduleToRoomName(agent.schedule[:2]))
        """
        
    def replaceScheduleEntry(self, antecedent):
        """
            replace locations with each agent's initial location

            Parameters:
            - antecedent: the string to replace with the agent's initial location
        """
        for agentId, agent in self.agents.items():
            agent.schedule = [[a if a != antecedent else agent.initial_location for a in row] for row in agent.schedule] 

    def replacewithTwo(self, agentIds):
        socialSpace = self.findMatchingRooms("building_type", "social")
        for index, agentId in enumerate(agentIds):
            twoFriendGroup = np.random.choice(socialSpace, size=2, replace=False)
            for i, row in enumerate(self.agents[agentId].schedule):
                for j, item in enumerate(row):
                    if item == "social":
                        if index < 2:
                            self.agents[agentId].schedule[i][j] = twoFriendGroup[0]
                        else:
                            self.agents[agentId].schedule[i][j] = twoFriendGroup[1]

    def replaceByType(self, agentParam=None, agentParamValue=None, partitionTypes=None, perEntry=False):
        """
            go over the schedules of the agents of a specific type and convert entries in their schedules

            Parameters:
            - agentParam: a string of the attribute name
            - agentParamValue: the value of the agentParam attribute, filter agents with this value and apply the replace function
            - SuperStrucType: a string to replace 
            - perEntry: boolean, if True, it randomly chooses an Id from the pool every time it locates the identifier, if False, one Id is taken from the pool per agent
        """
        # filter rooms with specific value for building_type, returned roomIds dont include hub ids
        index = 0
        if not isinstance(partitionTypes, list): # if only one value is passed
            if agentParam != None and agentParamValue != None:
                filteredId = [agentId for agentId, agent in self.agents.items() if getattr(agent, agentParam) == agentParamValue]
            else: filteredId = list(self.agents.keys())
            roomIds = self.findMatchingRooms("building_type", partitionTypes)
           
            if not perEntry:
                randomVec = np.random.choice(roomIds, size=len(filteredId), replace=True)
            for agentId in filteredId:
                for i, row in enumerate(self.agents[agentId].schedule):
                    for j, item in enumerate(row):
                        if item == partitionTypes:
                            if not perEntry:
                                self.agents[agentId].schedule[i][j] = randomVec[index]
                            else:
                                self.agents[agentId].schedule[i][j] = np.random.choice(roomIds)
                index +=1
        else: # if a list of values is passed
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
            
            randRoomIds = []
            for idList in partitionIds:
                randRoomIds.append(np.random.choice(idList, size=agentCount, replace=True))

            for agentId in filteredId:
                for i, row in enumerate(self.agents[agentId].schedule):
                    for j, item in enumerate(row):
                        indx = indexVal(partitionTypes, item) 
                        if  indx != -1:
                            self.agents[agentId].schedule[i][j] = randRoomIds[indx][index]  
                index+=1
 
    def updateSteps(self, step = 1): 
        if self.time == 0:
            self.storeInformation()
        for _ in range(step):     
            self.time+=1
            modTime = self.time%24
            # between [7AM, 10PM] 
            if  23 > modTime > 6 and len(self.state2IdDict["recovered"]) != len(self.agents): 
                # update 4 times to move the agents to their final destination
                # 4 is the max number of updates required for moving the agents from room --> building_hub --> transit_hub --> building_hub --> room
                if self.lazySunday and self.dateDescriptor == "LS":
                    if self._debug and False:
                        print(f"at time {self.time} lazy sunday, no one is moving")
                else:
                    for _ in range(4):
                        self.updateAgent()
                        self.hub_infection()
                self.infection()
           
            # if weekdays
            if self.dateDescriptor != "W" or self.dateDescriptor!="LS":
                if modTime == 8:
                    self.checkForWalkIn()
                if self.quarantine_intervention and self.time%self.quarantineInterval == self.config["Quarantine"]["offset"]: 
                    self.testForDisease()
                self.delayed_quarantine()
            # its a weekend and sunday midnight
            if (self.dateDescriptor == "LS" or self.dateDescriptor=="W") and self.time%(24*7) == 0:
                self.big_gathering()
            if self.storeVal and self.time%self.timeIncrement == 0:
                self.storeInformation()
            if self.date < 8:
                self.logRoomData()

            if modTime==0: # change the date once its past midnight
                self.date+=1 # its the next day
                if self.lazySunday and self.date%7 == 6:
                        self.dateDescriptor = "LS"
                elif self.date%7 > 3: # Friday follows a "weekend" schedule
                    self.dateDescriptor = "W"  
                elif self.date&1: # bitwise opperation, if date is an odd number, then its an even day because of 0 based index 
                    self.dateDescriptor = "E"
                else:
                    self.dateDescriptor ="O"
                
    def convertScheduleToRoomName(self, schedule):
        """
            for debugging/output purpose, return the agent's schedule but replace all Ids with the name of the room 

            Parameters:
            - agentId:  the Id of the agent that we want to observe the schedule
        """
        return [[self.rooms[roomId].room_name for roomId in row] for row in schedule]
    
    def initializeR0(self):
        self.R0Calculation = True
            
    def returnR0(self):
        counter = 0
        timeRem = self.time//self.timeIncrement
        for key, value in self.parameters.items():
            if key != "susceptible" and key != "falsePositive":
                counter += value[timeRem]                
        self.printRelevantInfo()
        print(f"# infected: {counter}, initial: {self.config['Infection']['SeedNumber']}, Ave R0: {(counter - self.config['Infection']['SeedNumber'])/self.config['Infection']['SeedNumber']}")
        return (counter - self.config["Infection"]["SeedNumber"])/self.config["Infection"]["SeedNumber"]
    
    def initializeStoringParameter(self, listOfStatus):
        """
            tell the code which values to keep track of. 
            t defines the frequency of keeping track of the information
        """
        self.storeVal = True
        self.timeIncrement = self.config["World"]["stateCounterInterval"]
        numEntry = int((self.config["World"]["InferedSimulatedDays"] * 24)/self.timeIncrement)
        self.parameters = dict((stateName, [0]*numEntry) for stateList in self.config["Agents"]["PossibleStates"].values() for stateName in stateList)    
        self.timeSeries = list(range(0, (self.config["World"]["InferedSimulatedDays"]*24)+1, self.timeIncrement))
    
    def storeInformation(self):
        if not (self.time//self.timeIncrement < len(self.timeSeries)-1): 
            for param in self.parameters.keys():
                self.parameters[param].append((len(self.state2IdDict[param])))
            
            self.timeSeries.append(self.time)
        else:
            for param in self.parameters.keys():
                self.parameters[param][self.time//self.timeIncrement] = len(self.state2IdDict[param])
          
    def printRelevantInfo(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this functio n will be converted to the proper format using __repr__"""
        
        stateList = [state for stateGroup in self.config["Agents"]["PossibleStates"].values() for state in stateGroup]
        num = [len(self.state2IdDict[state]) for state in stateList]
        def trunk(words):
            wordList = words.split()
            newWord = [a[:4] for a in wordList]
            return " ".join(newWord)

        stateListTrunked = []
        for state, number in zip(stateList, num):
            stateListTrunked.append(":".join([trunk(state), str(number)]))
        print(f"time: {self.time}, states occupied: {' | '.join(stateListTrunked)}")

    def updateAgent(self):
        """call the update function on each person"""
        # change location if the old and new location is different
        index = 0
        transitionP = self.config["World"]["offCampusInfectionProbability"]
        offCampusNumber = len(self.rooms[self.roomNameId["offCampus_hub"]].agentsInside)
        if not self.R0Calculation and offCampusNumber > 0 and self.time%24 < 12:
            randomVec = np.random.random(offCampusNumber) 
        for agentId, agent in self.agents.items():
            loc = agent.updateLoc(self.time, self.adjacencyDict)
            if loc[0] != loc[1]:
                # if the agent is coming back to the network from the offcampus node
                if not self.R0Calculation and loc[0] == self.roomNameId["offCampus_hub"] and loc[1] == self.roomNameId[self.config["World"]["transitName"]] and self.time%24<12: 
                    if agent.state == "susceptible" and randomVec[index] < transitionP:
                        if self._debug:
                            print("*"*5, "changed state from susceptible to exposed through transit")
                        self.changeStateDict(agentId,agent.state, "exposed")
                        self.rooms[loc[0]].infectedNumber+=1
                    index+=1
                    
                self.rooms[loc[0]].leave(agentId)
                self.rooms[loc[1]].enter(agentId)
  
    def hub_infection(self):
        randVec = np.random.random(len(self.state2IdDict["susceptible"]))
        index = 0
        for roomId, room in self.rooms.items():
            if room.room_name.endswith("_hub") and room.building_type != "offCampus":
                totalInfection = self.infectionInRoom(roomId)
                for  agentId in room.agentsInside:
                    if self.agents[agentId].state == "susceptible":
                        coeff = 1
                        if self.faceMask_intervention and self.agents[agentId].compliance: # check for compliance
                            if self.rooms[roomId].building_type != "social":
                                coeff *= self.maskB
                    
                        if randVec[index] < coeff*totalInfection:
                            self.changeStateDict(agentId,"susceptible", "exposed")
                            room.infectedNumber+=1
                            room.hubCount+=1
                            index+=1
                            if self._debug:
                                print(f"at time {self.time}, in {(roomId, room.room_name)}, 1 got infected by the comparison randomValue < {totalInfection}. Kv is {room.Kv}, limit is {room.limit},  {len(room.agentsInside)} people in room ")
                            
    def infection(self):
        """
            the actual function that takes care of the infection
            goes over rooms and check if an infected person is inside and others were infected
        """
        # time it takes to transition states, negative means, states doesnt change
        transition = self.config["Infection"]["TransitionTime"]
        transitionProbability = self.config["Infection"]["TransitionProbability"]
        randVec = np.random.random(len(self.state2IdDict["susceptible"]))
        randVec2 = np.random.random(len(self.state2IdDict["exposed"]) + len(self.state2IdDict["infected Asymptomatic"]))
        index1, index2 = 0, 0
        for roomId, room in self.rooms.items():
            if room.building_type != "offCampus":
                totalInfection = self.infectionInRoom(roomId)
                if totalInfection > 0:
                    for agentId in room.agentsInside:
                        if self.agents[agentId].state == "susceptible":
                            coeff = 1
                            if self.faceMask_intervention and self.agents[agentId].compliance: # check for compliance
                                if self.rooms[roomId].building_type not in self.nonCompliantLeaf:
                                    coeff *= self.maskB
                            
                            if randVec[index1] < coeff*totalInfection:
                                self.changeStateDict(agentId,"susceptible", "exposed")
                                room.infectedNumber+=1
                                index1+=1
                                if self._debug and False:
                                    contribution = self.infectionWithinPopulation(self.rooms[roomId].agentsInside, roomId)
                                    
                                    if room.building_type == "social":
                                        print(f"at time {self.time}, in {(roomId, room.room_name)}, 1 got infected by the comparison randomValue < {totalInfection}. Kv is {room.Kv}, limit is {(5*int(len(self.rooms[roomId].agentsInside)/5+1))},  {len(room.agentsInside)} people in room, contrib: {contribution}")
                                    else:
                                        print(f"at time {self.time}, in {(roomId, room.room_name)}, 1 got infected by the comparison randomValue < {totalInfection}. Kv is {room.Kv}, limit is {room.limit},  {len(room.agentsInside)} people in room, contrib: {contribution}")


            # this loop takes care of agent's state transitions
            for agentId in room.agentsInside:   
                state = self.agents[agentId].state
                if self.agents[agentId].transitionTime() < self.time and state == "quarantined":
                    # go back to the susceptible state, because the agent was never infected, just self isolated
                    # or recovered from infection during quarantine
                    exitState = "recovered" if self.agents[agentId].infected else "susceptible" 
                    self.changeStateDict(agentId, "quarantined", exitState)
                elif self.agents[agentId].transitionTime() < self.time and state != "quarantined" and state != "susceptible" and transition[state] > 0:
                    cdf = 0
                    if False and (agentId in self.R0_agentIds):
                            # only for R0, go to the worst case scenario, exposed --> infected Asymptomatic --> infected Symptomatic Mild
                        tup = transitionProbability[state][0]
                        self.changeStateDict(agentId, self.agents[agentId].state, tup[0])
                    else:
                        if len(transitionProbability[state]) > 1:
                            
                            for tup in transitionProbability[state]:
                                if tup[1] > randVec2[index2] > cdf:
                                    cdf+=tup[1]
                                    nextState = tup[0]
                            index2+=1
                        else:
                            nextState = transitionProbability[state][0][0]

                        self.changeStateDict(agentId, self.agents[agentId].state, nextState)
    
    def infectionInRoom(self, roomId):
        """find the total infectiousness of a room by adding up the contribution of all agents in the room"""
        contribution = self.infectionWithinPopulation(self.rooms[roomId].agentsInside, roomId)
        if self.rooms[roomId].building_type == "social" and not self.rooms[roomId].room_name.endswith("_hub"): # check for division by zero
            if len(self.rooms[roomId].agentsInside) == 0:
                return 0
            cummulativeFunc = (self.baseP*2*contribution)/(5*int(len(self.rooms[roomId].agentsInside)/5+1))
        else:
            cummulativeFunc = (self.baseP*self.rooms[roomId].Kv*contribution)/self.rooms[roomId].limit
        return cummulativeFunc

    def infectionWithinPopulation(self, agentIds, roomId=None):
        contribution = 0
        for agentId in agentIds:
            lastUpdate = self.agents[agentId].lastUpdate
            individualContribution =  self.infectionContribution(agentId, lastUpdate)
            if self.faceMask_intervention:
                if roomId == -1: # social or large gathering
                    if self.agents[agentId].compliance:
                        individualContribution*=self.maskP
                elif self.rooms[roomId].building_type in self.nonCompliantLeaf: # if dorm, social or dining
                    if self.rooms[roomId].room_name.endswith("_hub") and self.rooms[roomId].building_type in self.compliantZone:
                        individualContribution*=self.maskP # put mask if dorm or dining hub
                    elif self.rooms[roomId].building_type in self.nonCompliantZone:
                        if self.agents[agentId].compliance:
                            individualContribution*=self.maskP # some compliance with social
                    # otherwise no mask
                else: # any other spaces
                    individualContribution*=self.maskP
                
                
            contribution+= individualContribution
        return contribution

    def infectionContribution(self, agentId, lastUpdate):
        """return the contribution to the infection for a specific agent"""
        if self.R0Calculation:
            if agentId in self.R0_agentIds: 
                return self.config["Infection"]["Contribution"].get(self.agents[agentId].state, 0)
            return 0
        else: 
            return self.config["Infection"]["Contribution"].get(self.agents[agentId].state, 0)
        return 0

    def testForDisease(self): 
        """
            This function tests people randomly or by batch, and save the result in the log.  The log is read and with a delay, the agents who are listed in the log is qurantined
            the false positive rate adds uninfected agents to the log.  The false negative rate is related to the number of infected agents that can get a false result (not-infected),
            otherwise they go through the normal screening process and they get added to the log based on their state.

            Parameters:
            - None
        """
        if self.config["Quarantine"]["RandomSampling"]: # if random
            listOfId = np.random.choice(self.groupIds, size=self.config["Quarantine"]["RandomSampleSize"], replace=False)
        else: # we cycle through groups to check infected
            listOfId = self.groupIds[self.quarantineGroupIndex]
            self.quarantineGroupIndex = (self.quarantineGroupIndex+1)% self.quarantineGroupNumber
    
        if self.config["Quarantine"]["ShowingUpForScreening"] == 1:
            pass# everyone shows up
        else:
            notSymptomatic = {agentId for agentId in listOfId 
                    if self.agents[agentId].state != "infected Symptomatic Mild" and self.agents[agentId].state != "infected Symptomatic Severe"}
            randomVec = np.random.random(len(notSymptomatic))
            complyingP = self.config["Quarantine"]["ShowingUpForScreening"]
            nonComplyingAgent = [agentId for i, agentId in enumerate(notSymptomatic) if randomVec[i] > complyingP]
            listOfId = list(set(listOfId) - set(nonComplyingAgent))
        fpDelayedList, delayedList = [], []
        falsePositiveMask = np.random.random(len(listOfId))
        falsePositiveResult = [agentId for agentId, prob in zip(listOfId, falsePositiveMask) if prob < self.config["Quarantine"]["falsePositive"] and agentId in self.state2IdDict["susceptible"]]
        normalScreeningId = list(set(listOfId) - set(falsePositiveResult))
        # these people had false positive results and are quarantined
        for agentId in falsePositiveResult:
            fpDelayedList.append(agentId)
        
        falseNegVec = np.random.random(len(normalScreeningId))
        # these are people who are normally screened
        for i, agentId in enumerate(normalScreeningId):
            # double the difficulty to catch Asymptomatic compared to symptomatic
            coeff = 1 if self.agents[agentId].state != "infected Asymptomatic Fixed" else 2
            if self.agents[agentId].state in self.config["Agents"]["PossibleStates"]["infected"]:
                if falseNegVec[i] > coeff*self.config["Quarantine"]["falseNegative"]: # infected and not a false positive result
                    delayedList.append(agentId)
        if self._debug:
            print(f"testing at time {self.time}, dayDes: {self.dateDescriptor}, caught the following (FalsePositive: {len(fpDelayedList)}, infected: {len(delayedList)})")
        self.falsePositiveList.append(fpDelayedList)
        self.quarantineList.append(delayedList)
        self.screeningTime.append(self.time)
     
    def delayed_quarantine(self): 
        """
            the people who gets a mandatory testing will get their results in t time (t=0 means the result are given without any delay),
            in the testing phase, the agents are tested and the people who had false positive result and people with the covid is quarantined
            The agents are put in the quarantine state after a delay, and if the delay > time between successive testing, then there's a backlog with the resultsbeing returned. 
            since the testing and isolating based on the results could have a delay, I use a FIFO queue, meaning you get the results for the 1st group first, then 2nd, then 3rd, ....

            Parameters:
            - None
        """
        
        # if agents got a screening, they get their results 
        if self.quarantine_intervention and len(self.quarantineList) > 0:
            if (self.time-self.config["Quarantine"]["ResultLatency"]) >= self.screeningTime[0]:  
                print(self.quarantineList, self.falsePositiveList, self.screeningTime)
                quarantined_agent = self.quarantineList.pop(0) # get the test result for the first group in the queue
                falsePos_agent = self.falsePositiveList.pop(0)
                resultTime = self.screeningTime.pop(0)
                
                if len(quarantined_agent)+len(falsePos_agent) > 0: 
                    if self._debug:
                        print(f"Isolating at time: {self.time}, {self.dateDescriptor}, {self.config['Quarantine']['ResultLatency']} delay isolation of {len(quarantined_agent) + len(falsePos_agent)} agents, there are {len(self.quarantineList)} group backlog")
                    for agentId in quarantined_agent:
                        self.changeStateDict(agentId, self.agents[agentId].state, "quarantined")
                    for agentId in falsePos_agent:
                        self.changeStateDict(agentId, self.agents[agentId].state, "quarantined")
                        self.addFalsePositive(agentId)

    def addFalsePositive(self, agentId):
        self.state2IdDict["falsePositive"].add(agentId)

    def checkForWalkIn(self):
        """
        when its 8AM, agents with symptoms will walkin for a check up, the probability that they will walkin differs based on how severe it is.

        Parameters:
        - None
        """
        if self.walkIn: # if people have a tendency of walkins and if it's 8AM
            mild, severe = self.state2IdDict["infected Symptomatic Mild"], self.state2IdDict["infected Symptomatic Severe"] 
            for agentId in mild|severe: # union of the two sets
                if self.agents[agentId].lastUpdate+23 > self.time: # people walkin if they seen symptoms for a day
                    # with some probability the agent will walkin
                    tupP = np.random.random(2) # (P of walking in,  P for false Pos)
                    if tupP[0] < self.config["Quarantine"]["walkinProbability"].get(self.agents[agentId].state, 0): # walkin occurs
                        if tupP[1] > self.config["Quarantine"]["falseNegative"]: # no false negatives
                            self.changeStateDict(agentId,self.agents[agentId].state, "quarantined")
         
    def big_gathering(self):
        if self.largeGathering: # big gathering at sunday midnight
            agentIds = [agentId for agentId, agent in self.agents.items() if agent.gathering]
            if len(agentIds) < 50:
                print("not enough for a party")
                return
            groupNumber = 3
            groupMinCount, groupMaxCount = 20, 60
            subsets, randVecs = [], []
            newly_infected = 0
            for _ in range(groupNumber):
                size = random.randint(groupMinCount,groupMaxCount)
                subsets.append(np.random.choice(agentIds, size=size, replace=False))
                randVecs.append(np.random.random(size))
            totalSubset = list({agentId for subset in subsets for agentId in subset})
            
            counter = self.countAgentsInGroup(totalSubset, "susceptible")
            totalinfectionVec = [0, 0, 0]
            for index, (subset, randVec) in enumerate(zip(subsets, randVecs)):
                totalInfection = self.gathering_infection(subset)
                totalinfectionVec[index] = totalInfection
                for index, agentId in enumerate(subset):
                    if self.agents[agentId].state == "susceptible" and randVec[index] < totalInfection: 
                        self.changeStateDict(agentId,"susceptible" ,"exposed")
                        newly_infected+=1
            self.gathering_count+=newly_infected
            if self._debug:
                print(f"big gathering at day {self.time/24}, at the gathering there were {counter} healthy out of {len(totalSubset)} and {newly_infected} additionally infected agents,", totalinfectionVec)

    def gathering_infection(self, subset):
        if self.faceMask_intervention:
            contribution = self.infectionWithinPopulation(subset, -1)
        else:
            contribution = self.infectionWithinPopulation(subset)
        cummulativeFunc = (self.baseP*3*contribution)/(40*(int(len(subset)/40)+1))
        return cummulativeFunc

    def returnStoredInfo(self):
        return self.parameters

    def returnMassInfectionTime(self):
        counts = np.zeros(len(self.parameters["recovered"]))
        massInfectionTime = 0
        for state in ["recovered", "infected Asymptomatic", "infected Asymptomatic Fixed", "infected Symptomatic Mild", "infected Symptomatic Severe"]:
                for row in self.parameters[state]:
                    counts+=np.array(row)
        
        for index, count in enumerate(counts):
            if count > len(self.agents)*self.config["massInfectionRatio"]:
                massInfectionTime = index
                
        return massInfectionTime

    def visualOverTime(self, boolVal = True, savePlt=False, saveName="defaultpic.png"):
        """
        Parameters:
        - boolVal
        - saveName
        """
        if boolVal:
            data = dict()
            print(list(self.parameters.keys()))
            
            data["Total infected"] = np.zeros(len(self.parameters[list(self.parameters.keys())[0]]))
            for key in self.parameters.keys():
                if key in ["susceptible", "quarantined", "recovered"]:
                    data[key] = self.parameters[key]
                elif key not in self.config["Agents"]["PossibleStates"]["debugAndGraphingPurpose"]: #ignore keys with debug purpose add the rest to infection count
                    data["Total infected"]+=np.array(self.parameters[key])
            data["recovered"] = self.parameters["recovered"]
        else:
            data = {k:v for k,v in self.parameters.items() if k not in self.config["Agents"]["PossibleStates"]["debugAndGraphingPurpose"]}
        data["susceptible"] = np.array(self.parameters["falsePositive"]) + np.array(data["susceptible"])    
        print([(key, value[-1], len(value)) for key, value in data.items()])
        x = int(self.time/self.config["World"]["stateCounterInterval"])+1
        data = {k:v[:x] for k, v in data.items()}
        #print("susceptible", data["susceptible"][:x])
        #print(self.time, x)    
        vs.timeSeriesGraph(self.timeSeries[:x], (0, self.time), (0,len(self.agents)), data, savePlt=savePlt, saveName=saveName, animatePlt=False)
    
    def visualizeBuildings(self):
        pairs = [(room, adjRoom[0]) for room, adjRooms in self.adjacencyDict.items() for adjRoom in adjRooms]
        nameDict = dict((roomId, room.room_name) for roomId, room in self.rooms.items())
        Building2Rooms = {buildingId:building.roomsInside for buildingId, building in self.buildings.items()}
        Rooms2Building = {roomId:buildingId for buildingId, value in Building2Rooms.items() for roomId in value}
        clusterName = {buildingId:building.building_type for buildingId, building in self.buildings.items()}
        roomCapacity = {roomId:room.capacity for roomId, room in self.rooms.items()}
        vs.makeGraph(self.rooms.keys(), pairs,Rooms2Building, Building2Rooms,clusterName, roomCapacity)
    
    def final_check(self):
        """
            used to print relevant inormation
        """
        # type and count dictionary
        print("*"*20, "abstactly represented location:")
        print("large gathering", self.gathering_count)
        print("*"*20, "breakdown for specific rooms:")
        for building in self.buildings.values():
            if building.building_type == "dining":
                for roomId in building.roomsInside:
                    if "faculty" in self.rooms[roomId].room_name:
                        print(f"in {self.rooms[roomId].room_name}, there were {self.rooms[roomId].infectedNumber} infection")
        print("*"*20, "filtering by building type:")
        
        for buildingType, count in self.infectedPerBuilding().items():
            print(buildingType, count)
           

    def infectedPerBuilding(self):
        counterDict, hubCounterDict = dict(), dict()
        for buildingId, building in self.buildings.items():
            buildingCount, buildingHub = 0, 0
            for roomId in building.roomsInside:
                buildingCount+=self.rooms[roomId].infectedNumber
                buildingHub+=self.rooms[roomId].hubCount
            counterDict[building.building_type] = counterDict.get(building.building_type, 0)+buildingCount 
            hubCounterDict[building.building_type] = hubCounterDict.get(building.building_type, 0)+buildingHub
            if self._debug:
                print(building.building_name, building.building_type, "whole building", buildingCount, "hubs", buildingHub)
        return counterDict
    
    def outputs(self):
        totalExposed = self.totalExposed()
        data = dict()
        data["TotalInfected"] = np.zeros(len(self.parameters[list(self.parameters.keys())[0]]))
        for key in self.parameters.keys():
            if key in ["susceptible", "quarantined", "recovered"]:
                data[key] = self.parameters[key]
            elif key not in self.config["Agents"]["PossibleStates"]["debugAndGraphingPurpose"]: #ignore keys with debug purpose add the rest to infection count
                data["TotalInfected"]+=np.array(self.parameters[key])
        
        newdata = dict()
        newdata["largeGathering"] = self.gathering_count
        for buildingType, count in self.infectedPerBuilding().items():
            newdata[buildingType] = count
        
        maxInfected = max(data["TotalInfected"])
        
        print(f"p: {self.baseP}, R0: {self.R0Calculation}, total ever in exposed {totalExposed}, max infected {maxInfected}")
        otherData = {"total":totalExposed, "max":maxInfected}
        return (newdata, otherData, data, totalExposed)

    def totalExposed(self):
        return len(self.agents) - self.parameters["susceptible"][-1] - self.parameters["falsePositive"][-1]

    def findDoubleTime(self):
        """
            returns a tuple of (doublingTime, doublingInterval, doublingValue)
        """
        data = dict()
        data["infected"] = np.zeros(len(self.parameters["susceptible"]))
        for key in self.parameters.keys():
            if key in ["susceptible"]:
                data[key] = self.parameters[key]
            else:
                data["infected"]+=np.array(self.parameters[key]) 
        doublingTime = []
        doublingValue = []
        previousValue = 0
        for i, entry in enumerate(data["infected"]):
            if entry >= 2*previousValue:
                doublingTime.append(i/24)
                doublingValue.append(entry)
                previousValue = entry
        doublingInterval = []
        for i in range(len(doublingTime)-1):
            doublingInterval.append(doublingTime[i+1]-doublingTime[i])
        return (doublingTime, doublingInterval, doublingValue)

def main():
    import start_here
    modelConfig = {
        "Agents" : {
            "PossibleStates":{
                "neutral" : ["susceptible", "exposed"],
                "infected" : ["infected Asymptomatic", "infected Asymptomatic Fixed", "infected Symptomatic Mild", "infected Symptomatic Severe"],  
                "recovered" : ["quarantined", "recovered"],
                "debugAndGraphingPurpose": ["falsePositive"],
                },
            "ExtraParameters":[
                        "agentId","path", "destination", "currLocation",
                        "statePersistance","lastUpdate", "personality", 
                        "arrivalTime", "schedule",  "gathering",
                        # "travelTime", "officeAttendee",
                ], # travelTime and officeAttendee will be commented out
            "ExtraZipParameters": [("motion", "stationary"), ("infected", False), ("compliance", False)],
            "booleanAssignment":[ ("gathering", 0.5)], # ("officeAttendee", 0),
            
        },
        "Rooms" : {
            "ExtraParameters": ["roomId","agentsInside","oddCap", "evenCap", "classname", "infectedNumber"],
        },
        "Buildings" : {
            "ExtraParameters": ["buildingId","roomsInside"],
        },
        "Infection" : {
            "baseP" : 1,
            "SeedNumber" : 10,
            "SeedState" : "exposed",
            "Contribution" : {
                "infected Asymptomatic":0.5,
                "infected Asymptomatic Fixed":0.5,
                "infected Symptomatic Mild":1,
                "infected Symptomatic Severe":1,
            },
            # INFECTION STATE
            "TransitionTime" : {
                "susceptible" : -1, # never, unless acted on
                "exposed" : 2*24, # 2 days
                "infected Asymptomatic" : 2*24, # 2 days
                "infected Asymptomatic Fixed" : 10*24, # 10 days
                "infected Symptomatic Mild" : 10*24,# 10 Days
                "infected Symptomatic Severe" : 10*24, # 10 days
                "recovered" : -1, # never
                "quarantined" : 24*14, # 2 weeks 
            },
            # INFECTION TRANSITION PROBABILITY
            "TransitionProbability" : {
                "susceptible" : [("exposed", 1)],
                "exposed" : [("infected Asymptomatic", 0.85), ("infected Asymptomatic Fixed", 1)],
                "infected Asymptomatic Fixed": [("recovered", 1)],
                "infected Asymptomatic": [("infected Symptomatic Mild", 0.5), ("infected Symptomatic Severe", 1)],
                "infected Symptomatic Mild": [("recovered", 1)],
                "infected Symptomatic Severe": [("recovered", 1)],
                "quarantined":[("susceptible", 1)],
                "recovered":[("susceptible", 0.5), ("recovered", 1)],
            },
        },
        "World" : {
            "UnitTime" : "Hours",
            # by having the supposed days to be simulated, 
            # we can allocate the required space beforehand to speedup data storing
            "InferedSimulatedDays":100,
            # put the name(s) of intervention(s) to be turned on 
            "TurnedOnInterventions":[],# ["HybridClasses", "ClosingBuildings", "Quarantine", "FaceMasks"], 
            "permittedAction": [],#["walkin"],
            #possible values:
            #    1: facemask
            #    3: testing for covid and quarantining
            #    4: closing large buildings
            #    5: removing office hours with professors
            #    6: shut down large gathering 
            "transitName": "transit_space_hub",
            "offCampusInfectionProbability":0.125/880,
            "massInfectionRatio":0.10,
            "complianceRatio": 0,
            "stateCounterInterval": 5,
            "socialInteraction": 0.2,
            "LazySunday": True,
           
        },
       
        # interventions
        "FaceMasks" : {
            "MaskInfectivity" : 0.5,
            "MaskBlock":0.75,
            "NonCompliantLeaf": ["dorm", "dining", "faculty_dining_hall"],
            "CompliantHub" : ["dorm", "dining"],
            "NonCompliantBuilding" : ["social", "largeGathering"],
        },
        "Quarantine" : {
            # this dictates if we randomly sample the population or cycle through Batches
            "RandomSampling": False,
            # for random sampling from the agent population
            "SamplingProbability" : 0,
   
            "ResultLatency":24,
            "walkinProbability" : {
                "infected Symptomatic Mild": 0.7, 
                "infected Symptomatic Severe": 0.95,
                },
            "BatchSize" : 400,
            
            "offset": 9, # start at 9AM
            "checkupFrequency": 24*1,
            "falsePositive":0.001,
            "falseNegative":0#0.03,
        },
        "ClosingBuildings": {
            "ClosedBuildingType" : ["gym", "library"],
            "ClosedButKeepHubOpened" : [],
        },
        "HybridClass":{
            "RemoteStudentCount": 1000,
            "RemoteFacultyCount": 180,
            "TurnOffLargeGathering": True,
        },

    }
    #model = createModel(modelConfig)
    #model.visualizeBuildings()
    start_here.main()

if __name__ == "__main__":
    main()