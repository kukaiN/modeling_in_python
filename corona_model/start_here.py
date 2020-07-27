import model_framework
import platform


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
            "SampleSizeForTesting":50,
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

    # you can control for multiple interventions by adding a case:
    #  [(modified attr1, newVal), (modified attr2, newVal), ...]

    # simulation name --> simulation controlled variable(s)
    # dont use . or - in the simulation name because the names are used to save images, or any symbols below
    """
        < (less than)
        > (greater than)
        : (colon - sometimes works, but is actually NTFS Alternate Data Streams)
        " (double quote)
        / (forward slash)
        \ (backslash)
        | (vertical bar or pipe)
        ? (question mark)
        * (asterisk)
    """
    ControlledExperiment = {
        "baseModel":{}, # no changes
        "Minimal": {
            "World": [
                ("TurnedOnInterventions", ["FaceMask", "Quarantine"]),
                ("ComplianceRatio", 0.5),
                ],
            "Quarantine": [
                ("ResultLatency", 3*24), 
                ("SampleSizeForTesting", 100)
                ],
        }, 
        "Moderate": {
            "World": [
                ("TurnedOnInterventions", ["FaceMask", "Quarantine"]),
                ("ComplianceRatio", 0.5)
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), 
                ("SampleSizeForTesting", 250)
                ],
            "ClosingBuildings": [
                ("ClosedBuildingType", ["gym", "library"])
            ]
        },    
        "Moderate+Facemask": {
            "World": [
                ("TurnedOnInterventions", ["FaceMask", "Quarantine"]),
                ("ComplianceRatio", 1),
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), 
                ("SampleSizeForTesting", 250)
                ],
            "ClosingBuildings": [
                ("ClosedBuildingType", ["gym", "library"])
            ]
        },
        "Moderate+Hybrid": {
            "World": [
                ("TurnedOnInterventions", ["FaceMask", "Quarantine", "HybridClasses"]),
                ("ComplianceRatio", 0.5)
            ],
            "Quarantine": [
                ("ResultLatency", 3*24), 
                ("SampleSizeForTesting", 250)
                ],
            "ClosingBuildings": [
                ("ClosedBuildingType", ["gym", "library"])
            ]
        },
        "Maximal": {
            "World": [
                ("TurnedOnInterventions", ["FaceMask", "Quarantine", "ClosingBuildings","HybridClasses"]),
                ("ComplianceRatio", 1),
                
            ],
            "Infection":[
                ("SeedNumber", 5),
            ],
            "Quarantine": [
                ("ResultLatency", 1*24), 
                ("SampleSizeForTesting", 500),
                ("BatchSize", 500)
                ],
            "ClosingBuildings": [
                ("ClosedBuildingType", ["gym", "library", "office"]),
                ("ClosedButKeepHubOpened", ["dining"]),
            ]
        },
    }
    R0_controls = {
        "World": []
    }
    R0Dict = dict()
    for index, (modelName, modelControl) in enumerate(ControlledExperiment.items()):
        configCopy = dict(modelConfig)
        print("*"*20)
        print(f"started working on initializing the simualtion for {modelName}")
        for categoryKey, listOfControls in modelControl.items():
            for (specificKey, specificValue) in listOfControls:
                configCopy[categoryKey][specificKey] = specificValue
        if index < 1:
            R0Count = 100
            osName = platform.system()
            if osName.lower() == "windows":
                files = "images\\"
            else:
                files = "images/"
        else:
            R0Count = 20
        if index in [0, 1, 2, 3, 4, 5]:
            typeName = "p_" + str(configCopy["Infection"]["baseP"]) + "_"
            model_framework.simpleCheck(configCopy, days=20, visuals=True, debug=False, modelName=files+typeName+modelName)
            returnVal = model_framework.R0_simulation(modelConfig, R0_controls,100, debug=False, visual=False)
            R0Dict[modelName] = returnVal
            
    print(R0Dict.items())
if __name__ == "__main__":
    main()