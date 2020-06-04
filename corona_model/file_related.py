import os
import pandas as pd

def load_pickle(filepath, default):
    """load an existing pickle file or make a pickle with default data and return the pickled data"""
    try:
        with open(filepath, "rb") as f:
            x = pickle.load(f)
    except Exception:
        x = default
        with open(path, "wb") as f:
            pickle.dump(x, f)
    return x

def open_csv(filepath, default = ["new here"]):
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

def format_data(filename):
    """get the relevant data from the file with the corresponding filename, then make a dictionary out of it"""
    cd, filepath = get_cd()
    content = open_csv(filepath+"configuration\\" + filename, [])
    df_list = [content.columns.values.tolist()]+content.values.tolist()
    df_list = [[txt.strip() if type(txt) == str else txt for txt in lst] for lst in df_list]
    # make a new dataframe from the list
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
    scriptpath, filepath = os.path.realpath(__file__), "" # Get the file path to the screenshot image to analize 
    for i in range(1,len(scriptpath)+1):
        if scriptpath[-i] == "\\":
            scriptpath = scriptpath[0:-i]#current path, relative to root direcotory or C drive
            break
    if os.getcwd() != scriptpath: filepath = scriptpath + "\\"
    return scriptpath, filepath
