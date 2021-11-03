# main working face detector uses MONGO
from PIL import ImageFont, ImageDraw,Image
import cv2
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime
import pprint
import requests, urllib.parse
import pandas as pd
import lcd_font


client = MongoClient(
        'mongodb+srv://test123:test123@clusteractivity.oqe3k.mongodb.net/LoginDB?retryWrites=true&w=majority')
db = client['LoginDB']

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("recognizer/trainingData.xml")
# font = cv2.InitFont(cv2.CV_FONT_HERSHEY_COMPLEX_SMALL,5,1,0,4)
# Font1 = ImageFont.truetype("browalia.ttc", 14)
fontface = cv2.FONT_HERSHEY_PLAIN
fontscale = 1
fontcolor = (0, 0, 0)
progress = 0
state = 0
id = 0
key = 0
time = datetime.now().timestamp()
count_data = 0
font_data = lcd_font.font()



token = "mtf1gxq3x75d9rHSFt54zyuCgotm07GklL3nccPosbe"
url = 'https://notify-api.line.me/api/notify'
HEADERS = {'Authorization': 'Bearer ' + token}

listWeing = ['bour', 'chiangrang', 'jomtong', 'kaluang', 'lor', 'namtao']
listWeingThai =['บัว','เชียงแรง','จอมทอง','กาหลวง','ลอ','น้ำเต้า']

# activityname = input("Enter Name : ")
# 
#     data = db["data"]
#     for p in data.find():
#         if (datetime.strptime(x['endTime'], '%Y-%m-%dT%H:%M').microsecond - datetime.strptime(x['startTime'], '%Y-%m-%dT%H:%M').microsecond < 0): return p

#     return
    # print

def findWeingNameThai(weingNameEN):
    if weingNameEN=='':
        return ''
    else:
        index = listWeing.index(weingNameEN)
        if index>-1:
            return listWeingThai[index]
        else:
            return ''

def write_tt_text(image,x,y,text):
    label_w = 250
    label_h = 40
    try:
        win_text=text.decode('UTF-8')
        win_text=win_text+unichr(0x0020)+unichr(0x0020)
    except:
        win_text=text+'  '
    Font1 = ImageFont.truetype("AgaraDull.ttf", 30)
    image_pil = Image.new("RGB",(label_w,label_h),(0,0,0))
    draw = ImageDraw.Draw(image_pil)
    draw.text((5,5),win_text,(255,255,255),font=Font1)
    del draw
    
    cv_image = np.array(image_pil) 
    cv_image = cv_image[:, :, ::-1].copy() 
    imageout = image.copy()    
    if y>=0 and x>=0:
        if x+label_w<=imageout.shape[1] and y+label_h<=imageout.shape[0]:
            imageout[0+y:0+y+label_h , 0+x:0+x+label_w] = cv_image
    return imageout

def getActivity():
    global count_data
    data = db["data"]
    status = 0    
    time = datetime.utcnow()
    condition = {'$and' : [{'startTime':{'$lte':time}},{'endTime':{'$gte':time}}]}
    # condition = {'$and' : [{'startTime':{'$lte':time}}]}
    #condition = {'$and' : [{'endTime':{'$gte':time}}]}
    # print(condition)
    xc = data.find_one(condition)
    # print(xc)
    if xc!=None:
        o = xc['ActivityName']
    else:
        o = ""
    if len(o)>0:
        status=1    

    

    # print(str(datetime.now()))
    # for x in data.find():
    #     s = str(x['startTime']).split(' ')
    #     ss0 = s[0].split('-') #date 00/00/0000
    #     ss1 = s[1].split(':') #time   

    #     n = str(datetime.now()).split(' ')
    #     ns0 = n[0].split('-') #date
    #     ns1 = n[1].split(':') #time

    #     e = str(x['endTime']).split(' ')
    #     es0 = e[0].split('-') #date
    #     es1 = e[1].split(':') #time

    #     # e=50000000 
    #     # s=0
    #     count_data = x['count']
        
    #     if (int(ss0[0]) <= int(ns0[0]) and int(ns0[0]) <= int(es0[0])): 
    #         if(int(ss0[1]) <= int(ns0[1]) and int(ns0[1]) <= int(es0[1])):
    #             if(int(ss0[2]) <= int(ns0[2]) and int(ns0[2]) <= int(es0[2])):
    #                 st1 = (int(ss1[0])*60*60) + (int(ss1[1])*60)
    #                 now = (int(ns1[0])*60*60 )+ (int(ns1[1])*60)
    #                 end = (int(es1[0])*60*60) + (int(es1[1])*60)
    #                 # print(str(st1)+"<="+str(now)+"<="+str(end))
    #                 if(st1 <= now and now <= end):
    #                         o = x['ActivityName'] 
    #                         xc = x
    #                         print(str(o))
    #                         status = 1
    #                         break 
    return o , xc , status 
    

def getProfile(id):
    posts = db["posts"]

    #print(posts.find_one({'id': id}))

    return posts.find_one({'id': id})
    
def isDuplicateId(id, activity):
    Log = db["Log"]
    print(id,activity)
    x = Log.find_one({"id":id ,"activity":activity})
    print ("x",x)
    if  x==None:
        print("Not duplicate")
        return False
    else:
        print("Is duplicate")
        return True
   

def send(id):
    global count_data 
    global GWeingName
    Log = db["Log"]
    data = db["data"]
    post = db["post"]
    name = getProfile(id)["name"]
    activity = getActivity()
    print(activity)

    weing = getWeingFromStuID(id)    
    GWeingName = findWeingNameThai(weing)

    #Query from mongodb and set current count data
    count_data = getCurrentCountByActivity(activity[0])
    
    # print(activity)
    date = datetime.now()
    if(activity[2] == 1):
        post = {"name": name, "id": id, "date": date,"activity":activity[0],'weing':weing}        
        urlform ="https://b657-2403-6200-8858-b4dd-3954-4f23-6127-1323.ngrok.io/assessmentform/{}/{}".format(activity[0],id);
        msg = "{} ชื่อ-นามสกุล: {} รหัสนิสิต: {} เวียง: {} เวลาที่เข้าร่วม: {} หลังจากเสร็จสิ้นกิจกรรม กรุณาทำแบบประเมินกิจกรรมให้ด้วยครับ แบบฟอร์มตาม URL นี้ : {}".format(activity[0],name,id,GWeingName,date,urlform.replace(' ','_'))
                
        if(not isDuplicateId(id,activity[0])):
            count_data += 1
            print("Count activity "+ activity[0] +" update : "+ str(count_data))
            data.update_one(activity[1], {'$set': {'count': count_data}})
            Log.insert_one(post).inserted_id
        
        print("Current Count Data : "+ str(count_data))
        
        requests.post(url, headers=HEADERS, params={"message": msg})
        print('success')

def inTime():
    date = datetime.now()
    if (date.hour == 10): return True
    else: return False

def confirm(id):    
    cv2.rectangle(img, (50, 50), (400, 100), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(img, (50, 50), (400, 100), (0, 0, 0), 2)    
    # weingName = getWeingFromStuID(id)
    # print(weingName)
    cv2.putText(img, "Your STUID is {} ".format(id), (80, 80) ,fontface, fontscale, (0, 0, 0))    
    # cv2.putText(img, "Your STUID is {} weing {} ".format(id,weingName), (80, 80) , fontface, fontscale, (0, 0, 0))    
    send(id)

def getCurrentCountByActivity(activity):
    currentCountData =0
    data = db["data"]
    filters = {'ActivityName':activity}
    x = data.find_one(filters)
    print(x)
    if(x != None):
        currentCountData = x['count']
    print("currentCountData :" + str(currentCountData))
    return currentCountData

def getWeingFromStuID(stuID):
    post = db["posts"]
    filters = {'id':stuID}
    x = post.find_one(filters)
    # print(x)
    if(x != None):
        #print('Student ID :'+ str(stuID)+' is weing :'+ x['weing'])
        if x==None:
            return ''
        else:
            # print(x['weing'])
            return x['weing']
    else:
        #print('Student ID :'+ str(stuID)+' is not found weing :')
        return ''

#Start Program
#--------------------------------------------------------------------------
# print(getWeingFromStuID('610507897'))
# GetActivity():
# 1. กิจกรรม 64 12:00 - 17:00    
# 2. กิจกรรม 65 12:00 - 17:00
# Start Date กิจกรรม -30 นาที เทียบกับเวลาปัจจุบัน ถ้ามันเร็วไป เราก็แค่แจ้งเตือนนะ 
# Select Choice before run : 
# พอหมดเวลากิจกรรม ก็ให้โปรแกรมขึ้นถามว่ายังต้องการรันต่อหรือเปล่า ถ้ารันต่อจะเลือกกิจกรรมไหน..

#selectedActivityName =""
#startActivty =

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
        try:
            confirm(str(id))            
            state = 2
            time = datetime.now().timestamp()
        except NameError:
            print(NameError)
            pass                
    if (state == 2):
        # cv2.rectangle(img, (50, 50), (300, 100), (255, 255, 255), cv2.FILLED)
        # cv2.rectangle(img, (50, 50), (300, 100), (0, 0, 0), 2)
        # print("Show Weing :"+GWeingName)
        # cv2.putText(img, "STUID is {} {}".format(id,GWeingName), (80, 80) , fontface, fontscale, (0, 0, 0))
        # write_tt_text(img,80,80,"STUID is {} {}".format(id,GWeingName))
        img = write_tt_text(img,80,80,"STUID is {} {}".format(id,GWeingName))

        
    if (state == 2 and len(faces) == 0 and datetime.now().timestamp() - time > 2): 
        state = 0
        GWeingName =""
    # print(datetime.now().timestamp() - time)
		
    cv2.imshow("Face", img)
    if(key == ord('q')):
        break

cam.release()
cv2.destroyAllWindows()

# ต่อๆๆ เลย