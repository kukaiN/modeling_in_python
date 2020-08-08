import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
# the code works but a bit slow, so open for change



## NOTES
##
## schedule.py returns the list of schedules in the following form:
## [S1,S2,S3,....S2000]
## Where Si is the schedule for student i
##
## Each schedule Si has the Following format:
## [A,B,W]
## That is, the schedule for day A, the schedule for Day B, and the schedule for the weekend
##
## Each of the A,B,W schedules is of length 24, of the following form:
## ['sleep',...,'sleep','dining',(0,1),(0,1),'dining','library','gym',.....]
##
## The possible options inside of the schedule:
## 'gym', 'library','social','dining','sleep','dorm'

def ticketCreation(countArray, seatRoomMatrix, buildingMatrix):
    tickets = []
    roomCounts = [seatRoomMatrix[i] for buildingCounts in buildingMatrix 
                    for i, buildingCount in enumerate(buildingCounts) for _ in range(buildingCount)]
    
    ticketNumber = 0
    for roomCount in roomCounts:
        for roomNum ,count in zip(roomCount, countArray):
            for num in range(roomNum):
                tickets.extend([ticketNumber]*count)
                ticketNumber+=1
    
    return tickets

def scheduleCreator(social, onCampusCount=1500, offCampusCount = 500):
    #Params
    g = 0.15 # the probability of going to the gym on any particular day
    s = social # the probability of going to a social space
    lib = 0.15 # the probability of going to the library
    sp = social #the probability of going to a social space, as an off-campus student
    libp = 0.15 #the probability or going to the library, as an off-campus student
    d = 1 - s - lib # the probability of going back to your dorm for an off campus student

   
    # Create Agents
    agentTypes = ["STEM","Humanities","Arts"]
    numAgent = onCampusCount+offCampusCount
    modTime = 24
    StudentDistribution = [0.5, 0.25, 0.25]
    studentTypes = ["S", "H", "A"]
    studentDistinction = [studentTp for studentTp, distribution in zip(studentTypes, StudentDistribution) 
                            for _ in range(int(distribution*numAgent))]
    OnorOff = list(itertools.repeat("On",1500))
    OnorOff.extend(list(itertools.repeat("Off",500)))
    random.shuffle(OnorOff)

    #Define the classtimes
    class_times = [10,12,14,16]
    class_days = ["O","E"]
    days = ["O", "E", "W"]
    # Define the sizes of the classrooms and buildlings
    roomCountArray = [10, 15, 20]
    small_building=[3,0,0] #number of [small,medium,large] classrooms
    medium_building=[2,3,0]
    large_building=[5,3,3]
    num_STEM_buildings = [2,2,3] #number of [small,medium,large] buildings
    num_Arts_buildings = [2,1,1]
    num_Hum_buildings = [1,2,1]
    #total_num_classrooms = num_STEM_buildings[0]*sum(small_building_sizes) + num_STEM_buildings[1]*sum(medium_building_sizes) + num_STEM_buildings[2]*sum(large_building_sizes) + num_Hum_buildings[0]*sum(small_building_sizes) + num_Hum_buildings[1]*sum(medium_building_sizes) + num_Hum_buildings[2]*sum(large_building_sizes) + num_Arts_buildings[0]*sum(small_building_sizes) + num_Arts_buildings[1]*sum(medium_building_sizes) + num_Arts_buildings[2]*sum(large_building_sizes)
    classId = 0

    sizeMatrix = [small_building, medium_building, large_building]
    buildingMatrix = [num_STEM_buildings, num_Arts_buildings, num_Hum_buildings] 
    tickets = ticketCreation(roomCountArray, sizeMatrix, buildingMatrix)
    A_day_tickets = [[(roomId, timeVal) for roomId in tickets] for timeVal in class_times]
    B_day_tickets = [[(roomId, timeVal) for roomId in tickets] for timeVal in class_times]
    
    print(tickets)

    schedules = [0] * numAgent
    onCampusTemplate = ['sleep']*8 + [None]*14 + ['sleep']*2
    offCampusTemplate = ['Off']*9 + [None]*9 + ['Off']*6
    classTimeIndices = [(i, j) for i in range(len(class_days)) for j in range(len(class_times))]

    Type_to_class = []
    

    print(classTimeIndices)
    for index, OnVOff in enumerate(OnorOff):
        schedule = [template for _ in days] if OnVOff == "On" else [offCampusTemplate for _ in days]
        

    
            


    # print the first 5 agent's schedule
    #print(schedule[:5])

    #createMask(numAgent)
    return (schedule, OnorOff)

def main():
    schedule = scheduleCreator(0.00)
    print(schedule[0][:10])
if __name__ == "__main__":
    main()
