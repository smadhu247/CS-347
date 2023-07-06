import time
import tkinter as tk
import datetime 
import pandas as pd
import os
import tkinter.font as fonts
from tkinter import *

class InformationLog:
    ##############################################################################################################
    ##  Information Log Class: Creates and stores information logs with information about the train trip
    ##############################################################################################################
   

    def __init__(self, entry, **saved):
        """ 
            InformationLog constructor
                entry:      list entry to be added to the log
                saved:      dictionary where logs are saved
        """
        self.entry = entry
        self.saved = saved
        
    def getCurrentLog(self):
        """ 
            Gets the current log for the trip 
        """
        print("Todays log: ", self.saved)
        return self.saved.setdefault(datetime.datetime.now())
        

    def createNewLog(self, d, humid_sensor, precip_sensor, wheel_sensor, gps_sensor, dis_sensor):
        """ 
            Creates a new log for the trip by getting current data from sensors
        """
        rain = precip_sensor.getRain()
        snow = precip_sensor.getSnow()
        distance = dis_sensor.getDistance()
        humidity = humid_sensor.getHumdidity()
        wheelspeed = wheel_sensor.getWheelSpeed()
        speed = gps_sensor.getGPSSpeed()

        self.saved.update({d: [ "Rain Data: " + str(rain), 
                                "Snow Data: " + str(snow), 
                                "Distance Data: " + str(distance), 
                                "Humidity Data: " + str(humidity), 
                                "Wheel Speed Data: " + str(wheelspeed), 
                                "GPS Speed Data: " + str(speed) ]
                        })


class HumiditySensor:
    ##############################################################################################################
    ##  Humidity Sensor Class: Collects information from the humidity sensor
    ##############################################################################################################

    def __init__(self, humidty):
        """ 
            HumiditySensor constructor
                humidty:    int humidity level detected by sensor
        """
        self.humidty = humidty

    def getHumdidity(self):
        """ 
            Gets humidity level from the humidity sensor
        """
        return self.humidty


class GPSSensor:
    ##############################################################################################################
    ##  GPS Sensor Class: Collects information from the GPS sensor
    ##############################################################################################################

    def __init__(self, GPS_speed, GPS_connection, gate):
        """ 
            GPSSensor constructor
                GPS_speed:      int GPS speed level detected by sensor
                GPS_connection: bool connection detected by sensor
                gate:           bool gate checker that detects locations of gates    
        """
        self.GPS_speed = GPS_speed
        self.gate = gate
        self.GPS_connection = GPS_connection

    def getGate(self):
        """ 
            Checks whether there's a gate in the path of the train
        """
        return self.gate
    
    def getGPSSpeed(self):
        """ 
            Gets the GPS speed from the GPS speed sensor
        """
        if (self.GPS_connection == False):
            return False
        if (self.GPS_connection == True):
            return self.GPS_speed


class WheelSensor:
    ##############################################################################################################
    ##   Wheel Sensor Class: Collects information from the wheel sensor
    ##############################################################################################################

    def __init__(self, rotations_per_min):
        """ 
            WheelSensor constructor
                rotations_per_min:      int rotations per minute detected by sensor 
        """
        self.rotations_per_min = rotations_per_min

    def getWheelSpeed(self):
        """ 
            Gets the wheel speed from the wheel sensor
        """
        return self.rotations_per_min

class PrecipitationSensor:
    ##############################################################################################################
    ##  Precipitation Sensor Class: Collects information from the precipitation sensor
    ##############################################################################################################

    def __init__(self, precip_level, temperature, rain, snow):
        """ 
            PrecipitationSensor constructor
                precip_level:   int precipitation level detected by sensor 
                temperature:    int temperature detected by sensor 
                rain:           bool rain checker
                snow:           bool snow checker
        """
        self.precip_level = precip_level
        self.temperature = temperature
        self.rain = False
        self.snow = False

    def getWeather(self):
        """ 
            Checks whether there is rain or snow when precipitation is detected
        """
        if (self.precip_level > 4 and self.temperature < 32):
            self.snow = True
            self.rain = False
        else:
            self.snow = False
            self.rain = True
            
    def getRain(self):
        """ 
            Checks if there is rain from the precipitation sensor
        """
        PrecipitationSensor.getWeather(self)
        return self.rain

    def getSnow(self):
        """ 
            Checks if there is snow from the precipitation sensor
        """
        PrecipitationSensor.getWeather(self)
        return self.snow    

class DistanceSensor:
    ##############################################################################################################
    ##  Distance Sensor Class: Collects information from the distance sensor
    ##############################################################################################################

    def __init__(self, distance):
        """ 
            DistanceSensor constructor
                distance: int distance away from closest object detected by sensor 
        """
        self.distance = distance

    def getDistance(self):
        return self.distance

class IotEngine():

    ##############################################################################################################
    ##  IotEngine Class: Performs calculations with data collected from the sensors to display reccomendations to the conductor. 
    ##############################################################################################################

    is_on = False
    admin = False
    conductor = False
    is_logged_on = False

    conductor_username = "conductor"
    conductor_password = "password"
    admin_username = "admin"
    admin_password = "password"

    ## Changable variables for Warnings
    slippingtexts = "No Warnings"
    distancetexts = "No Warnings"
    gatestexts = "No Gates"

    SwarningColor = "green"
    DwanrningColor = "green"
    GwarningColor = "green"

    values = 0
    iter_val = 0 
   
    def loginAdmin(self):
        """ 
            Logs the administrator into the IoT Engine
        """
        print("************** ADMIN LOGGED IN **************")
        time.sleep(2)
        print("IoT Engine calibrating...\n")
        time.sleep(1)
        self.admin = True
        self.is_logged_on = True
        self.is_on = True

   
    def loginConductor(self):
        """ 
            Logs the conductor into the IoT Engine
        """
        print("************** CONDUCTOR LOGGED IN **************")
        time.sleep(2)
        print("IoT Engine calibrating...\n")
        time.sleep(1)
        self.conductor = True
        self.is_logged_on = True
        self.is_on = True

    
    def calculateDistance(self, dis_sensor):
        """ 
            Calculates the distance away from the closest object and sends
            a notification or warning to the conductor
        """
        distance = dis_sensor.getDistance()
        if (distance > 1600):
            self.distancetexts = "Object more than 1600 meters away. Do not change speed."
            self.DwarningColor = "green"
        else:
            self.distancetexts = "Object is " + str(distance) + " meters away. Brake to slow down."
            self.DwarningColor = "red"

   
    def calculateSlippage(self, humid_sensor, precip_sensor, wheel_sensor, gps_sensor):
        """ 
            Calculates the if there is slippage and sends a notification 
            or warning to the conductor
        """
        rain = precip_sensor.getRain()
        snow = precip_sensor.getSnow()
        wheelspeed = wheel_sensor.getWheelSpeed()
        gpsspeed = gps_sensor.getGPSSpeed()
        humidity = humid_sensor.getHumdidity()

        slipping = False
        speed = wheelspeed * 33 * 3.14 * 60 / 63360

        if (abs(speed - gpsspeed) > 5):
            slipping = True
        if (humidity > 50):
            slipping = True
        if (rain == True):
            slipping = True
        if (snow == True):
            slipping = True
        if (slipping):
            self.slippingtexts = "Slippage is occurring. Brake to slow down."
            self.SwarningColor = "red"
        else:
            self.slippingtexts = "No slippage. Continue speed."
            self.SwarningColor = "green"

    def checkGates(self, dis_sensor, gps_sensor):
        """ 
            Checks if a gate is nearby and sends a notification or warning 
            to the conductor
        """
        distance = dis_sensor.getDistance()
        gate = gps_sensor.getGate()

        horn = False
        near = False
        arrived = False

        if (1500 < distance < 1700):
            horn = True
        if (distance < 100):
            arrived = True
        if (100 < distance < 1500):
            near = True
        if (gate and horn):
            self.gatestexts = "Gate is " + str(distance) + " meters away. Blow horn for 15 seconds."
            self.GwarningColor = "orange"
        elif (gate and arrived):
            self.gatestexts = "Gate is " + str(distance) + " meters away. Blow horn for 5 seconds."
            self.GwarningColor = "red"
        elif (gate and near):
            self.gatestexts = "Gate is " + str(distance) + " meters away."
            self.GwarningColor = "orange"
        else:
            self.gatestexts = "No gates nearby. Continue speed."
            self.GwarningColor = "green"

   
    def tsnr(self):
        """ 
            Grabs data from sensors (csv file) and initializes lists to hold data.
            Allows admin to view logs
            Allows conductor to start a new trip 
        """
        cwd = os.getcwd() + '/sensordata.csv'
        df = pd.read_csv(cwd)
        df = df.dropna()

        dist_list = []
        wheel_list = []
        humid_list = []
        precip_list = []
        temp_list = []
        gps_list = []
        gate_list = []

        for i in range(len(df)):
            dist_list.append(df["Object Distance"][i])
            wheel_list.append(df["Wheel Speed"][i])
            humid_list.append(df["Humidity"][i])
            precip_list.append(df["Precipitation Level"][i])
            temp_list.append(df["Temperature"][i])
            gps_list.append(df["GPS Speed"][i])
            gate_list.append(df["Gate"][i])

        invalid_login = True
        login_count = 0

        while (invalid_login and login_count < 8):
            print("************** WELCOME **************")
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            if (username == self.conductor_username and password == self.conductor_password):
                self.loginConductor()
                invalid_login = False
            if (username == self.admin_username and password == self.admin_password):
                self.loginAdmin()
                invalid_login = False
            if (invalid_login == True):
                login_count = login_count + 1
                print("Invalid Login. Try Again.")
        
        if (login_count >= 8):
            print("Too many attempts to login, please contact LCS for manual override.")
        
        if (self.admin):
            old_logs = {}
            now = datetime.datetime.now()
            infolog = InformationLog(now, **old_logs)
            infolog.getCurrentLog()

        ## GUI Items
        window = tk.Tk()

        window.title("IoT HTR")
        window.geometry('900x380')
        window.config(bg="gray")

        titlefont = fonts.Font(family="Univers", size=36, weight="bold")
        standardfont = fonts.Font(family="Univers", size=24)
        labelfont = fonts.Font(family="Univers", size=20)

        title = Label(text="IoT Display", fg="white", bg="gray", font=titlefont)

        slippingtext = Label(text="Slippage", fg="white", bg="gray", font=labelfont)
        slippingcontainer = LabelFrame(labelwidget=slippingtext, labelanchor='n', fg="gray", bg="gray", padx=20, pady=10)

        distancetext = Label(text="Distance", fg="white", bg="gray", font=labelfont)
        distancecontainer = LabelFrame(labelwidget=distancetext, labelanchor='n', fg="gray", bg="gray", padx=20, pady=10)

        gatetext = Label(text="Gates", fg="white", bg="gray", font=labelfont)
        gatecontainer = LabelFrame(labelwidget=gatetext, labelanchor='n', fg="gray", bg="gray", padx=20, pady=10)

        slippinglabel = Label(slippingcontainer, text=self.slippingtexts, fg="white", bg=self.SwarningColor, font=standardfont, justify=tk.LEFT)
        objectlabel = Label(distancecontainer, text=self.distancetexts, fg="white", bg=self.DwanrningColor, font=standardfont, justify=tk.LEFT)
        gatelabel = Label(gatecontainer, text=self.gatestexts, fg="white", bg=self.GwarningColor, font=standardfont, justify=tk.LEFT)

        title.pack()
        slippingcontainer.pack()
        slippinglabel.pack()
        distancecontainer.pack()
        objectlabel.pack()
        gatecontainer.pack()
        gatelabel.pack()

        
        if (self.conductor): 
            self.values = len(df)
            self.iter_val = 0            
            old_logs = {}
            def loop():

                if (self.values == 0):
                    window.destroy()
                    return

                precipsensor = PrecipitationSensor(precip_list[self.iter_val],
                                                    temp_list[self.iter_val],
                                                    False,
                                                    False)
                dissensor = DistanceSensor(dist_list[self.iter_val])
                humidsensor = HumiditySensor(humid_list[self.iter_val])
                wheelsensor = WheelSensor(wheel_list[self.iter_val])
                gpssensor = GPSSensor(gps_list[self.iter_val], True, gate_list[self.iter_val])           

                self.calculateDistance(dissensor)
                self.calculateSlippage(humidsensor, precipsensor, wheelsensor, gpssensor)
                self.checkGates(dissensor, gpssensor)

                slippinglabel.config(text=self.slippingtexts, bg=self.SwarningColor)
                objectlabel.config(text=self.distancetexts, bg=self.DwarningColor)
                gatelabel.config(text=self.gatestexts, bg=self.GwarningColor)
                window.after(5000, loop)

                now = datetime.datetime.now()
                infolog = InformationLog(now, **old_logs)
                infolog.createNewLog(now, humidsensor, precipsensor, wheelsensor, gpssensor, dissensor)

                self.values = self.values - 1
                self.iter_val = self.iter_val + 1
        
            loop()
            window.mainloop()
            print("Thank you for riding\n")
            time.sleep(3)

        self.is_on = False

iot = IotEngine()
iot.tsnr()