import model_framework as mfw

def main():
    """intialize and run the model, for indepth detail about the config or how to run the code, go to the github page for this code"""    
    modelConfig = {
        # time intervals
        "unitTime" : "hour",

        # AGENTS
        "AgentPossibleStates": {
            "neutral" : ["susceptible", "exposed"],
            "infected" : ["infected Asymptomatic", "infected Asymptomatic Fixed", "infected Symptomatic Mild", "infected Symptomatic Severe"],  
            "recovered" : ["quarantined", "recovered"],
            "debugAndGraphingPurpose": ["falsePositive"],
            },

        "absorbingStates": ["recovered"],
        # these are parameters, that are assigned later or is ok to be initialized with default value 0
        "extraParam": {
            "Agents": ["agentId","path", "destination", "currLocation",
                        "statePersistance","lastUpdate", "personality", 
                        "arrivalTime", "schedule", "travelTime",
                        "officeAttendee", "gathering"],
            "Rooms":  ["roomId","agentsInside","oddCap", "evenCap", "classname", "infectedNumber"],
            "Buildings": ["buildingId","roomsInside"],
        },
        "extraZipParam": {
            "Agents" : [("motion", "stationary"), ("infected", False), ("compliance", False)],
            
        },
        "booleanAssignment":{
            "Agents" : [("officeAttendee", 0), ("gathering", 0.5)],
        },
        "baseP" :1.25,
        "infectionSeedNumber": 10,
        "infectionSeedState": "exposed",
        "infectionContribution":{
            "infected Asymptomatic":0.5,
            "infected Asymptomatic Fixed":0.5,
            "infected Symptomatic Mild":1,
            "infected Symptomatic Severe":1,
        },
        # INFECTION STATE
        "transitionTime" : {
            "susceptible":-1,
            "exposed":2*24, # 2 days
            "infected Asymptomatic":2*24, # 2 days
            "infected Asymptomatic Fixed":10*24, # 10 days
            "infected Symptomatic Mild":10*24,# 10 Days
            "infected Symptomatic Severe":10*24, # 10 days
            "recovered":-1,
            "quarantined":24*14, # 2 weeks 
        },
        
        "transitionProbability" : {
            "susceptible": [("exposed", 1)],
            "exposed": [("infected Asymptomatic", 0.85), ("infected Asymptomatic Fixed", 1)],
            "infected Asymptomatic Fixed": [("recovered", 1)],
            "infected Asymptomatic": [("infected Symptomatic Mild", 0.5), ("infected Symptomatic Severe", 1)],
            "infected Symptomatic Mild": [("recovered", 1)],
            "infected Symptomatic Severe": [("recovered", 1)],
            "quarantined":[("susceptible", 1)],
            "recovered":[("susceptible", 0.5), ("recovered", 1)],
        },

        # QUARANTINE
        "quarantineSamplingProbability" : 0,
        "quarantineDelay":0,
        "walkinProbability" : {"infected Symptomatic Mild": 0.7, "infected Symptomatic Severe": 0.95},
        "quarantineSampleSize" : 100,
        "quarantineSamplePopulationSize":0.10,
        "quarantineRandomSubGroup": False,
        "closedBuildings": ["eating", "gym", "study"],
        "quarantineOffset": 1*24+9,
        "quarantineInterval": 24*1,
        "falsePositive":0.03,
        "falseNegative":0.001,
        "remoteStudentCount": 1000,
        
        # face mask
        "maskP":0.5,
        "nonMaskBuildingType": ["dorm", "dining", "faculty_dining_hall"],
        "nonMaskExceptionsHub": ["dorm", "dining"],
        "semiMaskBuilding": ["social", "large gathering"],
        
        # OTHER parameters
        "transitName": "transit_space_hub",
        # change back to 0.001
        "offCampusInfectionP":0.125/700,
        "trackLocation" : ["_hub"],
        #possible values:
        #    1: facemask
        #    3: testing for covid and quarantining
        #    4: closing large buildings
        #    5: removing office hours with professors
        #    6: shut down large gathering 
     
        "interventions":[5],#[1,3,4,5,6], # no office hour
        "allowedActions": [],#["walkin"],#["walkin"],
        "massInfectionRatio":0.10,
        "complianceRatio": 0,
        "randomSocial":False,
    }
    # you can control for multiple interventions by adding a case:
    #  [(modified attr1, newVal), (modified attr2, newVal), ...]
    simulationControls = [
        [("complianceRatio", 0)],
        [("complianceRatio", 0.33)],
        [("complianceRatio", 0.66)],
        [("complianceRatio", 1)],
    ]




    R0_controls = [("infectionSeedNumber", 10),("quarantineSamplingProbability", 0),
                    ("allowedActions",[]),("quarantineOffset", 20*24), ("interventions", [5])]
    
    allIn = [("complianceRatio", 1), ("interventions", [1,3,4,5,6]), ("allowedActions", ["walkin"]),]

    
    configCopy = dict(modelConfig)
    for variableTup in allIn:
        configCopy[variableTup[0]] = variableTup[1]
    mfw.simpleCheck(configCopy, days=100, visuals=True, name="default_125p")
    # for dining add return at the end
    #R0_simulation(modelConfig, R0_controls,20, debug=True, visual=True)
    
    allInSimulation = [
        [("booleanAssignment",{"Agents" : [("compliance", 0.5), ("officeAttendee", 0.2), ("gathering", 0.5)]})],
        [("booleanAssignment",{"Agents" : [("compliance", 1), ("officeAttendee", 0.2), ("gathering", 0.5)]})],
    ]
    return
    createdFiles = mfw.initializeSimulations(simulationControls, modelConfig, True)
    mfw.simulateAndPlot(createdFiles, 5, 24*100, additionalName="050P_", title="mask with 0.5 effectiveness", labels=labels)



if __name__ == "__main__":
    main()