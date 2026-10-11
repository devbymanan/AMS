from flask import Blueprint, render_template
from models.models import Employee, Attendance, Report, Shift
from extensions import db
from datetime import datetime

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    total_employees = 0
    present_today = 0
    late_today = 0
    absent_today = 0
    recent_punches = []
    shift_breakdown = []
    today_date = datetime.today().strftime("%A, %B %d, %Y")
    today_obj = datetime.today().date()

    try:
        total_employees = Employee.query.filter_by(Status=True).count()

        # Present today
        present_today = (
            db.session.query(Attendance.EmployeeID)
            .filter(db.cast(Attendance.PunchTime, db.Date) == today_obj)
            .distinct()
            .count()
        )

        # Late today
        late_today = Report.query.filter_by(
            AttendanceDate=today_obj, Status="Late"
        ).count()

        absent_today = max(total_employees - present_today, 0)

        # Recent punches
        punches = (
            db.session.query(
                Employee.FirstName,
                Employee.LastName,
                Attendance.PunchTime,
                Report.CheckIn,
            )
            .join(Employee, Employee.EmployeeCode == Attendance.EmployeeID)
            .outerjoin(
                Report,
                (Report.EmployeeID == Employee.EmployeeID)
                & (Report.AttendanceDate == today_obj),
            )
            .order_by(Attendance.PunchTime.desc())
            .limit(8)
            .all()
        )

        for punch in punches:
            name = f"{punch.FirstName} {punch.LastName or ''}".strip()
            punch_time_obj = punch.PunchTime
            p_time_str = punch_time_obj.strftime("%I:%M %p")

            # Type logic
            if punch.CheckIn and punch_time_obj.time() == punch.CheckIn:
                p_type = "Check In"
            else:
                p_type = "Check Out"

            recent_punches.append({"name": name, "time": p_time_str, "type": p_type})

        # Shift breakdown
        shifts = Shift.query.all()
        colors = [
            "bg-brand-600",
            "bg-amber-500",
            "bg-slate-700",
            "bg-emerald-600",
            "bg-rose-500",
        ]

        for i, shift in enumerate(shifts):
            emp_count = Employee.query.filter_by(
                ShiftID=shift.ShiftID, Status=True
            ).count()
            shift_breakdown.append(
                {
                    "name": shift.ShiftName,
                    "count": emp_count,
                    "total": total_employees or 1,
                    "color": colors[i % len(colors)],
                }
            )

    except Exception as e:
        print(f"Error loading dashboard: {e}")

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        today_date=today_date,
        total_employees=total_employees,
        present_today=present_today,
        late_today=late_today,
        absent_today=absent_today,
        recent_punches=recent_punches,
        shift_breakdown=shift_breakdown,
    )
