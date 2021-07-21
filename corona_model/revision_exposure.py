import model_framework
import platform
import statfile
import copy
import fileRelated
import pandas as pd
import matplotlib.pyplot as plt
import experiment as experiment
import main_config
from pathlib import Path



def main():
    """
    This function calls on a special case of the base model that
    simulates a week on campus and randomly select 4 students for
    investigation.  Output is a set of 4 vectors
    """

    modelConfig = main_config.modelConfig

    exposure_model = {
        "exposure": {
            "Exposure":[("CollectData", True),
                        ("OnCampusData", 100),
                        ("OffCampusData",100),
                        ("facultyData",100)]
            }
    }
    # index is the simulation number and each item will be a set of vector
    exposure_array = []
    simulation_count = 1 # num of simulations
    simuated_time = 7 # a week

    for index, (modelName, modelControl) in enumerate(exposure_model.items()):
        configCopy = copy.deepcopy(modelConfig)
        for categoryKey, listOfControls in modelControl.items():
            #print(listOfControls)
            for (specificKey, specificValue) in listOfControls:
                if specificKey not in configCopy[categoryKey].keys():
                    print("error", specificKey, specificValue, " was not assigned correctly")

                    #return
                else:
                    configCopy[categoryKey][specificKey] = specificValue


    # we now have a model configuration that we want to use

    for i in range(simulation_count):
        print(f"simulation # {i}")
        output = model_framework.exposure_count(configCopy, simuated_time, debug=False)
        exposure_array.append(output)

    list_ver = []
    for arr_collection in exposure_array:
        for arr in arr_collection:
            list_ver.append(list(arr))


    df = pd.DataFrame(list_ver)

    num_agents = len(exposure_array[0][0])

    df.columns = ["agent_"+str(id_num) for id_num in range(num_agents)]

    fileRelated.save_df_to_csv(fileRelated.fullPath("exposure_data.csv", "outputs"), df)
    def visual1():
        for arr in list_ver:
            x = sorted(arr)
            plt.bar(range(100), x[-100:])
        plt.show()
    def visual2():
        for arr in list_ver:
            x = sorted(arr)
            plt.bar(range(num_agents-1), x[0:-1], alpha=0.5)
        plt.show()

    visual1()
    #visual2()

if __name__ == "__main__":
    main()