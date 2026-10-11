import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

AMS_DB_DRIVER = os.getenv("AMS_DB_DRIVER", "ODBC Driver 17 for SQL Server")
AMS_DB_SERVER = os.getenv("AMS_DB_SERVER", "localhost")
AMS_DB_NAME = os.getenv("AMS_DB_NAME", "AttendanceManagementSystem")
AMS_DB_USER = os.getenv("AMS_DB_USER", "sa")
AMS_DB_PASSWORD = os.getenv("AMS_DB_PASSWORD", "")


def AMS_connection():
    conn = pyodbc.connect(
        f"DRIVER={{{AMS_DB_DRIVER}}};"
        f"SERVER={AMS_DB_SERVER};"
        f"DATABASE={AMS_DB_NAME};"
        f"UID={AMS_DB_USER};"
        f"PWD={AMS_DB_PASSWORD}"
    )
    return conn


def fetch_all_dicts(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
