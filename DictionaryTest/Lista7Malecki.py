#Malecki

import os
import datetime

#Zadanie 1

from collections import defaultdict

all_cases = []
by_date = defaultdict(list)
by_country = defaultdict(list)


f = open('.\Covid.txt', "r")

#5print( "\n"*15)
#print( datetime("10.06.2020"))


with open('.\Covid.txt', "r", encoding="utf-8") as f:
    temp = False
    for line in f:
        l = line.split("\t")
        if len(l) != 12:
            print("ups")
        elif temp:
            all_cases.append( (l[6], int(l[3]), int(l[2]), int(l[1]), int(l[5]), int(l[4]) ) )
            by_date[(int(l[3]), int(l[2]), int(l[1]))].append((l[6], int(l[5]), int(l[4])))
            by_country[l[6]].append( (int(l[3]), int(l[2]), int(l[1]), int(l[5]), int(l[4])) )
        temp = True

#print(all_cases[1])
#print( by_country["Afghanistan"][3])


print( all_cases[573])

#Zadanie 2
import time


timerResult = 0.0

'''
print("-"*15)
print("Zadanie 2")
print("-"*15)
'''

def timer(fun):
    def innerTimer(*args):
        #print("Timer for {} has started!".format(fun.__name__))
        startT = time.time()
        retValue = fun(*args)
        startT = time.time() - startT
        #print( "Timer for {} has stopped!".format(fun.__name__))
        #print("Run time: %5.20f miliseconds" % (startT*1000))
        global timerResult
        timerResult = startT*1000
        return retValue
    return innerTimer

@timer
def for_date_a( year, month, day):
    retVal = [0, 0]
    for (x1, y, m, d, death, case) in all_cases:
        if day == d and month == m and year == y:
            retVal[0] += death
            retVal[1] += case
    return tuple(retVal)

@timer
def for_date_d( year, month, day):
    retVal = [0, 0]
    for (x1, death, case) in by_date[(year, month, day)]:
        retVal[0] += death
        retVal[1] += case
    return tuple(retVal)

@timer
def for_date_c( year, month, day):
    retVal = [0, 0]
    for country in by_country.values():
        for (y, m, d, death, case) in country:
            if day == d and month == m and year == y:
                retVal[0] += death
                retVal[1] += case
                break #znacznie przyspiesza - wiemy, ze tylko jedna data na panstwo (predkosc zalezy od kolejnosci)
    return tuple(retVal)


dateToSearch = (2020, 8, 8)


print(for_date_a(*dateToSearch))
print(for_date_d(*dateToSearch))
print(for_date_c(*dateToSearch))


#Zadanie 3

print("-"*15)
print("Zadanie 3")
print("-"*15)


@timer
def for_country_a( country):
    retVal = [0, 0]
    for (c, y, m, d, death, case) in all_cases:
        if c == country:
            retVal[0] += death
            retVal[1] += case
    return tuple(retVal)

@timer
def for_country_d( country):
    retVal = [0, 0]
    for temp in by_date.values():
        for (c, death, case) in temp:
            if c == country:
                retVal[0] += death
                retVal[1] += case
                break
    return tuple(retVal)

@timer
def for_country_c( country):
    retVal = [0, 0]
    for (y, m, d, death, case) in by_country[country]:
            retVal[0] += death
            retVal[1] += case
    return tuple(retVal)

countryToSearch = "Philippines"

print(for_country_a(countryToSearch))
print(for_country_d(countryToSearch))
print(for_country_c(countryToSearch))


#Zadanie 4
'''
print("-"*15)
print("Zadanie 4")
print("-"*15)
'''

@timer
def for_date_country_a( year, month, day, country):
    retVal = [0, 0]
    for (c, y, m, d, death, case) in all_cases:
        if c == country and day == d and month == m and year == y:
            retVal[0] += death
            retVal[1] += case
            break
    return tuple(retVal)

@timer
def for_date_country_d( year, month, day, country):
    retVal = [0, 0]
    for (c, death, case) in by_date[(year, month, day)]:
        if c == country:
            retVal[0] += death
            retVal[1] += case
            break
    return tuple(retVal)

@timer
def for_date_country_c( year, month, day, country):
    retVal = [0, 0]
    for (y, m, d, death, case) in by_country[country]:
        if day == d and month == m and year == y:
            retVal[0] += death
            retVal[1] += case
            break #znacznie przyspiesza - wiemy, ze tylko jedna data na panstwo (predkosc zalezy od kolejnosci)
    return tuple(retVal)

#Philippines 08.08.2020 - 18 death, 3294 cases

print(for_date_country_a( *dateToSearch, countryToSearch))
print(for_date_country_d( *dateToSearch, countryToSearch))
print(for_date_country_c( *dateToSearch, countryToSearch))

#Zadanie 5

methodsCovid = [ for_date_a, for_date_d, for_date_c, for_country_a, for_country_d, \
 for_country_c, for_date_country_a, for_date_country_d, for_date_country_c]

methodsPerTask = 3
numberOfTasks = 3

import random

def testTimes(nr):
    with open('.\Result%d.txt' % nr, "w", encoding="utf-8") as f:
        maxLen = len(all_cases)
        testNumber = 1000 #Here you can change the number of records for testing
        if testNumber*5 > maxLen:
            f.write("Error: input testNumber was too high.\n")
        
        zadX_Y = [0, 0, 0, 0, 0, 0, 0, 0, 0 ] #laczny czas wykonania
        i = 0
        usedIndexes = set()
        while i < testNumber:
            tempIndex = random.randrange(0, maxLen)

            if not tempIndex in usedIndexes:
                usedIndexes.add(tempIndex)
                i += 1
                ( c, y, m, d, int, int) = all_cases[tempIndex]

                for ( j ,myFun) in enumerate(methodsCovid):
                    if j < methodsPerTask*1:
                        myFun(y, m, d)
                        zadX_Y[j] += timerResult
                    elif j < methodsPerTask*2:
                        myFun(c)
                        zadX_Y[j] += timerResult
                    else:
                        myFun(y, m, d, c)
                        zadX_Y[j] += timerResult
                    pass
        zadX_Y  = map( ( lambda x: x/testNumber), zadX_Y)

        for (j, miliSec) in enumerate(zadX_Y):
            if j%3 == 0:
                f.write("Zad %d results in miliseconds:\n" % (j//3 + 2) )
            f.write("\tApproximate time needed to accomplish the task: %5.20f\n" % miliSec)



tempNum = input("Wpisz pod jakim numerem chcesz zapisać rezultat:\n")
try:
    tempNum = int(tempNum)
    testTimes(tempNum)
except:
    print("Podano zle dane.\n")





                    

