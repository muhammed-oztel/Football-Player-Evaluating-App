from flask import Flask, request, redirect, session, url_for, flash
import mysql.connector
from flask import render_template
import search_process
from wtforms import *
import hashlib
from passlib.hash import sha256_crypt
import bcrypt

app = Flask(__name__)
app.secret_key = "super secret key"
database = mysql.connector.connect(host="localhost",
                                   user="root",
                                   password="databaseclass",
                                   database="scout_database")

cursor = database.cursor()


@app.route('/')
@app.route('/home')
def hello_world():
    cursor.execute('SELECT * FROM Users ')
    users = cursor.fetchall()

    cursor.execute("select * from analysis a "
                    "left join users u on a.owner_id = u.user_id "
                    "left join plays_in p on a.player_id = p.player_id and p.contract_start<a.share_time<p.contract_end "
                    "left join player pl on pl.player_id = a.player_id order by share_time desc")
    data = cursor.fetchall()
    if 'logged_in' in session:
        if session['logged_in']:
            print(session['nick'])
            return render_template('stream.html',data = data)
    return render_template("main.html" )


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        nick = request.form["nick"]
        name = request.form["name"]
        surname = request.form["surname"]
        mail = request.form["mail"]
        password = request.form["password"]
        # password =sha256_crypt.encrypt(password)
        password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        print(name, surname, mail, nick, password)

        cursor.execute("select * from Users")

        all_users = cursor.fetchall()
        print(all_users)
        check = True
        for user in all_users:
            if user[4] == nick:
                check = False
            if user[3] == mail:
                check = False

        if check == True:
            cursor.execute("insert into Users(user_name,user_surname,user_mail,nick,fav_team,password,profile_img_path)"
                           "values(%s,%s,%s,%s,%s,%s,%s)",
                           (name, surname, mail, nick, 'Sehir Club', password, '../static/img/avatar-auto/default_scout.png'))

            database.commit()
            print("eklendi")

            return redirect(url_for("login"))

        else:
            return redirect("/register")
        return redirect("/")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template("login.html")

    else:

        user_nick = request.form["nick"]
        user_password = request.form["password"]
        cursor.execute("select * from Users")
        all_users = cursor.fetchall()
        print(type(user_password))
        login = False
        for user in all_users:
            if user[4] == user_nick :
                print(user_nick)
                print(type(user[6]), "user[6]")
                # if sha256_crypt.verify(user_password,user[6]):
                if bcrypt.checkpw(user_password.encode('utf-8'),user[6].encode('utf-8')):
                    print("verified pass")

                    login = True
                    print(login)
                    id = user[0]
                    break

        if login == True:
            session["nick"] = user_nick
            session["logged_in"] = True
            session["id"] = id
            return redirect("/users/{nick}".format(nick=user_nick))
        else:
            session["logged_in"] = False
            return redirect("/login")


@app.route("/users/<nick_name>")
def profile(nick_name):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect('/login')
    if 'logged_in' not in session:
        return redirect('/login')
    cursor.execute("select * from Analysis where owner_id=(select user_id from Users where nick = %s)", (nick_name,))
    tweets = cursor.fetchall()
    temp_tweets = []
    for tweet in tweets:
        temp_tweets.append({'tweet': tweet})

        cursor.execute("select * from users where nick = %s", (nick_name,))
        tmp = cursor.fetchone()
        temp_tweets[-1]['user'] = tmp

        cursor.execute("select player_id,name_surname, position,img_url from player where player_id = %s", (tweet[4],))
        tmp = cursor.fetchone()
        temp_tweets[-1]['player'] = tmp

        cursor.execute("select team from plays_in where player_id=%s", (tweet[4],))
        tmp = cursor.fetchone()
        temp_tweets[-1]['team'] = tmp

        cursor.execute("select * from MatchBasedAnalysis where matchanalysis_id = %s", (tweet[0],))
        tmp = cursor.fetchone()
        if tmp:
            tweet += tmp[1:]

        cursor.execute("select * from VideoAnalysis where analysis_id = %s", (tweet[0],))
        tmp = cursor.fetchone()
        if tmp:
            tweet += tmp[1:]
    data = temp_tweets
    print(data)
    return render_template("dashboard.html", data=data)


@app.route('/players', methods=['GET', 'POST'])
def players():
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect('/login')
    if 'logged_in' not in session:
        return redirect('/login')

    print(session)
    if request.method == "POST":
        print("post mehod")
        entered = request.form['entered']
        filters = request.form['filters']
        print(entered, filters)
        search_process.search_players(entered, filters)
        # search by author or book
        # all in the search box will return all the tuples
        data = search_process.search_players(entered, filters)
        # if len(data) == 0:
        #     cursor.execute("SELECT p.player_id,p.name_surname,p.nationality,pi.team,p.position,fa.fifa_ranking,p.img_url"
        #                " FROM player p JOIN plays_in pi ON p.player_id=pi.player_id"
        #                " JOIN fifaattributes fa ON fa.player_id=pi.player_id order by p.player_id")
        #     data = cursor.fetchall()
        #     print(data)
        #     database.commit()
        return render_template('players.html', data=data)
    return render_template('players.html')


#
# @app.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     return render_template("dashboard.html")


@app.route('/players/player_id=<player_id>', methods=['GET', 'POST'])
def player_profile(player_id=None):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect('/login')
    if 'logged_in' not in session:
        return redirect('/login')
    cursor.execute("select * from Player where player_id = %s", (player_id,))
    p_info = cursor.fetchone()
    print(p_info)
    id = p_info[0]
    print(id)
    cursor.execute("select * from"
                   "(select p.player_id,p.team,p.contract_start,p.contract_end, t.club_logo from plays_in p "
                   "JOIN team t on p.team = t.team_fullname) as drv "
                   " where player_id = %s", (id,))
    team = cursor.fetchone()
    cursor.execute("select * from fifaattributes where player_id = %s", (id,))
    fifa = cursor.fetchone()
    cursor.execute("select * from analysis where player_id = %s",(id,))
    tweets = cursor.fetchall()
    temp_tweets = []
    for tweet in tweets:
        temp_tweets.append({'tweet': tweet})

        match_l = []
        video_l = []

        cursor.execute("select * from users where user_id = %s", (tweet[3],))
        tmp = cursor.fetchone()
        temp_tweets[-1]['user'] = tmp

        cursor.execute("select player_id,name_surname, position,img_url from player where player_id = %s", (player_id,))
        ply = cursor.fetchone()
        temp_tweets[-1]['player'] = ply

        cursor.execute("select team from plays_in where player_id=%s and contract_start< now() < contract_end", (player_id,))
        tmp = cursor.fetchone()
        temp_tweets[-1]['team'] = tmp

        cursor.execute("select * from MatchBasedAnalysis where matchanalysis_id = %s", (tweet[0],))
        match = cursor.fetchone()
        if match:
            cursor.execute("select * from (select aa.player_id,aa.owner_id,a.position_played,a.matchanalysis_id,a.match_id,"
                           "m.home_team, m.away_team, s.score from matchbasedanalysis a "
                           "left join matches m on a.match_id = m.match_id "
                           "left join score s on m.match_id = s.match_id "
                           "left join analysis aa on a.matchanalysis_id = aa.analysis_id) as drv "
                           "where drv.player_id = %s and drv.match_id = %s", (ply[0],match[-1],))
            match_l = cursor.fetchone()

        cursor.execute("select * from VideoAnalysis where analysis_id = %s", (tweet[0],))
        video = cursor.fetchone()
        if video_l:
            video_l = video[1:]
        temp_tweets[-1]['match'] = match_l
        temp_tweets[-1]['video'] = video_l

    data = {
        'info': p_info,
        'team': team,
        'fifa': fifa,
        'tweets': temp_tweets
    }
    import pprint
    pprint.pprint(data)
    if request.method == "POST":
        con = request.form['content']
        dribble = int(request.form['dribbling'])
        shoot = int(request.form['shooting'])
        physical = int(request.form['physical'])
        speed = int(request.form['speed'])
        defense = int(request.form['defense'])
        passing = int(request.form['passing'])
        avg = sum([shoot, dribble, passing, physical,speed,defense])/6
        print(con, shoot, dribble, passing, physical,speed,defense)
        cursor.execute(
            "insert into analysis(share_time,content,owner_id,player_id,shooting_rate,dribbling_rate,passing_rate,physical_rate,"
            "speed_rate,defense_rate, average_rate)"
            " values (NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (con,session['id'],player_id,shoot,dribble,passing,physical,speed,defense,avg))
        database.commit()

        flash("Your analysis is added!")

    return render_template("index.html", data=data)


@app.route('/teams', methods=['GET', 'POST'])
def teams():
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect('/login')
    if 'logged_in' not in session:
        return redirect('/login')
    print("we ar in teams")
    if request.method == "POST":
        print("post mehod")
        team = request.form['team']
        # search by author or book
        cursor.execute("SELECT  * from Team WHERE team_fullname LIKE %s", (team,))
        data = cursor.fetchall()
        database.commit()
        print(data)
        # all in the search box will return all the tuples
        if len(data) == 0 and team == 'all':
            cursor.execute("SELECT * from Team")
            data = cursor.fetchall()
            print(data)
            database.commit()
        return render_template('teams.html', data=data)
    return render_template('teams.html')


@app.route('/teams/team_code=<team_code>', methods=['GET', 'POST'])
def team(team_code):
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect('/login')
    if 'logged_in' not in session:
        return redirect('/login')
    data = {}
    cursor.execute("select * from Team where short_name = %s", (team_code,))
    info = cursor.fetchone()
    print(data)
    data['info'] = info
    print(info)
    cursor.execute("select * from Stadium where stadium_name = (select stadium from StadiumOwner where team_name = %s)",
                   (info[0],))
    stadium = cursor.fetchone()
    data['stadium'] = stadium
    print(stadium)

    cursor.execute("select * from (SELECT p.player_id,p.name_surname,p.date_of_birth,p.nationality,pi.team,p.position,"
                   "fa.fifa_ranking,p.img_url, contract_start,pi.contract_end "
                   "FROM player p JOIN plays_in pi ON p.player_id=pi.player_id "
                   "JOIN fifaattributes fa ON fa.player_id=pi.player_id) as drv "
                   "where drv.team = %s  and drv.contract_start< now() < contract_end",
                   (info[0],))
    players = cursor.fetchall()
    data['players'] = players
    print(players)

    cursor.execute("select * from (select m.match_id, m.home_team, m.away_team, m.match_time, t1.league_name, "
                   "t1.team_fullname as home_name, t1.short_name as home_code,"
                   " t1.club_logo as t_1, t2.team_fullname as away_name, t2.short_name as away_code, t2.club_logo as t_2 from matches m "
                   "LEFT JOIN team t1 on t1.team_fullname = m.home_team "
                   "LEFT JOIN team t2 on t2.team_fullname = m.away_team) as drv "
                   "where (drv.home_team=%s or drv.away_team=%s) and drv.match_time>now()  ",
                   (info[0],info[0]))
    nxt_match = cursor.fetchall()[:3]
    print(nxt_match)
    data['next'] = nxt_match
    cursor.execute("select * from (select m.match_id, m.home_team, m.away_team, m.match_time, t1.league_name, "
                   "t1.team_fullname as home_name, t1.short_name as home_code,"
                   " t1.club_logo as t_1, t2.team_fullname as away_name, t2.short_name as away_code, t2.club_logo as t_2, "
                   " s.score as sc from matches m "
                   "LEFT JOIN team t1 on t1.team_fullname = m.home_team "
                   "LEFT JOIN team t2 on t2.team_fullname = m.away_team "
                   "LEFT JOIN score s on s.match_id = m.match_id)as drv "
                   "where (drv.home_team=%s or drv.away_team=%s) and drv.match_time<now()  ",
                   (info[0],info[0]))
    old_matc= cursor.fetchall()[-3:]
    print(len(old_matc))
    data['old'] = old_matc
    database.commit()
    return  render_template("team_dash.html", data  = data)

@app.route('/settings')
def scouts():
    session.clear()
    session['logged_in'] = False
    print(session)
    return redirect('/home')



@app.route('/players/create_analysis=<player_id>', methods=['GET', 'POST'])
def create_tweet(player_id):
    if not session['logged_in']:
        return redirect('/login')
    cursor.execute("select name_surname from player where player_id = %s",(player_id,))
    name = cursor.fetchone()
    data = [player_id,name]
    print(data)
    if request.method == "POST":
        print("we are in post")
        con = request.form['content']
        dribble = int(request.form['dribbling'])
        shoot = int(request.form['shooting'])
        physical = int(request.form['physical'])
        speed = int(request.form['speed'])
        defense = int(request.form['defense'])
        passing = int(request.form['passing'])
        avg = sum([shoot, dribble, passing, physical, speed, defense]) / 6
        print(con, shoot, dribble, passing, physical, speed, defense)
        cursor.execute(
            "insert into analysis(share_time,content,owner_id,player_id,shooting_rate,dribbling_rate,passing_rate,physical_rate,"
            "speed_rate,defense_rate, average_rate)"
            " values (NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (con, session['id'], player_id, shoot, dribble, passing, physical, speed, defense, avg))
        database.commit()
        return redirect('/players/player_id=%s'%player_id)
    return render_template("create_analysis.html",data=data)

@app.route('/missions')
def missions():
    return render_template("missions.html")


if __name__ == '__main__':

    app.run()
