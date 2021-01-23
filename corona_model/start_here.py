import model_framework
import platform
import statfile
import copy
import fileRelated
import pandas as pd
import experiment
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
            "offCampusInfectionMultiplyer" : 1,
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



    def cross_scenarios(scenario1, scenario2):
        experiments = {}
        for keyname, experiment1 in scenario1.items():
            for screenname, screen in scenario2.items():
                experiment_name = screenname +"_" + keyname
                experiments[experiment_name] = screen.copy()
                for key, value in experiment1.items():
                    #print(key, value)
                    experiments[experiment_name][key] = value.copy()
        return copy.deepcopy(experiments)

    def print_nicely(experiment_scenarios):
        for ex_name, ex_config in experiment_scenarios.items():
            print("\n","*"*20,"\n", ex_name)
            for ex_config_name, ex_config_list in ex_config.items():
                print(ex_config_name, ":" ,ex_config_list)

    #experiment2 = cross_scenarios(experiment.vaccine3, experiment.low_med)
    #experiment3 =cross_scenarios(experiment.vaccine4, experiment.facemask3)
    experiment1 = experiment.original_3x3
    experiment2 = cross_scenarios(experiment.different_base_p_jump_025, experiment.medium_student_vary_policy)
    experiment3 = cross_scenarios(experiment.medium_student_vary_policy, experiment.off_campus_multiplier)
    print(len(experiment3))
    #print_nicely(experiment3)
    return 
    R0Dict = dict()
    InfectedCountDict = dict()

    basemodel = {"basemodel": {}}
    
    for index, (modelName, modelControl) in enumerate(experiment2.items()):

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