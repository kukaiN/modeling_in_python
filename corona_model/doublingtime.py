import model_framework
import platform
import statfile
import copy
import fileRelated
import pandas as pd
import experiment
import numpy as np
import main_config
from pathlib import Path

def main():
    """intialize and run the model, for indepth detail about the config or how to run the code, go to the github page for this code"""
    # you can control for multiple interventions by adding a case:
    #  [(modified attr1, newVal), (modified attr2, newVal), ...]

    # simulation name --> simulation controlled variable(s)
    # dont use . or - in the simulation name because the names are used to save images, or any symbols below
    modelConfig = main_config.modelConfig

    # this overrides the previous experiments, since base_p is being chnaged
    R0_controls = {
        "World" : [
            ("DynamicCapacity", False),
            ],
        "HybridClass":[
            ("ChangedSeedNumber", 10),
        ],
    }

    multi_experiments = {
        "doublingtime": {"basemodel": {}},
    }

    

    for (request_name, modelConfigs) in multi_experiments.items():
        if True:

            output_dir = fileRelated.fullPath(request_name, "outputs")
            Path(output_dir).mkdir(parents=False, exist_ok=True)
            output_folder = "outputs/"+ request_name
            print(request_name)
            for index, (modelName, modelControl) in enumerate(modelConfigs.items()):
                print("finished", index)
                configCopy = copy.deepcopy(modelConfig)

                for categoryKey, listOfControls in modelControl.items():
                    #print(listOfControls)
                    for (specificKey, specificValue) in listOfControls:
                        configCopy[categoryKey][specificKey] = specificValue

                simulation_count = 0
                timeSeriesList = model_framework.doubletime(simulation_count, configCopy, days=100, debug=False, modelName=modelName, outputDir=output_folder)

            doublingtime = []
            for timeseries in timeSeriesList:
                arrlen = len(timeseries)
                baseArr = timeseries[0] * np.ones(arrlen)
                infectionCountSeries = baseArr - np.array(timeseries)
                print("infection days")
                print(infectionCountSeries)
                doublevalue = 20
                index = 0
                for t, value in enumerate(infectionCountSeries):
                    if value >= doublevalue:
                        if len(doublingtime) < index+1:
                            doublingtime.append([])

                        doublingtime[index].append(t)
                        doublevalue*=2
                        index+=1

            doublet = 20
            timeSeriesDict = dict()
            for t, timelist in enumerate(doublingtime):
                print(t, doublet, timelist)
                timeSeriesDict[doublet] = timelist
                doublet *=2


            if True:
                double_data = {20: [23, 22, 27, 33, 27, 26, 32, 27, 30, 28, 32, 37, 37, 21, 28, 27, 28, 36, 26, 27, 33, 26, 23, 33, 27, 22, 21, 23, 22, 27, 22, 32, 28, 27, 25, 32, 26, 22, 28, 23, 21, 27, 27, 25, 27, 25, 25, 27, 27, 26, 27, 26, 21, 23, 21, 31, 33, 26, 27, 26, 33, 26, 27, 23, 26, 34, 28, 22, 28, 28, 25, 31, 26, 35, 23, 22, 22, 27, 22, 25, 28, 22, 26, 32, 26, 23, 27, 26, 26, 33, 27, 22, 33, 27, 27, 27, 16, 25, 27, 27], 
                40: [33, 32, 44, 46, 42, 39, 47, 39, 45, 49, 37, 47, 50, 36, 41, 41, 45, 46, 37, 37, 40, 42, 42, 40, 37, 37, 35, 41, 34, 42, 35, 40, 46, 40, 44, 44, 35, 37, 47, 35, 35, 42, 41, 35, 40, 37, 37, 37, 37, 37, 36, 47, 32, 44, 35, 44, 44, 37, 46, 37, 42, 42, 36, 35, 37, 37, 40, 35, 42, 40, 35, 41, 44, 41, 40, 31, 32, 44, 37, 40, 42, 36, 37, 45, 36, 36, 40, 39, 37, 46, 39, 39, 47, 40, 40, 40, 27, 36, 37, 37], 
                80: [51, 49, 61, 67, 61, 59, 59, 56, 59, 67, 56, 67, 66, 54, 66, 54, 60, 67, 55, 49, 55, 59, 56, 61, 56, 54, 47, 55, 52, 56, 47, 51, 61, 56, 58, 65, 50, 51, 61, 55, 52, 64, 60, 52, 54, 59, 55, 59, 56, 55, 47, 60, 46, 57, 50, 57, 56, 52, 61, 55, 55, 60, 50, 54, 51, 59, 56, 49, 60, 56, 54, 55, 59, 56, 56, 51, 49, 60, 54, 56, 61, 55, 55, 61, 50, 54, 56, 59, 54, 61, 52, 60, 61, 59, 57, 54, 41, 47, 54, 56],
                160: [74, 67, 88, 89, 88, 83, 80, 80, 87, 97, 80, 90, 93, 79, 87, 70, 83, 90, 81, 67, 71, 80, 83, 83, 85, 71, 70, 83, 76, 79, 67, 70, 84, 80, 84, 88, 70, 79, 88, 80, 67, 88, 88, 71, 74, 83, 85, 84, 89, 80, 70, 87, 75, 84, 75, 85, 78, 74, 85, 79, 80, 83, 69, 76, 71, 85, 76, 75, 85, 80, 80, 80, 80, 75, 80, 75, 67, 85, 73, 83, 90, 78, 80, 85, 71, 78, 79, 80, 75, 92, 78, 84, 85, 82, 78, 71, 67, 71, 79, 80], 
                320: [104, 100, 114, 116, 122, 127, 117, 109, 121, 137, 113, 128, 122, 113, 122, 100, 123, 122, 121, 99, 107, 113, 112, 107, 116, 100, 104, 114, 104, 104, 89, 100, 114, 112, 118, 119, 100, 107, 117, 113, 88, 118, 122, 103, 102, 109, 121, 119, 131, 116, 103, 127, 119, 119, 107, 114, 109, 103, 114, 104, 113, 114, 99, 103, 100, 121, 108, 109, 118, 113, 107, 112, 113, 102, 113, 117, 100, 117, 109, 112, 127, 105, 107, 123, 100, 104, 117, 109, 103, 138, 112, 116, 112, 118, 109, 103, 94, 100, 119, 112], 
                640: [151, 145, 161, 152, 174, 171, 156, 154, 167, 181, 150, 180, 167, 167, 172, 141, 174, 167, 165, 134, 148, 161, 155, 148, 156, 145, 154, 160, 151, 151, 128, 141, 156, 155, 159, 161, 138, 146, 160, 148, 126, 156, 170, 147, 145, 155, 161, 172, 179, 162, 137, 180, 167, 161, 161, 160, 151, 146, 157, 147, 167, 159, 136, 145, 136, 169, 162, 156, 167, 161, 154, 160, 156, 134, 156, 164, 136, 157, 151, 152, 171, 150, 145, 167, 136, 147, 159, 164, 152, 193, 155, 169, 155, 157, 151, 145, 134, 140, 166, 148], 
                1280: [229, 209, 228, 194, 238, 235, 209, 224, 235, 256, 194, 248, 227, 249, 243, 201, 251, 228, 222, 186, 210, 235, 224, 213, 217, 205, 235, 214, 222, 222, 196, 208, 213, 223, 210, 219, 200, 208, 218, 214, 179, 217, 237, 223, 204, 235, 222, 242, 246, 224, 195, 248, 235, 222, 238, 227, 208, 203, 222, 204, 246, 237, 203, 207, 201, 243, 244, 223, 237, 227, 219, 239, 223, 180, 214, 235, 200, 219, 205, 213, 235, 222, 203, 223, 193, 229, 220, 238, 239, 280, 222, 237, 213, 223, 218, 208, 186, 204, 238, 201]}

                timeSeriesDict = double_data
                saveName = "doubletime"
                double_df = pd.DataFrame(timeSeriesDict)
                fileRelated.save_df_to_csv(fileRelated.fullPath("doubling_data.csv", output_folder), double_df)
                statfile.comparingBoxPlots(timeSeriesDict ,plottedData="double", saveName=saveName, outputDir=output_folder)
        
            
if __name__ == "__main__":
    main()