# Script to build mysql table

import config
import pymysql

'''
Create_table.py looks for MySQL Config in config.py 
Creates a connection to the database using the supplied config

Creates a TABLE named WEB_URL with the specified rows.
Needs to RUN once when setting up the application on local or
web server.

You need to have a database already defined.
'''
host = config.host
user = config.user
passwrd = config.passwrd
db = config.db
table = config.table_name

create_database = f'''
CREATE DATABASE IF NOT EXISTS {db}
'''

create_table = f'''
CREATE TABLE IF NOT EXISTS {table}
(
    ID             INT AUTO_INCREMENT,
    URL            VARCHAR(512),
    S_URL          VARCHAR(80),
    TAG            VARCHAR(80),
    COUNTER        INT DEFAULT 0,
    CHROME         INT DEFAULT 0,
    FIREFOX        INT DEFAULT 0,
    SAFARI         INT DEFAULT 0,
    OTHER_BROWSER  INT DEFAULT 0,
    ANDROID        INT DEFAULT 0,
    IOS            INT DEFAULT 0,
    WINDOWS        INT DEFAULT 0,
    LINUX          INT DEFAULT 0,
    MAC            INT DEFAULT 0,
    OTHER_PLATFORM INT DEFAULT 0,
    PRIMARY KEY (ID)
);
'''



conn = pymysql.connect(host=host , user=user , password=passwrd)

cursor = conn.cursor()

cursor.execute(create_database)
conn.select_db(db)
cursor.execute(create_table)
conn.close()