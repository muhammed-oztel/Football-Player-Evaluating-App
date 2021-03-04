import urllib.request
import mysql.connector
import os

import urllib.request
from PIL import Image

database = mysql.connector.connect(host = "localhost",
                                   user = "root",
                                   password = "databaseclass",
                                   database= "scout_database")

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'


def download_img(image_url, file_path, file_name):
    full_path = file_path + file_name + '.jpg'
    headers={'User-Agent':user_agent,}
    request=urllib.request.Request(image_url,None,headers)
    response = urllib.request.urlopen(request)
    #install PIL package to convert the response into a PIL Image object to further save it
    image=Image.open(response)
    image.save(full_path)
    pass



cursor = database.cursor(buffered = True)

cursor.execute("select player_id, name_surname,img_url from player")
datas = cursor.fetchall()
database.commit()
print(datas)
print(os.curdir)
print(len("https://cdn.sofifa.com/players/"))

for d in datas:
    dir = os.curdir+"/static/players/"+d[2][31:-10]
    try:
        # Create target Directory
        os.makedirs(dir)
        print("Directory ", " Created ", d[0],d[1])
    except FileExistsError:
        print("Directory ", " already exists")
    try:
        full_path = dir + '20_120.png'
        headers={'User-Agent':user_agent,}
        request=urllib.request.Request(d[2],None,headers)
        response = urllib.request.urlopen(request)
        #install PIL package to convert the response into a PIL Image object to further save it
        image=Image.open(response)
        image.save(full_path)
    except :
        pass



for d in datas:
    try:
        dir = os.curdir + "/static/players/" + d[2][31:-10] + '20_120.png'
        print(dir, d)
        cursor.execute("update player set img_url =  %s where player_id = %s",(dir,d[0]))
        database.commit()
        print("updating process is done for %s as %s"%(d[0],dir))
    except:
        print("An exception Occured",)
        pass