import statfile as sf
import pickle 
import pandas as pd
import os
import platform


def formatData(folder, fileName):
    """
        get the relevant data from the file with the corresponding filename, then make a dictionary out of it

        Parameters:
        - folder: the folder where the file is located, use empty string, "", if the file isnt nested
        - fileName: the name of the file
    """
    fullName = fullPath(fileName, folder)
    # get the content of the file and convert it to a panda dataframe
    content = openCsv(fullName, [])
    df_list = [content.columns.values.tolist()]+content.values.tolist()
    # remove white spaces in font and back of all entries
    df_list = [[txt.strip() if type(txt) == str else txt for txt in lst] for lst in df_list]
    # make a new dataframe from the list, also use the first line in the dataframe as the new header
    new_df = pd.DataFrame(df_list)
    header = new_df.iloc[0]
    new_df = new_df[1:]
    new_df.columns = header
    return new_df

def fullPath(fileName, folder=""):
    """
        given the folder and the file name, it returns a string object that have the type of slash right for the computer's OS

        Parameters:
        - fileName: the name of the file
        - folder: the folder where the file is located in, if it's in the same directory, then use an empty string
    """
    _, filePath = get_cd()
    # we need the os name because different OS uses / or \ to navigate the file system
    osName = platform.system()
    # get the full path to the file that we're trying to open, and depending on the OS, the slashes changes
    fullLocName = filePath + folder + "\\" + fileName
    if osName == "Windows": pass
    else:
        # for OS' like linux and mac(Darwin)
        fullLocName = fullLocName.replace("\\", "/")
    return fullLocName

def loadConfig(folder, fileName):
    """load config information from a txt file

        Parameters:
        - folder: the folder where the file is located, empty string if its not in any folder
        - fileName: the file name
    """
    fullName = fullPath(fileName, folder)
    # get the content of the file and convert it to a list
    with open(fullName) as f:
        content = [line.strip() for line in f.readlines()]
    return content

def openCsv(filePath, default = ["new df here"]):
    """
        returns the content of the csv file if it exists.

        Parameters:
        - filePath: the absolute or relative path to the .csv file
        - default: default value to load if the file is not located
    """
    try:
        content = pd.read_csv(filePath, error_bad_lines=False)
    except Exception:
        print(f"exception, the filename {filePath} you requested to open was not found.")
        if (int(input("do you want to make a new file? 1 for yes, 0 for no")) == 1):
            content = pd.dataframe(default)
            content.toCsv(filePath, index=False, header=False)
    return content

def get_cd():
    """
    uses the os.path function to get the filename and the absolute path to the current directory
    Also does a primative check to see if the path is correct, there has been instances where the CD was different, hence the check.

    return Value(s):
    - scriptPath: the full directory path
    - filePath: the full path that includes the current file
    """
    # Get the path to this file
    scriptPath, filePath = os.path.realpath(__file__), ""
    # get the os name and the backslash or forward slash depending on the OS
    os_name = platform.system()
    path_slash = "/" if os_name in ["Linux", 'Darwin'] else "\\"
    # remove the file name from the end of the path
    for i in range(1,len(scriptPath)+1):
        if scriptPath[-i] == path_slash:
            scriptPath = scriptPath[0:-i]#current path, relative to root direcotory or C drive
            break
    if os.getcwd() != scriptPath: filePath = scriptPath + path_slash
    return scriptPath, filePath



def main():
    vacc = ["v1", "v2", "v3"]
    vacc_p = [0.3, 0.6, 0.9]
    facemask = ["f0", "f1", "f2"]
  
    
    # 10 is the index for total
    name_list = []
    matrix_data = []

    total_pop = 2380
    for vX, vac_p in zip(vacc, vacc_p):
        for fX in facemask:
            new_name = vX+"_"+fX+".csv"

            x = openCsv(fullPath( new_name, folder="outputs//new_semester"))
            print(new_name)
            
            data_points = []
            for index, column_name in enumerate(x.columns):
                if index == 0:
                    location = x[column_name]
                if index > 0:
                    total_infection = x[column_name][10]
                    print(total_infection)
                    data_points.append(total_infection/(vac_p*total_pop))
            name_list.append(new_name)
            matrix_data.append(data_points)
    print(matrix_data)

    sf.boxplot(matrix_data, xlabel=name_list, ylabel="percentage", savePlt=True, saveName="new_semster1")
    #print(x)
  

    admin = ["NC", "SC"]
    policy = ["WP", "MP", "SP"]
    policy_total = [2380, 2380-650, 2380-1280]
 
    # for mp remote 650
    name_list2 = []
    matrix_data2 = []
    for vX, vac_p in zip(vacc, vacc_p):
        for cc in admin:
            for p, p_count in zip(policy, policy_total):
                new_name = cc+"_"+p+"_"+vX+".csv"

                x = openCsv(fullPath( new_name, folder="outputs//new_semester2"))
              
                data_points = []
                for index, column_name in enumerate(x.columns):
                    if index == 0:
                        location = x[column_name]
                    if index > 0:
                        total_infection = x[column_name][10]
                        print(total_infection)
                        data_points.append(total_infection/(vac_p*p_count))
                name_list2.append(new_name)
                matrix_data2.append(data_points)

    sf.boxplot(matrix_data2, xlabel=name_list2, ylabel="percentage", savePlt=True, saveName="new_semester2")

if __name__ == "__main__":
    main()