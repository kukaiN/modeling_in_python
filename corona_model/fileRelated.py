import os
import platform
import pandas as pd
import pickle
import dill

def loadPickledData(filePath, default=["default"]):
    """
    load an existing pickle file or make a pickle with default data
    then return the pickled data

    Parameters:
    - filePath: the absolute path or the relative path
    - default: default value if the path is invalid for some reason
    """
    try:
        with open(filePath, "rb") as f:
            content = pickle.load(f)
    except Exception:
        content = default
        with open(filePath, "wb") as f:
            pickle.dump(content, f)
    return content

def saveObjUsingPickle(filePath, content):
    """
    save the content as a byte file using pickle to a specific location
    use the alternate dill function for complex objects

    Parameters:
    - filePath: The absolute or relative path of the pickle file
        - Ex for win: C:\\Users\\....\\filename.pkl
        - Ex for linux and mac: /home/username/.../filename.pkl
    - content: object to be saved"""

    with open(filePath, "wb") as f:
        pickle.dump(content, f)

def savedf2Pickle(filePath, content):
    """
        save a panda dataframe as a .pkl file

        Parameters:
        - filePath: either the relative path or the absolute path
        - content: the df to be saved
    """
    content.to_pickle(filePath)

def loadUsingDill(filePath):
    """
    open and retrieve the contents of a file

    use this when opening a file that contains a complex Class object,
    if the object is "simple" use the function loadPickledData()

    Parameters:
    - filePath: either the relative path or the absolute path
    """
    with open(filePath, "rb") as f:
        print("unpickling content in {filePath}")
        return dill.load(f)

def saveUsingDill(filePath, content):
    """
    same as pickle version, save the content in the provided location

    Parameters:
    - filePath: either the relative path or the absolute path
    - content: the content to be saved, allows complex class instance
    """
    with open(filePath, "wb") as f:
        dill.dump(content, f)
        print(f"successfully saved {content} at {filePath}")

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

def make_df(folder, fileName, debug=True):
    """
        creates a panda dataframe from the contents in a csv file

        Parameters:
        - folder: the folder where the file is located, use empty string, "", if the file isnt nested
        - fileName: the name of the file
    """
    a = formatData(folder, fileName)
    a.fillna(0, inplace =True)
    if debug:
        print("this is a preview of the data that you're loading:")
        print(a.head(3))
    return a

def save_df_to_csv(filepath, content):
    content.to_csv(filepath)

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

def mergeR0(pastR0, R0_location):
    pastdata = openCsv(R0_location)
    
    for k, v in pastdata.iteritems():
        if k != "Unnamed: 0":
            datastring = v[0]
            
            datastring = "".join([i for i in datastring if i not in ["[", "]"]])
            datastring = datastring.split(",")
            datastring = [float(i) for i in datastring]
            
            pastR0[k]= (datastring, '(npMean, stdev, rangeVal, median)',)
    

    """
    request_name = "request_7"
    saveName = "R0"
    output_dir = fileRelated.fullPath(request_name, "outputs")
    Path(output_dir).mkdir(parents=False, exist_ok=True)
    output_folder = "outputs/"+ request_name
    statfile.comparingBoxPlots(dict_A, plottedData="R0", saveName=saveName, outputDir=output_folder)
    """

def main():
    # run this to check if the files can be extracted
    a = formatData("configuration", "agents.csv")
    print(a)




if __name__ == "__main__":
    main()