from flask import Flask, abort, render_template, request, redirect, url_for
from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)


def fetch_all_dicts(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

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
    return render_template('dashboard.html', active_page='dashboard', total_employees=total_employees)


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
                s.ShiftName,
                p.PositionName
            FROM employees e
            LEFT JOIN Shift s ON s.ShiftID = e.ShiftID
            LEFT JOIN Positions p ON p.PositionID = e.PositionID
            ORDER BY e.EmployeeID;
        """)
        employees = fetch_all_dicts(cursor)

        cursor.execute("SELECT * FROM Shift ORDER BY ShiftName")
        shifts = fetch_all_dicts(cursor)
    except Exception as e:
        print(f"Error fetching employees: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('employees.html', active_page='employees', employees=employees, shifts=shifts)




@app.route('/view_employee/<int:employee_id>')
def view_employee(employee_id):
    conn = None
    attendance = []
    employee = {}

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
                d.DepartmentName,
                e.PositionID,
                p.PositionName,
                e.SupervisorID,
                CONCAT(ISNULL(sp.FirstName, ''), ' ', ISNULL(sp.LastName, '')) AS SupervisorName,
                e.Status,
                e.DevicePassword,
                e.DeviceSerialNumber,
                e.ShiftID,
                s.ShiftName,
                s.StartTime,
                s.EndTime
            FROM employees e
            LEFT JOIN Shift s ON s.ShiftID = e.ShiftID
            LEFT JOIN Department d ON d.DepartmentID = e.DepartmentID
            LEFT JOIN Positions p ON p.PositionID = e.PositionID
            LEFT JOIN employees sp ON sp.EmployeeID = e.SupervisorID
            WHERE e.EmployeeID = ?
        """, (employee_id,))
        row = cursor.fetchone()

        if not row:
            abort(404)

        columns = [col[0] for col in cursor.description]
        employee = {key: (value if value is not None else "") for key, value in zip(columns, row)}
        employee["FirstInitial"] = (employee.get("FirstName") or "")[:1]
        employee["LastInitial"] = (employee.get("LastName") or "")[:1]

        cursor.execute(
            "SELECT AttendanceDate, CheckIn, CheckOut, LateMinutes, Status FROM Report WHERE EmployeeID = ? ORDER BY AttendanceDate DESC",
            (employee_id,),
        )
        attendance = fetch_all_dicts(cursor)

        if not attendance:
            cursor.execute("""
                SELECT
                    CAST(a.PunchTime AS DATE) AS AttendanceDate,
                    CAST(a.PunchTime AS TIME) AS CheckIn,
                    NULL AS CheckOut,
                    0 AS LateMinutes,
                    'Device' AS Status,
                    COALESCE(d.DeviceName, rt.terminal_alias) AS DeviceName
                FROM Attendance a
                LEFT JOIN RawTransactions rt ON rt.id = a.ZKBioTransactionID
                LEFT JOIN Device d ON d.SerialNumber = rt.terminal_sn
                WHERE a.EmployeeID = ?
                ORDER BY a.PunchTime DESC
            """, (employee_id,))
            attendance = fetch_all_dicts(cursor)
    except Exception as e:
        print("Error fetching employee:", e)
        abort(500)
    finally:
        if conn:
            conn.close()

    return render_template('view_employee.html', active_page='employees', employee=employee, attendance=attendance)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    conn = None
    departments = []
    positions = []
    shifts = []
    supervisors = []
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Department ORDER BY DepartmentName")
        departments = fetch_all_dicts(cursor)

        cursor.execute("SELECT * FROM Positions ORDER BY PositionName")
        positions = fetch_all_dicts(cursor)
        
        cursor.execute("SELECT * FROM Shift ORDER BY ShiftName")
        shifts = fetch_all_dicts(cursor)

        cursor.execute("SELECT EmployeeID, FirstName, LastName FROM employees ORDER BY FirstName")
        supervisor_rows = fetch_all_dicts(cursor)
        supervisors = [
            {
                **sup,
                'FullName': f"{sup.get('FirstName', '')} {sup.get('LastName', '')}".strip(),
            }
            for sup in supervisor_rows
        ]

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
            PhotoPath = ""

            photo_file = request.files.get('photo')
            if photo_file and photo_file.filename:
                filename = secure_filename(photo_file.filename)
                upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                photo_file.save(os.path.join(upload_dir, filename))
                PhotoPath = f"/static/uploads/{filename}"

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
            Status = 1 if request.form.get('status') else 0
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
            """, (
                EmployeeCode,
                CardNumber,
                FirstName,
                LastName,
                NickName,
                Gender,
                DateOfBirth,
                CNIC,
                Passport,
                Nationality,
                Religion,
                PhotoPath,
                Mobile,
                OfficePhone,
                Email,
                City,
                Address,
                PostalCode,
                HireDate,
                EmploymentType,
                DepartmentID,
                PositionID,
                ShiftID,
                SupervisorID,
                Status,
                DevicePassword,
                DeviceSerialNumber,
            ))
            conn.commit()
            return redirect(url_for('employees'))
    except Exception as e:
        print(f"Error adding employee: {e}")
    finally:
        if conn:
            conn.close()

    return render_template(
        'add_employee.html',
        active_page='employees',
        departments=departments,
        positions=positions,
        shifts=shifts,
        supervisors=supervisors,
    )

@app.route('/update_employee_shift', methods=['POST'])
def update_employee_shift():
    employee_id = request.form.get('employee_id')
    shift_id = request.form.get('shift_id')

    if employee_id and shift_id:
        conn = None
        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE employees SET ShiftID = ? WHERE EmployeeID = ?",
                (shift_id, employee_id),
            )
            conn.commit()
        except Exception as e:
            print(f"Error updating employee shift: {e}")
        finally:
            if conn:
                conn.close()

    return redirect(url_for('employees'))


@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    conn = None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE EmployeeID = ?", (employee_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting employee: {e}")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('employees'))

@app.route('/shifts')
def shifts():
    conn = None
    shifts = []
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                s.ShiftID,
                s.ShiftName,
                s.StartTime,
                s.EndTime,
                s.GracePeriod,
                s.WorkingHours,
                COUNT(e.EmployeeID) AS EmployeeCount
            FROM Shift s
            LEFT JOIN employees e ON e.ShiftID = s.ShiftID
            GROUP BY
                s.ShiftID,
                s.ShiftName,
                s.StartTime,
                s.EndTime,
                s.GracePeriod,
                s.WorkingHours
            ORDER BY s.ShiftName
        """)
        shifts = fetch_all_dicts(cursor)
    except Exception as e:
        print(f"Error fetching shifts: {e}")
        shifts = []
    finally:
        if conn:
            conn.close()
    return render_template('shifts.html', active_page='shifts', shifts=shifts)


@app.route('/add_shift', methods=['POST'])
def add_shift():
    conn = None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        shift_name = request.form.get('shift_name')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        grace_period = request.form.get('grace_period') or 0
        working_hours = request.form.get('working_hours') or 0
        cursor.execute(
            "INSERT INTO Shift (ShiftName, StartTime, EndTime, GracePeriod, WorkingHours) VALUES (?, ?, ?, ?, ?)",
            (shift_name, start_time, end_time, grace_period, working_hours),
        )
        conn.commit()
    except Exception as e:
        print(f"Error adding shift: {e}")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('shifts'))

@app.route('/delete_shift/<int:shift_id>', methods=['POST'])
def delete_shift(shift_id):
    conn = None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Shift WHERE ShiftID = ?",
            (shift_id,)
        )

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error deleting shift: {e}")

    finally:
        if conn:
            conn.close()

    return redirect(url_for('shifts'))

@app.route('/edit_shift/<int:shift_id>', methods=['GET', 'POST'])
def edit_shift(shift_id):
    conn = None
    shift = {}

    if request.method == 'POST':
        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            shift_name = request.form.get('shift_name')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            grace_period = request.form.get('grace_period') or 0
            working_hours = request.form.get('working_hours') or 0

            cursor.execute(
                "UPDATE Shift SET ShiftName = ?, StartTime = ?, EndTime = ?, GracePeriod = ?, WorkingHours = ? WHERE ShiftID = ?",
                (shift_name, start_time, end_time, grace_period, working_hours, shift_id),
            )
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error editing shift: {e}")
        finally:
            if conn:
                conn.close()

        return redirect(url_for('shifts'))

    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Shift WHERE ShiftID = ?", (shift_id,))
        row = cursor.fetchone()
        if not row:
            abort(404)
        columns = [col[0] for col in cursor.description]
        shift = {key: value for key, value in zip(columns, row)}
    except Exception as e:
        print(f"Error fetching shift details: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

    return render_template('edit_shift.html', active_page='shifts', shift=shift)


@app.route('/devices')
def devices():
    conn = None
    devices = []
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                d.DeviceID, d.DeviceName, d.SerialNumber, d.DeviceType, d.IPAddress,
                d.Port, d.Location, d.Model, d.Status, d.Notes, d.CreatedAt,
                rt.PunchCount, rt.LastSeen
            FROM Device d
            OUTER APPLY (
                SELECT COUNT(*) AS PunchCount, MAX(punch_time) AS LastSeen
                FROM RawTransactions
                WHERE terminal_sn = d.SerialNumber
            ) rt
            ORDER BY d.DeviceName
        """)
        devices = fetch_all_dicts(cursor)
    except Exception as e:
        print(f"Error fetching devices: {e}")
        devices = []
    finally:
        if conn:
            conn.close()
    return render_template('devices.html', active_page='devices', devices=devices)


@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    conn = None
    if request.method == 'POST':
        device_name = request.form.get('device_name')
        serial_number = request.form.get('serial_number')
        device_type = request.form.get('device_type')
        ip_address = request.form.get('ip_address')
        port = request.form.get('port') or None
        location = request.form.get('location')
        model = request.form.get('model')
        status = 1 if request.form.get('status') else 0
        notes = request.form.get('notes')

        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Device (
                    DeviceName, SerialNumber, DeviceType, IPAddress,
                    Port, Location, Model, Status, Notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_name, serial_number, device_type, ip_address,
                port, location, model, status, notes,
            ))
            conn.commit()
            return redirect(url_for('devices'))
        except Exception as e:
            print(f"Error adding device: {e}")
        finally:
            if conn:
                conn.close()

    return render_template('add_device.html', active_page='devices')


@app.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    conn = None
    device = {}

    if request.method == 'POST':
        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            device_name = request.form.get('device_name')
            serial_number = request.form.get('serial_number')
            device_type = request.form.get('device_type')
            ip_address = request.form.get('ip_address')
            port = request.form.get('port') or None
            location = request.form.get('location')
            model = request.form.get('model')
            status = 1 if request.form.get('status') else 0
            notes = request.form.get('notes')

            cursor.execute("""
                UPDATE Device
                SET DeviceName = ?, SerialNumber = ?, DeviceType = ?, IPAddress = ?,
                    Port = ?, Location = ?, Model = ?, Status = ?, Notes = ?
                WHERE DeviceID = ?
            """, (
                device_name, serial_number, device_type, ip_address,
                port, location, model, status, notes, device_id,
            ))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error editing device: {e}")
        finally:
            if conn:
                conn.close()

        return redirect(url_for('devices'))

    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Device WHERE DeviceID = ?", (device_id,))
        row = cursor.fetchone()
        if not row:
            abort(404)
        columns = [col[0] for col in cursor.description]
        device = {key: value for key, value in zip(columns, row)}
    except Exception as e:
        print(f"Error fetching device details: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

    return render_template('edit_device.html', active_page='devices', device=device)


@app.route('/delete_device/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    conn = None
    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Device WHERE DeviceID = ?", (device_id,))
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error deleting device: {e}")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('devices'))


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = None
    attendance_records = []
    employees = []
    total_records = 0
    selected_date = request.args.get('selected_date') or datetime.today().strftime('%Y-%m-%d')
    selected_employee_id = request.args.get('employee_id')
    last_sync_time = None

    try:
        conn = AMS_connection()
        cursor = conn.cursor()

        attendance_query = """
                                SELECT
                                    a.AttendanceID,
                                    CONCAT(e.FirstName, ' ', e.LastName) AS FullName,
                                    a.PunchTime,
                                    a.ZKBioTransactionID,
                                    a.EmployeeID,
                                    a.Source AS source,
                                    COALESCE(d.DeviceName, rt.terminal_alias) AS DeviceName,
                                    d.Location AS DeviceLocation
                                FROM Attendance a
                                LEFT JOIN Employees e
                                    ON e.EmployeeID = a.EmployeeID
                                LEFT JOIN RawTransactions rt
                                    ON rt.id = a.ZKBioTransactionID
                                LEFT JOIN Device d
                                    ON d.SerialNumber = rt.terminal_sn
                                WHERE CAST(a.PunchTime AS DATE) = ?
                            """
        params = [selected_date]

        if selected_employee_id:
            attendance_query += " AND a.EmployeeID = ?"
            params.append(selected_employee_id)

        attendance_query += " ORDER BY a.PunchTime DESC"
        cursor.execute(attendance_query, tuple(params))
        attendance_records = fetch_all_dicts(cursor)

        cursor.execute(
            "SELECT EmployeeID, CONCAT(FirstName, ' ', LastName) AS FullName FROM employees ORDER BY FirstName"
        )
        employees = fetch_all_dicts(cursor)

        count_query = "SELECT COUNT(*) FROM Attendance WHERE CAST(PunchTime AS DATE) = ?"
        count_params = [selected_date]
        if selected_employee_id:
            count_query += " AND EmployeeID = ?"
            count_params.append(selected_employee_id)
        cursor.execute(count_query, tuple(count_params))
        total_records = cursor.fetchone()[0] or 0
        
        
        cursor.execute("""
                    SELECT
                        EmployeeID,
                        CONCAT(FirstName, ' ', LastName) AS FullName
                    FROM Employees
                    WHERE Status = 1
                    ORDER BY FirstName, LastName
                """)

        rows = cursor.fetchall()

        employees = []

        for row in rows:
            employees.append({
                'EmployeeID': row.EmployeeID,
                'FullName': row.FullName
            })

        # cursor.execute("SELECT MAX(sync_time) FROM SyncLog")
        # sync_row = cursor.fetchone()
        # if sync_row:
        #     last_sync = sync_row[0]
        #     if last_sync:
        #         last_sync_time = last_sync.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error fetching attendance records: {e}")
        attendance_records = []
        employees = []
        total_records = 0
        last_sync_time = None
    finally:
        if conn:
            conn.close()

    return render_template(
        'attendance.html',
        active_page='attendance',
        attendance_records=attendance_records,
        employees=employees,
        selected_date=selected_date,
        selected_employee_id=selected_employee_id,
        total_records=total_records,
        last_sync_time=last_sync_time,
    )


@app.route('/add_attendance', methods=['POST'])
def add_attendance():
    employee_id = request.form.get('employee_id')
    punch_time = datetime.strptime(
    request.form['punch_time'],
    '%Y-%m-%dT%H:%M'
)

    if employee_id and punch_time:
        conn = None
        try:
            conn = AMS_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Attendance (EmployeeID, PunchTime) VALUES (?, ?)",
                (employee_id, punch_time),
            )
            conn.commit()
        except Exception as e:
            print(f"Error adding attendance entry: {e}")
        finally:
            if conn:
                conn.close()

    return redirect(url_for('attendance'))


@app.route('/reports')
def reports():
    conn = None
    report_records = []
    shifts = []
    selected_date = request.args.get('selected_date') or datetime.today().strftime('%Y-%m-%d')
    selected_shift_id = request.args.get('shift_id')
    selected_status = request.args.get('status')
    total_report_records = 0

    try:
        conn = AMS_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ShiftID, ShiftName FROM Shift ORDER BY ShiftName"
        )
        shifts = fetch_all_dicts(cursor)

        report_query = """
            SELECT
                COALESCE(e.FullName, CONCAT(e.FirstName, ' ', e.LastName)) AS FullName,
                r.AttendanceDate,
                s.ShiftName,
                r.CheckIn,
                r.CheckOut,
                r.WorkingHours,
                r.LateMinutes,
                r.OvertimeHours,
                r.Status
            FROM Report r
            LEFT JOIN employees e ON e.EmployeeID = r.EmployeeID
            LEFT JOIN Shift s ON s.ShiftID = r.ShiftID
            WHERE CAST(r.AttendanceDate AS DATE) = ?
        """
        params = [selected_date]

        if selected_shift_id:
            report_query += " AND r.ShiftID = ?"
            params.append(selected_shift_id)

        if selected_status:
            report_query += " AND r.Status = ?"
            params.append(selected_status)

        report_query += " ORDER BY r.AttendanceDate DESC"
        cursor.execute(report_query, tuple(params))
        report_records = fetch_all_dicts(cursor)
        total_report_records = len(report_records)
    except Exception as e:
        print(f"Error fetching reports: {e}")
        report_records = []
        shifts = []
        total_report_records = 0
    finally:
        if conn:
            conn.close()

    return render_template(
        'reports.html',
        active_page='reports',
        report_records=report_records,
        shifts=shifts,
        selected_date=selected_date,
        selected_shift_id=selected_shift_id,
        selected_status=selected_status,
        total_report_records=total_report_records,
    )


if __name__ == "__main__":
    app.run(debug=True)
