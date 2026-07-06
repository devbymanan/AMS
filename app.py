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


def AMS_connection():
    conn = pyodbc.connect(
        f"DRIVER={AMS_DB_DRIVER};"
        f"SERVER={AMS_DB_SERVER};"
        f"DATABASE={AMS_DB_NAME};"
        f"UID={AMS_DB_USER};"
        f"PWD={AMS_DB_PASSWORD}"
    )
    return conn



@app.route('/')
def dashboard():
    conn = None
    total_employees = 0
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM personnel_employee")
        total_employees = cursor.fetchone()[0]
        print(total_employees)
    except Exception as e:
        print(f"Error fetching total employees: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('dashboard.html',total_employees=total_employees)


@app.route('/employees')
def employees():
    conn=None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT
                            p.id AS EmployeeID,

                            CONCAT(
                                p.first_name,
                                CASE
                                    WHEN p.last_name IS NULL OR p.last_name = ''
                                    THEN ''
                                    ELSE ' ' + p.last_name
                                END
                            ) AS FullName,

                            p.email AS Email,

                            p.emp_code AS ZKBioEmployeeID,

                            e.ShiftID,

                            s.ShiftName

                        FROM personnel_employee p

                        LEFT JOIN EmployeeShiftAssignments e
                            ON p.id = e.EmployeeID

                        LEFT JOIN Shift s
                            ON s.ShiftID = e.ShiftID

                        ORDER BY p.id;
                        """)
        employees = cursor.fetchall()
        print(employees)
    except Exception as e:
        print(f"Error fetching employees: {e}")
        employees = []
    finally:
        if conn:
            conn.close()
    return render_template('employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    conn = None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        EmployeeCode=request.form.get('employee_code')
        CardNumber=request.form.get('card_number')
        FirstName=request.form.get('first_name')
        LastName=request.form.get('last_name')
        NickName=request.form.get('nick_name')
        Gender=request.form.get('gender')
        DateOfBirth=request.form.get('date_of_birth')
        CNIC=request.form.get('cnic')
        Passport=request.form.get('passport')
        Nationality=request.form.get('nationality')
        Religion=request.form.get('religion')
        Photo=request.form.get('photo')
        
        
        Mobile=request.form.get('mobile')
        OfficePhone=request.form.get('office_phone')
        Email=request.form.get('email')
        City=request.form.get('city')
        Address=request.form.get('address')
        PostalCode=request.form.get('postal_code')
        HireDate=request.form.get('hire_date')
        EmploymentType=request.form.get('employment_type')
        DepartmentID=request.form.get('department_id')
        PositionID=request.form.get('position_id')
        CompanyID=request.form.get('company_id')
        SupervisorID=request.form.get('supervisor_id')
        Status=request.form.get('status')
        DevicePassword=request.form.get('device_password')
        DeviceSerialNumber=request.form.get('device_serial_number')
        cursor.execute("INSERT INTO employees (EmployeeCode, CardNumber, FirstName, LastName, NickName, Gender, DateOfBirth, CNIC, Passport, Nationality, Religion, Photo, Mobile, OfficePhone, Email, City, Address, PostalCode, HireDate, EmploymentType, DepartmentID, PositionID, CompanyID, SupervisorID, Status, DevicePassword, DeviceSerialNumber) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (EmployeeCode, CardNumber, FirstName, LastName, NickName, Gender, DateOfBirth, CNIC, Passport, Nationality, Religion, Photo, Mobile, OfficePhone, Email, City, Address, PostalCode, HireDate, EmploymentType, DepartmentID, PositionID, CompanyID, SupervisorID, Status, DevicePassword, DeviceSerialNumber))
        conn.commit()
    except Exception as e:
        print(f"Error adding employee: {e}")

    finally:
        if conn:
            conn.close()
    return render_template('add_employee.html')

@app.route('/update_employee_shift', methods=['POST'])
def update_employee_shift():
    emp_id = request.form.get('emp_id')
    new_shift = request.form.get('new_shift')

    if emp_id and new_shift:
        conn = None
        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE personnel_employee SET shift = ? WHERE id = ?", (new_shift, emp_id))
            conn.commit()
        except Exception as e:
            print(f"Error updating employee shift: {e}")
        finally:
            if conn:
                conn.close()

    return redirect(url_for('employees'))

@app.route('/shifts')
def shifts():
    conn=None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shift")
        shifts = cursor.fetchall()
        print(shifts)
    except Exception as e:
        print(f"Error fetching shifts: {e}")
        shifts = []
    finally:
        if conn:
            conn.close()
    return render_template('shifts.html', shifts=shifts)

@app.route('/add_shift', methods=['GET', 'POST'])
def add_shift():
    conn=None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        shift_name = request.form.get('shift_name')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        grace_period = request.form.get('grace_period')
        working_hours = request.form.get('working_hours')
        cursor.execute("INSERT INTO shift (ShiftName, StartTime, EndTime, GracePeriod, WorkingHours) VALUES (?, ?, ?, ?, ?)", (shift_name, start_time, end_time, grace_period, working_hours))
        conn.commit()
        shifts = cursor.fetchall()
        print(shifts)
    except Exception as e:
        print(f"Error adding shift: {e}")
        shifts = []
    finally:
        if conn:
            conn.close()
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
