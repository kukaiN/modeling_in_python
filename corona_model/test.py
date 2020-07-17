import schedule_students as sts


#schedule = sts.main()

def replaceEntry(schedule, antecedent, replacement):
    """
        replace entry with a different value convert all antecedent to replacement
    
        Parameters:
        - schedule: the whole schedule( include A, B, W)
        - antecedent: the value to convert
        - replacement: the value to be converted to

    """
    return [[a if a != antecedent else replacement for a in row] for row in schedule]

"""
for i, sche in enumerate(schedule):
    print(i, "th agent")
    
    #row = replaceEntry(sche, "Off", "Dorm")
    #row = replaceEntry(row, "Off", "Dorm")
    print(sche)
    if i > 40:
        break

"""
def test():
    """Stupid test function"""
    a = 5
    for i in range(10000):
        a = 5

def test2():
    for i in range(10000):
        # comment
        pass

def rand1():
    for i in range(24*40):
        a = np.random.random(2200)

def rand2():
    for i in range(24*20):
        a = np.random.random(2200-(3*i))


if __name__ == '__main__':
    import timeit
    #print(timeit.timeit("test()", setup="from __main__ import test"))
    #print(timeit.timeit("test2()", setup="from __main__ import test2"))
    #print(timeit.timeit("rand1()", setup="import numpy as np"))
    #print(timeit.timeit("rand2()", setup="import numpy as np"))    
    a = [1, 2, 3]
    b = set(a)
    b.add(4)
    b.add(7)
    b.add(99)
    b.discard(9)
    b.discard(99)
    for x in b:
        print(x)