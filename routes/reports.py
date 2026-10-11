from flask import Blueprint, render_template, request, Response
from models.models import Report, Employee, Shift
from extensions import db
from datetime import datetime
import io
import csv

bp = Blueprint("reports", __name__)


@bp.route("/reports")
def reports():
    selected_date = request.args.get("selected_date") or datetime.today().strftime(
        "%Y-%m-%d"
    )
    selected_shift_id = request.args.get("shift_id")
    selected_status = request.args.get("status")
    export_csv = request.args.get("export") == "1"

    target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    shifts_query = Shift.query.order_by(Shift.ShiftName).all()
    shifts = [{"ShiftID": s.ShiftID, "ShiftName": s.ShiftName} for s in shifts_query]

    query = (
        db.session.query(
            Report.AttendanceDate,
            Report.CheckIn,
            Report.CheckOut,
            Report.WorkingHours,
            Report.LateMinutes,
            Report.OvertimeHours,
            Report.Status,
            Employee.FirstName,
            Employee.LastName,
            Shift.ShiftName,
        )
        .outerjoin(Employee, Employee.EmployeeID == Report.EmployeeID)
        .outerjoin(Shift, Shift.ShiftID == Report.ShiftID)
        .filter(Report.AttendanceDate == target_date)
    )

    if selected_shift_id:
        query = query.filter(Report.ShiftID == selected_shift_id)
    if selected_status:
        query = query.filter(Report.Status == selected_status)

    records = query.order_by(Report.AttendanceDate.desc()).all()

    report_records = []
    for r in records:
        full_name = f"{r.FirstName} {r.LastName or ''}".strip()
        report_records.append(
            {
                "FullName": full_name,
                "AttendanceDate": r.AttendanceDate,
                "ShiftName": r.ShiftName,
                "CheckIn": r.CheckIn,
                "CheckOut": r.CheckOut,
                "WorkingHours": r.WorkingHours,
                "LateMinutes": r.LateMinutes,
                "OvertimeHours": r.OvertimeHours,
                "Status": r.Status,
            }
        )

    total_report_records = len(report_records)

    if export_csv:
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "FullName",
                "AttendanceDate",
                "ShiftName",
                "CheckIn",
                "CheckOut",
                "WorkingHours",
                "LateMinutes",
                "OvertimeHours",
                "Status",
            ],
        )
        writer.writeheader()
        for row in report_records:
            writer.writerow(
                {
                    "FullName": row.get("FullName") or "",
                    "AttendanceDate": row.get("AttendanceDate") or "",
                    "ShiftName": row.get("ShiftName") or "",
                    "CheckIn": row.get("CheckIn") or "",
                    "CheckOut": row.get("CheckOut") or "",
                    "WorkingHours": row.get("WorkingHours") or "",
                    "LateMinutes": row.get("LateMinutes") or "",
                    "OvertimeHours": row.get("OvertimeHours") or "",
                    "Status": row.get("Status") or "",
                }
            )
        csv_output = output.getvalue()
        return Response(
            csv_output,
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=attendance_report_{selected_date}.csv"
            },
        )

    return render_template(
        "reports.html",
        active_page="reports",
        report_records=report_records,
        shifts=shifts,
        selected_date=selected_date,
        selected_shift_id=selected_shift_id,
        selected_status=selected_status,
        total_report_records=total_report_records,
    )
