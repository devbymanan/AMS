import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models.models import (
    Employee,
    Shift,
    Department,
    Position,
    Attendance,
    Report,
    RawTransaction,
    Device,
)
from extensions import db

bp = Blueprint("employees", __name__)


@bp.route("/employees")
def employees():
    employees_data = (
        db.session.query(Employee, Shift.ShiftName, Position.PositionName)
        .outerjoin(Shift, Shift.ShiftID == Employee.ShiftID)
        .outerjoin(Position, Position.PositionID == Employee.PositionID)
        .order_by(Employee.EmployeeID)
        .all()
    )

    employees_list = []
    for emp, shift_name, pos_name in employees_data:
        full_name = f"{emp.FirstName} {emp.LastName or ''}".strip()
        employees_list.append(
            {
                "EmployeeID": emp.EmployeeID,
                "FullName": full_name,
                "Email": emp.Email,
                "ZKBioEmployeeID": emp.EmployeeCode,
                "ShiftID": emp.ShiftID,
                "ShiftName": shift_name,
                "PositionName": pos_name,
            }
        )

    shifts = Shift.query.order_by(Shift.ShiftName).all()
    shifts_list = [{"ShiftID": s.ShiftID, "ShiftName": s.ShiftName} for s in shifts]

    return render_template(
        "employees.html",
        active_page="employees",
        employees=employees_list,
        shifts=shifts_list,
    )


@bp.route("/view_employee/<int:employee_id>")
def view_employee(employee_id):
    emp = Employee.query.get_or_404(employee_id)

    employee_dict = {
        "EmployeeID": emp.EmployeeID,
        "EmployeeCode": emp.EmployeeCode,
        "CardNumber": emp.CardNumber,
        "FirstName": emp.FirstName,
        "LastName": emp.LastName,
        "NickName": emp.NickName,
        "Gender": emp.Gender,
        "DateOfBirth": emp.DateOfBirth,
        "CNIC": emp.CNIC,
        "Passport": emp.Passport,
        "Nationality": emp.Nationality,
        "Religion": emp.Religion,
        "PhotoPath": emp.Photo,
        "Mobile": emp.Mobile,
        "OfficePhone": emp.OfficePhone,
        "Email": emp.Email,
        "City": emp.City,
        "Address": emp.Address,
        "PostalCode": emp.PostalCode,
        "HireDate": emp.HireDate,
        "EmploymentType": emp.EmploymentType,
        "DepartmentID": emp.DepartmentID,
        "DepartmentName": emp.department.DepartmentName if emp.department else "",
        "PositionID": emp.PositionID,
        "PositionName": emp.position.PositionName if emp.position else "",
        "SupervisorID": emp.SupervisorID,
        "Status": emp.Status,
        "DevicePassword": emp.DevicePassword,
        "DeviceSerialNumber": emp.DeviceSerialNumber,
        "ShiftID": emp.ShiftID,
        "ShiftName": emp.shift.ShiftName if emp.shift else "",
        "StartTime": (
            emp.shift.StartTime.strftime("%H:%M:%S")
            if emp.shift and emp.shift.StartTime
            else ""
        ),
        "EndTime": (
            emp.shift.EndTime.strftime("%H:%M:%S")
            if emp.shift and emp.shift.EndTime
            else ""
        ),
    }

    if emp.SupervisorID:
        sup = Employee.query.get(emp.SupervisorID)
        employee_dict["SupervisorName"] = (
            f"{sup.FirstName} {sup.LastName or ''}".strip() if sup else ""
        )
    else:
        employee_dict["SupervisorName"] = ""

    employee_dict["FirstInitial"] = (emp.FirstName or "")[:1]
    employee_dict["LastInitial"] = (emp.LastName or "")[:1]

    reports = (
        Report.query.filter_by(EmployeeID=employee_id)
        .order_by(Report.AttendanceDate.desc())
        .all()
    )
    attendance_list = []

    if reports:
        for r in reports:
            attendance_list.append(
                {
                    "AttendanceDate": r.AttendanceDate,
                    "CheckIn": r.CheckIn,
                    "CheckOut": r.CheckOut,
                    "LateMinutes": r.LateMinutes,
                    "Status": r.Status,
                }
            )
    else:
        atts = (
            db.session.query(
                Attendance.PunchTime,
                RawTransaction.terminal_sn,
                Device.DeviceName,
                RawTransaction.terminal_alias,
            )
            .outerjoin(
                RawTransaction, RawTransaction.id == Attendance.ZKBioTransactionID
            )
            .outerjoin(Device, Device.SerialNumber == RawTransaction.terminal_sn)
            .filter(Attendance.EmployeeID == emp.EmployeeCode)
            .order_by(Attendance.PunchTime.desc())
            .all()
        )

        for punch, sn, dev_name, alias in atts:
            attendance_list.append(
                {
                    "AttendanceDate": punch.date(),
                    "CheckIn": punch.time(),
                    "CheckOut": None,
                    "LateMinutes": 0,
                    "Status": "Device",
                    "DeviceName": dev_name or alias,
                }
            )

    return render_template(
        "view_employee.html",
        active_page="employees",
        employee=employee_dict,
        attendance=attendance_list,
    )


@bp.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        PhotoPath = ""
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            filename = secure_filename(photo_file.filename)
            upload_dir = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            photo_file.save(os.path.join(upload_dir, filename))
            PhotoPath = f"/static/uploads/{filename}"

        new_emp = Employee(
            EmployeeCode=request.form.get("employee_code"),
            CardNumber=request.form.get("card_number"),
            FirstName=request.form.get("first_name"),
            LastName=request.form.get("last_name"),
            NickName=request.form.get("nick_name"),
            Gender=request.form.get("gender"),
            DateOfBirth=request.form.get("date_of_birth") or None,
            CNIC=request.form.get("cnic"),
            Passport=request.form.get("passport"),
            Nationality=request.form.get("nationality"),
            Religion=request.form.get("religion"),
            Photo=PhotoPath,
            Mobile=request.form.get("mobile"),
            OfficePhone=request.form.get("office_phone"),
            Email=request.form.get("email"),
            City=request.form.get("city"),
            Address=request.form.get("address"),
            PostalCode=request.form.get("postal_code"),
            HireDate=request.form.get("hire_date") or None,
            EmploymentType=request.form.get("employment_type") or None,
            DepartmentID=request.form.get("department_id") or None,
            PositionID=request.form.get("position_id") or None,
            ShiftID=request.form.get("shift_id") or None,
            SupervisorID=request.form.get("supervisor_id") or None,
            Status=bool(request.form.get("status")),
            DevicePassword=request.form.get("device_password"),
            DeviceSerialNumber=request.form.get("device_serial_number"),
        )
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for("employees.employees"))

    departments = [
        {"DepartmentID": d.DepartmentID, "DepartmentName": d.DepartmentName}
        for d in Department.query.order_by(Department.DepartmentName).all()
    ]
    positions = [
        {"PositionID": p.PositionID, "PositionName": p.PositionName}
        for p in Position.query.order_by(Position.PositionName).all()
    ]
    shifts = [
        {"ShiftID": s.ShiftID, "ShiftName": s.ShiftName}
        for s in Shift.query.order_by(Shift.ShiftName).all()
    ]
    supervisors = []
    for emp in Employee.query.order_by(Employee.FirstName).all():
        supervisors.append(
            {
                "EmployeeID": emp.EmployeeID,
                "FullName": f"{emp.FirstName} {emp.LastName or ''}".strip(),
            }
        )

    return render_template(
        "add_employee.html",
        active_page="employees",
        departments=departments,
        positions=positions,
        shifts=shifts,
        supervisors=supervisors,
    )


@bp.route("/update_employee_shift", methods=["POST"])
def update_employee_shift():
    employee_id = request.form.get("employee_id")
    shift_id = request.form.get("shift_id")

    if employee_id and shift_id:
        emp = Employee.query.get(employee_id)
        if emp:
            emp.ShiftID = shift_id
            db.session.commit()

    return redirect(url_for("employees.employees"))


@bp.route("/delete_employee/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    emp = Employee.query.get(employee_id)
    if emp:
        db.session.delete(emp)
        db.session.commit()
    return redirect(url_for("employees.employees"))
