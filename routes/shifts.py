from flask import Blueprint, render_template, request, redirect, url_for
from models.models import Shift, Employee
from extensions import db
from sqlalchemy import func

bp = Blueprint("shifts", __name__)


@bp.route("/shifts")
def shifts():
    shifts_data = (
        db.session.query(Shift, func.count(Employee.EmployeeID).label("EmployeeCount"))
        .outerjoin(Employee, Employee.ShiftID == Shift.ShiftID)
        .group_by(
            Shift.ShiftID,
            Shift.ShiftName,
            Shift.StartTime,
            Shift.EndTime,
            Shift.GracePeriod,
            Shift.WorkingHours,
        )
        .order_by(Shift.ShiftName)
        .all()
    )

    shifts_list = []
    for shift, emp_count in shifts_data:
        shifts_list.append(
            {
                "ShiftID": shift.ShiftID,
                "ShiftName": shift.ShiftName,
                "StartTime": (
                    shift.StartTime.strftime("%H:%M") if shift.StartTime else ""
                ),
                "EndTime": shift.EndTime.strftime("%H:%M") if shift.EndTime else "",
                "GracePeriod": shift.GracePeriod,
                "WorkingHours": shift.WorkingHours,
                "EmployeeCount": emp_count,
            }
        )

    return render_template("shifts.html", active_page="shifts", shifts=shifts_list)


@bp.route("/add_shift", methods=["POST"])
def add_shift():
    shift_name = request.form.get("shift_name")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    grace_period = request.form.get("grace_period") or 0
    working_hours = request.form.get("working_hours") or 0

    new_shift = Shift(
        ShiftName=shift_name,
        StartTime=start_time,
        EndTime=end_time,
        GracePeriod=grace_period,
        WorkingHours=working_hours,
    )
    db.session.add(new_shift)
    db.session.commit()

    return redirect(url_for("shifts.shifts"))


@bp.route("/delete_shift/<int:shift_id>", methods=["POST"])
def delete_shift(shift_id):
    shift = Shift.query.get(shift_id)
    if shift:
        db.session.delete(shift)
        db.session.commit()
    return redirect(url_for("shifts.shifts"))


@bp.route("/edit_shift/<int:shift_id>", methods=["GET", "POST"])
def edit_shift(shift_id):
    shift = Shift.query.get_or_404(shift_id)

    if request.method == "POST":
        shift.ShiftName = request.form.get("shift_name")
        shift.StartTime = request.form.get("start_time")
        shift.EndTime = request.form.get("end_time")
        shift.GracePeriod = request.form.get("grace_period") or 0
        shift.WorkingHours = request.form.get("working_hours") or 0

        db.session.commit()
        return redirect(url_for("shifts.shifts"))

    return render_template("edit_shift.html", active_page="shifts", shift=shift)
