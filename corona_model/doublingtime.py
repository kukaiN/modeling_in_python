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
        "doublingtime": {"basemodel": {"World" : [("stateCounterInterval", 1)],}},
    }

    load_data = True

    for (request_name, modelConfigs) in multi_experiments.items():
        output_dir = fileRelated.fullPath(request_name, "outputs")
        Path(output_dir).mkdir(parents=False, exist_ok=True)
        output_folder = "outputs/"+ request_name
        if not load_data:
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
                for t, cumm_infection in enumerate(infectionCountSeries):
                    if cumm_infection >= doublevalue:
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


        
        if load_data:
            double_data = {20: [114.0, 106.0, 135.0, 129.0, 157.0, 167.0, 115.0, 167.0, 127.0, 159.0, 158.0, 167.0, 135.0, 115.0, 176.0, 133.0, 131.0, 178.0, 135.0, 167.0, 116.0, 157.0, 140.0, 129.0, 161.0, 115.0, 117.0, 159.0, 134.0, 126.0, 167.0, 150.0, 161.0, 130.0, 167.0, 117.0, 131.0, 165.0, 161.0, 110.0, 135.0, 133.0, 177.0, 167.0, 135.0, 112.0, 174.0, 140.0, 136.0, 132.0, 175.0, 157.0, 130.0, 134.0, 140.0, 156.0, 130.0, 167.0, 111.0, 135.0, 131.0, 128.0, 130.0, 109.0, 112.0, 127.0, 129.0, 167.0, 154.0, 129.0, 133.0, 139.0, 117.0, 115.0, 114.0, 115.0, 136.0, 114.0, 139.0, 157.0, 139.0, 138.0, 129.0, 109.0, 113.0, 127.0, 131.0, 111.0, 133.0, 134.0, 141.0, 131.0, 129.0, 113.0, 199.0, 115.0, 134.0, 133.0, 182.0, 113.0], 
            40: [189.0, 167.0, 230.0, 188.0, 185.0, 209.0, 167.0, 250.0, 189.0, 209.0, 208.0, 230.0, 205.0, 167.0, 250.0, 188.0, 200.0, 236.0, 203.0, 229.0, 181.0, 204.0, 223.0, 205.0, 227.0, 188.0, 186.0, 184.0, 187.0, 198.0, 246.0, 223.0, 208.0, 174.0, 252.0, 176.0, 186.0, 224.0, 212.0, 180.0, 198.0, 187.0, 252.0, 236.0, 202.0, 179.0, 225.0, 223.0, 209.0, 199.0, 232.0, 208.0, 176.0, 188.0, 205.0, 209.0, 188.0, 211.0, 163.0, 201.0, 188.0, 179.0, 202.0, 184.0, 180.0, 186.0, 205.0, 209.0, 211.0, 186.0, 183.0, 205.0, 179.0, 167.0, 164.0, 177.0, 204.0, 186.0, 186.0, 233.0, 200.0, 212.0, 176.0, 167.0, 167.0, 185.0, 185.0, 164.0, 185.0, 200.0, 210.0, 199.0, 188.0, 188.0, 271.0, 186.0, 199.0, 188.0, 246.0, 176.0], 
            80: [295.0, 254.0, 300.0, 307.0, 260.0, 271.0, 236.0, 344.0, 284.0, 281.0, 274.0, 306.0, 282.0, 235.0, 368.0, 258.0, 277.0, 335.0, 277.0, 328.0, 257.0, 276.0, 284.0, 303.0, 322.0, 248.0, 271.0, 272.0, 261.0, 281.0, 344.0, 278.0, 297.0, 255.0, 371.0, 258.0, 280.0, 335.0, 301.0, 250.0, 285.0, 270.0, 335.0, 295.0, 297.0, 272.0, 328.0, 282.0, 276.0, 270.0, 306.0, 303.0, 258.0, 277.0, 275.0, 297.0, 282.0, 284.0, 258.0, 284.0, 280.0, 260.0, 261.0, 284.0, 234.0, 276.0, 308.0, 294.0, 273.0, 282.0, 252.0, 308.0, 276.0, 234.0, 261.0, 236.0, 281.0, 261.0, 276.0, 335.0, 271.0, 300.0, 246.0, 229.0, 231.0, 271.0, 232.0, 278.0, 278.0, 274.0, 304.0, 271.0, 250.0, 261.0, 335.0, 279.0, 277.0, 270.0, 347.0, 258.0], 
            160: [403.0, 367.0, 427.0, 428.0, 378.0, 403.0, 344.0, 462.0, 438.0, 391.0, 403.0, 420.0, 368.0, 350.0, 512.0, 392.0, 373.0, 423.0, 391.0, 450.0, 367.0, 426.0, 428.0, 403.0, 419.0, 368.0, 392.0, 371.0, 419.0, 401.0, 462.0, 400.0, 426.0, 345.0, 520.0, 393.0, 357.0, 463.0, 418.0, 351.0, 391.0, 401.0, 451.0, 416.0, 404.0, 396.0, 465.0, 391.0, 398.0, 393.0, 423.0, 428.0, 354.0, 378.0, 404.0, 403.0, 402.0, 380.0, 343.0, 420.0, 357.0, 366.0, 395.0, 428.0, 335.0, 371.0, 463.0, 405.0, 399.0, 392.0, 354.0, 444.0, 376.0, 335.0, 402.0, 373.0, 393.0, 398.0, 380.0, 469.0, 357.0, 405.0, 335.0, 355.0, 335.0, 400.0, 399.0, 418.0, 393.0, 404.0, 425.0, 367.0, 354.0, 392.0, 440.0, 400.0, 374.0, 357.0, 427.0, 379.0], 
            320: [572.0, 520.0, 608.0, 569.0, 569.0, 562.0, 491.0, 631.0, 590.0, 538.0, 568.0, 610.0, 520.0, 503.0, 752.0, 565.0, 536.0, 570.0, 547.0, 615.0, 503.0, 615.0, 610.0, 566.0, 586.0, 520.0, 582.0, 570.0, 573.0, 560.0, 638.0, 524.0, 584.0, 503.0, 710.0, 572.0, 523.0, 640.0, 562.0, 512.0, 565.0, 540.0, 620.0, 571.0, 560.0, 519.0, 633.0, 544.0, 537.0, 610.0, 543.0, 616.0, 520.0, 537.0, 573.0, 582.0, 562.0, 523.0, 503.0, 633.0, 524.0, 521.0, 541.0, 573.0, 489.0, 525.0, 654.0, 607.0, 565.0, 518.0, 503.0, 589.0, 513.0, 475.0, 608.0, 519.0, 547.0, 569.0, 515.0, 637.0, 513.0, 542.0, 476.0, 547.0, 503.0, 562.0, 525.0, 582.0, 536.0, 562.0, 573.0, 503.0, 513.0, 521.0, 585.0, 606.0, 534.0, 541.0, 569.0, 523.0]}
            timeSeriesDict = double_data
        else:
            double_df = pd.DataFrame(timeSeriesDict)
            fileRelated.save_df_to_csv(fileRelated.fullPath("doubling_data.csv", output_folder), double_df)


        if True:
            def graphdoubling(timeseries, scale, output_folder, scaleStr ="", limit=320):
                timeSeriesD = copy.deepcopy(timeseries)
                del_key = []
                for k, v in timeSeriesD.items():
                    if (k <= limit):
                        print(k)
                        timeSeriesD[k] = [item/scale for item in v]
                    else:
                        del_key.append(k)
                for key in del_key:
                    del timeSeriesD[key]

                saveName = "doubletime_scale_"+str(scale)+"h"
                statfile.comparingBoxPlots(timeSeriesD,plottedData="double", saveName=saveName, outputDir=output_folder, scale=scaleStr)

            

            graphdoubling(timeSeriesDict, 1, output_folder)
            graphdoubling(timeSeriesDict, 6, output_folder, "6 hours")
            graphdoubling(timeSeriesDict, 24, output_folder, "24 hours")




if __name__ == "__main__":
    main()