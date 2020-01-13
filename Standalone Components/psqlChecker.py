import psycopg2
import json

print("Starting PSQL check")
with open("db.json", "r") as configjsonFile:
    dbInfo = json.load(configjsonFile)
    configjsonFile.close()
trigger = dbInfo["trigger-file"]
database_name = dbInfo["database-name"]
database_host = dbInfo["database-host"]
database_password = dbInfo["database-password"]
database_user = dbInfo["database-username"]
connect_str = "dbname='" + database_name + "' user='" + database_user \
                              + "'host='" + database_host + "' " + \
                              "password='" + database_password + "'"
try:
    connection = psycopg2.connect(connect_str, connect_timeout=3)
    connection.close()
except psycopg2.OperationalError as ex:
    f = open(trigger, "w+")
    f.write("Uh oh")
    f.close()