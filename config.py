import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    AMS_DB_DRIVER = os.getenv("AMS_DB_DRIVER", "ODBC Driver 17 for SQL Server")
    AMS_DB_SERVER = os.getenv("AMS_DB_SERVER", "localhost")
    AMS_DB_NAME = os.getenv("AMS_DB_NAME", "AttendanceManagementSystem")
    AMS_DB_USER = os.getenv("AMS_DB_USER", "sa")
    AMS_DB_PASSWORD = os.getenv("AMS_DB_PASSWORD", "")

    # Configure SQLAlchemy URI for pyodbc
    params = urllib.parse.quote_plus(
        f"DRIVER={{{AMS_DB_DRIVER}}};"
        f"SERVER={AMS_DB_SERVER};"
        f"DATABASE={AMS_DB_NAME};"
        f"UID={AMS_DB_USER};"
        f"PWD={AMS_DB_PASSWORD}"
    )
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
