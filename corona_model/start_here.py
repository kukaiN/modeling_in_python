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
    experiment1 = experiment.marginals
    experiment2 = experiment.original_3x3
    experiment3 = cross_scenarios(experiment.different_base_p_jump_025, experiment.medium_student_vary_policy)
    experiment4 = cross_scenarios(experiment.medium_student_vary_policy, experiment.off_campus_multiplier)
    experiment5 = experiment.diff_seed_number
    experiment6 = experiment.smaller_seed_number
    #print(len(experiment3))
    #print_nicely(experiment3)

    print(len(experiment1))


    basemodel = {"basemodel": {}}

    multi_experiments = {
        "request_1": experiment1,
        "request_2": experiment2,
        "request_3": experiment3,
        "request_4": experiment4,
        "request_5": experiment5,
        "request_6": experiment6,
    }
    #multi_experiments = {"new_request4": experiment.new_check}
    user_input = input("which request # do you want to run? 0 to run all in one thread")
    user_input = int(user_input)
    if user_input < 0 or user_input > len(multi_experiments):
        print("input number does not match experiment number, exiting program")
        return


    for sp_index, (request_name, modelConfigs) in enumerate(multi_experiments.items()):
        if (sp_index == user_input-1) or (user_input == 0):
            R0Dict = dict()
            InfectedCountDict = dict()
            output_dir = fileRelated.fullPath(request_name, "outputs")
            Path(output_dir).mkdir(parents=False, exist_ok=True)
            output_folder = "outputs/"+ request_name
            print(request_name)
            for index, (modelName, modelControl) in enumerate(modelConfigs.items()):

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

                R0Count, multiCounts = 200, 0

                #print(configCopy)
                if index > -1:
                    #model_framework.simpleCheck(configCopy, days=10, visuals=True, debug=True, modelName=modelName)
                    InfectedCountDict[modelName] = model_framework.multiSimulation(multiCounts, configCopy, days=100, debug=False, modelName=modelName, outputDir=output_folder)
                    R0Dict[modelName] = model_framework.R0_simulation(configCopy, R0_controls,R0Count, debug=False, timeSeriesVisual=False, R0Visuals=True, modelName=modelName, outputDir=output_folder)

                    # the value of the dictionary is ([multiple R0 values], (descriptors, (tuple of useful data like mean and stdev))
                print(InfectedCountDict.items())
                print(R0Dict.items())

            if True:


                simulationGeneration = "0"
                saveName = "comparingModels_"+simulationGeneration
                # reads R0 data
                fileRelated.mergeR0(R0Dict, fileRelated.fullPath("request_5/R0_data.csv", "outputs"))
                merged = True
                statfile.comparingBoxPlots(R0Dict, plottedData="R0", saveName=saveName, outputDir=output_folder)

                statfile.comparingBoxPlots(InfectedCountDict ,plottedData="inf", saveName=saveName, outputDir=output_folder)

                for key, value in R0Dict.items():
                    if R0Dict[key][1]== "(npMean, stdev, rangeVal, median)":
                        R0Dict[key] = value[0]
                    # else do nothing
                    #print(key, value)
                print(R0Dict)
                # check if dict is not empty
                if not merged:
                    R0_df = pd.DataFrame(R0Dict)
                    fileRelated.save_df_to_csv(fileRelated.fullPath("R0_data.csv", output_folder), R0_df)

            else:  # never ran after jan 30
                #statfile.generateVisualByLoading(ControlledExperiment, plottedData="inf", saveName=saveName)
                model_framework.createFilledPlot(modelConfig, modelName="baseModel",
                                                                    simulationN=3, outputDir=output_folder)




if __name__ == "__main__":
    main()



