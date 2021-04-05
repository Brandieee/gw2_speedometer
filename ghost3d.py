import tkinter as tk
from tkinter import simpledialog
from tkinter import *
from math import pi, cos, sin
import ctypes
import mmap
import time
import datetime
import math
from scipy.spatial import distance
from pynput.keyboard import Key, Controller
import csv
import sys, os
import numpy as np
from playsound import playsound
from datetime import date
import json
import glob
import pandas as pd

import random

import paho.mqtt.client as mqtt #import the client1
import time
from datetime import datetime

import threading
import queue


import numpy as np
import PySide2
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys
from opensimplex import OpenSimplex
from pyqtgraph import Vector
from pynput import keyboard


np.seterr(divide='ignore', invalid='ignore')


fAvatarPosition = [57.30902862548828, 21.493343353271484, 49.639732360839844]
fAvatarFront = [-0.6651103496551514, 0.0, 0.7467450499534607]
fAvatarTop = [0.0, 0.0, 0.0]
fCameraPosition = [61.54618453979492, 26.199399948120117, 43.35494613647461]
fCameraFront = [-0.6211158633232117, -0.35765624046325684, 0.6973500847816467]


timer = 0
guildhall_name = ""
filename_timer = 99999
ghost_number = 1



class Link(ctypes.Structure):
    def __str__(self): 
        
        return  " uiVersion:" + str(self.uiVersion) \
        + " \n uiTick: " + str(self.uiTick) \
        + " \n fAvatarPosition: " + str(self.fAvatarPosition) \
        + " \n fAvatarFront: " + str(self.fAvatarFront) \
        + " \n fAvatarTop: " + str(self.fAvatarTop) \
        + " \n name: " + str(self.name) \
        + " \n fCameraPosition: " + str(self.fCameraPosition) \
        + " \n fCameraFront: " + str(self.fCameraFront) \
        + " \n fCameraTop: " + str(self.fCameraTop) \
        + " \n identity: " + str(self.identity) \
        + " \n context_len: " + str(self.context_len)

    _fields_ = [
        ("uiVersion", ctypes.c_uint32),           # 4 bytes
        ("uiTick", ctypes.c_ulong),               # 4 bytes
        ("fAvatarPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fAvatarFront", ctypes.c_float * 3),     # 3*4 bytes
        ("fAvatarTop", ctypes.c_float * 3),       # 3*4 bytes
        ("name", ctypes.c_wchar * 256),           # 512 bytes
        ("fCameraPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fCameraFront", ctypes.c_float * 3),     # 3*4 bytes
        ("fCameraTop", ctypes.c_float * 3),       # 3*4 bytes
        ("identity", ctypes.c_wchar * 256),       # 512 bytes
        ("context_len", ctypes.c_uint32),         # 4 bytes
        # ("context", ctypes.c_byte * 256),       # 256 bytes, see below
        # ("description", ctypes.c_byte * 2048),  # 2048 bytes, always empty
    ]

class Context(ctypes.Structure):
    def __str__(self): 
        return  ""\
        + " \n serverAddress:" + str(self.serverAddress) \
        + " \n mapId:" + str(self.mapId) \
        + " \n mapType:" + str(self.mapType) \
        + " \n shardId:" + str(self.shardId) \
        + " \n instance:" + str(self.instance) \
        + " \n buildId:" + str(self.buildId) \
        + " \n uiState:" + str(self.uiState) \
        + " \n compassWidth:" + str(self.compassWidth) \
        + " \n compassHeight:" + str(self.compassHeight) \
        + " \n compassRotation:" + str(self.compassRotation) \
        + " \n playerX:" + str(self.playerX) \
        + " \n playerY:" + str(self.playerY) \
        + " \n mapCenterX:" + str(self.mapCenterX) \
        + " \n mapCenterY:" + str(self.mapCenterY) \
        + " \n mapScale:" + str(self.mapScale) 
        
    _fields_ = [
        ("serverAddress", ctypes.c_byte * 28),    # 28 bytes
        ("mapId", ctypes.c_uint32),               # 4 bytes
        ("mapType", ctypes.c_uint32),             # 4 bytes
        ("shardId", ctypes.c_uint32),             # 4 bytes
        ("instance", ctypes.c_uint32),            # 4 bytes
        ("buildId", ctypes.c_uint32),             # 4 bytes
        ("uiState", ctypes.c_uint32),             # 4 bytes
        ("compassWidth", ctypes.c_uint16),        # 2 bytes
        ("compassHeight", ctypes.c_uint16),       # 2 bytes
        ("compassRotation", ctypes.c_float),      # 4 bytes
        ("playerX", ctypes.c_float),              # 4 bytes
        ("playerY", ctypes.c_float),              # 4 bytes
        ("mapCenterX", ctypes.c_float),           # 4 bytes
        ("mapCenterY", ctypes.c_float),           # 4 bytes
        ("mapScale", ctypes.c_float),             # 4 bytes
    ]

class MumbleLink:
    data: Link
    context: Context

    def __init__(self):
        self.size_link = ctypes.sizeof(Link)
        self.size_context = ctypes.sizeof(Context)
        size_discarded = 256 - self.size_context + 4096  # empty areas of context and description

        # GW2 won't start sending data if memfile isn't big enough so we have to add discarded bits too
        memfile_length = self.size_link + self.size_context + size_discarded

        self.memfile = mmap.mmap(fileno=-1, length=memfile_length, tagname="MumbleLink")

    def read(self):
        self.memfile.seek(0)

        self.data = self.unpack(Link, self.memfile.read(self.size_link))
        self.context = self.unpack(Context, self.memfile.read(self.size_context))

    def close(self):
        self.memfile.close()

    @staticmethod
    def unpack(ctype, buf):
        cstring = ctypes.create_string_buffer(buf)
        ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
        return ctype_instance

class Ghost3d(object):
    def on_press(self,key):
        global filename_timer
        try:
            if key.char == "t":
                filename_timer = time.perf_counter()
            if key.char == "y":
                self.file_ready = False

                if self.balls != {}:
                    balls = self.balls.values()
                    value_iterator = iter(balls)
                    first_value = next(value_iterator)
                    
                    self.w.removeItem(first_value)


                self.searchGhost()
                self.balls = {}
                self.last_balls_positions = {}
                self.file_ready = True
                filename_timer = 99999
        except AttributeError:
            None
        
    def on_release(self,key):
        try:
            if key.char == "t":
                print('GHOST RESET')
            if key.char == "y":
                print('UPDATING GHOST')
        except AttributeError:
            None

    def searchGhost(self):
        
        global guildhall_name
        #actualizamos el nombre del guildhall o mapa
        file = open(os.path.dirname(os.path.abspath(sys.argv[0])) + "\\" + "guildhall.txt")
        guildhall_name = file.read()
        
        print("-----------------------------------------------")
        print("---------- ZONE:", guildhall_name, "------------")
                
        #obtener los ficheros de replay
        path = os.path.dirname(os.path.abspath(sys.argv[0])) + "/"                  
        self.all_files = glob.glob(os.path.join(path, guildhall_name+"_log*.csv"))

        if len(self.all_files) > 0:
            self.df = pd.DataFrame()
            for file_ in self.all_files:
                file_df = pd.read_csv(file_)
                file_df['file_name'] = file_
                self.df = self.df.append(file_df)

            #aquí tenemos que quedarnos solo con el mejor tiempo

            min_time = 99999
            self.best_file = ''

            for x in self.all_files:
                data = self.df[(self.df['file_name'] == x)]
                #print(list(data.values[-1]))
                last_elem = [list(data.values[-1])[0],list(data.values[-1])[1],list(data.values[-1])[2]]
                #print(last_elem)
                try:
                    last_elem_array = (ctypes.c_float * len(last_elem))(*last_elem)

                    #CHECK POSITION TO RESTART THE GHOST
                    endpoint = [0,0,0]
                    if guildhall_name == "GWTC":
                        endpoint = [-37.9, 1.74, -26.7]
                    elif guildhall_name == "RACE":
                        endpoint = [-276.66, 42.59, -320.23]
                    elif guildhall_name == "EQE":
                        endpoint = [117, 158, 256]
                    elif guildhall_name == "SoTD":
                        endpoint = [61.96, 512.09, -58.64]
                    elif guildhall_name == "LRS":
                        endpoint = [-26.74, 0.55, -51.33]
                    elif guildhall_name == "HUR":
                        endpoint = [42.5, 103.87, -187.45]
                    elif guildhall_name == "TYRIA INF.LEAP":
                        endpoint = [166.077, 1.25356, -488.581]
                    elif guildhall_name == "TYRIA DIESSA PLATEAU":
                        endpoint = [-166.1, 30.8, -505.5]
                    elif guildhall_name == "TYRIA SNOWDEN DRIFTS":
                        endpoint = [302.6, 35.05, -38.4]
                    elif guildhall_name == "TYRIA GENDARRAN":
                        endpoint = [283.9, 12.9, 463.9]
                    elif guildhall_name == "TYRIA BRISBAN WILD.":
                        endpoint = [-820.6, 66.1, 454.4]
                    elif guildhall_name == "TYRIA GROTHMAR VALLEY":
                        endpoint = [511.1, 16.2, 191.8]
                    elif guildhall_name == "OLLO SmallLoop":
                        endpoint = [134, 12, -20]
                    elif guildhall_name == "OLLO SpeedLine":
                        endpoint = [-358, 996, -379]
                
                    try:
                        if distance.euclidean(endpoint, last_elem_array) < 20:
                            #candidato a válido
                            time = list(data.values[-1])[6]
                            if time < min_time:
                                min_time = time
                                self.best_file = x
                    except:
                        print("File",x,"is corrupted, you can delete it")

                except:
                    print("File",x,"is corrupted, you can delete it")

            if min_time == 99999:
                print("-----------------------------------------------")
                print("- NO TIMES YET, YOU NEED TO RACE WITH SPEEDOMETER TO CREATE NEW ONE" )
                print("-----------------------------------------------")
            else:            
                print("-----------------------------------------------")
                print("- YOUR BEST TIME IS" , datetime.strftime(datetime.utcfromtimestamp(min_time), "%M:%S:%f")[:-3] )
                print("- LOG FILE" , self.best_file )
                print("- PRESS KEY 'T' TO REPLAY THAT FILE")
                print("- PRESS KEY 'Y' TO RECALCULATE THE BEST FILE")
                print("- Speedometer program will automatically press 't' and 'y' each time you start or finish a timed track")
                print("-----------------------------------------------")
        else:
            print("THERE IS NO LOG FILES YET")

    def __init__(self):

        global fAvatarPosition
        global guildhall_name

        self.file_ready = False

        """
        Initialize the graphics window and mesh
        """

        self.root = Tk()
        self.root.title("Ghost2")

        # setup the view window
        self.app = QtGui.QApplication(sys.argv)
        
        self.w = gl.GLViewWidget()
        self.w.setGeometry(0, 0, 1920, 1040)
        self.w.setWindowTitle('GhooOOoosst')
        self.w.setCameraPosition(distance=100, elevation=8, azimuth=42)
        self.w.opts['center'] = Vector(0,0,0)

        self.w.setWindowFlags(self.w.windowFlags() |
            QtCore.Qt.WindowTransparentForInput |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint)
        self.w.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.w.setWindowOpacity(0.85)
        self.w.setBackgroundColor(0,0,0,1)

        def empty(ev):
            return None
        self.w.mouseMoveEvent = empty
        self.w.wheelEvent = empty
        
        self.w.show()

        self.searchGhost()
        self.file_ready = True


        self.balls = {}
        self.last_balls_positions = {}

        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()

        self.animation()


    def update(self):

        global fAvatarPosition
        global timer
        global ghost_number
        global filename_timer

        ml.read()

        #print(ml.data)
        #print(ml.context)

        if ml.data.uiVersion == 0:
            return

        fov = json.loads(ml.data.identity)["fov"]
        fAvatarPosition = [ml.data.fAvatarPosition[0],ml.data.fAvatarPosition[1],ml.data.fAvatarPosition[2]]
        fAvatarFront = [ml.data.fAvatarFront[0],ml.data.fAvatarFront[1],ml.data.fAvatarFront[2]]
        fAvatarTop = [ml.data.fAvatarTop[0],ml.data.fAvatarTop[1],ml.data.fAvatarTop[2]]

        fCameraPosition = [ml.data.fCameraPosition[0],ml.data.fCameraPosition[1],ml.data.fCameraPosition[2]]
        fCameraFront = [ml.data.fCameraFront[0],ml.data.fCameraFront[1],ml.data.fCameraFront[2]]
        fCameraTop = [ml.data.fCameraTop[0],ml.data.fCameraTop[1],ml.data.fCameraTop[2]]

        #UPDATE CAMERA POSITION
        angle2 = math.atan2(fCameraFront[2], fCameraFront[0])  # ALWAYS USE THIS
        angle2 *= 180 / math.pi
        if angle2 < 0: angle2 += 360
        self.w.opts['elevation'] = -(float(fCameraFront[1]) * float(50)) 
        self.w.opts['distance'] = distance.euclidean(fAvatarPosition, fCameraPosition) *1.3
        self.w.opts['azimuth'] = angle2 + 180
        self.w.opts['center'] = Vector(fAvatarPosition[0],fAvatarPosition[2],fAvatarPosition[1])
        self.w.opts['fov'] = (fov * 56 / 1.2) + 29 
        self.w.pan(0,0,3)

        timer = time.perf_counter() - filename_timer

        #for x in self.all_files[-ghost_number:]:
        if hasattr(self, 'df') and self.file_ready == True:
            data = self.df[(self.df['TIME'] > timer) & (self.df['file_name'] == self.best_file)]

            ##print("duro ",len(data))
            if len(data) > 0:

                userpos = list(self.df[(self.df['TIME'] > timer) & (self.df['file_name'] == self.best_file)].values[0])
                
                posx = userpos[0]
                posy = userpos[1]
                posz = userpos[2]
                vel = userpos[3]
                file = userpos[8]

                #self.createMarker(posx+900,posy+500,posz,vel,30,datetime.fromtimestamp(int(file.split("\\")[4][:-4].split("_")[2].split(".")[0])))

                #dibujamos un marcador por lectura , hay que cambiar para no crear muchos
                speedcolor = [120, 152, 255]

                if vel > 65 :
                    speedcolor = [201, 112, 204]
                if vel > 80 :
                    speedcolor = [255, 138, 54]
                if vel > 99 :
                    speedcolor = [235, 55, 52]

                #print(vel, speedcolor)

                self.md = gl.MeshData.sphere(rows=2, cols=4)
                colors = np.ones((self.md.faceCount(), 4), dtype=float)
                colors[::1,0] = 1
                colors[::1,1] = 0
                colors[::1,2] = 0
                colors[:,1] = np.linspace(0, 1, colors.shape[0])
                #self.md.setFaceColors(colors)

                if not file in self.balls:
                    self.balls[file] = gl.GLMeshItem(meshdata=self.md, smooth=False, drawFaces=True, glOptions='additive', shader='shaded', color=(QtGui.QColor(speedcolor[0], speedcolor[1], speedcolor[2])))
                    self.balls[file].scale(1.5, 1.5, 1.5)
                    self.w.addItem(self.balls[file])

                if self.last_balls_positions.get(file):
                    last_pos = self.last_balls_positions.get(file)
                else: 
                    last_pos = [0,0,0]

                transx = float(posx) - float(last_pos[0])
                transy = float(posz) - float(last_pos[1])
                transz = float(posy) - float(last_pos[2])

                #self.balls[file].resetTransform()
                self.balls[file].rotate(1,0,0,1,True)
                self.balls[file].translate(transx,transy,transz)
                
                self.balls[file].setColor(QtGui.QColor(speedcolor[0], speedcolor[1], speedcolor[2]))

                self.last_balls_positions[file] = [posx,posz,posy]

        self.loop = self.root.after(1, self.update)


    def start(self):
        """
        get the graphics window open and setup
        """
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def animation(self):
        """
        calls the update method to run in a loop
        """
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)

        self.start()


if __name__ == '__main__':

    #root.mainloop() 

    root = tk.Tk()
    root.call('wm', 'attributes', '.', '-topmost', '1')

    windowWidth = root.winfo_screenwidth()
    windowHeight = root.winfo_screenheight()
    root.title("Move Speedometer windows")
    root.geometry("170x50+{}+{}".format(windowWidth - 470, 0)) #Whatever vel
    root.overrideredirect(1) #Remove border
    root.wm_attributes("-transparentcolor", "#666666")
    root.attributes('-topmost', 1)
    root.configure(bg='#666666')

    ml = MumbleLink()
    
    t = Ghost3d()
    ts = TrackSelector()

    root.mainloop()
