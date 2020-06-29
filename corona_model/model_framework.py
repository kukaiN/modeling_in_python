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
    loadDill = False
    saveDill = False
    pickleName = flr.fullPath("coronaModel.pkl", "picklefile")
    if not loadDill:
        model = AgentBasedModel()
        model.loadDefaultData(fileLoc)
        model.loadBuilder("newBuilding.csv")
        model.loadAgent("newAgent.csv")
        model.generateAgentFromDf()
        model.initializeWorld()
        model.startLog()
        model.initializeAgents()
        if saveDill:
            flr.saveUsingDill(pickleName, model)
            # save an instance for faster loading
            return 0
    else:
        model = flr.loadUsingDill(pickleName)
        print("loaded pickled object successfully")
    model.initilize_infection()
    
    # make schedules for each agents, outside of pickle for testing and for randomization
    model.makeSchedule()
    model.initializeRandomSchedule()
    model.initializeStoringParameter(["susceptible","exposed", "infected Asymptomatic" ,"infected Symptomatic", "recovered"], 
                                        steps=1)
    model.printRelevantInfo()
    
    for i in range(60):
        # change to steps
        model.updateSteps(10)
        model.printRelevantInfo()
    model.printLog()
    model.visualOverTime()
    #model.visualizeBuildings()
    
   
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
                        [nextNode, self.transit, lastNode] 
                    
                    self.move(adjDict)
            elif self.motion == "moving" and currTime >= self.travelTime + self.arrivalTime:
                self.move(adjDict)
                self.arrivalTime = currTime
            else: 
                
                return (self.currLocation, self.currLocation)
            return (curr_room, self.currLocation)

        def checkschedule(self, currTime):
            # there are 24*7 hours in a week
            # currTime%24*7 will give you the time in terms of week, then // 24 give you days
            # if the value is greater than 5, then its a weekday
            # if currTime is odd, then its a odd day and vise versa with even days
            dayOfWeek = (currTime%(24*7))//24
            hourOfDay = currTime%24
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
                #print("found destinations")
            elif self.path == []:
                pass
                self.motion = "stationary"
            else: # the agent is still moving
                self.motion = "moving"
                self.currLocation = self.path.pop()
                self.travelTime = 0
            return (pastLocation, self.currLocation)
   
        def getNextLocation(self):
            pass

        def simulate(self, numSimulation, steps):
            print(f"starting {numSimulation} simulation for {steps}")

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
        self.storeVal = False
        self.directedGraph = False
        self.randSchedule = False


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
        self.building_df, self.room_df = mod_df.mod_building(filename, folderName)
    
    
    def initializeWorld(self):
        # add a column to store the id of agents or rooms inside the strucuture
        for agentAttribute in ["archetypes","path", "destination", "currLocation","state_persistance","lastUpdate", "personality", "arrivalTime", "schedule", "travelTime"]:
            self.agent_df[agentAttribute] = 0 
        self.agent_df["motion"] = "stationary"
       
        
        self.building_df["rooms_inside"] = 0
        
        for roomVal in ["agentsInside", "odd_cap", "even_cap", "classname"]:
            self.room_df[roomVal] = 0
        print("*"*20)
        self.adjacencyDict = self.makeAdjDict()
        self.buildings = self.makeClass(self.building_df, superStrucFactory)
        self.rooms = self.makeClass(self.room_df, roomFactory)
        
        self.roomsInBuilding = dict((buildingId, []) for buildingId in self.buildings.keys())
        self.buildingNameId = dict((getattr(building, "building_name"), buildingId) for buildingId, building in self.buildings.items())
        self.buildingTypeId = dict((getattr(building, "building_type"), buildingId) for buildingId, building in self.buildings.items())
        self.roomNameId = dict((getattr(room, "room_name"), roomId) for roomId, room in self.rooms.items())
        self.setTransitHub()
        self.addRoomsToBuildings()
        self.agents = self.makeClass(self.agent_df, agentFactory)
        self.randomPersonality()


    def setTransitHub(self):
        transit_id = self.roomNameId["transit_space_hub"]
        print("adj", self.adjacencyDict[transit_id])
        self.agent_df["transit"] = transit_id

    def randomPersonality(self):
        """
            randomly assign a major and personality to the agents
        """

        personalities = ["athletic", "introvert", "party people", "people", "terminators", "aliens"]
        majors = ["stem", "humanities", "arts"]
        numAgent = len(self.agents)
        randPersonalities = np.random.choice(personalities, numAgent)
        randMajors = np.random.choice(majors, numAgent)
        for index, agent in enumerate(self.agents.values()):
            agent.personality = randPersonalities[index]
            agent.archetypes = randMajors[index]

    

    def addRoomsToBuildings(self):
        """add room_id to associated buildings"""
        for roomId, rooms in self.rooms.items():
            self.roomsInBuilding[self.buildingNameId[rooms.located_building]].append(roomId) 

    def generateAgentFromDf(self, counterColumn="totalCount"):
        """use this to multiple the number of agents, multiplies by looking at the counterColumn"""
        slotVal = self.agent_df.columns.values.tolist()
        if counterColumn in slotVal:
            slotVal.remove(counterColumn)
        tempList = []
        for _, row in self.agent_df.iterrows():
            counter = row[counterColumn]
            rowCopy = row.drop(counterColumn).to_dict()
            tempList+=[rowCopy for _ in range(counter)]
        self.agent_df = pd.DataFrame(tempList)     
        

    def initializeAgents(self):
        # convert agent's location to the corresponding room_id and add the agent's id to the room member
        for rooms in self.rooms.values():
            rooms.agentsInside = []
        numOfRooms = len(self.rooms)
        for agentId, agent in self.agents.items():
            initialLoc = getattr(agent, "initial_location")
            if initialLoc in self.buildingNameId.keys(): # if location is under building name
                # randomly choose rooms from the a building
                possibleRooms = self.roomsInBuilding[self.buildingNameId[initialLoc]]
                location = np.random.choice(possibleRooms)
            elif initialLoc in self.buildingTypeId.keys(): # if location is under building type
                
                possibleRooms = self.roomsInBuilding[self.buildingTypeId[initialLoc]]
                location = np.random.choice(possibleRooms)
            elif initialLoc in self.roomNameId.keys(): # if the room is specified
                # convert the location name to the corresponding id
                location = self.roomNameId[initialLoc]
            else:
                print("something wrong")
                # either the name isnt properly defined or the room_id was given
                location = initialLoc
                location = random.randint(0, numOfRooms-1)
            agent.currLocation = location
            agent.initial_location = location
            self.rooms[location].agentsInside.append(agentId)

    def makeSchedule(self):
        """part 1, dedicate a class to rooms"""
        
        self.numAgent = len(self.agents.items())
        archetypeList = [agent.archetypes for agent in self.agents.values()]
        classIds = list(roomId for roomId, room in self.rooms.items() if room.building_type == "classroom" and not room.room_name.endswith("hub"))
        capacities = list(self.rooms[classId].limit for classId in classIds)
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
          

    def replaceStaticEntries(self):
        """
        part 2
        replaces the static locations with the corresponding Ids
        """
        for i, agent in enumerate(self.agents.values()):
            self.scheduleList[i] = self.replaceEntry(self.scheduleList[i], "sleep", getattr(agent, "currLocation"))

    def initializeRandomSchedule(self,t=-1, agentTypes=[]):
        """random schedule part 1"""
        self.randSchedule = True if t < 0 else False 
        self.activityList = ["eating", "gym", "study", "off_campus"]
        self.buildingList = ["dining_hall", "gym", "library", "node"]
        self.activityCount = schedule.countSchedule(self.scheduleList, self.activityList)
        self.activityLocList = [self.findMatchingRooms("building_type", loc) for loc in self.buildingList]
        print(len(self.activityLocList))
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
        for scheduleIndex, agent in self.agents.items():
            scheduleChart = self.scheduleList[scheduleIndex]
            # replace and randomize the rest
            for index, location in enumerate(self.randomSchedule):
                for i, row in enumerate(scheduleChart):
                    for j, content in enumerate(row):
                        if content == self.activityList[index]:
                            scheduleChart[i][j] = location[indices[index]]
                            indices[index]+=1
            agent.schedule = scheduleChart
            

    def replaceEntry(self, schedule, antecedent, replacement):
        """ replace entry with a different value"""
        return [[a if a != antecedent else replacement for a in row] for row in schedule]

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



    def findMatchingRooms(self, roomParam, roomVal, strType=False):
        """returns a list of room IDs that have a specific value for one of its parameter"""
        if strType: # case insensitive
            return [roomId for roomId, room in self.rooms.items() if getattr(room, roomParam).strip().lower() == roomVal.strip().lower() and not getattr(room, "room_name").endswith("hub")]
        else:
            return [roomId for roomId, room in self.rooms.items() if getattr(room, roomParam) == roomVal and not getattr(room, "room_name").endswith("hub")]

    def convertToRoomName(self, idList):
        return [[self.rooms[roomId].room_name for roomId in row] for row in idList]
        


    # update functions
    def updateSteps(self, step = 1):
        """ 
        a function that updates the time and calls other update functions, 
        you can also set how many steps to update"""
        for t in range(step):
            print(self.agents[1].currLocation)
            self.time+=1
            if self.time % (24*7) == 0:
                self.replaceScheduleValues()
                print(self.convertToRoomName(self.scheduleList[0]))
            for _ in range(4):
                self.updateAgent()
            if 22 > self.time%24 > 8:
                self.infection()
            if self.storeVal and self.time%self.timeIncrement == 0:
                self.storeInformation()
            self.logData()

    def startLog(self):
        self.building_log = dict((key,[]) for key in self.buildings.keys())
        self.room_log = dict((key,[]) for key in self.rooms.keys())
        self.room_cap_log = dict((key,[]) for key in self.rooms.keys())

    def logData(self):
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
            1208 library
            1209 library2
            1210 library3
            1211 library4
            1212 library5
            1213 library6
            1214 library7
            1215 library8
            1216 library_hub
            1217 gym
            1218 gym2
            1219 gym3
            1220 gym4
            1221 gym5
            1222 gym6
            1223 gym7
            1224 gym8
            1225 gym_hub
        """
        sus = "susceptible"
        exp = "exposed"
        infA = "infected Asymptomatic"
        infS = "infected Symptomatic"
        rec = "recovered"
        for roomId, room in self.rooms.items():
            total_infected = sum(self.countWithinAgents(room.agentsInside, stateName) for stateName in [exp, infA, infS])
            self.room_log[roomId].append(total_infected)
        
        for roomId, room in self.rooms.items():
            #if "gym" in room.room_name:
            #    print(room.room_name, len(room.agentsInside))
            self.room_cap_log[roomId].append(len(room.agentsInside))

    def printLog(self):
        for agentId in self.rooms[self.roomNameId["gym"]].agentsInside:
            print(self.agents[agentId].motion)
        
        for i in range(1, 10):
            sche = self.agents[i].schedule
            for row in sche:
                print(self.getRoomNames(row))
        for key, value in self.room_cap_log.items():
            if self.rooms[key].building_type == "gym":
                a = np.array(value).reshape((-1,24))
                x, y = a.shape
                zzz = np.sum(a, axis=0)
                print("gym", zzz)

        for roomId, room in self.rooms.items():
            if room.building_type in ["classroom"]:
                pass
            else:
                print(roomId, room.room_name)

    def getRoomNames(self, listOfRoomsId):
        return list(self.rooms[roomId].room_name for roomId in listOfRoomsId)

    def updateAgent(self):
        """call the update function on each person"""
        count = 0
        
        for agentId, agent in self.agents.items():
      
            loc = agent.updateLoc(self.time, self.adjacencyDict)
            if loc[0] != loc[1]:
                self.rooms[loc[0]].leave(agentId)
                self.rooms[loc[1]].enter(agentId)
                count+=1
      

      # handles the infection
    
    def initilize_infection(self):
        sus = "susceptible"
        sp = "state_persistance"
        exp = "exposed"
        for agent in self.agents.values():
            agent.state = sus
            # negative means it goes for infinity
            agent.state_persistance = -1
        seed_num = 20
        for agent_num in np.random.choice(range(1, len(self.agents.keys())),size=seed_num):
            self.agents[agent_num].state = exp
    
    def findR0(self):
        print("findinf R0")
    
    def infection(self):
        sus = "susceptible"
        exp = "exposed"
        infA = "infected Asymptomatic"
        infS = "infected Symptomatic"
        rec = "recovered"
        transition = {
            exp:4*24,
            infA:4*24,
            infS:7*24,
            rec:-1
            }
        transition_probability = {
            exp: [(infA, 1)],
            infA: [(infS, 0.5), (rec, 1)],
            infS: [(rec, 1)]
        }
        baseP = 0.01 # 0.01
        randVec = np.random.random(len(self.agents))
        index = 0
        for roomId, room in self.rooms.items():
            #totalInfected = sum(self.countWithinAgents(room.agentsInside, strVal) for strVal in [exp, infA, infS])
            totalInfected = self.infectivityPerRoom(roomId)
            for agentId in room.agentsInside:
                if room.capacity == 0: print(room.room_name, room.located_building)
                if self.agents[agentId].state == sus and randVec[index] < (baseP*room.Kv*totalInfected)/room.limit: 
                    self.agents[agentId].state = exp
                    self.agents[agentId].state_persistance = transition[exp]
                    self.agents[agentId].lastUpdate = self.time
                else:
                    state = self.agents[agentId].state
                    if self.agents[agentId].lastUpdate + self.agents[agentId].state_persistance > self.time and transition[state] > 0:
                        cdf = 0
                        for tup in transition_probability[state]:
                            if tup[1] > randVec[index] >= cdf:
                                cdf+=tup[1]
                                next_state = tup[0] 
                        self.agents[agentId].state = next_state
                        self.agents[agentId].state_persistance = transition[state] 
                index +=1    


    def infectivityPerRoom(self, roomId, states = [ "exposed", "infected Asymptomatic", "infected Symptomatic"]):
        agentsInRoom = self.rooms[roomId].agentsInside
        contribution = 0 
        for agentId in agentsInRoom:
            agentState = self.agents[agentId].state
            lastUpdate = self.agents[agentId].lastUpdate
            contribution+= self.infectionContribution(agentState, lastUpdate)
        return contribution

    def infectionContribution(self, state, lastUpdate):
        if state == "exposed":
            return (self.time - lastUpdate)/2
        elif state == "infected Asymptomatic":
            return (self.time - lastUpdate)*2
        elif state == "infected Symptomatic":
            return 10/(self.time - lastUpdate)
        else:
            return 0

                
    # functions used to store or print information
    def countWithinAgents(self, agentList, stateName):
        return len(list(filter(lambda x: x.state == stateName, [self.agents[val] for val in agentList]))) 

    def countAgents(self, stateVal, attributeName="state"):
        return len(list(filter(lambda x: getattr(x, attributeName) == stateVal, self.agents.values() )))

    def printRelevantInfo(self):
        """ print relevant information about the model and its current state, 
        this is the same as __str__ or __repr__, but this function is for debug purpose,
        later on this functio n will be converted to the proper format using __repr__"""
        sus = "susceptible"
        exp = "exposed"
        infA = "infected Asymptomatic"
        infS = "infected Symptomatic"
        rec = "recovered"
        susc = self.countAgents(sus)
        expo = self.countAgents(exp)
        ia = self.countAgents(infA)
        ias = self.countAgents(infS)
        recovered = self.countAgents(rec)
        print(f"time: {self.time}, Susceptible {susc} E: {expo}, I Asympto: {ia}, I Sympto: {ias}, recovered: {recovered}")
    
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
            self.parameters[param].append(self.countAgents(param, attributeName="state"))

    def visualOverTime(self):
        vs.timeSeriesGraph(self.timeSeries, (0, self.time+1), (0,len(self.agents)), self.parameters)
    
    def visualizeBuildings(self):
        if True:
            pairs = [(room, adjRoom[0]) for room, adjRooms in self.adjacencyDict.items() for adjRoom in adjRooms]
            nameDict = dict((roomId, room.room_name) for roomId, room in self.rooms.items())
            vs.makeGraph(self.rooms.keys(), nameDict, pairs, self.buildings, self.roomsInBuilding, self.rooms)
        
  
    # need to build
    def MMs_QueueingModel(self, lambda_val, mean):
        pass


    # need to build
    def define_offcampus(self):
        for agent in self.agent():
            pass

if __name__ == "__main__":
    main()    
