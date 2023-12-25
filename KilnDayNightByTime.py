#!/usr/bin/env python3

#Solar Wood Kiln control software
#Author: Jason Wheelwright (Fall/Winter of 2017/18)
#for this to work the Arduino must be running "KilnSensors2"
#and must be connected to serial via usb

#update April2020(2nd) Day/Night shift by time only + added nightime fan settings

import csv
from threading import Thread
from threading import Lock
import time
import serial
import RPi.GPIO as GPIO
import re
import os.path

lock = Lock()

#varible list
global text
global ser
global stop
global datafile #file name to store data from arduino via serial port
global counter
global Light
global HumIn
global HumOut
global TempHot
global TempComp
global TempIn
global TempOut
global DewIn
global DewOut
global topcount
global bottomcount
global LastTime
global Top
global Bottom
global Fan
global Vent
global StatusFile #file name to store kiln physical settings
global diff #difference between inside dewpoint and outside temp
global LastHour
global Readings
global DayNight

#Pi outputs/inputs (LOW turns on relays for power)
GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT) #16 and 26 power top vent linear actuator
GPIO.setup(26,GPIO.OUT) #16 low is close, 26 low is open
GPIO.output(16,GPIO.HIGH)
GPIO.output(26,GPIO.HIGH)
GPIO.setup(25,GPIO.OUT) #25 and 27 power bottom vent linear actuator
GPIO.setup(27,GPIO.OUT) #25 low is close, 27 low is open
GPIO.output(25,GPIO.HIGH)
GPIO.output(27,GPIO.HIGH)
GPIO.setup(12,GPIO.OUT) #110 volt power to kiln fan
GPIO.output(12,GPIO.HIGH) #high is off
GPIO.setup(24,GPIO.OUT) #12 volt power to computer box vent fan
GPIO.output(24,GPIO.HIGH) #high is off
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # these 4 are magnetic sensors
GPIO.setup(18,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #17 top closed 18 open
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #22 bottom closed 23 open
GPIO.setup(23,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#functions start here

def TopVentIn(secs): #run for number of seconds input
    GPIO.output(16,GPIO.LOW)
    GPIO.output(26,GPIO.HIGH)
    time.sleep(secs)
    GPIO.output(16,GPIO.HIGH)
    GPIO.output(26,GPIO.HIGH)

def TopVentOut(secs): #run for number of seconds input
    GPIO.output(26,GPIO.LOW)
    GPIO.output(16,GPIO.HIGH)
    time.sleep(secs)
    GPIO.output(16,GPIO.HIGH)
    GPIO.output(26,GPIO.HIGH)

def BottomVentIn(secs): #run for number of seconds input
    global bottomcount
    GPIO.output(25,GPIO.LOW)
    GPIO.output(27,GPIO.HIGH)
    time.sleep(secs)
    GPIO.output(25,GPIO.HIGH)
    GPIO.output(27,GPIO.HIGH)

def BottomVentOut(secs): #run for number of seconds input
    global bottomcount
    GPIO.output(27,GPIO.LOW)
    GPIO.output(25,GPIO.HIGH)
    time.sleep(secs)
    GPIO.output(25,GPIO.HIGH)
    GPIO.output(27,GPIO.HIGH)

def CloseTop(): #close until magnet sensor is High
    global topcount
    loops = 0
    while GPIO.input(17) == False:
        GPIO.output(16,GPIO.LOW)
        GPIO.output(26,GPIO.HIGH)
        time.sleep(2)
        loops = loops + 2
        if loops > 75: #this is to break if sensor does not trip
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(26,GPIO.HIGH)
            topcount = -1 #this is one lower than min to signal problem with magnets
            break
    else:
        GPIO.output(16,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        topcount = 0
    return

def OpenTop(): #open until magnet sensor is High
    global topcount
    loops = 0
    while GPIO.input(18) == False:
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.HIGH)
        time.sleep(2)
        loops = loops + 2
        if loops > 75: #this is to break if sensor does not trip
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(26,GPIO.HIGH)
            topcount = 66 #this is one higher than max to signal problem with magnets
            break
    else:
        GPIO.output(16,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        topcount = 65
    return

def CloseBottom(): #close until magnet sensor is High
    global bottomcount
    loops = 0
    while GPIO.input(22) == False:
        GPIO.output(25,GPIO.LOW)
        GPIO.output(27,GPIO.HIGH)
        time.sleep(2)
        loops = loops + 2
        if loops > 75: #this is to break if sensor does not trip
            GPIO.output(25,GPIO.HIGH)
            GPIO.output(27,GPIO.HIGH)
            bottomcount = -1 #this is one lower than min to signal problem with magnets
            break
    else:
        GPIO.output(25,GPIO.HIGH)
        GPIO.output(27,GPIO.HIGH)
        bottomcount = 0
    return

def OpenBottom(): #open until magnet sensor is High
    global bottomcount
    loops = 0
    while GPIO.input(23) == False:
        GPIO.output(27,GPIO.LOW)
        GPIO.output(25,GPIO.HIGH)
        time.sleep(2)
        loops = loops + 2
        if loops > 75: #this is to break if sensor does not trip
            GPIO.output(25,GPIO.HIGH)
            GPIO.output(27,GPIO.HIGH)
            bottomcount = 66 #this is one higher than max to signal problem with magnets
            break
    else:
        GPIO.output(25,GPIO.HIGH)
        GPIO.output(27,GPIO.HIGH)
        bottomcount = 65
    return

def TopMoveTo(spot): #this calculates direction and distance to move top vent,
#then activates runnin or out and updates position counter
    global topcount
    if GPIO.input(17) == True: #if closed set to 0
        topcount = 0
    if GPIO.input(18) == True: #if all open set to max
        topcount = 65
    spot = int(spot)
    if spot < topcount:
        secs = topcount - spot
        TopVentIn(secs)
        topcount = topcount - secs
        return
    if spot > topcount:
        secs = spot - topcount
        TopVentOut(secs)
        topcount = topcount + secs
        return

def BottomMoveTo(spot): #this calculates direction and distance to move bottom vent,
#then activates runnin or out and updates position counter
    global bottomcount
    if GPIO.input(22) == True: #if closed set to 0
        bottomcount = 0
    if GPIO.input(23) == True: #if all open set to max
        bottomcount = 65
    spot = int(spot)
    if spot < bottomcount:
        secs = bottomcount - spot
        BottomVentIn(secs)
        bottomcount = bottomcount - secs
        return
    if spot > bottomcount:
        secs = spot - bottomcount
        BottomVentOut(secs)
        bottomcount = bottomcount + secs
        return

def FanOn(): #kiln air mover fan
    GPIO.output(12,GPIO.LOW)

def FanOff():
    GPIO.output(12,GPIO.HIGH)

def CoolOn(): #computer box cooling fan
    GPIO.output(24,GPIO.LOW)

def CoolOff():
    GPIO.output(24,GPIO.HIGH)

def countdown():#lowers -1 the time to midnight counter each minute, makes new file at 0
    global counter
    while counter > 0:
        time.sleep(60)
        counter = counter -1
    if counter == 0: #when counter gets to 0, make a new file then restart countdown thread
        time.sleep(3)
        newdayfile()
        recountdown() #restarts itself after a short nap
    else:
        return #this is so that when countdown is set to -1 by interrupt, the thread will exit

def recountdown():#restarts countdown to midnight Thread on newday
    time.sleep(3)
    T3=Thread(target=countdown)
    T3.start()

def setcounter():#sets counter at minutes to midnight
    global counter
    hr = time.strftime("%H",time.localtime())
    mn = time.strftime("%M",time.localtime())
    counter = ((23-int(hr))*60)+(60-int(mn))

def newdayfile():#makes csv file names for this date
    global datafile, StatusFile
    day = time.strftime("%b%d",time.localtime()) #Month and Day eg. Nov14
    datafile = "/home/pi/Desktop/Kiln Data/" + day + "datafile.csv"
    StatusFile = "/home/pi/Desktop/Kiln Data/" + day + "StatusFile.csv"
    lock.acquire()
    makeheader() #create file and write header line
    lock.release()
    setcounter() #sets number of minutes to midnight for coundown to new files creation

def makeheader():#makes file and writes header in csv files in not already present
    global datafile, StatusFile
    if not os.path.isfile(datafile):
        with open(datafile, 'a') as h:
            writer=csv.writer(h)
            header=["Time","Light","HumIn","HumOut","TempHot","TempComp","TempIn","TempOut","DewIn","DewOut"]#do this on setup to create headers
            writer.writerow(header)
            h.close()
    if not os.path.isfile(StatusFile):
        with open(StatusFile, 'a') as h:
            writer=csv.writer(h)
            header=["DataTime","Wood","TopVent","DPdiff","BottomVent","Hot","KilnFan","Box","BoxVent"]#do this on setup to create headers
            writer.writerow(header)
            h.close()

def getdata(): #this pulls raw dataline from the serial port
    global Readings
    global datafile
    Readings=[] #empty list for data
    while len(Readings) != 10 or float(Readings[7]) > 110:#must have 10 numbers and outside temp less than 110
        global text
        global ser
        Readings=[]
        text = ""
        data="hi" #these write over previous ones to make sure new data is pulled
        time.sleep(10)
        data=ser.readline()
        time.sleep(5)
        text=data.decode("utf-8","strict")
        text=text.rstrip()
        text=text.split(' ') #turn text into list
        text.insert(0,(time.strftime("%H:%M",time.localtime())))

        for word in text: #text was created in getdata()
            if re.match("^\d",word):#get only numbers
                Readings.append(word)#add numbers to the list
        #if len(text)==19: #check for proper length list before passing
            #break
    return(Readings); #this varialble is the data

def writedata():#This pulls out Titles, makes a list, then prints numbers to csv file
    #numbers=[]
    global datafile
    global Readings
    #for word in text: #text was created in getdata()
        #if re.match("^\d",word):#get only numbers
            #numbers.append(word)#add numbers to the list
    with open(datafile, 'a') as f:
        writer=csv.writer(f)
        writer.writerow(Readings) #here you write the list to the last row of the cvs file
        f.close()

def writeStatus(): #write position status to file
    global LastTime, Top, Bottom,Fan, Vent, StatusFile, diff, TempHot, TempComp, TempIn
    Status =[LastTime,TempIn,Top,diff,Bottom,TempHot,Fan,TempComp,Vent]
    with open(StatusFile, 'a') as g:
        writer=csv.writer(g)
        writer.writerow(Status) #here you write the list to the last row of the cvs file
        g.close()

def pulldata():#primary loop to get data and write to csv file every 3 minutes
    global stop
    global counter
    global ser
    try:
        while stop == 1:
            ser=serial.Serial('/dev/ttyACM0',115200) #open serial port to/from arduino
            time.sleep(165) #wait for good line of data to be recieved
            lock.acquire()
            getdata()
            ser.close() #close port
            writedata() #to csv file
            lock.release()
            time.sleep(15)
        else:
            print("getdata error")
            EndProgram() #stop is set to 1 on interupt to trigger this
    except:
        print("pulldata exception")
        EndProgram()

def readVariables():#turns last data collection into usable variables for main action stuff
    global text, Light, HumIn, HumOut, TempHot, TempComp, TempIn, TempOut, DewIn, DewOut, LastTime, Readings
    try:
        lock.acquire()
        #while True:
        movers=Readings #turn Readings list into movers list
        #for word in text:
            #if re.match("^-?\d",word):#get only numbers
                #movers.append(word)#add numbers to the list
            #if len(movers)==10: #ensures a good pile of data
                #break
        lock.release()

        LastTime = movers[0]#These make the readings as variables
        Light = int(movers[1])
        HumIn = float(movers[2])
        HumOut = float(movers[3])
        TempHot = float(movers[4])
        TempComp = float(movers[5])
        TempIn = float(movers[6])
        TempOut = float(movers[7])
        DewIn = float(movers[8])
        DewOut = float(movers[9])
    except: #try again on next data read if something gets missed
        time.sleep(165)
        readVariables()

def ReadPositions(): #find physical kiln setup
    global topcount, bottomcount, Top, Bottom, Fan, Vent
    if GPIO.input(17) == True:
        Top = 'Closed'
        topcount = 0
    if GPIO.input(18) == True:
        Top = 'Open'
        topcount = 65
    if GPIO.input(22) == True:
        Bottom = 'Closed'
        bottomcount = 0
    if GPIO.input(23) == True:
        Bottom = 'Open'
        bottomcount = 65
    if GPIO.input(17) == False and GPIO.input(18) == False:
        Top = str(topcount)
    if GPIO.input(22) == False and GPIO.input(23) == False:
        Bottom = str(bottomcount)
    if GPIO.input(12) == True:
        Fan = 'Off'
    if GPIO.input(12) == False:
        Fan = 'On'
    if GPIO.input(24) == True:
        Vent = 'Off'
    if GPIO.input(24) == False:
        Vent = 'On'

def SetFans(): #turns fans on or off at set points
    if TempComp > 90: #cooling fan for computer box
        CoolOn()
    if TempComp <= 90:
        CoolOff()
    if TempHot > 90: #circulation fan in Kiln off top thermometer reading
        FanOn()
    if TempHot <= 90:
        FanOff()

def SetFansNight(): #turns fans on or off at set points
    if TempComp > 90: #cooling fan for computer box
        CoolOn()
    if TempComp <= 90:
        CoolOff()
    if TempHot > 110: #circulation fan in Kiln off top thermometer reading
        FanOn()
    if TempHot <= 110:
        FanOff()

def SetBottom(): #set bottom vent to half if inside dewpoint compared to outside temp is greater than set point, othewise close
    global DewIn, TempOut, diff
    diff = float(DewIn - TempOut)
    diff = round(diff,1)
    if diff > 25:
        BottomMoveTo(30)
    if diff <= 25:
        CloseBottom()

def nightmode():
    global diff
    CloseBottom()
    CloseTop()
    SetFansNight()
    diff = float(DewIn - TempOut)
    diff = round(diff,1)

def SetTop():
    global TempIn
    if TempIn > 150:
        OpenTop()
    elif TempIn > 140:
        TopMoveTo(45)
    elif TempIn > 130:
        TopMoveTo(30)
    else:
        CloseTop()

def Twilight(): #at dark and dawn, open both vents and purge air for 10 minutes
    OpenTop()
    OpenBottom()
    FanOn()
    ReadPositions() #get stats of moving parts
    lock.acquire()
    writeStatus() #write positions to csv file
    lock.release()
    time.sleep(600)
    CloseTop()
    CloseBottom()
    FanOff()

def EndProgram():#clean exit of program
    global counter
    global stop
    counter = -1 #These settings cause threads to end
    stop = 0
    if T1.is_alive == True: #These wait for treads to end
        T1.join()
    if T3.is_alive == True:
        T3.join()
    ser.close()
    CloseTop()
    CloseBottom()
    GPIO.cleanup()
    print("Program Stopped") #this signal final shutdown

#Program starts here
print("Kiln Software Running")
T1=Thread(target=pulldata) #def to get and store data every 3 minutes
T3=Thread(target=countdown) #def for countdown to new day/file


# Experiment with opening bottom more if DPdiff gets even higher
# put in GUI with manual override (t2 tread that puts in varaibles to change things at periodic check in main thread)
#evenutally add more fans to step increase circulation and have a small one for nightime

try:
    #setup and start data collection
    newdayfile()#make a csv file and set counter
    stop = 1#set as 1 lets the pulldata and main thread loop run
    CloseTop() #start with everything off and closed
    CloseBottom()
    T1.start()#start pulldata
    T3.start()#start countown to new day
    time.sleep(200) #wait for data collection from arduino
    LastHour = "start" #an inital day/night reading that should not cause chaos

    #begin main program loop
    while stop ==1:
        readVariables() #get variables from most recent sensor reading @ getdata()
        hour=int(time.strftime("%H", time.localtime())) #use hour to set day/night modes
        if hour < 8 or hour > 19:
            DayNight = "night"
        else:
            DayNight = "day"

        print("DataTime", LastTime, "L:", Light, "HI:", HumIn, "HO:", HumOut, "TH:", TempHot, "TB:", TempComp, "TW:", TempIn, "TO:", TempOut, "DI:", DewIn, "DO:", DewOut)

        if DayNight == "night":
            if LastHour == "day": #just became night
                Twilight() #open all and purge air for 10 minutes
                readVariables()
            nightmode() #close vents and turn fans on/off
            ReadPositions() #get stats of moving parts
            lock.acquire()
            writeStatus() #write positions to csv file
            lock.release()
            LastHour = DayNight

        if DayNight == "day": #if not darkest possible
            if LastHour == "night": #if day just started
                Twilight() #open all and purge air for 10 minutes
                readVariables()
            SetFans() #turn fans on or off
            SetBottom() #move bottom vent to half way if inside dew point is high
            SetTop() #set top vent based on wood temperature
            ReadPositions() #get stats of moving parts
            lock.acquire()
            writeStatus() #write positions to csv file
            lock.release()
            LastHour = DayNight

        print("Wood",TempIn,", Top Vent",Top,", DPdiff",diff,", Bottom Vent",Bottom, ", Hot",TempHot,", Fan",Fan,", Box",TempComp,", Vent",Vent)
        time.sleep(600) #wait this much time before repeating

except KeyboardInterrupt:  #clean exit if control c is pressed
    counter = -1 #makes counter stop(T3 thread)
    stop = 0 #stops pulldata and main thread loop, then starts EndProgram()
    print("Stopped by Interrupt... wait for program stopped message!")

except: #clean exit if error interupts
    counter = -1 #makes counter stop(T3 thread)
    stop = 0 #stops pulldata and main thread loop, then starts EndProgram()
    print("Stopped by Badstuff... wait for program stopped message!")
