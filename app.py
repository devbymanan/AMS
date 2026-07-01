from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_DRIVER = os.getenv("DB_DRIVER")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def connection():
    conn = pyodbc.connect(
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD}"
    )
    return conn


@app.route('/')
def dashboard():
    return render_template('dashboard.html', active_page='dashboard')


@app.route('/employees')
def employees():
    return render_template('employees.html', active_page='employees')


@app.route('/shifts')
def shifts():
    return render_template('shifts.html', active_page='shifts')


@app.route('/attendance')
def attendance():
    return render_template('attendance.html', active_page='attendance')


@app.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')


if __name__ == "__main__":
    app.run(debug=True)
