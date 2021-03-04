create table if not exists Player(
	player_id int auto_increment,
    name_surname varchar(75) not null,
    nationailty varchar(20) not null,
    position varchar(3) not null,
    date_of_birth date not null,
    height float not null,
    weight float not null,
    foot char(4) check (foot in ('Right','Left','Both')) not null,
    primary key (player_id)
);

create table if not exists League(
	league_name varchar(50) not null,
    country varchar(25) not null,
    primary key (league_name)
);

create table if not exists Team(
	team_fullname varchar(50),
    short_name char(3) unique,
    league_name varchar(50),
    city varchar(15),
    budget float,
    primary key (team_fullname),
    foreign key (league_name) references League(league_name)
);

create table if not exists Stadium(
	stadium_name varchar(100) not null,
    city varchar(25) not null,
    capacity int,
    primary key (stadium_name)
);



create table if not exists Matches(
	match_id int auto_increment,
    home_team varchar(50),
    away_team varchar(50),
    match_time timestamp,
    league_name varchar(30),
    primary key (match_id),
    foreign key (home_team) references Team(team_fullname) on delete cascade,
    foreign key (away_team) references Team(team_fullname) on delete cascade,
    foreign key (league_name)references League(league_name) on delete cascade
    
);

create table if not exists Score(
	match_id int primary key references Matches(match_id) on delete cascade,
    score varchar(5) not null
);

create table if not exists fifaAttributes(
	player_id int primary key references Player(player_id) on delete cascade,
    fifa_ranking float not null,
    dribbling float not null,
    shooting float not null,
    physical float not null,
    speed float not null,
    defense float not null,
    passing float not null
);

create table if not exists Users( 
	user_id int auto_increment,
    user_name varchar(50) not null,
    user_surname varchar(50) not null,
    user_mail varchar(256) not null unique,
    nick varchar(50) not null unique,
    fav_team varchar(50),
    password varchar(255),
    profile_img_path varchar(256) default null,
    primary key (user_id),
    foreign key (fav_team) references Team(team_fullname)
);

create table if not exists ScoutMission(
	mission_id int auto_increment,
    match_id int not null,
    content varchar(256),
    primary key(mission_id),
    foreign key (match_id) references Matches(match_id) on delete cascade
);

create table if not exists Analysis(
	analysis_id int not null auto_increment,
    share_time timestamp,
    content varchar(140),
    owner_id int not null ,
    player_id int not null ,
    shooting_rate float not null,
    dribbling_rate float not null,
    passing_rate float not null,
    physical_rate float not null,
    speed_rate float not null,
    defense_rate float not null,
    average_rate float not null,
    primary key (analysis_id),
    foreign key (owner_id) references Users(user_id) on delete cascade,
    foreign key (player_id) references Player(player_id) on delete cascade
);

create table if not exists VideoAnalysis(
	analysis_id int primary key references Analysis(analysis_id),
    video_path varchar(256)
);

create table if not exists MatchBasedAnalysis(
	matchanalysis_id int primary key references Analysis(analysis_id),
    position_played varchar(3),
    match_id int not null,
    foreign key (match_id) references Matches(match_id)
);

create table if not exists StadiumOwner(
	team_name varchar(50) unique references Team(team_fullname) on delete cascade,
	stadium varchar(100) references Stadium(stadium_name) on delete cascade,
    primary key (team_name)
);

create table if not exists plays_in(
	player_id int not null,
    team varchar(50) not null,
    contract_start date not null,
    contract_end date not null,
    primary key(player_id, contract_start,contract_end),
    foreign key (player_id) references Player(player_id) on delete cascade,
    foreign key (team) references Team(team_fullname) on delete cascade
);

create table if not exists MissionAssigning(
	user_id int references Users(user_id) on delete cascade,
    mission_id int references ScoutMission(mission_id) on delete cascade,
    primary key (mission_id)
);
