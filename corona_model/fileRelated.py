import os
import platform
import pandas as pd
import pickle
import dill

def loadPickle(filePath, default=["default"]):
    """load an existing pickle file or make a pickle with default data and return the pickled data"""
    try:
        with open(filePath, "rb") as f:
            content = pickle.load(f)
    except Exception:
        content = default
        with open(filePath, "wb") as f:
            pickle.dump(content, f)
    return content

def savedf2Pickle(filePath, content):
    content.to_pickle(filePath)

def pickleModel(filePath, content):
    with open(filePath, "wb") as fileLoc:
        pickle.dump(content, fileLoc)
        print("pickling success")

def loadUsingDill(filepath):
    with open(filepath, "rb") as f:
        print("unpickling content in {filepath}")
        return dill.load(f)

def saveUsingDill(filepath, content):
    with open(filepath, "wb") as f:
        dill.dump(content, f)
        print(f"successfully saved {content} at {filepath}")

def fullPath(fileName, folder=""):
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
    """load config information from a txt file"""
    fullName = fullPath(fileName, folder)
    # get the content of the file and convert it to a list
    with open(fullName) as f:
        content = [line.strip() for line in f.readlines()]
    return content

def openCsv(filePath, default = ["new df here"]):
    """returns the content of the csv file if it exists."""
    try:
        content = pd.read_csv(filePath, error_bad_lines=False)
    except Exception:
        print(f"exception, the filename {filePath} you requested to open was not found.")
        if (int(input("do you want to make a new file? 1 for yes, 0 for no")) == 1):
            content = pd.dataframe(default)
            content.toCsv(filePath, index=False, header=False)
    return content
    

def formatData(folder, fileName):
    """get the relevant data from the file with the corresponding filename, then make a dictionary out of it"""
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

def make_df(folderName, fileName):
    """ creates a panda dataframe from the content in a csv file"""
    a = formatData(folderName, fileName)
    a.fillna(0, inplace =True)
    print("this is a preview of the data that you're loading:")
    print(a.head(3))
    return a


def get_cd():
    """
    uses the os.path function to get the filename and the absolute path to the current directory
    Also does a primative check to see if the path is correct, there has been instances where the CD was different, hence the check.
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
    # run this to check if the files can be extracted
    a = formatData("configuration", "agents.csv")
    print(a)
    



if __name__ == "__main__":
    main()