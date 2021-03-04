from wtforms import Form, StringField, validators,BooleanField
import mysql.connector

database = mysql.connector.connect(host = "localhost",
                                   user = "root",
                                   password = "databaseclass",
                                   database= "scout_database")


cursor = database.cursor(buffered = True)


class PlayerSearchForm(Form):
    name = StringField('Player Name', [validators.Length(min=0, max=25)])
    surname = StringField('Player Surname', [validators.Length(min=0, max=35)])
    team = StringField('Current Team', [validators.Length(min=0, max=35)])
    nation = StringField('Nationality', [validators.Length(min=0, max=35)])
    dob = StringField('Date of Birth', [validators.Length(min=0, max=35)])
    overall_min = BooleanField('Min. Overall', [validators.DataRequired()])
    overall_max = BooleanField('Max. Overall', [validators.DataRequired()])


def search_players(value, filter):
    if value =='':
        return []
    if filter =='name':
        cursor.execute("select *"
                       " from (SELECT p.player_id,p.name_surname,p.nationality,pi.team,p.position,fa.fifa_ranking,p.img_url"
                       " FROM player p JOIN plays_in pi ON p.player_id=pi.player_id"
                       " JOIN fifaattributes fa ON fa.player_id=pi.player_id order by p.player_id) as drv"
                       " where drv.name_surname like %s",(value,) )
        data = cursor.fetchall()

    elif filter == 'team':
        cursor.execute("select *"
                       " from (SELECT p.player_id,p.name_surname,p.nationality,pi.team,p.position,fa.fifa_ranking,p.img_url"
                       " FROM player p JOIN plays_in pi ON p.player_id=pi.player_id"
                       " JOIN fifaattributes fa ON fa.player_id=pi.player_id order by p.player_id) as drv"
                       " where drv.team like %s",(value,) )
        data = cursor.fetchall()
    elif filter == 'nation':
        cursor.execute("select *"
                       " from (SELECT p.player_id,p.name_surname,p.nationality,pi.team,p.position,fa.fifa_ranking,p.img_url"
                       " FROM player p JOIN plays_in pi ON p.player_id=pi.player_id"
                       " JOIN fifaattributes fa ON fa.player_id=pi.player_id order by p.player_id) as drv"
                       " where drv.nationality like %s", (value,))
        data = cursor.fetchall()
    elif filter == 'position':
        cursor.execute("select *"
                       " from (SELECT p.player_id,p.name_surname,p.nationality,pi.team,p.position,fa.fifa_ranking,p.img_url"
                       " FROM player p JOIN plays_in pi ON p.player_id=pi.player_id"
                       " JOIN fifaattributes fa ON fa.player_id=pi.player_id order by p.player_id) as drv"
                       " where drv.position like %s", (value,))
        data = cursor.fetchall()
    elif filter == 'overall':
        cursor.execute("select *"
                       " from (SELECT p.player_id,p.name_surname,p.nationality,pi.team,p.position,fa.fifa_ranking,p.img_url"
                       " FROM player p JOIN plays_in pi ON p.player_id=pi.player_id"
                       " JOIN fifaattributes fa ON fa.player_id=pi.player_id order by p.player_id) as drv"
                       " where drv.fifa_ranking >= %s", (value,))
        data = cursor.fetchall()
    else:
        data =[]
    database.commit()
    return data

data = []
if not data:
    print("empty is true")
else:
    print("empty is not true")