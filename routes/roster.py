from flask import Blueprint, render_template, request, redirect, url_for
from models.models import Roster, RosterAssignment, Shift, Employee, Department
from extensions import db
from datetime import datetime
from sqlalchemy import func

bp = Blueprint("roster", __name__)

WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def is_off_day(date_str, off_days_str):
    if not off_days_str:
        return False
    off_days = {d.strip() for d in off_days_str.split(",") if d.strip()}
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%a") in off_days


@bp.route("/roster", methods=["GET"])
def roster():
    selected_date = request.args.get("selected_date") or datetime.today().strftime(
        "%Y-%m-%d"
    )
    selected_shift_id = request.args.get("shift_id")

    target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    shifts = [
        {"ShiftID": s.ShiftID, "ShiftName": s.ShiftName}
        for s in Shift.query.order_by(Shift.ShiftName).all()
    ]

    emps = Employee.query.filter_by(Status=True).order_by(Employee.FirstName).all()
    employees = [
        {
            "EmployeeID": e.EmployeeID,
            "DepartmentID": e.DepartmentID,
            "FullName": f"{e.FirstName} {e.LastName or ''}".strip(),
        }
        for e in emps
    ]

    deps = (
        Department.query.filter_by(IsActive=True)
        .order_by(Department.DepartmentName)
        .all()
    )
    departments = [
        {"DepartmentID": d.DepartmentID, "DepartmentName": d.DepartmentName}
        for d in deps
    ]

    # Needs a specialized query string_agg which is SQL server specific
    # In SQLAlchemy for SQL server:
    from sqlalchemy.sql.expression import text

    query = (
        db.session.query(
            Roster.RosterID,
            Roster.StartDate,
            Roster.EndDate,
            Roster.OffDays,
            Roster.TeamName,
            Roster.Notes,
            Shift.ShiftID,
            Shift.ShiftName,
            Shift.StartTime,
            Shift.EndTime,
            func.count(RosterAssignment.EmployeeID).label("EmployeeCount"),
            func.string_agg(
                Employee.FirstName + " " + func.isnull(Employee.LastName, ""),
                text("', '"),
            ).label("EmployeeNames"),
        )
        .join(Shift, Shift.ShiftID == Roster.ShiftID)
        .outerjoin(RosterAssignment, RosterAssignment.RosterID == Roster.RosterID)
        .outerjoin(Employee, Employee.EmployeeID == RosterAssignment.EmployeeID)
        .filter(Roster.StartDate <= target_date, Roster.EndDate >= target_date)
    )

    if selected_shift_id:
        query = query.filter(Roster.ShiftID == selected_shift_id)

    roster_data = (
        query.group_by(
            Roster.RosterID,
            Roster.StartDate,
            Roster.EndDate,
            Roster.OffDays,
            Roster.TeamName,
            Roster.Notes,
            Shift.ShiftID,
            Shift.ShiftName,
            Shift.StartTime,
            Shift.EndTime,
        )
        .order_by(Shift.ShiftName, Roster.TeamName)
        .all()
    )

    roster_entries = []
    for r in roster_data:
        roster_entries.append(
            {
                "RosterID": r.RosterID,
                "StartDate": r.StartDate,
                "EndDate": r.EndDate,
                "OffDays": r.OffDays,
                "TeamName": r.TeamName,
                "Notes": r.Notes,
                "ShiftID": r.ShiftID,
                "ShiftName": r.ShiftName,
                "StartTime": r.StartTime,
                "EndTime": r.EndTime,
                "EmployeeCount": r.EmployeeCount,
                "EmployeeNames": r.EmployeeNames,
                "IsOffToday": is_off_day(selected_date, r.OffDays),
            }
        )

    return render_template(
        "roster.html",
        active_page="roster",
        roster_entries=roster_entries,
        shifts=shifts,
        employees=employees,
        departments=departments,
        selected_date=selected_date,
        selected_shift_id=selected_shift_id,
        weekdays=WEEKDAY_ABBR,
    )


@bp.route("/add_roster", methods=["POST"])
def add_roster():
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date") or start_date_str
    shift_id = request.form.get("shift_id")
    team_name = request.form.get("team_name")
    notes = request.form.get("notes")
    off_days = request.form.getlist("off_days")
    employee_ids = request.form.getlist("employee_ids")

    off_days_str = ",".join(off_days) if off_days else None

    if (
        start_date_str
        and end_date_str
        and shift_id
        and employee_ids
        and end_date_str >= start_date_str
    ):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        new_roster = Roster(
            StartDate=start_date,
            EndDate=end_date,
            OffDays=off_days_str,
            ShiftID=shift_id,
            TeamName=team_name,
            Notes=notes,
        )
        db.session.add(new_roster)
        db.session.flush()

        for emp_id in employee_ids:
            assignment = RosterAssignment(
                RosterID=new_roster.RosterID, EmployeeID=emp_id
            )
            db.session.add(assignment)

        db.session.commit()

    return redirect(url_for("roster.roster", selected_date=start_date_str))


@bp.route("/edit_roster/<int:roster_id>", methods=["GET", "POST"])
def edit_roster(roster_id):
    roster_entry = Roster.query.get_or_404(roster_id)

    if request.method == "POST":
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date") or start_date_str

        roster_entry.StartDate = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        roster_entry.EndDate = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        roster_entry.ShiftID = request.form.get("shift_id")
        roster_entry.TeamName = request.form.get("team_name")
        roster_entry.Notes = request.form.get("notes")

        off_days = request.form.getlist("off_days")
        roster_entry.OffDays = ",".join(off_days) if off_days else None

        employee_ids = request.form.getlist("employee_ids")

        RosterAssignment.query.filter_by(RosterID=roster_id).delete()
        for emp_id in employee_ids:
            assignment = RosterAssignment(RosterID=roster_id, EmployeeID=emp_id)
            db.session.add(assignment)

        db.session.commit()
        return redirect(url_for("roster.roster", selected_date=start_date_str))

    roster_dict = {
        "RosterID": roster_entry.RosterID,
        "StartDate": roster_entry.StartDate.strftime("%Y-%m-%d"),
        "EndDate": roster_entry.EndDate.strftime("%Y-%m-%d"),
        "OffDaysList": (
            (roster_entry.OffDays or "").split(",") if roster_entry.OffDays else []
        ),
        "ShiftID": roster_entry.ShiftID,
        "TeamName": roster_entry.TeamName,
        "Notes": roster_entry.Notes,
    }

    shifts = [
        {"ShiftID": s.ShiftID, "ShiftName": s.ShiftName}
        for s in Shift.query.order_by(Shift.ShiftName).all()
    ]
    emps = Employee.query.filter_by(Status=True).order_by(Employee.FirstName).all()
    employees = [
        {
            "EmployeeID": e.EmployeeID,
            "DepartmentID": e.DepartmentID,
            "FullName": f"{e.FirstName} {e.LastName or ''}".strip(),
        }
        for e in emps
    ]
    deps = (
        Department.query.filter_by(IsActive=True)
        .order_by(Department.DepartmentName)
        .all()
    )
    departments = [
        {"DepartmentID": d.DepartmentID, "DepartmentName": d.DepartmentName}
        for d in deps
    ]

    assigned = RosterAssignment.query.filter_by(RosterID=roster_id).all()
    assigned_ids = [str(a.EmployeeID) for a in assigned]

    return render_template(
        "edit_roster.html",
        active_page="roster",
        roster=roster_dict,
        shifts=shifts,
        employees=employees,
        departments=departments,
        assigned_ids=assigned_ids,
        weekdays=WEEKDAY_ABBR,
    )


@bp.route("/delete_roster/<int:roster_id>", methods=["POST"])
def delete_roster(roster_id):
    RosterAssignment.query.filter_by(RosterID=roster_id).delete()
    Roster.query.filter_by(RosterID=roster_id).delete()
    db.session.commit()
    return redirect(url_for("roster.roster"))
