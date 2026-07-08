from flask import Flask, abort, render_template, request, redirect, url_for
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
        cursor.execute("SELECT COUNT(*) FROM employees")
        total_employees = cursor.fetchone()[0]
    except Exception as e:
        print(f"Error fetching total employees: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('dashboard.html',total_employees=total_employees)


@app.route('/employees')
def employees():
    conn = None
    employees = []
    shifts = []
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.EmployeeID,
                CONCAT(
                    e.FirstName,
                    CASE
                        WHEN e.LastName IS NULL OR e.LastName = ''
                        THEN ''
                        ELSE ' ' + e.LastName
                    END
                ) AS FullName,
                e.Email AS Email,
                e.EmployeeCode AS ZKBioEmployeeID,
                e.ShiftID,
                s.ShiftName
            FROM employees e
            LEFT JOIN Shift s
                ON s.ShiftID = e.ShiftID
            ORDER BY e.EmployeeID;
        """)
        employee_rows = cursor.fetchall()
        employee_columns = [col[0] for col in cursor.description]
        employees = [dict(zip(employee_columns, row)) for row in employee_rows]

        cursor.execute("SELECT * FROM Shift")
        shift_rows = cursor.fetchall()
        shift_columns = [col[0] for col in cursor.description]
        shifts = [dict(zip(shift_columns, row)) for row in shift_rows]
    except Exception as e:
        print(f"Error fetching employees: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('employees.html', employees=employees, shifts=shifts)




@app.route('/view_employee/<int:employee_id>')
def view_employee(employee_id):
    conn = None
    attendance = []

    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.EmployeeID,
                e.EmployeeCode,
                e.CardNumber,
                e.FirstName,
                e.LastName,
                e.NickName,
                e.Gender,
                e.DateOfBirth,
                e.CNIC,
                e.Passport,
                e.Nationality,
                e.Religion,
                e.Photo AS PhotoPath,
                e.Mobile,
                e.OfficePhone,
                e.Email,
                e.City,
                e.Address,
                e.PostalCode,
                e.HireDate,
                e.EmploymentType,
                e.DepartmentID,
                e.PositionID,
                e.SupervisorID,
                e.Status,
                e.DevicePassword,
                e.DeviceSerialNumber,
                e.ShiftID,
                s.ShiftName,
                s.StartTime,
                s.EndTime
            FROM employees e
            LEFT JOIN Shift s
                ON s.ShiftID = e.ShiftID
            WHERE e.EmployeeID = ?
        """, employee_id)
        row = cursor.fetchone()

        if not row:
            abort(404)

        columns = [col[0] for col in cursor.description]
        employee = {key: (value if value is not None else "") for key, value in zip(columns, row)}
        employee.setdefault("DepartmentName", "")
        employee.setdefault("PositionName", "")
        employee.setdefault("CompanyName", "")
        employee.setdefault("SupervisorName", "")
        employee["FirstInitial"] = (employee.get("FirstName") or "")[:1]
        employee["LastInitial"] = (employee.get("LastName") or "")[:1]
    except Exception as e:
        print("Error fetching employee:", e)
        abort(500)
    finally:
        if conn:
            conn.close()

    return render_template('view_employee.html', employee=employee, attendance=attendance)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    conn = None
    departments = []
    positions = []
    shifts = []
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Department")
        departments = cursor.fetchall()

        cursor.execute("SELECT * FROM Positions")
        positions = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Shift")
        shifts = cursor.fetchall()

        if request.method == 'POST':
            EmployeeCode = request.form.get('employee_code')
            CardNumber = request.form.get('card_number')
            FirstName = request.form.get('first_name')
            LastName = request.form.get('last_name')
            NickName = request.form.get('nick_name')
            Gender = request.form.get('gender')
            DateOfBirth = request.form.get('date_of_birth')
            CNIC = request.form.get('cnic')
            Passport = request.form.get('passport')
            Nationality = request.form.get('nationality')
            Religion = request.form.get('religion')
            Photo = request.form.get('photo')

            Mobile = request.form.get('mobile')
            OfficePhone = request.form.get('office_phone')
            Email = request.form.get('email')
            City = request.form.get('city')
            Address = request.form.get('address')
            PostalCode = request.form.get('postal_code')
            HireDate = request.form.get('hire_date')
            EmploymentType = request.form.get('employment_type')

            DepartmentID = request.form.get('department_id')
            PositionID = request.form.get('position_id')
            ShiftID = request.form.get('shift_id')
            SupervisorID = request.form.get('supervisor_id')
            Status = request.form.get('status')
            DevicePassword = request.form.get('device_password')
            DeviceSerialNumber = request.form.get('device_serial_number')

            cursor.execute("""
                INSERT INTO employees (
                    EmployeeCode, CardNumber, FirstName, LastName, NickName, Gender,
                    DateOfBirth, CNIC, Passport, Nationality, Religion, Photo,
                    Mobile, OfficePhone, Email, City, Address, PostalCode,
                    HireDate, EmploymentType, DepartmentID, PositionID,
                    ShiftID, SupervisorID, Status, DevicePassword, DeviceSerialNumber
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (EmployeeCode, CardNumber, FirstName, LastName, NickName, Gender,
                  DateOfBirth, CNIC, Passport, Nationality, Religion, Photo,
                  Mobile, OfficePhone, Email, City, Address, PostalCode,
                  HireDate, EmploymentType, DepartmentID, PositionID,
                  ShiftID, SupervisorID, Status, DevicePassword, DeviceSerialNumber))
            conn.commit()

            return redirect(url_for('employees'))  

    except Exception as e:
        print(f"Error adding employee: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('add_employee.html', departments=departments, positions=positions, shifts=shifts)

@app.route('/update_employee_shift', methods=['POST'])
def update_employee_shift():
    employee_id = request.form.get('employee_id')
    shift_id = request.form.get('shift_id')

    if employee_id and shift_id:
        conn = None
        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM EmployeeShiftAssignments WHERE EmployeeID = ?", employee_id)
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE EmployeeShiftAssignments SET ShiftID = ? WHERE EmployeeID = ?",
                    (shift_id, employee_id),
                )
            else:
                cursor.execute(
                    "INSERT INTO EmployeeShiftAssignments (EmployeeID, ShiftID) VALUES (?, ?)",
                    (employee_id, shift_id),
                )
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

@app.route('/add_attendance', methods=['GET','POST'])
def add_attendance():
    return redirect(url_for('attendance'))


@app.route('/reports')
def reports():
    return render_template('reports.html')


if __name__ == "__main__":
    app.run(debug=True)
