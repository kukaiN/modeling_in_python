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

                simulation_count = 100
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
                saveName = "doubletime"
                statfile.comparingBoxPlots(timeSeriesDict ,plottedData="double", saveName=saveName, outputDir=output_folder)


if __name__ == "__main__":
    main()