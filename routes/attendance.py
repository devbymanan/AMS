from flask import Blueprint, render_template, request, redirect, url_for
from models.models import Attendance, Employee
from extensions import db
from datetime import datetime
from sqlalchemy import func

bp = Blueprint("attendance", __name__)


@bp.route("/attendance", methods=["GET", "POST"])
def attendance():
    selected_date = request.args.get("selected_date")
    selected_employee_id = request.args.get("employee_id")

    if not selected_date:
        latest = db.session.query(func.max(Attendance.PunchTime)).scalar()
        if latest:
            selected_date = latest.strftime("%Y-%m-%d")
        else:
            selected_date = datetime.today().strftime("%Y-%m-%d")

    target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    query = (
        db.session.query(
            Attendance.AttendanceID,
            Attendance.PunchTime,
            Attendance.ZKBioTransactionID,
            Attendance.EmployeeID,
            Attendance.Source,
            Employee.FirstName,
            Employee.LastName,
        )
        .outerjoin(Employee, Employee.EmployeeCode == Attendance.EmployeeID)
        .filter(db.cast(Attendance.PunchTime, db.Date) == target_date)
    )

    if selected_employee_id:
        query = query.filter(Attendance.EmployeeID == selected_employee_id)

    records = query.order_by(Attendance.PunchTime.desc()).all()

    attendance_records = []
    for r in records:
        full_name = (
            f"{r.FirstName} {r.LastName or ''}".strip()
            if r.FirstName
            else "Unknown Employee"
        )
        attendance_records.append(
            {
                "AttendanceID": r.AttendanceID,
                "FullName": full_name,
                "PunchTime": r.PunchTime,
                "ZKBioTransactionID": r.ZKBioTransactionID,
                "EmployeeID": r.EmployeeID,
                "source": r.Source,
            }
        )

    total_records = len(attendance_records)

    emps = Employee.query.filter_by(Status=True).order_by(Employee.FirstName).all()
    employees = [
        {
            "EmployeeID": e.EmployeeID,
            "EmployeeCode": e.EmployeeCode,
            "FullName": f"{e.FirstName} {e.LastName or ''}".strip(),
        }
        for e in emps
    ]

    latest_sync = db.session.query(func.max(Attendance.PunchTime)).scalar()
    last_sync_time = latest_sync.strftime("%Y-%m-%d %H:%M:%S") if latest_sync else None

    return render_template(
        "attendance.html",
        active_page="attendance",
        attendance_records=attendance_records,
        employees=employees,
        selected_date=selected_date,
        selected_employee_id=selected_employee_id,
        total_records=total_records,
        last_sync_time=last_sync_time,
    )


@bp.route("/add_attendance", methods=["POST"])
def add_attendance():
    employee_id = request.form.get("employee_id")
    punch_time_str = request.form.get("punch_time")

    if employee_id and punch_time_str:
        punch_time = datetime.strptime(punch_time_str, "%Y-%m-%dT%H:%M")
        new_att = Attendance(
            EmployeeID=employee_id, PunchTime=punch_time, Source="Manual"
        )
        db.session.add(new_att)
        db.session.commit()

    return redirect(url_for("attendance.attendance"))
