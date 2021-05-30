from PyQt5 import QtCore, QtWidgets
from betadesign import Ui_Form
import sys
import speech_recognition as sr 
import pyttsx3
import pywhatkit
import requests
from datetime import datetime
import time
import random
import json
import sqlite3 as sql
import os
import csv
import webbrowser
import wikipedia 

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

PINCODE = 382424
AGE = 45
ENDPOINT = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin"
todays_date = datetime.now()
DATE = f"{todays_date.day}-{todays_date.month}-{todays_date.year}"


def wishMe():
    hour = int(todays_date.hour)
    if hour>=6 and hour<12:
        talk("Good Morning!")

    elif hour>=12 and hour<18:
        talk("Good Afternoon!")

    elif hour>=18 and hour<20:
        talk("Good Evening!")   

    else:
        talk("Pleasant Night!")  

    talk("I am Terrobyte Sir. Please tell me how may I help you")

def talk(text):
    engine.say(text)
    engine.runAndWait()

r = sr.Recognizer()
def take_command():
    with sr.Microphone() as source:
        print('listening...')
        r.pause_threshold = 1
        voice = listener.listen(source)

    try:
        print("Recognizing...")
        command = listener.recognize_google(voice)
        command = command.lower()
        print(f"User said: {command}\n")

    except Exception as e:
        print("Say that again please...")  
        return "None"
    return command

def run_terrobyte():
    wishMe()
    while True:
        command = take_command()
        if 'play' in command:
            song = command.replace('play', '')
            talk('playing ' + song)
            print('terrobyte: playing' + song)
            pywhatkit.playonyt(song)

        elif 'check for vaccine' in command:
            response = requests.get(f"{ENDPOINT}?pincode={PINCODE}&date={DATE}")
            vaccine_slots = response.json()

            slot_available = False
            center_count = 1
            slots_data = ""
            for center in vaccine_slots["centers"]:
                for session in center["sessions"]:
                    #print(session)
                    if session["min_age_limit"] <= AGE and len(session["slots"]) > 0 and session['available_capacity'] > 0:
                        slot_available = True
                        slots_data += f"\n{center_count}) {center['name']} on {session['date']} with capacity of {session['available_capacity']}"
                        center_count += 1
                        print(f"Center Name\t{center['name']}")
                        print(f"Slots available\t{session['available_capacity']}")
                        print("-----------------------------------")
                        break

            if slot_available:
                notification_data = f"HURRY! Vaccine is availabe for age {AGE} at these centers: {slots_data}"
                requests.get("https://api.telegram.org/bot1803125913:AAFD5G60d0ZaKMvme5xRlO3ZWbCfmToCBMg/sendMessage?chat_id=-1001375421232&text={}".format(notification_data))
                talk(notification_data)

            else:
                a = f"\nNO Slot Available for age {AGE} in this week as of {datetime.now()}"
                requests.get("https://api.telegram.org/bot1803125913:AAFD5G60d0ZaKMvme5xRlO3ZWbCfmToCBMg/sendMessage?chat_id=-1001375421232&text={}".format(a))
                talk(a)

        elif 'trivia' in command:
            play()

        elif 'oxygen' in command:
            oxy()

        elif 'report' in command:
            stats()

        elif 'search' in command:
            command = command.replace("search", "")
            webbrowser.open(command)
        
        elif 'wikipedia' in command:
            talk('Searching Wikipedia...')
            command = command.replace("wikipedia", "")
            results = wikipedia.summary(command, sentences=2)
            talk("According to Wikipedia")
            print(results)
            talk(results)
        
        elif 'open youtube' in command:
            webbrowser.open("youtube.com")

        elif 'open google' in command:
            webbrowser.open("google.com")

        elif 'open stack overflow' in command:
            webbrowser.open("stackoverflow.com")

        elif 'exit' in command:
            quit() 


def play():
    score =0
    with open("questions.json", "r+") as f:
        j=json.load(f)
        for i in range(1):
            no = len(j)
            ch = random.randint(0, no-1)
            print(f'\nQuestion-{i+1} {j[ch]["question"]}\n')
            talk(f'\nQuestion-{i+1} {j[ch]["question"]}\n')
            for option in j[ch]["options"]:
                print(option)
                talk(option)
            answer= take_command()
            if j[ch]["answer"][0] == answer[0].upper():
                print("\nYou are correct")
                talk("\nYou are correct")
                score+=1
            else:
                print("\nYou are incorrect")
                talk("\nYou are incorrect")
            del j[ch]
        print(f'\nFINAL SCORE: {score}')
        talk(f'\nFINAL SCORE: {score}')

def oxy():
    conn = sql.connect('oxygen.db');
    with conn:
        cursor=conn.cursor();
        cursor.execute('CREATE TABLE IF NOT EXISTS oxy (Date TEXT, Oxygen INT)');
        talk("Please tell your Oxygen Level")
        oxy_level = take_command()
        cursor.execute('INSERT INTO oxy (Date, Oxygen) VALUES(?,?)',(DATE,int(oxy_level)));
        conn.commit();
        talk("Your Data is recorded sir!")
        print("Exporting data into CSV............")
        cursor = conn.cursor()
        data = cursor.execute("select * from oxy")
        with open("oxygen_data.csv", "w") as csv_file:
            csv_writer = csv.writer(csv_file) 
            csv_writer.writerow(['Date', 'Oxygen'])
            csv_writer.writerows(data)

        dirpath = os.getcwd() + "/oxygen_data.csv"
        print("Data exported Successfully into {}".format(dirpath))

        
def stats():
    p = "E:\\Abhishek\\hackon\\oxygen_data.csv"
    os.system(p)
            
class moWidget(QtWidgets.QWidget):
    def __init__(self):
        super(moWidget, self).__init__()
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

class terrobyte(moWidget, Ui_Form):
    def __init__(self):
        super(terrobyte, self).__init__()
        self.setupUi(self)
        self.pushButton_3.clicked.connect(sys.exit)
        self.pushButton.clicked.connect(run_terrobyte)
        
if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        Form = terrobyte()
        Form.show()
        sys.exit(app.exec_())

