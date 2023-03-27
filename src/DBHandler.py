import configparser
import psycopg
import openpyxl

conn = None
cursor = None


def connect():
    # Connect to database
    # Read ini file
    config = configparser.ConfigParser()
    config.read(r'properties.ini')

    # connect to AWS RDS Postgresql
    global conn, cursor
    conn = psycopg.connect(dbname=config['Database']['DATABASE'],
                           host=config['Database']['HOST'],
                           user=config['Database']['USER'],
                           password=config['Database']['PASSWORD'],
                           port=config['Database']['PORT'])
    cursor = conn.cursor()
    conn.autocommit = True
    # cursor.execute("CREATE database projectdb;")


def closeconnection():
    cursor.close()
    conn.close()


def pushdata():
    # Push data from xls to db, only run this to add new data
    connect()
    print("Data being pushed to db")
    dataframe = openpyxl.load_workbook("../data/parking_lot.xlsx")
    dataframe1 = dataframe.active
    for row in dataframe1.iter_rows(values_only=True):
        cursor.execute(
            "INSERT INTO parkinglots(place_id,name,rating, geom) VALUES('" + str(row[3]) + "', '" + str(
                row[2]) + "', " +
            str(row[4]) + ", ST_SetSRID( ST_MakePoint(" + str(row[0]) + ", " + str(row[1]) + "), 4326) );")
    closeconnection()


def getdata():
    # Push data from xls to db
    connect()
    print("Data returned from db")
    cursor.execute("select * from parkinglots;")
    result = cursor.fetchall()
    for row in result:
        print(row)
    closeconnection()
    return result


def getcoordinates():
    # Transform point data from db to latitude and longitude coordinates
    connect()
    cursor.execute("SELECT place_id, ST_X (ST_Transform (geom, 4326)) AS lat, ST_Y (ST_Transform (geom, 4326)) AS "
                   "long FROM parkinglots;")
    result = cursor.fetchall()
    for row in result:
        print(row)
    closeconnection()
    return result
