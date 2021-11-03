"""
	code creates a dataset of images to be trained by opening camera and capturing
	20 images of a detected face 
	also takes input of user id and name of persons face and inserts into a database
"""
import cv2
import numpy as np
import os
from pymongo import MongoClient
import datetime
import pprint


def inputData(ID, NAME, Weing,sexid,facid):
    client = MongoClient(
        'mongodb+srv://test123:test123@clusteractivity.oqe3k.mongodb.net/LoginDB?retryWrites=true&w=majority')
    db = client['LoginDB']
    collection = db['Log']

    post = {"id": ID,
            "name": NAME,
            "weing": Weing,
            "sex": sexid,
            "facultyID": facid,
            "date": datetime.datetime.now()}
    Log = db.Log
    posts = db.posts
	
    post_id = posts.insert_one(post)


def retrieveData(ID):
    client = MongoClient(
        'mongodb+srv://test123:test123@clusteractivity.oqe3k.mongodb.net/LoginDB?retryWrites=true&w=majority')
    db = client['LoginDB']
    collection = db['Log']
    posts = db.posts

    pprint.pprint(posts.find_one({"id": ID}))


faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)

id = input('Please Enter Student ID:')
name = input('Please Enter your name and lastname:')
 
Facultylistthai =['คณะเกษตรศาสตร์และทรัพยากรธรรมชาติ',
'คณะเทคโนโลยีสารสนเทศและการสื่อสาร',
'คณะทันตแพทยศาสตร์',
'คณะนิติศาสตร์',
'คณะบริหารธุรกิจและนิเทศศาสตร์',
'คณะพยาบาลศาสตร์',
'คณะพลังงานและสิ่งแวดล้อม',
'คณะแพทยศาสตร์',
'คณะเภสัชศาสตร์',
'คณะรัฐศาสตร์และสังคมศาสตร์',
'คณะวิทยาศาสตร์',
'คณะวิทยาศาสตร์การแพทย์',
'คณะวิศวกรรมศาสตร์',
'คณะสถาปัตยกรรมศาสตร์และศิลปกรรมศาสตร์',
'คณะสหเวชศาสตร์',
'คณะสาธารณสุขศาสตร์',
'คณะศิลปศาสตร์']
sexlistthai =['ชาย', 'หญิง']

listWeing = ['bour', 'chiangrang', 'jomtong', 'kaluang', 'lor', 'namtao']
listWeingThai =['บัว','เชียงแรง','จอมทอง','กาหลวง','ลอ','น้ำเต้า']
weingCorrent = False
while not weingCorrent:
    print("Please Select Weing From choice 1-6:")
    for i in range(len(listWeingThai)):
        print(str(i+1)+". " + listWeingThai[i])
    try:
        weing = int(input('Please Enter your weing:')) - 1 
    except:
        pass

    if weing < len(listWeing) and weing>=0:
        weingCorrent = True

sexCorrent = False
sexID=0
while not sexCorrent:
    print("Please Select Sex From choice 1-"+str(len(sexlistthai))+" : ")
    for i in range(len(sexlistthai)):
        print(str(i+1)+". " + sexlistthai[i])
    try:
        sexID = int(input('Please Enter Your Sex :'))
    except:
        pass

    if sexID < len(sexlistthai)+1 and sexID>0:
        sexCorrent = True

facCorrent = False
facID=0
while not facCorrent:
    print("Please Select Faculty From choice 1-"+str(len(Facultylistthai))+" : ")
    for i in range(len(Facultylistthai)):
        print(str(i+1)+". " + Facultylistthai[i])
    try:
        facID = int(input('Please Enter Your faculty :')) 
    except:
        pass

    if facID < len(Facultylistthai)+1 and facID>0:
        facCorrent = True


inputData(id, name, listWeing[weing],sexID,facID)
retrieveData(id)

sampleNum = 0

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    for(x, y, w, h) in faces:
        sampleNum += 1
        cv2.imwrite("dataset/User."+str(id)+"." +
                    str(sampleNum)+".jpg", gray[y:y+h, x:x+w])
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.waitKey(100)
    cv2.imshow("Face", img)
    cv2.waitKey(1)
    if(sampleNum > 20):
        break

cam.release()
cv2.destroyAllWindows()
