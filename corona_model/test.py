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

if __name__ == '__main__':
    import timeit
    print(timeit.timeit("test()", setup="from __main__ import test"))
    print(timeit.timeit("test2()", setup="from __main__ import test2"))