import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='soccermatchdb.craqsywqek0z.eu-north-1.rds.amazonaws.com',
        user='admin',
        password='',
        database='SoccerMatch'
    )
