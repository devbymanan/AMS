from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

AMS_DB_DRIVER = os.getenv("AMS_DB_DRIVER")
AMS_DB_SERVER = os.getenv("AMS_DB_SERVER")
AMS_DB_NAME = os.getenv("AMS_DB_NAME")
AMS_DB_USER = os.getenv("AMS_DB_USER")
AMS_DB_PASSWORD = os.getenv("AMS_DB_PASSWORD")


ZK_DB_DRIVER = os.getenv("ZK_DB_DRIVER")
ZK_DB_SERVER = os.getenv("ZK_DB_SERVER")
ZK_DB_NAME = os.getenv("ZK_DB_NAME")
ZK_DB_USER = os.getenv("ZK_DB_USER")
ZK_DB_PASSWORD = os.getenv("ZK_DB_PASSWORD")


def AMS_connection():
    conn = pyodbc.connect(
        f"DRIVER={AMS_DB_DRIVER};"
        f"SERVER={AMS_DB_SERVER};"
        f"DATABASE={AMS_DB_NAME};"
        f"UID={AMS_DB_USER};"
        f"PWD={AMS_DB_PASSWORD}"
    )
    return conn

def ZK_connection():
    conn = pyodbc.connect(
        f"DRIVER={ZK_DB_DRIVER};"
        f"SERVER={ZK_DB_SERVER};"
        f"DATABASE={ZK_DB_NAME};"
        f"UID={ZK_DB_USER};"
        f"PWD={ZK_DB_PASSWORD}"
    )
    return conn






@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/add_employee')
def add_employee():
    return render_template('employees.html')

@app.route('/shifts')
def shifts():
    return render_template('shifts.html')

@app.route('/add_shift')
def add_shift():
    return render_template('shifts.html')


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn=None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()

    except Exception as e:
        print(f"Error fetching attendance records: {e}")
        attendance_records = []
    finally:
        if conn:
            conn.close()                                                                                
    return render_template('attendance.html')

@app.route('/add_attendance', methods=['GET''POST'])
def add_attendance():
    return redirect(url_for('attendance'))


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == "__main__":
    app.run(debug=True)
