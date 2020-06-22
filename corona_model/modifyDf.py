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
        for _ in range(rows[objCount]):
            rowList.append( {key:val for key, val in zip(colName, rows[colName])})
    return pd.DataFrame(rowList)

def createPartitions(df):
    """
        creates a new df filled with informations on the partitions,
        the default header is ["room_name", "capacity", "located_building", "connected_to", "travel_time"]

    """
    leaves, capacities = ["sl", "ml", "ll"] , ["sc", "mc", "lc"]
    nameStr, connection = "room_name", "connected_to"
    rowList, colName = [], list(df.columns.values)
    
    for index, rows in df.iterrows(): # iterate over each structure
        for leafName, capacity in zip(leaves, capacities):# create the small, medium, large
            for _ in range(rows[leafName]): # for each size make the corresponding rooms
                hubName = "_hub"# if rows["room_name"] != "transit_space" else ""
                
                dict1 = {"room_name": rows["room_name"], 
                        "capacity" : rows[capacity],
                        "located_building": rows["building_name"],
                        "connected_to": rows["building_name"]+hubName,
                        "travel_time": 1,
                        "building_type":rows["building_type"]               
                }
                rowList.append(dict1)
         
        # add the hallways, for each building 
        flippedHub =dict(rowList[-1])
        flippedHub[nameStr], flippedHub["connected_to"] = flippedHub["connected_to"], "transit_space_hub"
        rowList.append(flippedHub)
    #row_list.append({"room_name":"transit_space", "capacity": 1000, "located_building": "transit_space", "connected_to": "transit_space", "travel_time": 1})
    return pd.DataFrame(rowList)

def mod_building():
    original_df = flr.make_df("configuration", "new_building.csv")
    building_df = assignUniqueName(createSuperStruc(original_df), "building_name")
    building_df.index+=1
    print(building_df)
    room_df = createPartitions(building_df)
    room_df = assignUniqueName(room_df, "room_name")
    print(room_df)
    room_df.index +=1
  
    print(room_df.loc[room_df["located_building"] == "dorm17"])
    return building_df, room_df
    
def main():
    mod_building()
   

if __name__ == "__main__":
    main()