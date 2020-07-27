import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
# the code works but a bit slow, so open for change


def pickClass(tickets,ASched,BSched):
   j = 0
   found = 0
   while found == 0 and j < len(tickets):
      TOD = tickets[j][3]
      D = tickets[j][4]
      if D == "A":
         if ASched[TOD] == None:
            found = 1
            return j
      else:
         if BSched[TOD] == None:
            found = 1
            return j
      j+=1
   if found == 0:
      return None

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
   

def scheduleCreator(social):
    #Params
    g = 0.15 # the probability of going to the gym on any particular day
    s = social # the probability of going to a social space
    lib = 0.25 # the probability of going to the library
    sp = social #the probability of going to a social space, as an off-campus student
    libp = 0.25 #the probability or going to the library, as an off-campus student
    d = 1 - s - lib # the probability of going back to your dorm for an off campus student

   
    # Create Agents
    agentTypes = ["STEM","Humanities","Arts"]
    numAgent = 2000
    modTime = 24
    randomizedAgents = list(itertools.repeat("S",1000))
    randomizedAgents.extend(list(itertools.repeat("H",500)))
    randomizedAgents.extend(list(itertools.repeat("A",500)))
    OnorOff = list(itertools.repeat("On",1500))
    OnorOff.extend(list(itertools.repeat("Off",500)))
    random.shuffle(OnorOff)

    #Define the classtimes
    class_times = [10,12,14,16]
    class_days = ["A","B"]

    # Define the sizes of the classrooms and buildlings
    small_class_size = 10
    medium_class_size = 15
    large_class_size = 20
    small_building_size=[3,0,0] #number of [small,medium,large] classrooms
    medium_building_size=[2,3,0]
    large_building_size=[5,3,3]
    num_STEM_buildings = [2,2,3] #number of [small,medium,large] buildings
    num_Arts_buildings = [2,1,1]
    num_Hum_buildings = [1,2,1]
    #total_num_classrooms = num_STEM_buildings[0]*sum(small_building_sizes) + num_STEM_buildings[1]*sum(medium_building_sizes) + num_STEM_buildings[2]*sum(large_building_sizes) + num_Hum_buildings[0]*sum(small_building_sizes) + num_Hum_buildings[1]*sum(medium_building_sizes) + num_Hum_buildings[2]*sum(large_building_sizes) + num_Arts_buildings[0]*sum(small_building_sizes) + num_Arts_buildings[1]*sum(medium_building_sizes) + num_Arts_buildings[2]*sum(large_building_sizes)


    #Create a set of tickets
    #STEM
    stem_tickets = []

    classroom_counter=0
    building_counter=0
    for i in range(0,num_STEM_buildings[0]):  #small STEM buildings
        for j in range(0,small_building_size[0]): #small classrooms in small STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,small_building_size[1]): #medium classrooms in small STEM buildings
            for	k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for	m in range(0,medium_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,small_building_size[2]): #large classrooms in small STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    for i in range(0,num_STEM_buildings[1]): #medium STEM buildings
        for j in range(0,medium_building_size[0]): #small classrooms in medium STEM buildings
            for	k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for	m in range(0,small_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,medium_building_size[1]): #medium classrooms in medium STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,medium_building_size[2]): #large classrooms in medium STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    for i in range(0,num_STEM_buildings[2]): #large STEM buildings
        for j in range(0,large_building_size[0]): #small classrooms in large STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,large_building_size[1]): #medium classrooms in large STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,large_building_size[2]): #large classrooms in large STEM buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        stem_tickets.append((classroom_counter,building_counter,"STEM",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    

    #Humanities
    hum_tickets=[]
    for i in range(0,num_Hum_buildings[0]):  #small Hum buildings
        for j in range(0,small_building_size[0]): #small classrooms in small Hum buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                       hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,small_building_size[1]): #medium classrooms in small Hum  buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,small_building_size[2]): #large classrooms in small Hum buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    for i in range(0,num_Hum_buildings[1]):  #medium Hum buildings
        for j in range(0,medium_building_size[0]): #small classrooms in medium Hum buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,medium_building_size[1]): #medium classrooms in medium Hum  buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,medium_building_size[2]): #large classrooms in medium Hum buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    for i in range(0,num_Hum_buildings[2]):  #large Hum buildings
        for j in range(0,large_building_size[0]): #small classrooms in large Hum buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,large_building_size[1]): #medium classrooms in large Hum  buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,large_building_size[2]): #large classrooms in large Hum buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        hum_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1

    #ARTS
    arts_tickets=[]
    for i in range(0,num_Arts_buildings[0]):  #small Arts buildings
        for j in range(0,small_building_size[0]): #small classrooms in small Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Arts",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,small_building_size[1]): #medium classrooms in small Arts  buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Arts",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,small_building_size[2]): #large classrooms in small Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Arts",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    for i in range(0,num_Arts_buildings[1]):  #medium Arts buildings
        for j in range(0,medium_building_size[0]): #small classrooms in medium Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Arts",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,medium_building_size[1]): #medium classrooms in medium Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Arts",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,medium_building_size[2]): #large classrooms in medium Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Arts",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1
    for i in range(0,num_Arts_buildings[2]):  #large Arts buildings
        for j in range(0,large_building_size[0]): #small classrooms in large Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,small_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,large_building_size[1]): #medium classrooms in large Arts  buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,medium_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        for j in range(0,large_building_size[2]): #large classrooms in large Arts buildings
            for k in range(0,len(class_times)):
                for l in range(0,len(class_days)):
                    for m in range(0,large_class_size):
                        arts_tickets.append((classroom_counter,building_counter,"Hum",class_times[k],class_days[l]))
            classroom_counter+=1
        building_counter+=1



    #Shuffle the groups of tickets
    random.shuffle(stem_tickets)
    random.shuffle(hum_tickets)
    random.shuffle(arts_tickets)
    """
    print(len(stem_tickets))
    print(len(hum_tickets))
    print(len(arts_tickets))

    print(classroom_counter)
    print(building_counter)
    """
    schedule = []

    #Assign the in-division courses first
    for i in range(0,numAgent): #i is my variable for the agent ID
        if OnorOff[i] == "On":
           mySchedA=['sleep']*8 + [None]*14 + ['sleep']*2 #Initialize the schedule
           mySchedB=['sleep']*8 + [None]*14 + ['sleep']*2
        else:
           mySchedA=['Off']*9 + [None]*9 + ['Off']*6
           mySchedB=['Off']*9 + [None]*9 + ['Off']*6

        foundClasses = 0
        if randomizedAgents[i] == 'S':
           j = pickClass(stem_tickets,mySchedA,mySchedB)
           if j != None:
              TOD = stem_tickets[j][3]
              if stem_tickets[j][4] == "A":
                 mySchedA[TOD] = (stem_tickets[j][0],stem_tickets[j][1],"STEM") #store the class ID and the building ID
                 mySchedA[TOD+1] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
              else:
                 mySchedB[TOD] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                 mySchedB[TOD+1] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
              stem_tickets.pop(j)
              foundClasses+=1
           j = pickClass(stem_tickets,mySchedA,mySchedB)
           if j != None:
              if stem_tickets[j][4] == "A":
                 mySchedA[stem_tickets[j][3]] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                 mySchedA[stem_tickets[j][3]+1] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
              else:
                 mySchedB[stem_tickets[j][3]] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                 mySchedB[stem_tickets[j][3]+1] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
              stem_tickets.pop(j)
              foundClasses+=1
        elif randomizedAgents[i] == 'H':
            j = pickClass(hum_tickets,mySchedA,mySchedB)
            if j != None:
               TOD = hum_tickets[j][3]
               if hum_tickets[j][4] == "A":
                  mySchedA[TOD] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                  mySchedA[TOD+1] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
               else:
                  mySchedB[TOD] =(hum_tickets[j][0],hum_tickets[j][1],"Hum")
                  mySchedB[TOD+1] =(hum_tickets[j][0],hum_tickets[j][1],"Hum")
               hum_tickets.pop(j)
               foundClasses+=1
            j=pickClass(hum_tickets,mySchedA,mySchedB)
            if j != None:
               if hum_tickets[j][4] == "A":
                  mySchedA[hum_tickets[j][3]] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                  mySchedA[hum_tickets[j][3]+1] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
               else:
                  mySchedB[hum_tickets[j][3]] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                  mySchedB[hum_tickets[j][3]+1] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
               hum_tickets.pop(j)
               foundClasses+=1
        else:
            j = pickClass(arts_tickets,mySchedA,mySchedB)
            if j != None:
               TOD = arts_tickets[j][3]
               if arts_tickets[j][4] == "A":
                  mySchedA[TOD] = (arts_tickets[j][0],arts_tickets[j][1],"Arts")
                  mySchedA[TOD+1] = (arts_tickets[j][0],arts_tickets[j][1],"Arts")
               else:
                  mySchedB[TOD] = (arts_tickets[j][0],arts_tickets[j][1],"Arts")
                  mySchedB[TOD+1] = (arts_tickets[j][0],arts_tickets[j][1],"Arts")
               arts_tickets.pop(j)
               foundClasses+=1
            j=pickClass(arts_tickets,mySchedA,mySchedB)
            if j != None:
               if arts_tickets[j][4] == "A":
                  mySchedA[arts_tickets[j][3]] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
                  mySchedA[arts_tickets[j][3]+1] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
               else:
                  mySchedB[arts_tickets[j][3]] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
                  mySchedB[arts_tickets[j][3]+1] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
               arts_tickets.pop(j)
               foundClasses+=1


        #done with the initial major classes, now pick two additional classes
        tried = [0,0,0]
        while foundClasses < 4 and min(tried)<=2: #Then I still need to find another class
           m = random.randint(1,3)
           if m == 1:
              tried[0]+=1
              j = pickClass(stem_tickets,mySchedA,mySchedB)
              if j != None:
                 if stem_tickets[j][4] == "A":
                    mySchedA[stem_tickets[j][3]] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                    mySchedA[stem_tickets[j][3]+1] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                 else:
                    mySchedB[stem_tickets[j][3]] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                    mySchedB[stem_tickets[j][3]+1] = (stem_tickets[j][0],stem_tickets[j][1],"STEM")
                 stem_tickets.pop(j)
                 foundClasses += 1
           elif m ==2:
              tried[1]+=1
              j = pickClass(hum_tickets,mySchedA,mySchedB)
              if j != None:
                 if hum_tickets[j][4] == "A":
                    mySchedA[hum_tickets[j][3]] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                    mySchedA[hum_tickets[j][3]+1] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                 else:
                    mySchedB[hum_tickets[j][3]] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                    mySchedB[hum_tickets[j][3]+1] = (hum_tickets[j][0],hum_tickets[j][1],"Hum")
                 hum_tickets.pop(j)
                 foundClasses +=1
           else:
              tried[2]+=1
              j = pickClass(arts_tickets,mySchedA,mySchedB)
              if j != None:
                 if arts_tickets[j][4] == "A":
                    mySchedA[arts_tickets[j][3]] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
                    mySchedA[arts_tickets[j][3]+1] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
                 else:
                    mySchedB[arts_tickets[j][3]] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
                    mySchedB[arts_tickets[j][3]+1] =(arts_tickets[j][0],arts_tickets[j][1],"Arts")
                 arts_tickets.pop(j)
                 foundClasses +=1

        #print(foundClasses)
        #Now pick dining hall
        if OnorOff[i] == "Off": #off campus student
           mySchedW = ["Off"]*24
           #Day A has one visit to the dining Hall
           meal = False
           while meal == False:
              x = random.choice([8,9,10,11,12,13,14,15,17,18,19,20])
              if mySchedA[x] == None:
                 meal = True
                 mySchedA[x] = 'dining'

           #Day B has one visit to the dining Hall
           meal = False
           while meal == False:
              x = random.choice([8,9,10,11,12,13,14,15,17,18,19,20])
              if mySchedB[x] == None:
                 meal = True
                 mySchedB[x] = 'dining'
        else:
           mySchedW = ['sleep']*8 + [None]*14 + ['sleep']*2
           #Visits to the Dining Hall on Day A
           B = False
           tries = 0
           while B == False and tries < 8:
              x = random.randint(8,11)
              tries+=1
              if mySchedA[x] == None:
                 B = True
                 mySchedA[x] = 'dining'
           L = False
           tries = 0
           while L == False and tries < 8:
              x = random.randint(12,15)
              tries+=1
              if mySchedA[x] == None:
                 L = True
                 mySchedA[x] = 'dining'
           D = False
           tries = 0
           while D == False and tries < 8:
              x = random.randint(17,20)
              tries += 1
              if mySchedA[x] == None:
                 D = True
                 mySchedA[x] = 'dining'

           #Visits to the dining Hall on Day B
           B = False
           tries = 0
           while B == False and tries < 8:
              x = random.randint(8,11)
              tries += 1
              if mySchedB[x] == None:
                 B = True
                 mySchedB[x] = 'dining'
           L = False
           tries = 0
           while L == False and tries < 8:
              x = random.randint(12,15)
              tries+=1
              if mySchedB[x] == None:
                 L = True
                 mySchedB[x] = 'dining'
           D = False
           tries = 0
           while D == False and tries < 8:
              x = random.randint(17,20)
              tries += 1
              if mySchedB[x] == None:
                 D = True
                 mySchedB[x] = 'dining'
                 
           #Visits to the dining hall on Day W
           x = random.randint(8,11)
           mySchedW[x] = 'dining'
           x = random.randint(12,15)
           mySchedW[x] = 'dining'
           x = random.randint(17,20)
           mySchedW[x] = 'dining'


        #Decide if we're going to the Gym each day
        if random.random() < g: #add a gym to Day A
           AvailableSlots = [m for m in range(len(mySchedA)) if mySchedA[m] == None]
           if len(AvailableSlots) != 0:
              gymtime = random.choice(AvailableSlots)
              mySchedA[gymtime] = 'gym'
        if random.random() < g: #add a gym to Day B
           AvailableSlots = [m for m in range(len(mySchedB)) if mySchedB[m] == None]
           if len(AvailableSlots) != 0:
              gymtime = random.choice(AvailableSlots)
              mySchedB[gymtime] = 'gym'
        if OnorOff[i] == "On" and random.random() < g: #add a gym to Day W
           AvailableSlots = [m for m in range(len(mySchedW)) if mySchedW[m] == None]
           if len(AvailableSlots) != 0:
              gymtime = random.choice(AvailableSlots)
              mySchedW[gymtime] = 'gym'
        
        #Now pick all extras: Social,Library,and Hanging out in Dorm
        AvailableSlots = [m for m in range(len(mySchedA)) if mySchedA[m] == None]
        for x in AvailableSlots: #for each available slot fill it in with something
           Task = random.random()
           if OnorOff[i] == "On" and Task < lib: #this is an l, for library
              mySchedA[x] = 'library'
           elif OnorOff[i] == "On" and Task < lib+s:
              mySchedA[x] = 'social'
           elif OnorOff[i] == "On":
              mySchedA[x] = 'dorm'
           elif Task < libp:
              mySchedA[x] = 'library'
           else:
              mySchedA[x] = 'social'
        AvailableSlots = [m for m in range(len(mySchedB)) if mySchedB[m] == None]
        for x in AvailableSlots:
           Task = random.random()
           if OnorOff[i] == "On" and Task < lib:
              mySchedB[x] = 'library'
           elif OnorOff[i] == "On" and Task < lib+s:
              mySchedB[x] = 'social'
           elif OnorOff[i] == "On":
              mySchedB[x] = 'dorm'
           elif Task < libp:
              mySchedB[x] = 'library'
           else:
              mySchedB[x] = 'social'
        AvailableSlots = [m for m in range(len(mySchedW)) if mySchedW[m] == None]
        for x in AvailableSlots:
           Task = random.random()
           if OnorOff[i] == "On" and Task < lib:
              mySchedW[x] = 'library'
           elif OnorOff[i] == "On" or Task < lib+s:
              mySchedW[x] = 'social'
           elif OnorOff[i] == "On":
              mySchedW[x] = 'dorm'
           elif Task < libp:
              mySchedW[x] = 'lirary'
           else:
              mySchedW[x] = 'social'
        

        #All done!
        schedule.append([mySchedA,mySchedB,mySchedW])
        
            


    # print the first 5 agent's schedule
    #print(schedule[:5])

    #createMask(numAgent)
    return (schedule, OnorOff)

def main():
    schedule = scheduleCreator(0.15)
    print(schedule[0][:5])
if __name__ == "__main__":
    main()
