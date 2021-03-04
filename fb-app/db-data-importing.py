import mysql.connector
months = {
    'Jan': 1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5,
    'Jun':6,
    'Jul':7,
    'Aug':8,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12
}



positions = {
    'Centre-Back':'CB',
    'Attacking Midfield':'AM',
    'Central Midfield':'CM',
    'Left Midfield':'LM',
    'Right Midfield':'RM',
    'Left-Back':'LB',
    'Right-Back':'RB',
    'Defensive Midfield':'DM',
    'Goalkeeper':'GK',
    'Left Winger':'LWF',
    'Right Winger': 'RWF',
    'Centre-Forward':'CF'

}

database = mysql.connector.connect(host = "localhost",
                                   user = "root",
                                   password = "databaseclass",
                                   database= "scout_database")


cursor = database.cursor(buffered = True)

def team_stadium_insert():
    with open("data/team-stadium-done - sheet 1 (2).csv", encoding='utf-8') as db:
        line = db.readline()
        line = db.readline()
        print(line)
        while line:
            splitted = line.split(",")
            # print(splitted)
            a = ' '.join(splitted)
            team = splitted[2]
            code = splitted[-6]
            league = splitted[-5]
            city= splitted[-2]
            budget= float(splitted[-1].split('\n')[0])
            stadium = splitted[-4]
            capacity= int(splitted[-3])
            print(team,code,league,stadium,capacity,city,(budget))
            cursor.execute("insert into Team(team_fullname,short_name,league_name,city,budget)"
                           "values ( %s,%s,%s,%s,%s) on duplicate key update team_fullname = %s",
                           (team,code,league,city,budget, team))

            cursor.execute("insert into Stadium(stadium_name,city,capacity)"
                           "values(%s,%s,%s) on duplicate key update stadium_name = %s",
                           (stadium,city,capacity, stadium))

            cursor.execute("insert into StadiumOwner(team_name,stadium)"
                           "values(%s,%s) on duplicate key update team_name = %s",
                           (team, stadium, team))
            database.commit()

            line = db.readline()

def player_insert_demo():
    with open('data/transfermarkt-team-player-v1.3 - transfermarkt-team-player.csv', 'r',encoding='utf-8') as data:
        lines =  data.readlines()
        for i in range(1,2):
            splitted = lines[i].strip('\n').split(',')
            print(splitted)
            name = splitted[2]
            team = splitted[1]
            nation = splitted[4]
            birth = splitted[5]
            height = float(splitted[6][:-2])
            position = positions[splitted[7]]
            foot = splitted[8].capitalize()
            contract_end = splitted[9]
            img = splitted[-1]

            if foot =='null':foot= 'Right'
            if contract_end =='null':contract_end='12.12.2022'

            month = months[birth[:3]]
            day = birth[4:6].strip(' ')
            year = birth[-4:]
            birth = "%s-%s-%s"%(day,month,year)
            print(name, "%s-%s-%s"%(day,month,year), foot,len(foot))

            cursor.execute("insert into Player(name_surname,nationality, position,date_of_birth,height,weight,foot,img_url)"
                           "values(%s,%s,%s,STR_TO_DATE(%s,'%d-%m-%Y'),%s,%s,%s,%s)",
                           (name, nation, position,birth,height,75,foot, img))

            cursor.execute("insert into plays_in(player_id, team,contract_start,contract_end)"
                           "values((select player_id "
                           "from Player where name_surname = %s and nationality =%s and height = %s),%s,STR_TO_DATE(%s, '%d.%m.%Y'),STR_TO_DATE(%s,'%d.%m.%Y'))",
                           (name, nation,height,team,'10.10.2017',contract_end))
            database.commit()

def player_photos():
    with open("data/with_photos - with_photos.csv",'r', encoding='utf-8') as data:
        lines = data.readlines()
        for i in range(1,len(lines)):
            line = lines[i].strip('\n').split(',')
            name = line[2]
            dob = line[4]
            height = line[5]
            weight = line[6]
            nation = line[7]
            team = line[8]
            overall = line[9]
            position = line[10]
            foot= line[11]
            contract_start = line[13]
            contract_end = line[14][:-2] + "-12-12"
            photo = line[-1]
            # print(line)

            dribb = float(line[-7])
            shoot = float(line[-6])
            phys = float(line[-5])
            speed =float( line[-4])
            defense = float(line[-3][:4])
            passing =float(line[-2])
            print(name, dob, height ,weight, nation, overall, team,position, foot,contract_start, contract_end,photo,dribb,shoot,speed,defense,passing)
            if team not in ['Alanyaspor','Antalyaspor', 'Besiktas JK', 'Caykur Rizespor','Denizlispor', 'Fenerbahce SK','Galatasaray SK', 'Gaziantep FK','Genclerbirligi Ankara', 'Göztepe', 'Istanbul Basaksehir FK', 'Kasimpasa', 'Kayserispor','Konyaspor', 'MKE Ankaragücü','Sehir Club', 'Sivasspor','Trabzonspor','Yeni Malatyaspor']:
                print("passed")
                continue
            if contract_start =="nan":
                contract_start = line[12]
            print(name, dob, height ,weight, nation, overall, team,position, foot,contract_start, contract_end,photo,dribb,shoot,speed,defense,passing)

            cursor.execute("insert into Player(name_surname,nationality, position,date_of_birth,height,weight,foot,img_url)"
                           "values(%s,%s,%s,STR_TO_DATE(%s,'%Y-%m-%d'),%s,%s,%s,%s)",
                           (name, nation, position, dob, height, weight, foot, photo))
            print(photo)
            cursor.execute("SELECT LAST_INSERT_ID() from player")
            id = cursor.fetchone()
            print((id[0]))
            cursor.execute("insert into plays_in(player_id, team,contract_start,contract_end)"
                           "values(%s, %s,STR_TO_DATE(%s, '%Y-%m-%d'),STR_TO_DATE(%s,'%Y-%m-%d'))",
                           (id[0], team, contract_start, contract_end))

            cursor.execute("insert into fifaAttributes(player_id, fifa_ranking,dribbling,shooting,physical,speed,defense,passing)"
                           "values(%s, %s,%s,%s,%s,%s,%s,%s)",
                           (id[0],overall,dribb,shoot,phys,speed,defense,passing))
            database.commit()
player_photos()
def logo():
    with open('data/transfer-teams.csv', encoding='utf-8') as data:
        lines = data.readlines()
        for line in lines:
            line = line.strip('\n').split(',')
            team = line[2].strip('"')
            link = line[-1].strip('"')

            print(team, link)
            cursor.execute(" UPDATE team "
                           "set club_logo = %s where team_fullname = %s",(link,team))
            database.commit()

def week_1():
    with open('data/week-1-updated - dsadsa.csv', encoding="utf-8") as d:
        lines = d.readlines()
        for i in range(1,len(lines)):
            line = lines[i].strip('\n').split(',')
            # print(line)

            home = line[-3]
            score = line[-2]
            away= line[-1]
            date = line[-5]
            time = line[-4]
            timestamp = date+" "+time
            print(timestamp,home,score,away)
            cursor.execute("insert into Matches(home_team,away_team,match_time,league_name)"
                           "values (%s,%s,STR_TO_DATE(%s,'%d.%m.%Y %H:%i'),%s)",
                           (home,away,timestamp,'Super Lig'))
            cursor.execute("SELECT LAST_INSERT_ID() from Matches")
            id = cursor.fetchone()

            cursor.execute("insert into Score(match_id, score)"
                           "values (%s,%s)",
                           (id[0],score))


            database.commit()

# with open('data/tff-updated - tff (1).csv', encoding="utf-8") as d:
#     lines = d.readlines()
#     for i in range(len(lines)):
#         line = lines[i].strip('\n').split(',')
#         print(line)
#         if line[-1] =='':continue
#         home = line[-3].lstrip(' ')
#         score = line[-2]
#         away = line[-1].lstrip(' ')
#         date = line[-5]
#         time = line[-4]
#         if time == '':time = '20:00'
#
#         timestamp = date + " " + time
#
#         cursor.execute("insert into Matches(home_team,away_team,match_time,league_name)"
#                        "values (%s,%s,STR_TO_DATE(%s,'%d.%m.%Y %H:%i:'),%s)",
#                        (home, away, timestamp, 'Super Lig'))
#
#         database.commit()
#
#         print(timestamp, home, score, away)
#         if score=='-':
#             print('no score')
#             continue
#
#         cursor.execute("SELECT LAST_INSERT_ID() from Matches")
#         id = cursor.fetchone()
#         cursor.execute("insert into Score(match_id, score)"
#                        "values (%s,%s)",
#                        (id[0], score))
#
#         database.commit()

