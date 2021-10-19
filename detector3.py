# main working face detector uses MONGO
import cv2
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime
import pprint
import requests, urllib.parse
import pandas as pd

client = MongoClient(
        'mongodb+srv://test123:test123@clusteractivity.oqe3k.mongodb.net/LoginDB?retryWrites=true&w=majority')
db = client['LoginDB']

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("recognizer/trainingData.xml")
#font = cv2.InitFont(cv2.CV_FONT_HERSHEY_COMPLEX_SMALL,5,1,0,4)
fontface = cv2.FONT_HERSHEY_PLAIN
fontscale = 1
fontcolor = (0, 0, 0)
progress = 0
state = 0
id = 0
key = 0
time = datetime.now().timestamp()
count_data = 0

token = "mtf1gxq3x75d9rHSFt54zyuCgotm07GklL3nccPosbe"
url = 'https://notify-api.line.me/api/notify'
HEADERS = {'Authorization': 'Bearer ' + token}

# activityname = input("Enter Name : ")
# 
#     data = db["data"]
#     for p in data.find():
#         if (datetime.strptime(x['endTime'], '%Y-%m-%dT%H:%M').microsecond - datetime.strptime(x['startTime'], '%Y-%m-%dT%H:%M').microsecond < 0): return p

#     return
    # print

def getActivity():
    global count_data
    data = db["data"]
    status = 0
    o = ""
    xc = data.find()[0]
    time = datetime.now().microsecond
    # print(str(datetime.now()))
    for x in data.find():
        s = x['startTime'].split('T')
        ss0 = s[0].split('-') #date 00/00/0000
        ss1 = s[1].split(':') #time   

        n = str(datetime.now()).split(' ')
        ns0 = n[0].split('-') #date
        ns1 = n[1].split(':') #time

        e = x['endTime'].split('T')
        es0 = e[0].split('-') #date
        es1 = e[1].split(':') #time

        # e=50000000 
        # s=0
        count_data = x['count']
        # print(ss0[0]+ns0[0]+ns0[0]+es0[0])
        # print(ss0[1]+ns0[1]+ns0[1]+es0[1])
        # print(ss0[2]+ns0[2]+ns0[2]+es0[2])

        if (int(ss0[0]) <= int(ns0[0]) and int(ns0[0]) <= int(es0[0])): 
            if(int(ss0[1]) <= int(ns0[1]) and int(ns0[1]) <= int(es0[1])):
                if(int(ss0[2]) <= int(ns0[2]) and int(ns0[2]) <= int(es0[2])):
                    st1 = (int(ss1[0])*60*60) + (int(ss1[1])*60)
                    now = (int(ns1[0])*60*60 )+ (int(ns1[1])*60)
                    end = (int(es1[0])*60*60) + (int(es1[1])*60)
                    # print(str(st1)+"<="+str(now)+"<="+str(end))
                    if(st1 <= now and now <= end):
                            o = x['ActivityName'] 
                            xc = x
                            print(str(o))
                            status = 1
                            break 
    return o , xc , status 
    

def getProfile(id):
    posts = db["posts"]

    #print(posts.find_one({'id': id}))

    return posts.find_one({'id': id})
    
def isDuplicateId(id, activity):
    Log = db["Log"]
    x = Log.find_one({"id":id , "activity":activity[0]})
    print ("x",x)
    if not x:
        return False
    else:
        return True

    

def send(id):
    global count_data
    Log = db["Log"]
    data = db["data"]
    name = getProfile(id)["name"]
    activity = getActivity()
    # print(activity)
    date = datetime.now()
    if(activity[2] == 1):
        post = {"name": name, "id": id, "date": date,"activity":activity[0]}
        count_data += 1
        print(str(count_data))
        msg = "{}-{}-{}-{}".format(activity[0],name,id,date)
        Log.insert_one(post).inserted_id
        if(not isDuplicateId(id,activity[0])):
            data.update_one(activity[1], {'$set': {'count': count_data}})
            requests.post(url, headers=HEADERS, params={"message": msg})
        print('success')

def inTime():
    date = datetime.now()
    if (date.hour == 10): return True
    else: return False

def confirm(id):
    cv2.rectangle(img, (50, 50), (350, 100), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(img, (50, 50), (350, 100), (0, 0, 0), 2)
    cv2.putText(img, "Your STUID is {}".format(id), (80, 80) , fontface, fontscale, (0, 0, 0))
    
    send(id)

while True:
    key = cv2.waitKey(1)
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    name = ""
    if (True and state == 0):
        for(x, y, w, h) in faces:
            id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            # id=getNm(id)
            if(conf >= 4 and conf <= 100): # Matched
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if (len(faces) == 1): progress += 1
                cv2.putText(img, str(id), (x, y+h+30),
                    fontface, fontscale, (0, 255, 0))
            else:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(img, "unknown", (x, y+h+50), fontface,
                    fontscale, (0, 0, 255))
    if (len(faces) == 0): progress = 0
    if (state == 0 and progress == 25): 
        state = 1
    if (state == 1): 
        confirm(str(id))
        state = 2
        time = datetime.now().timestamp()
    if (state == 2):
        cv2.rectangle(img, (50, 50), (300, 100), (255, 255, 255), cv2.FILLED)
        cv2.rectangle(img, (50, 50), (300, 100), (0, 0, 0), 2)
        cv2.putText(img, "STUID is {}".format(id), (80, 80) , fontface, fontscale, (0, 0, 0))
    if (state == 2 and len(faces) == 0 and datetime.now().timestamp() - time > 2): 
        state = 0
    # print(datetime.now().timestamp() - time)
		
    cv2.imshow("Face", img)
    if(key == ord('q')):
        break

cam.release()
cv2.destroyAllWindows()
