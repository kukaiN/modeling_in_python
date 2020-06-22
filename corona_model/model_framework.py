import os
import random
import pandas as pd
import pickle
import fileRelated as flr
import numpy as np
import bisect
import visualize as vs
import modifyDf as mod_df
import schedule

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
        "schedule_info"     : "schedules.csv"
    }
    folderName, fileName = "configuration", "new_building.csv"
    model = AgentBasedModel()
    model.loadData(fileLoc, True, folderName, fileName)
    model.initialize()
    model.initializeAgents()
    model.initializeStoringParameter(["healthy", "infected", "recovered"])
    model.printRelevantInfo()
    
    for i in range(10):
        # change to steps
        model.updateSteps(10)
        model.printRelevantInfo()
        model.storeInformation()
    model.visualOverTime()
    model.visualizeBuildings()
    #model.printRelevantInfo()
    #if str(input("does all the information look correct?")) in ["T", "t", "y", "Y", "Yes"]:
    #    pass
   
def agentFactory(agent_df, slotVal =  ["name", "age", "gender", "immunity", "curr_location", "motion" "health_state", "archetype", "personality", "arrival_time", "path_to_dest", "waiting_time"]):
    """
        factory function used to dynamically assign __slots__, creates agents from the given df
        the values stored in __slots__ are the column of the df and some additional parameters that deals with relatinships and membership
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
            """
            threshold = 0.4
            if self.motion == "stationary" and currTime > self.arrivalTime:
                if random.random() < threshold:
                    rooms = list(adjDict.keys())
                    self.destination =  np.random.choice(rooms, 1)
                    self.moveTo(adjDict)
            elif self.motion == "moving" and currTime > self.travelTime + self.arrivalTime:
                self.moveTo(adjDict)
                self.arrivalTime = currTime
            else: 
                return (self.currLocation, self.currLocation)

        def move_to(self, adjDict):
            """
                chooses the random room and moves the agent inside
            """
            pastLocation = self.currLocation
            if findTuple(self.destination, adjDict[self.currLocation], 1) != None:
                # the agent reached it's destination, takes a rest
                self.currLocation = self.destination
                self.destination = None
                self.motion = "stationary"
            else: # the agent is still moving
                self.motion = "moving"
                # choose a random room and go to it
                nextPartition = np.random.choice(adjDict[self.currLocation])
                self.travelTime = nextPartition[1]
                self.currLocation = nextPartition[0]
            return (pastLocation, self.currLocation)

        def makeSchedule(self, scheduleList):
            a = self.personality
            b = self.archetypes

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
    """
    class Partitions:
        __slots__ = slotVal
        def __init__(self, roomParam):
            for slot, value in zip(self.__slots__, roomParam):
                self.__setattr__(slot, value)

        def enter(self, agentId):
            """ a put the id of the agent that entered the room"""
            if self.checkCapacity():
                self.agentsInRoom.append(agentId)

        def checkCapacity(self):
            """return a boolean, return True if theres capacity for one more agent, False if the room is at max capacity 
            """
            if len(self.agentsInRoom) < self.capacity:
                return True
            return False
    
        def leave(self, agentId):
            """ remove the id of the agent that exited the room"""
            if agentId in self.agentsInRoom:
                self.agentsInRoom.remove(agentId)
        
    tempDict = dict()
    for index, row in room_df.iterrows():
        tempDict[index] = Partitions(row.values.tolist())
    return tempDict
    
def superStrucFactory(struc_df, slotVal):
    """
        creates and returns a dictionary that keeps the building class
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
        # get the dataframe of individual components
        self.time = 0
        self.directedGraph = True

    def loadData(self, files, oneFile=False, fileName="configuration", folder="new_building.csv"):
        """load the data in a csv and load it as a panda dataframe"""
        if oneFile:
            self.building_df, self.room_df = mod_df.mod_building() 
        else:
            self.building_df = flr.make_df(files["info_folder"], files["building_info"]) 
            self.room_df = flr.make_df(files["info_folder"], files["room_info"]) 
        self.agent_df = flr.make_df(files["info_folder"], files["agent_info"]) 
        self.schedule_df = flr.make_df(files["info_folder"], files["schedule_info"]) 
        # get the config of the individual components
        self.agent_config = flr.loadConfig(files["config_folder"], files["agent_config"])
        self.room_config = flr.loadConfig(files["config_folder"], files["room_config"])
        self.building_config = flr.loadConfig(files["config_folder"], files["building_config"])
        self.schedule_config = flr.loadConfig(files["config_folder"], files["schedule_config"])
        
    def initialize(self):
        # add a column to store the id of agents or rooms inside the strucuture
        for agentAttribute in ["currLocation", "motion", "personality", "arrivalTime", "schedule", "travelTime"]:
            self.agent_df[agentAttribute] = 0 
        self.building_df["rooms_inside"] = 0
        for roomVal in ["agents_inside", "odd_cap", "even_cap", "classname"]:
            self.room_df[roomVal] = 0
        self.room_df["limit"] = [int(x*0.8 + 0.5) for x in self.room_df["capacity"]] # 80% limit
        print("*"*20)
        self.adjacencyDict = self.makeAdjDict()
        self.buildings = self.makeClass(self.building_df, superStrucFactory)
        self.rooms = self.makeClass(self.room_df, roomFactory)
        self.agents = self.makeClass(self.agent_df, agentFactory)
        self.randomPersonality()
        self.makeSchedule()
        self.roomsInBuilding = dict((buildingId, []) for buildingId in self.buildings.keys())
        self.buildingNameId = dict((getattr(building, "building_name"), buildingId) for buildingId, building in self.buildings.items())
        self.roomNameId = dict((getattr(room, "room_name"), roomId) for roomId, room in self.rooms.items())
        self.addRoomsToBuildings()

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

    def makeSchedule(self):
        """dedicate a class to rooms"""
        self.scheduleChart = ["math", "stem", "english", "humanities", "philosophy", "sleeping"]
        self.scheduleDict = dict((key, []) for key in self.scheduleChart)
        classroomsCount = len(self.room_df[self.room_df["building_type"] == "classroom"])
        print(classroomsCount)
        self.randomClass = np.random.choice(self.scheduleChart, classroomsCount)
        index = 0
        for room_id, room in self.rooms.items():
            if room.building_type == "classroom":
                room.classname = self.randomClass[index]
                self.scheduleDict[room.classname].append(room_id) 
                index +=1



    def addRoomsToBuildings(self):
        """add room_id to associated buildings"""
        for roomId, rooms in self.rooms.items():
            self.roomsInBuilding[self.buildingNameId[rooms.located_building]].append(roomId) 

    def initializeAgents(self):
        # convert agent's location to the corresponding room_id and add the agent's id to the room member
        for rooms in self.rooms.values():
            rooms.agents_inside = []
        numOfRooms = len(self.rooms)
        for agentId, agents in self.agents.items():
            initialLoc = getattr(agents, "initial_location")
            if initialLoc in self.buildingNameId.keys():
                # randomly choose rooms from the a building
                possibleRooms = self.roomsInBuilding[self.buildingNameId[initialLoc]]
                location = np.random.choice(possibleRooms)
            elif initialLoc in self.roomNameId.keys():
                # convert the location name to the corresponding id
                location = self.roomNameId[initialLoc]
            else:
                # either the name isnt properly defined or the room_id was given
                location = initialLoc
                location = random.randint(0, numOfRooms-1)
            agents.currLocation = location
            self.rooms[location].agents_inside.append(agentId)

    def makeAdjDict(self):
        """ creates an adjacency list implimented with a dictionary"""
        adjDict = dict()
        for roomId, row in self.room_df.iterrows():
            adjRoom = self.room_df.index[self.room_df["room_name"] == row["connected_to"]].tolist()[0]
            travelTime = row["travel_time"]
            adjDict[roomId] = adjDict.get(roomId, []) + [(adjRoom, travelTime)]
            if not self.directedGraph:
                adjDict[adjRoom] = adjDict.get(adjRoom,[]) + [(roomId, travelTime)]
        return adjDict
    
    def makeClass(self, dfRef, func):
        slotVal = dfRef.columns.values.tolist()
        tempDict = func(dfRef, slotVal)
        numObj, objVal = len(tempDict), list(tempDict.values())
        className = objVal[0].__class__.__name__ if numObj > 0 else "" 
        print(f"creating {numObj} {className} class objects, each obj will have __slots__ = {slotVal}")
        return tempDict

    def updateSteps(self, step = 1):
        """ 
        a function that updates the time and calls other update functions, 
        you can also set how many steps to update"""
        for t in range(step):
            self.time+=1
            self.updateAgent()
            self.infection()

    def updateAgent(self):
        """call the update function on each person"""
        for agentId, agent in self.agents.items():
            loc = agent.updateLoc(self.time, self.adjacencyDict)
            if loc[0] != loc[1]:
                self.rooms[loc[0]].leave(agentId)
                self.rooms[loc[1]].enter(agentId)

    def countWithinAgents(self, agentList, stateName):
        return len(list(filter(lambda x: x.state == stateName, [self.agents[val] for val in agentList]))) 

    def countAgents(self, stateName):
        return len(list(filter(lambda x: x.state == stateName, self.agents.values() )))

    def printRelevantInfo(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this functio n will be converted to the proper format using __repr__"""
        infected = self.countAgents("infected")
        carrier = self.countAgents("carrier")
        dead = self.countAgents("dead")
        healthy = self.countAgents("healthy")
        recovered = self.countAgents("recovered")
        print(f"time: {self.time} total healthy {healthy} infected: {infected}, carrier: {carrier}, dead: {dead}, recovered: {recovered}")
        #print(f" agent's locations is {list(room.agents_in_room for room in self.room_dict.values())}")
        #print(f"agent's location is {self.room_agent_dict}")
    
    def initializeStoringParameter(self, listOfStatus):
        self.parameters = dict((param, []) for param in listOfStatus)
        self.timeSeries = []

    def storeInformation(self):
        self.timeSeries.append(self.time)
        for param in self.parameters.keys():
            self.parameters[param].append(self.countAgents(param))

    def visualOverTime(self):
        vs.timeSeriesGraph(self.timeSeries, (0, self.time+1), (0,len(self.agents)), self.parameters)
    
    def visualizeBuildings(self):
        if True:
            pairs = [(room, adjRoom[0]) for room, adjRooms in self.adjacencyDict.items() for adjRoom in adjRooms]
            nameDict = dict((roomId, room.room_name) for roomId, room in self.rooms.items())
            vs.makeGraph(self.rooms.keys(), nameDict, pairs, self.buildings, self.roomsInBuilding, self.rooms)
        

    def infection(self):
        baseP = 0.001 # 0.01
        randVec = np.random.random(len(self.agents))
        index = 0
        for room in self.rooms.values():
            totalInfected = self.countWithinAgents(room.agents_inside, "infected")
            for agentId in room.agents_inside:
                if self.agents[agentId].state == "healthy" and randVec[index] < baseP*totalInfected/room.limit: 
                    self.agents[agentId].state = "infected"
                else:
                    state = self.agents[agentId].state
                    if state == "infected":
                        if randVec[index] < 0.05:
                            self.agents[agentId].state = "recovered"
                index +=1    

    def MMs_QueueingModel(self, lambda_val, mean):
        pass

if __name__ == "__main__":
    main()    
