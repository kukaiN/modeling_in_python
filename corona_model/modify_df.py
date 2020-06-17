import pandas as pd
import file_related as flr
import numpy as np

def assign_unique_name(df, column_name="building_name", grouping_col=""):
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
    header_val, name_count = list(df.columns.values), dict()
    column_name = header_val[0] if  column_name not in header_val else column_name
    
    # check if we want to group the names
    grouping = True if grouping_col != "" else False
    
    for index, row_val in df.iterrows():
        item_name = str(row_val[column_name])
        group_name = str(row_val[grouping_col]) + "_" if grouping else ""
        new_name = (group_name + item_name).replace(" ", "_")
        # count the occurrnace of unique names
        name_count[new_name] = name_count.get(new_name, 0) + 1
        entry = new_name
        if name_count[new_name] > 1 and new_name not in["transit_space_hallway", "transit_space_hub", "transit_space"]:
            entry+=str(name_count[entry])
        df.loc[index, column_name] = entry
    return df

def create_SuperStruc(df, obj_count="count"):
    """
       creates multiple of the same object by looking at the obj_count and returns a new df that contains the multiplied rows 
    """
    row_list, col_name = [], list(df.columns.values)
    col_name.remove(obj_count)
    for _, rows in df.iterrows():
        for _ in range(rows[obj_count]):
            row_list.append( {key:val for key, val in zip(col_name, rows[col_name])})
    return pd.DataFrame(row_list)

def create_Partitions(df):
    """
        creates a new df filled with informations on the partitions,
        the default header is ["room_name", "capacity", "located_building", "connected_to", "travel_time"]

    """
    leaves, capacities = ["sl", "ml", "ll"] , ["sc", "mc", "lc"]
    name_str, connection = "room_name", "connected_to"
    row_list, col_name = [], list(df.columns.values)
    
    for index, rows in df.iterrows(): # iterate over each structure
        for leaf_name, capacity in zip(leaves, capacities):# create the small, medium, large
            for _ in range(rows[leaf_name]): # for each size make the corresponding rooms
                hub_name = "_hub"# if rows["room_name"] != "transit_space" else ""
                
                dict1 = {"room_name": rows["room_name"], 
                        "capacity" : rows[capacity],
                        "located_building": rows["building_name"],
                        "connected_to": rows["building_name"]+hub_name,
                        "travel_time": 1               
                }
                row_list.append(dict1)
         
        # add the hallways, for each building 
        flipped_hub =dict(row_list[-1])
        flipped_hub[name_str], flipped_hub["connected_to"] = flipped_hub["connected_to"], "transit_space_hub"
        row_list.append(flipped_hub)
    #row_list.append({"room_name":"transit_space", "capacity": 1000, "located_building": "transit_space", "connected_to": "transit_space", "travel_time": 1})
    return pd.DataFrame(row_list)

def mod_building():
    original_df = flr.make_df("configuration", "new_building.csv")
    building_df = assign_unique_name(create_SuperStruc(original_df), "building_name")
    building_df.index+=1
    print(building_df)
    room_df = create_Partitions(building_df)
    room_df = assign_unique_name(room_df, "room_name")
    print(room_df)
    room_df.index +=1
  
    print(room_df.loc[room_df["located_building"] == "dorm17"])
    return building_df, room_df
    
def main():
    mod_building()
   

if __name__ == "__main__":
    main()