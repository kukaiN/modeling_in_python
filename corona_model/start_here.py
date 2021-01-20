import model_framework
import platform
import statfile
import copy
import fileRelated
import pandas as pd

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
            "immunity": 0,
            "vaccine": False,
            "vaccineEffectiveness": 0.9,
            "vaccinatedPopulation":0.3,
        },
        "Rooms" : {
            "ExtraParameters": ["roomId","agentsInside","oddCap", "evenCap", "classname", "infectedNumber", "hubCount"],
        },
        "Buildings" : {
            "ExtraParameters": ["buildingId","roomsInside"],
        },
        "Infection" : {
            "baseP" : 1.25,  # summer was 1.25
            "SeedNumber" : 10,
            "offCampusInfectionMultiplyer" : 8,
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
            "TurnedOnInterventions":[],# ["HybridClasses", "ClosingBuildings", "Quarantine", "Screening", "FaceMasks"],

            "transitName": "transit_space_hub",
            "offCampusStudentCount":880,
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
            "use_compliance":True,
            "Facemask_mode": 0,
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
            "TestFromVaccinated":False,
            "ShowingUpForScreening": 1,
            "offset": 8, # start at 8AM
            "checkupFrequency": 24*1,  # this is the interval between checkups, 24 = daily and 24*7 = weekly checkup
            "falsePositive":0.001,
            "falseNegative":0.03,
            "OnlySampleUnvaccinated": False,
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

    old_ControlledExperiment = {
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
    }
    original_3x3 = {
        "NC_WP":{
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 0, c = 0.80, h = 0.50, s' = 0
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "LessSocial", "ClosingBuildings"]),
                ("ComplianceRatio", 0), # f = 0
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 150), # N=150
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
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 150), # N=150
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
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 1, c = 1, h = 1, s' = 0.75, no large gatherings
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 1), # f = 1
                ("LargeGathering", False),
            ],
            "Quarantine": [
                ("ResultLatency", 4*24),
                 # L = 4
                ("BatchSize", 150), # N=150
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
            ("SeedNumber", 100),
        ],
        "HybridClass":[
            ("ChangedSeedNumber", 10),
        ],
    }
    # this overrides the previous experiments, since base_p is being chnaged
    R0_controls = {
        "World" : [
            ("DynamicCapacity", False),
            ],
        "HybridClass":[
            ("ChangedSeedNumber", 10),
        ],
    }

    new_ControlledExperiment1 = {
        "base_case1":{},
        "v1_f0":{
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.3),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 0),
            ],
        },
        "v1_f1":{
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.3),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 1),
            ],
        },
        "v1_f2":{
            "Agents":[
               ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.3),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 2),
            ],
        },
        "v2_f0":{
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.6),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 0),
            ],
        },
        "v2_f1":{
            "Agents":[
                     ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.6),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 1),
            ],
        },
        "v2_f2":{
            "Agents":[
                     ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.6),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 2),
            ],
        },
        "v3_f0":{
            "Agents":[
                      ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.9),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 0),
            ],
        },
        "v3_f1":{
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.9),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 1),
            ],
        },
        "v3_f2":{
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.9),
            ],
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks"]),
            ],
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 2),
            ],
        }
    }
    low_med = {
        "NC_WP":{
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 0, c = 0.80, h = 0.50, s' = 0
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "LessSocial", "ClosingBuildings"]),
                ("ComplianceRatio", 0), # f = 0
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 150), # N=150
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
            # N = 150, L = 4, B = {G, L}, D = 0
            # f = 0.5, c = 0.90, h = 0.75, s' = 0.25
            "World": [
                ("TurnedOnInterventions", ["FaceMasks", "Quarantine", "ClosingBuildings", "LessSocial"]),
                ("ComplianceRatio", 0.5), # f = 0.5
            ],
            "Quarantine": [
                ("ResultLatency", 4*24), # L = 4
                ("BatchSize", 150), # N=150
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
    }
    vaccine3 = {
        "v1" : {
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.3),
            ],
        },
        "v2" : {
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.6),
            ],
        },
        "v3" : {
            "Agents":[
              ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.9),
            ],
        },
    }

 # 30, 50, 70, 90
    vaccine4 = {
        "v1" : {
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
            ],
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.3),
            ],
                "Quarantine" : [
                # this dictates if we randomly sample the population or cycle through Batches
                ("RandomSampling", False),
                ("ResultLatency",3*24),
                ("WalkIn",True),
                ("BatchSize" , 250),
                ("OnlySampleUnvaccinated",True),
             ],
        },
        "v2" : {
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
            ],
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.5),
            ],
             "Quarantine" : [
                # this dictates if we randomly sample the population or cycle through Batches
                ("RandomSampling", False),
                ("ResultLatency",3*24),
                ("WalkIn",True),
                ("BatchSize" , 250),
                ("OnlySampleUnvaccinated",True),
             ],
        },

        "v3" : {
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
            ],
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.7),
            ],
            "Quarantine" : [
                # this dictates if we randomly sample the population or cycle through Batches
                ("RandomSampling", False),
                ("ResultLatency",3*24),
                ("WalkIn",True),
                ("BatchSize" , 250),
                ("OnlySampleUnvaccinated",True),
             ],
        },

        "v4" : {
            "World": [
                 ("TurnedOnInterventions", ["FaceMasks",  "Quarantine"]),
            ],
            "Agents":[
                ("immunity", 0.05),
                ("vaccine", True),
                ("vaccineEffectiveness", 0.9),
                ("vaccinatedPopulation",0.9),
            ],
            "Quarantine" : [
                # this dictates if we randomly sample the population or cycle through Batches
                ("RandomSampling", False),
                ("ResultLatency",3*24),
                ("WalkIn",True),
                ("BatchSize" , 250),
                ("OnlySampleUnvaccinated",True),
             ],
        }
    }
# 0, 1, 2
    facemask3 = {
        "f0": {
            "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 0),
            ],
        },
        "f1": {
             "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 1),
            ],
        },
        "f2": {
             "FaceMasks":[
                ("use_compliance", False),
                ("Facemask_mode", 2),
             ],
        }
    }

    base_p_experiments = {
        "p1.00": {"Infection" : [("baseP" , 1.00)],},
        "p1.05": {"Infection" : [("baseP" , 1.05)],},
        "p1.10": {"Infection" : [("baseP" , 1.10)],},
        "p1.15": {"Infection" : [("baseP" , 1.15)],},
        "p1.20": {"Infection" : [("baseP" , 1.20)],},
        "p1.25": {"Infection" : [("baseP" , 1.25)],},
        "p1.30": {"Infection" : [("baseP" , 1.30)],},
        "p1.35": {"Infection" : [("baseP" , 1.35)],},
        "p1.40": {"Infection" : [("baseP" , 1.40)],},
        "p1.45": {"Infection" : [("baseP" , 1.45)],},
        "p1.50": {"Infection" : [("baseP" , 1.50)],},
    }
    base_p_initial_count_experiment = {
        "p125_10" : { "Infection" : [("baseP" , 1.25), ("SeedNumber", 10)]},
        "p125_20" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 20)]},
        "p125_30" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 30)]},
        "p125_40" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 40)]},
        "p125_50" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 50)]},
        "p125_60" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 60)]},
        "p125_70" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 70)]},
        "p125_80" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 80)]},
        "p125_90" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 90)]},
        "p125_100" : {"Infection" : [("baseP" , 1.25), ("SeedNumber", 100)]},

    }

    def cross_screnarios(scenario1, scenario2):
        experiments = {}
        for keyname, experiment1 in scenario1.items():
            for screenname, screen in scenario2.items():
                experiment_name = screenname +"_" + keyname
                experiments[experiment_name] = screen.copy()
                for key, value in experiment1.items():
                    #print(key, value)
                    experiments[experiment_name][key] = value.copy()
        return copy.deepcopy(experiments)


    experiment2 = cross_screnarios(vaccine3, low_med)
    experiment3 =cross_screnarios(vaccine4, facemask3)

    print(len(experiment3))
    R0Dict = dict()
    InfectedCountDict = dict()

    basemodel = {"basemodel": {}}
    #for index, (modelName, modelControl) in enumerate(experiment2.items()):
    for index, (modelName, modelControl) in enumerate(original_3x3.items()):

        print("finished", index)
        configCopy = copy.deepcopy(modelConfig)
        #print("*"*20)
        #print(configCopy["Agents"].keys())
        #print("*"*20)
        #print(f"started working on initializing the simualtion for {modelName}")
        for categoryKey, listOfControls in modelControl.items():
            #print(listOfControls)
            for (specificKey, specificValue) in listOfControls:
                configCopy[categoryKey][specificKey] = specificValue

        R0Count, multiCounts = 100, 100

        #print(configCopy)
        if index >-1:
            #model_framework.simpleCheck(configCopy, days=10, visuals=True, debug=True, modelName=modelName)
            InfectedCountDict[modelName] = model_framework.multiSimulation(multiCounts, configCopy, days=100, debug=False, modelName=modelName)
            R0Dict[modelName] = model_framework.R0_simulation(configCopy, R0_controls,R0Count, debug=False, timeSeriesVisual=False, R0Visuals=True, modelName=modelName)

            # the value of the dictionary is ([multiple R0 values], (descriptors, (tuple of useful data like mean and stdev))
    print(InfectedCountDict.items())
    print(R0Dict.items())

    if True:


        simulationGeneration = "0"
        saveName = "comparingModels_"+simulationGeneration
        statfile.comparingBoxPlots(R0Dict, plottedData="R0", saveName=saveName)
        statfile.comparingBoxPlots(InfectedCountDict ,plottedData="inf", saveName=saveName)

        for key, value in R0Dict.items():
            R0Dict[key] = value[0]
        R0_df = pd.DataFrame(R0Dict)
        fileRelated.save_df_to_csv(fileRelated.fullPath("R0_data.csv", "outputs"), R0_df)

    else:
        #statfile.generateVisualByLoading(ControlledExperiment, plottedData="inf", saveName=saveName)
        model_framework.createFilledPlot(modelConfig, modelName="baseModel",
                                                            simulationN=3)

if __name__ == "__main__":
    main()