import model_framework
import platform
import statfile
import copy


def main():
    """intialize and run the model, for indepth detail about the config or how to run the code, go to the github page for this code"""
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
            "ExtraParameters": ["roomId","agentsInside","oddCap", "evenCap", "classname", "infectedNumber", "hubCount"],
        },
        "Buildings" : {
            "ExtraParameters": ["buildingId","roomsInside"],
        },
        "Infection" : {
            "baseP" : 1.25,
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

            "transitName": "transit_space_hub",
            "offCampusInfectionProbability":0.125/880,
            "massInfectionRatio":0.10,
            "complianceRatio": 0,
            "stateCounterInterval": 5,
            "socialInteraction": 0.15,
            "LazySunday": True,
            "LargeGathering": True,
            "DynamicCapacity": False,
        },

        # interventions
        "FaceMasks" : {
            "MaskInfectivity" : 0.5,
            "MaskBlock":0.75,
            "NonCompliantLeaf": ["dorm", "dining", "faculty_dining_hall", "faculty_dining_room"],
            "CompliantHub" : ["dorm", "dining"],
            "NonCompliantBuilding" : ["largeGathering"],
        },
        "Quarantine" : {
            # this dictates if we randomly sample the population or cycle through Batches
            "RandomSampling": False,
            "RandomSampleSize": 100,
            # for random sampling from the agent population
            "SamplingProbability" : 0,
            "ResultLatency":2*24,
            "WalkIn":True,
            "walkinProbability" : {
                "infected Symptomatic Mild": 0.7,
                "infected Symptomatic Severe": 0.95,
                },
            "BatchSize" : 100,
            "ShowingUpForScreening": 1,
            "offset": 8, # start at 8AM
            "checkupFrequency": 24*1,
            "falsePositive":0.001,
            "falseNegative":0.03
        },
        "ClosingBuildings": {
            "ClosedBuildingOpenHub" : [],
            # close buildings in the list(remove them from the schedule), and go home or go to social spaces
            "ClosedBuilding_ByType" : ["gym", "library"],
            "GoingHomeP": 0.5,
            # the building in the list will be removed with probability and replaced with going home, otherwise it stays
            "Exception_SemiClosedBuilding": [],
            "Exception_GoingHomeP":0.5,

        },
        "HybridClass":{
            "RemoteStudentCount": 500,
            "RemoteFacultyCount": 180,
            "RemovedDoubleCount": 0,
            "OffCampusCount": 500,
            "TurnOffLargeGathering": True,
            "ChangedSeedNumber": 10,
        },
        "LessSocializing":{
            "StayingHome":0.5
        }

    }

    # you can control for multiple interventions by adding a case:
    #  [(modified attr1, newVal), (modified attr2, newVal), ...]

    # simulation name --> simulation controlled variable(s)
    # dont use . or - in the simulation name because the names are used to save images, or any symbols below

    ControlledExperiment = {
        "baseModel":{
        }, # no changes
        "facemasks":{
            "World": [
                ("TurnedOnInterventions", ["FaceMasks"]),
                ("ComplianceRatio", 1),
                ],
        },
        "highDeden":{
            "World": [
                ("TurnedOnInterventions", ["HybridClasses"]),
                ],
            "HybridClass":[
                ("RemoteStudentCount", 500),
                ("RemoteFacultyCount", 300),
                ("RemovedDoubleCount", 525),
                ("OffCampusCount", 500),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 5),
            ],
        },
        "lessSocial":{
            "World": [
                ("TurnedOnInterventions", ["LessSocial"]),
                ],
        },
        "Quarantine":{
            "World": [
                ("TurnedOnInterventions", ["Quarantine"]),
            ],
            "Quarantine": [
                ("ResultLatency", 2*24),
                ("BatchSize", 500),
                ("ShowingUpForScreening", 1),
            ],
        },
        "Medium+L4":{
            "World": [
                ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
            ],
             "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", False),
                ("ChangedSeedNumber", 7),
            ],
        },
        "Medium+L3":{
            "World": [
                ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
            ],
             "Quarantine": [
                ("ResultLatency", 3*24), # L = 3
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", False),
                ("ChangedSeedNumber", 7),
            ],
        },
        "Medium+L2":{
            "World": [
                ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
            ],
             "Quarantine": [
                ("ResultLatency", 2*24), # L = 2
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", False),
                ("ChangedSeedNumber", 7),
            ],
        },
        "Medium+L1":{
            "World": [
                ("TurnedOnInterventions", ["Quarantine","HybridClasses"]),
            ],
             "Quarantine": [
                ("ResultLatency", 1*24), # L = 1
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", False),
                ("ChangedSeedNumber", 7),
            ],
        },

        "NC_WP":{
            # N = 100, L = 4, B = {G, L}, D = 0
            # f = 0, c = 0.80, h = 0.50, s' = 0
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "LessSocial", "ClosingBuildings"]),
                ("ComplianceRatio", 0), # f = 0
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 100), # N=100
                ("ShowingUpForScreening", 0.8), # c = 0.8
            ],
            "ClosingBuildings": [
            ("ClosedBuildingOpenHub", []),
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.5), # h = 0.5
            ("Exception_SemiClosedBuilding", []),
            ("Exception_GoingHomeP", 0.5),
            ],
            "LessSocializing":[
                ("StayingHome",0), # s'
            ],
        },
        "NC_MP":{
            #N = 250, L = 3, B = {G, L, DH, LG}, D=650
            # f = 0, c = 0.80, h = 0.50, s' = 0
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 0), # f = 0
                ("LargeGathering", False)
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), # L = 3
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 0.8), # c = 0.8
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0####################################
                ("ClosedBuilding_ByType", ["gym", "library"]),
                ("GoingHomeP", 0.5), # h = 0.5
                ("Exception_SemiClosedBuilding",["dining", "faculty_dining_room"]), # replace these entrys 50/50###############
                ("Exception_GoingHomeP", 0.5),
            ],
            "LessSocializing":[
                ("StayingHome",0), # s'
            ],
            "HybridClass":[############################################################
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 doubles, extra agents = 200, means need 200 double beds available
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 7),
            ],
        },
        "NC_SP":{
            #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
            # f = 0, c = 0.80, h = 0.50, s' = 0
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 0), # f = 0
                ("LargeGathering", False)
            ],
            "Quarantine": [
                ("ResultLatency", 2*24), # L = 2
                ("BatchSize", 500), # N=500
                ("ShowingUpForScreening", 0.8), # c=0.8
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]),
                ("ClosedBuilding_ByType", ["gym", "library", "office"]),
                ("GoingHomeP", 0.5), # h = 0.5
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
                ("Exception_GoingHomeP", 0.5), # h = 0.5
            ],
            "LessSocializing":[
                ("StayingHome",0), # s'
            ],
            "HybridClass":[
                ("RemoteStudentCount", 500),
                ("RemoteFacultyCount", 300),
                ("RemovedDoubleCount", 525), #525 = total number of double
                ("OffCampusCount", 500),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 5),
            ],
        },

        "SC_WP":{
            # N = 100, L = 4, B = {G, L}, D = 0
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 100), # N=100
                ("ShowingUpForScreening", 0.9), # c = 0.9#############
            ],
            "ClosingBuildings": [
            ("ClosedBuildingOpenHub", []),
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 0.75), # h = 0.75 ##################
            ("Exception_SemiClosedBuilding", []),
            ("Exception_GoingHomeP", 0.75),
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25 ######################
            ],
        },
        "SC_MP":{
            #N = 250, L = 3, B = {G, L, DH, LG}, D=650
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), # L = 3
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 0.9), # c = 0.9
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0
                ("ClosedBuilding_ByType", ["gym", "library"]),
                ("GoingHomeP", 0.75), # h = 0.75
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]), # replace these entrys 50/50
                ("Exception_GoingHomeP", 0.75),
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 7),
            ],
        },
        "SC_SP":{
            #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 2*24), # L = 2
                ("BatchSize", 500), # N=500
                ("ShowingUpForScreening", 0.9), # c = 0.9
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]),
                ("ClosedBuilding_ByType", ["gym", "library", "office"]),
                ("GoingHomeP", 0.75), # h = 0.75
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
                ("Exception_GoingHomeP", 0.75), # h = 0.5
            ],
            "LessSocializing":[
                ("StayingHome",0.25), # s' = 0.25
            ],
            "HybridClass":[
                ("RemoteStudentCount", 500),
                ("RemoteFacultyCount", 300),
                ("RemovedDoubleCount", 525), #525 = total number of double
                ("OffCampusCount", 500),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 5),
            ]
        },
        "VC_WP":{
            # N = 100, L = 4, B = {G, L}, D = 0
            # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 1), # f = 1
                ("LargeGathering", False),
            ],
            "Quarantine": [
                ("ResultLatency", 4*24),
                 # L = 4
                ("BatchSize", 100), # N=100
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "ClosingBuildings": [
            ("ClosedBuildingOpenHub", []),
            ("ClosedBuilding_ByType", ["gym", "library"]),
            ("GoingHomeP", 1), # h = 1
            ("Exception_SemiClosedBuilding", []),
            ("Exception_GoingHomeP", 1),
            ],
            "LessSocializing":[
                ("StayingHome",0.75), # s'
            ],
        },
        "VC_MP":{
            #N = 250, L = 3, B = {G, L, DH, LG}, D=650
            # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 1), # f = 1
                ("LargeGathering", False)
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), # L = 3
                ("BatchSize", 250), # N=250
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]), # ding stays open, but leaf Kv = 0
                ("ClosedBuilding_ByType", ["gym", "library"]),
                ("GoingHomeP", 1), # h = 1
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]), # replace these entrys 50/50
                ("Exception_GoingHomeP", 1),
            ],
            "LessSocializing":[
                ("StayingHome",0.75), # s'
            ],
            "HybridClass":[
                ("RemoteStudentCount", 250),
                ("RemoteFacultyCount", 150),
                ("RemovedDoubleCount", 325), # 525 - 250 = 275
                ("OffCampusCount", 250),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 7),
            ],
        },
        "VC_SP":{
            #N = 500, L = 2, B = {G, L, DH, LG, O}, D=1300
            # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial", "HybridClasses"]),
                ("ComplianceRatio", 1), # f = 1
                ("LargeGathering", False)
            ],
            "Quarantine": [
                ("ResultLatency", 2*24), # L = 2
                ("BatchSize", 500), # N=500
                ("ShowingUpForScreening", 1), # c = 1
            ],
            "ClosingBuildings": [
                ("ClosedBuildingOpenHub", ["dining"]),
                ("ClosedBuilding_ByType", ["gym", "library", "office"]),
                ("GoingHomeP", 1), # h = 1
                ("Exception_SemiClosedBuilding", ["dining", "faculty_dining_room"]),
                ("Exception_GoingHomeP", 1), # h = 1
            ],
            "LessSocializing":[
                ("StayingHome",0.75), # s' = 0.75
            ],
            "HybridClass":[
                ("RemoteStudentCount", 500),
                ("RemoteFacultyCount", 300),
                ("RemovedDoubleCount", 525), #525 = total number of double
                ("OffCampusCount", 500),
                ("TurnOffLargeGathering", True),
                ("ChangedSeedNumber", 5),
            ]
        },
    }

    R0_controls = {
        "World" : [
            ("DynamicCapacity", False),
            ],
        "Infection" : [
            ("baseP" , 1.25),
            ("SeedNumber", 10),
        ],
        "HybridClass":[
            ("ChangedSeedNumber", 10),
        ],
    }

    import time
    t1 = time.time()
    R0Dict = dict()
    InfectedCountDict = dict()
    simulationGeneration = "0"
    osName = platform.system()
    files = "images\\" if osName.lower() == "windows" else "images/"
    osExtension = "win" if osName.lower() == "windows" else "Linux"
    for index, (modelName, modelControl) in enumerate(ControlledExperiment.items()):

        configCopy = copy.deepcopy(modelConfig)
        print("*"*20)
        print(f"started working on initializing the simualtion for {modelName}")
        for categoryKey, listOfControls in modelControl.items():
            for (specificKey, specificValue) in listOfControls:
                configCopy[categoryKey][specificKey] = specificValue
        R0Count = 1
        multiCounts = 1
        
        if index > 8 or index == 0: #in [0, 9, 12, 15]:
            #model_framework.simpleCheck(configCopy, days=100, visuals=True, debug=True, modelName=modelName)
            InfectedCountDict[modelName] = model_framework.multiSimulation(multiCounts, configCopy, days=100, debug=False, modelName=modelName)
            R0Dict[modelName] = model_framework.R0_simulation(modelConfig, R0_controls,R0Count, debug=False, timeSeriesVisual=False, R0Visuals=True, modelName=modelName)

            # the value of the dictionary is ([multiple R0 values], (descriptors, (tuple of useful data like mean and stdev))
    print(InfectedCountDict.items())
    print(R0Dict.items())
    return
    if False:

        saveName = "comparingModels_"+simulationGeneration
        statfile.comparingBoxPlots(R0Dict, plottedData="R0", saveName=saveName)
        statfile.comparingBoxPlots(InfectedCountDict ,plottedData="inf", saveName=saveName)
    else:
        #statfile.generateVisualByLoading(ControlledExperiment, plottedData="inf", saveName=saveName)
        model_framework.createFilledPlot(modelConfig, modelName="baseModel",
                                                            simulationN=3)

    timetook = time.time()-t1
    print("took", timetook, "seconds", timetook/(60*60), "hours")
if __name__ == "__main__":
    main()