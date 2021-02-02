import model_framework
import platform
import statfile
import copy
import fileRelated
import pandas as pd
import experiment
import main_config
from pathlib import Path

def main():
    """intialize and run the model, for indepth detail about the config or how to run the code, go to the github page for this code"""
    

    # you can control for multiple interventions by adding a case:
    #  [(modified attr1, newVal), (modified attr2, newVal), ...]

    # simulation name --> simulation controlled variable(s)
    # dont use . or - in the simulation name because the names are used to save images, or any symbols below
    modelConfig = main_config.modelConfig
   

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
    #print(len(experiment3))
    #print_nicely(experiment3)
    experiment4 = cross_scenarios(experiment.only_medium, experiment.original_multiplier)
    experiment5 = cross_scenarios(experiment.medium_student_vary_policy, experiment.original_multiplier)
    

    experiment6 = cross_scenarios(experiment4, experiment.sp_batch1)
    experiment4 = cross_scenarios(experiment4, experiment.new_batch1)
    experiment5 = cross_scenarios(experiment5, experiment.new_batch2)
    print(len(experiment6))
    R0Dict = dict()
    InfectedCountDict = dict()

    basemodel = {"basemodel": {}}

    multi_experiments = {
        "request_1": experiment1,
        "request_2": experiment2,
        "request_3": experiment3,
    }

   


    for (request_name, modelConfigs) in multi_experiments.items():
        output_dir = fileRelated.fullPath(request_name, "outputs")
        Path(output_dir).mkdir(parents=False, exist_ok=True)
        


        for index, (modelName, modelControl) in enumerate(multi_experiment.items()):

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

            R0Count, multiCounts = 0, 40

            #print(configCopy)
            if index > -1:
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