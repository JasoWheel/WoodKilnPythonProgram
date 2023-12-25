#!/usr/bin/env python3
#This will make a input box to make full graph or partial graph with checkbox input

import matplotlib
matplotlib.use('TkAgg')
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import numpy as np
import matplotlib.pyplot as plt
import csv
from threading import Lock

root = Tk()
root.title("Print-A-Graph")

lock = Lock()
global a,b,c,d,e,f,g,h,i,Lines
Hot = IntVar()
Box = IntVar()
Light = IntVar()
WoodT = IntVar()
WoodH = IntVar()
WoodDP = IntVar()
OutT = IntVar()
OutH = IntVar()
OutDP = IntVar()
Mon = StringVar()
DT = StringVar()
MonDT =StringVar()
gday = StringVar()

Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
Days = ('01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16',
        '17','18','19','20','21','22','23','24','25','26','27','28','29','30','31')
def PrintAllGraph():
    day = gday.get()
    MakeGraph(day)
    
def PrintShortGraph():
    day = gday.get()
    MakeShortGraph(day)

mainframe = ttk.Frame(root, borderwidth=30, padding="1 1 1 1")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

ttk.Label(mainframe, text="Enter Mon & Day", foreground="#0000ff").grid(column=1, row=0)
ttk.Label(mainframe, text="Select Lines to Print", foreground="#0000ff").grid(column=2, row=0, columnspan=3)
       
#MonDT_entry = ttk.Entry(mainframe, width=5, textvariable=gday).grid(column=0, row=2)

ttk.Button(mainframe, text="MakeAllGraph", command=PrintAllGraph).grid(column=0, row=1)
ttk.Button(mainframe, text="MakeShortGraph", command=PrintShortGraph).grid(column=1, row=2)
ttk.Button(mainframe, text="Close", command=root.destroy).grid(column=1, row=3)

ttk.Checkbutton(mainframe, text="TopHot", onvalue=4, variable=Hot).grid(column=2, row =1)
ttk.Checkbutton(mainframe, text="CompBox", onvalue=5, variable=Box).grid(column=2, row =2)
ttk.Checkbutton(mainframe, text="Light", onvalue=1, variable=Light).grid(column=2, row =3)
ttk.Checkbutton(mainframe, text="WoodT", onvalue=6, variable=WoodT).grid(column=3, row =1)
ttk.Checkbutton(mainframe, text="WoodH", onvalue=2, variable=WoodH).grid(column=3, row =2)
ttk.Checkbutton(mainframe, text="WoodDP", onvalue=8, variable=WoodDP).grid(column=3, row =3)
ttk.Checkbutton(mainframe, text="OutT", onvalue=7, variable=OutT).grid(column=4, row =1)
ttk.Checkbutton(mainframe, text="OutH", onvalue=3, variable=OutH).grid(column=4, row =2)
ttk.Checkbutton(mainframe, text="OutDP", onvalue=9, variable=OutDP).grid(column=4, row =3)

ttk.Combobox(mainframe, values=Months, width=3, height=12, textvariable=Mon).grid(column=1, row=1, sticky=W, padx=15)
ttk.Combobox(mainframe, values=Days, width=3, height=31, textvariable=DT).grid(column=1, row=1, sticky=E, padx=15)

def MakeGraph(day):
    global Mon
    global DT
    Monn = Mon.get()
    DTt = DT.get()
    ff = '/Volumes/Home Directory/Desktop/Kiln Data/' + Monn + DTt + 'datafile.csv'
    def LinePlot(ind):
        lock.acquire()
        with open(ff) as d:
            y = []
            z = csv.reader(d)
            for line in z:
                try:
                    y.append(line[ind])
                except:
                    y.append(1)
        d.close()
        lock.release()
        global new
        new = []
        del y[0]
        for n in y:
            new.append(float(n))
        return(new)

    LinePlot(1)
    a = new
    LinePlot(2)
    b = new
    LinePlot(3)
    c = new
    LinePlot(4)
    d = new
    LinePlot(5)
    e = new
    LinePlot(6)
    f = new
    LinePlot(7)
    g = new
    LinePlot(8)
    h = new
    LinePlot(9)
    i = new

    t=len(i)
    x = np.arange(0,t,18.95)
    times = ("00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00","08:00",
    "09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00",
    "19:00","20:00","21:00","22:00","23:00","24:00")
    plt.margins(0)
    plt.grid(True)
    plt.xticks(x,times)
    plt.ylim(10,165)
    plt.plot(a, color="cyan")
    plt.plot(b, color="orange")
    plt.plot(c, color="green")
    plt.plot(d, color="red")
    plt.plot(e, color="purple")
    plt.plot(f, color="brown")
    plt.plot(g, color="blue")
    plt.plot(h, color="pink")
    plt.plot(i, color="olive")
    plt.ylabel('Temperature')
    plt.xlabel('Time')
    plt.show()

    
def MakeShortGraph(day):
    global Mon
    global DT
    Monn = Mon.get()
    DTt = DT.get()
    ff = '/Volumes/Home Directory/Desktop/Kiln Data/' + Monn + DTt + 'datafile.csv'
    def LinePlot(ind):
        lock.acquire()
        with open(ff) as d:
            y = []
            z = csv.reader(d)
            for line in z:
                try:
                    y.append(line[ind])
                except:
                    y.append(1)
        d.close()
        lock.release()
        global new
        new = []
        del y[0]
        for n in y:
            new.append(float(n))
        return(new)
        
    def SetColor(index):
        global col
        if index == 1:
            col="cyan"
        if index == 2:
            col="orange"
        if index == 3:
            col="green"
        if index == 4:
            col="red"
        if index == 5:
            col="purple"
        if index == 6:
            col="brown"
        if index == 7:
            col="blue"
        if index == 8:
            col="pink"
        if index == 9:
            col="olive"
        return col
        
    a=Hot.get()
    b=Box.get()
    c=Light.get()
    d=WoodT.get()
    e=WoodH.get()
    f=WoodDP.get()
    g=OutT.get()
    h=OutH.get()
    j=OutDP.get()
    Vars=[a,b,c,d,e,f,g,h,j]
    Lines=[]
    
    for i in Vars:
        if i != 0:
            Lines.append(i)
    
    for i in Lines:
        LinePlot(i)
        SetColor(i)
        plt.plot(new, color=col)

    t=len(new)
    x = np.arange(0,t,18.95)
    times = ("00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00","08:00",
    "09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00",
    "19:00","20:00","21:00","22:00","23:00","24:00")
    plt.margins(0)
    plt.grid(True)
    plt.xticks(x,times)
    plt.ylim(10,165)
    plt.ylabel('Temperature')
    plt.xlabel('Time')
    plt.show()

root.mainloop()
quit()