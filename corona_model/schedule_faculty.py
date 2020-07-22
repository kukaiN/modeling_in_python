import numpy as np
import matplotlib.pyplot as plt
import random
import itertools
# the code works but a bit slow, so open for change


def pickClass(tickets,ASched,BSched):
   q = 0
   found = 0
   while found == 0 and q < len(tickets):
      TOD = tickets[q][2]
      D = tickets[q][3]
      if D == "A":
         if ASched[TOD] == None:
            found = 1
            return q
      else:
         if BSched[TOD] == None:
            found = 1
            return q
      q+=1
   if found == 0:
      return None

## NOTES
##
## schedule.py returns the list of schedules in the following form:
## [F1,F2,F3,....]
## Where Fi is the schedule for faculty i
##
## Each schedule Si has the Following format:
## [A,B,W]
## That is, the schedule for day A, the schedule for Day B, and the schedule for the weekend
##
## Each of the A,B,W schedules is of length 24, of the following form:
## ['off',...,'off','dining',0,0,'office','office','office',.....]
##
## The possible options inside of the schedule:
## 'off',classroom-number, 'office','dining'
   

def scheduleCreator():
    #Params
    dh = 0.3 #probability of going to the dining hall on a particular day.
    # Create Agents
    total_num_classes = 760
    numAgent = round((total_num_classes)/2)
    modTime = 24
    randomizedAgents = list(itertools.repeat("S",round(numAgent/2)))
    randomizedAgents.extend(list(itertools.repeat("H",round(numAgent/4))))
    randomizedAgents.extend(list(itertools.repeat("A",round(numAgent/4)+1)))
    #print(numAgent)
    #print(len(randomizedAgents))


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

    #Notes:

    #There are 15 buildings
    #buildings 0 - 6 are STEM
    #buildings 7 - 10 are Hum
    #buildings 11 - 14 are Arts

    #There are 95 classrooms
    #classrooms 0 - 48 are STEM classrooms
    #classrooms 49 - 70 are Hum classrooms
    #classrooms 71 - 94 are Arts

    #Make classroom tickets
    stem_tickets = []
    hum_tickets = []
    arts_tickets = []
    for i in range(0,48):
       for j in class_times:
          for k in class_days:
             stem_tickets.append(('STEM',i,j,k))
    for i in range(49,70):
       for j in class_times:
          for k in class_days:
             hum_tickets.append(('Hum',i,j,k))
    for i in range(71,94):
       for j in class_times:
          for k in class_days:
             arts_tickets.append(('Arts',i,j,k))
    random.shuffle(stem_tickets)
    random.shuffle(hum_tickets)
    random.shuffle(arts_tickets)
    #print(len(stem_tickets))
    #print(len(arts_tickets))
    #print(len(hum_tickets))

    schedule = []

    for i in range(0,numAgent): #i is my variable for the agent ID
       mySchedA=['Off']*9 + [None]*9 + ['Off']*6
       mySchedB=['Off']*9 + [None]*9 + ['Off']*6
       mySchedW=['Off']*24

       #fill in the rest of the schedule as either 'office', 'classroom', 'dining'

       #classroom
       #assign classroom
       if randomizedAgents[i] == "S":
          j = pickClass(stem_tickets,mySchedA,mySchedB)
          if j != None:
             if stem_tickets[j][3] == "A":
                mySchedA[stem_tickets[j][2]] = stem_tickets[j][1]
                mySchedA[stem_tickets[j][2] + 1] = stem_tickets[j][1]
             else:
                mySchedB[stem_tickets[j][2]] = stem_tickets[j][1]
                mySchedB[stem_tickets[j][2]+1] = stem_tickets[j][1]
             stem_tickets.pop(j)
          j = pickClass(stem_tickets,mySchedA,mySchedB)
          if j != None:
             if stem_tickets[j][3] == "A":
                mySchedA[stem_tickets[j][2]] = stem_tickets[j][1]
                mySchedA[stem_tickets[j][2]+1] = stem_tickets[j][1]
             else:
                mySchedB[stem_tickets[j][2]] = stem_tickets[j][1]
                mySchedB[stem_tickets[j][2]] = stem_tickets[j][1]
             stem_tickets.pop(j)
       elif randomizedAgents[i] == "H":
          j = pickClass(hum_tickets,mySchedA,mySchedB)
          if j != None:
             if hum_tickets[j][3] == "A":
                mySchedA[hum_tickets[j][2]] = hum_tickets[j][1]
                mySchedA[hum_tickets[j][2]+1] = hum_tickets[j][1]
             else:
                mySchedB[hum_tickets[j][2]] = hum_tickets[j][1]
                mySchedB[hum_tickets[j][2]+1] = hum_tickets[j][1]
             hum_tickets.pop(j)
          j = pickClass(hum_tickets,mySchedA,mySchedB)
          if j != None:
             if hum_tickets[j][3] == "A":
                mySchedA[hum_tickets[j][2]] = hum_tickets[j][1]
                mySchedA[hum_tickets[j][2]+1] = hum_tickets[j][1]
             else:
                mySchedB[hum_tickets[j][2]] = hum_tickets[j][1]
                mySchedB[hum_tickets[j][2]] = hum_tickets[j][1]
             hum_tickets.pop(j)
       else:
          j = pickClass(arts_tickets,mySchedA,mySchedB)
          if j != None:
             if arts_tickets[j][3] == "A":
                mySchedA[arts_tickets[j][2]] = arts_tickets[j][1]
                mySchedA[arts_tickets[j][2]+1] = arts_tickets[j][1]
             else:
                mySchedB[arts_tickets[j][2]] = arts_tickets[j][1]
                mySchedB[arts_tickets[j][2]+1] = arts_tickets[j][1]
             arts_tickets.pop(j)
          j = pickClass(arts_tickets, mySchedA, mySchedB)
          if j != None:
             if arts_tickets[j][3] == "A":
                mySchedA[arts_tickets[j][2]] = arts_tickets[j][1]
                mySchedA[arts_tickets[j][2]+1] = arts_tickets[j][1]
             else:
                mySchedB[arts_tickets[j][2]] = arts_tickets[j][1]
                mySchedB[arts_tickets[j][2]+1] = arts_tickets[j][1]
             arts_tickets.pop(j)
         
       #dining hall
       if random.random() < dh: #go to the dining hall on day A
          AvailableSlots = [m for m in range(len(mySchedA)) if mySchedA[m] == None]
          mySchedA[random.choice(AvailableSlots)] = 'dining'
       if random.random() < dh:
          AvailableSlots = [m for m in range(len(mySchedB)) if mySchedB[m] == None]
          mySchedB[random.choice(AvailableSlots)] = 'dining'

       #Now fill in the remaining slots with office
       AvailableSlots = [m for m in range(len(mySchedA)) if mySchedA[m] == None]
       for x in AvailableSlots: #for each available slot fill it in with something
          mySchedA[x] = 'office'
       AvailableSlots = [m for m in range(len(mySchedB)) if mySchedB[m] == None]
       for x in AvailableSlots:
          mySchedB[x] = 'office'
        

       #All done!
       schedule.append([mySchedA,mySchedB,mySchedW])
        
            


    # print the first 5 agent's schedule
    #print(schedule[:5])

    #createMask(numAgent)
    return schedule

def main():
   scheduleCreator()

if __name__ == "__main__":
    main()
