import pandas as pd
import fileRelated as flr
import numpy as np

def assignUniqueName(df, columnName="building_name", groupingCol=""):
    """
        gets a column filled with names of building or rooms and assign comprehensible unqiue names to it,
        if the column_name is not a valid name in the header, then it will choose the first column as the name column
        the grouping_name is also a header value and should group the names.
        Example:
        code: column_name = "room_name", second_name = "building_name"
        csv file:
        room_name, building_name    -->     outputs (modified name)
        dorm,       DormA           -->     DormA_dorm_1
        dorm,       DormA           -->     DormA_dorm_2
        dorm,       DormB           -->     DormB_dorm
    """
    # use the first entry as the "name" column if the name is not valid
    headerVal, nameCount = list(df.columns.values), dict()
    columnName = headerVal[0] if  columnName not in headerVal else columnName
    
    # check if we want to group the names
    grouping = True if groupingCol != "" else False
    
    for index, rowVal in df.iterrows():
        itemName = str(rowVal[columnName])
        groupName = str(rowVal[groupingCol]) + "_" if grouping else ""
        newName = (groupName + itemName).replace(" ", "_")
        # count the occurrnace of unique names
        nameCount[newName] = nameCount.get(newName, 0) + 1
        entry = newName
        if nameCount[newName] > 1 and newName not in["transit_space_hallway", "transit_space_hub", "transit_space"]:
            entry+=str(nameCount[entry])
        df.loc[index, columnName] = entry
    return df

def createSuperStruc(df, objCount="count"):
    """
       creates multiple of the same object by looking at the obj_count and returns a new df that contains the multiplied rows 
    """
    rowList, colName = [], list(df.columns.values)
    colName.remove(objCount)
    for _, rows in df.iterrows():
        
        for _ in range(int(rows[objCount])):
            rowList.append( {key:val for key, val in zip(colName, rows[colName])})
    return pd.DataFrame(rowList)

def createPartitions(df):
    """
        creates a new df filled with informations on the partitions,
        the default header is ["room_name", "capacity", "located_building", "connected_to", "travel_time"]

    """
    leaves = ["leaf_S", "leaf_M", "leaf_L"]
    capacities = ["cap_S", "cap_M", "cap_L"]
    limits = ["enroll_S", "enroll_M", "enroll_L"]
    nameStr, connection = "room_name", "connected_to"
    rowList, colName = [], list(df.columns.values)
    hubName = "_hub"
    for index, rows in df.iterrows(): # iterate over each structure
        for leafName, capacity, limit in zip(leaves, capacities, limits):# create the small, medium, large
            for _ in range(int(rows[leafName])): # for each size make the corresponding rooms
                dict1 = {nameStr: rows[nameStr], 
                        "capacity" : rows[capacity],
                        "limit" : rows[limit],
                        "located_building": rows["building_name"],
                        "connected_to": rows["building_name"]+hubName,
                        "travel_time": 1,
                        "building_type":rows["building_type"],
                        "Kv":rows["Kv"]             
                }
                rowList.append(dict1)
        hubDict = {
            nameStr: rows[nameStr] + hubName, 
            "capacity" : rows["hubCapacity"],
            "limit": rows["hubCapacity"],
            "located_building": rows["building_name"],
            "connected_to": "transit_space_hub",
            "travel_time": 1,
            "building_type":rows["building_type"],
            "Kv":rows["hubKv"]
        }
        # add the hallways, for each building 
        previousRoom = dict(rowList[-1])
        hubDict[nameStr] = previousRoom["connected_to"]
        rowList.append(hubDict)
    return pd.DataFrame(rowList)

def mod_building(fileName, folder):
    original_df = flr.make_df(folder,fileName)
    building_df = assignUniqueName(createSuperStruc(original_df), "building_name")
    building_df.index+=1
    room_df = createPartitions(building_df)
    room_df = assignUniqueName(room_df, "room_name")
    room_df.index +=1
    return building_df, room_df
    
def main():
    mod_building()
   

if __name__ == "__main__":
    main()