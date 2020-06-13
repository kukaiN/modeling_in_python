import os
import platform
import pandas as pd
import pickle

def load_pickle(filepath, default):
    """load an existing pickle file or make a pickle with default data and return the pickled data"""
    try:
        with open(filepath, "rb") as f:
            x = pickle.load(f)
    except Exception:
        x = default
        with open(filepath, "wb") as f:
            pickle.dump(x, f)
    return x

def open_csv(filepath, default = ["new df here"]):
    """returns the content of the csv file if it exists."""
    try:
        x = pd.read_csv(filepath, error_bad_lines=False)
    except Exception:
        print(f"exception, the filename {filepath} you requested to open was not found.")
        if (int(input("do you want to make a new file? 1 for yes, 0 for no")) == 1):
            x = pd.dataframe(default)
            x.to_csv(filepath, index=False, header=False)
    return x
    
def save_pickle(filepath, content):
    content.to_pickle(filepath)

def format_data(folder, filename):
    """get the relevant data from the file with the corresponding filename, then make a dictionary out of it"""
    _, filepath = get_cd()
    # we need the os name because different OS uses / or \ to navigate the file system 
    os_name = platform.system()
    # get the full path to the file that we're trying to open, and depending on the OS, the slashes changes
    full_file_name = filepath + folder + "\\" + filename
    if os_name == "Linux":
        full_file_name = full_file_name.replace("\\", "/")
    elif os_name == "Windows":
        pass
    elif os_name == "Darwin":
        full_file_name = full_file_name.replace("\\", "/")
    # get the content of the file and convert it to a panda dataframe
    content = open_csv(full_file_name, [])
    df_list = [content.columns.values.tolist()]+content.values.tolist()
    # remove white spaces in font and back of all entries
    df_list = [[txt.strip() if type(txt) == str else txt for txt in lst] for lst in df_list]
    # make a new dataframe from the list, also use the first line in the dataframe as the new header
    new_df = pd.DataFrame(df_list)
    new_header = new_df.iloc[0]
    new_df = new_df[1:]
    new_df.columns = new_header
    return new_df


def get_cd():
    """
    uses the os.path function to get the filename and the absolute path to the current directory
    Also does a primative check to see if the path is correct, there has been instances where the CD was different, hence the check.
    """
    # Get the path to this file
    scriptpath, filepath = os.path.realpath(__file__), ""  
    # get the os name and the backslash or forward slash depending on the OS
    os_name = platform.system()
    path_slash = "/" if os_name in ["Linux", 'Darwin'] else "\\"
    # remove the file name from the end of the path
    for i in range(1,len(scriptpath)+1):
        if scriptpath[-i] == path_slash:
            scriptpath = scriptpath[0:-i]#current path, relative to root direcotory or C drive
            break    
    if os.getcwd() != scriptpath: filepath = scriptpath + path_slash
    return scriptpath, filepath

a = format_data("configuration", "agents.csv")
print(a)