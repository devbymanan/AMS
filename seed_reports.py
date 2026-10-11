import os
import random
from datetime import datetime, timedelta, date, time
from main import create_app
from extensions import db
from models.models import Department, Position, Shift, Employee, Report

def generate_bulk_reports():
    app = create_app()
    with app.app_context():
        d = Department.query.filter_by(DepartmentName='Operations').first()
        if not d:
            d = Department(DepartmentName='Operations', IsActive=True)
            db.session.add(d)
            db.session.commit()
            
        p = Position.query.filter_by(PositionName='Analyst').first()
        if not p:
            p = Position(PositionName='Analyst', IsActive=True)
            db.session.add(p)
            db.session.commit()
            
        s = Shift.query.filter_by(ShiftName='Standard Shift').first()
        if not s:
            s = Shift(
                ShiftName='Standard Shift', 
                StartTime=time(9, 0, 0),
                EndTime=time(17, 0, 0),
                GracePeriod=15,
                WorkingHours=8.00
            )
            db.session.add(s)
            db.session.commit()
            
        names = [("Alice", "Smith"), ("Bob", "Johnson"), ("Charlie", "Brown"), ("Diana", "Prince"), ("Evan", "Wright")]
        employees = []
        for i, (first, last) in enumerate(names, start=1000):
            emp = Employee.query.filter_by(EmployeeCode=f'EMP{i}').first()
            if not emp:
                emp = Employee(
                    EmployeeCode=f'EMP{i}',
                    FirstName=first,
                    LastName=last,
                    DepartmentID=d.DepartmentID,
                    PositionID=p.PositionID,
                    ShiftID=s.ShiftID,
                    Status=True
                )
                db.session.add(emp)
                db.session.commit()
            employees.append(emp)
            
        today = date.today()
        dates = [today - timedelta(days=x) for x in range(7)]
        
        statuses = ['Present', 'Present', 'Present', 'Late', 'Late', 'Absent', 'Half Day']
        
        for emp in employees:
            for d_date in dates:
                existing = Report.query.filter(
                    db.cast(Report.AttendanceDate, db.Date) == d_date,
                    Report.EmployeeID == emp.EmployeeID
                ).first()
                if existing:
                    continue
                    
                status = random.choice(statuses)
                
                if status == 'Absent':
                    r = Report(
                        EmployeeID=emp.EmployeeID,
                        AttendanceDate=d_date,
                        ShiftID=s.ShiftID,
                        CheckIn=None,
                        CheckOut=None,
                        WorkingHours=0,
                        LateMinutes=0,
                        OvertimeHours=0,
                        Status='Absent'
                    )
                    db.session.add(r)
                elif status == 'Present':
                    check_in = datetime.combine(d_date, time(8, random.randint(45, 59), 0))
                    check_out = datetime.combine(d_date, time(17, random.randint(5, 30), 0))
                    r = Report(
                        EmployeeID=emp.EmployeeID,
                        AttendanceDate=d_date,
                        ShiftID=s.ShiftID,
                        CheckIn=check_in,
                        CheckOut=check_out,
                        WorkingHours=round(8.0 + random.uniform(0.1, 0.5), 2),
                        LateMinutes=0,
                        OvertimeHours=round(random.uniform(0.0, 1.5), 2) if random.random() > 0.7 else 0.0,
                        Status='Present'
                    )
                    db.session.add(r)
                elif status == 'Late':
                    check_in = datetime.combine(d_date, time(9, random.randint(16, 45), 0))
                    check_out = datetime.combine(d_date, time(17, random.randint(0, 10), 0))
                    r = Report(
                        EmployeeID=emp.EmployeeID,
                        AttendanceDate=d_date,
                        ShiftID=s.ShiftID,
                        CheckIn=check_in,
                        CheckOut=check_out,
                        WorkingHours=round(7.5 + random.uniform(0.1, 0.3), 2),
                        LateMinutes=random.randint(16, 45),
                        OvertimeHours=0,
                        Status='Late'
                    )
                    db.session.add(r)
                elif status == 'Half Day':
                    check_in = datetime.combine(d_date, time(9, 0, 0))
                    check_out = datetime.combine(d_date, time(13, 0, 0))
                    r = Report(
                        EmployeeID=emp.EmployeeID,
                        AttendanceDate=d_date,
                        ShiftID=s.ShiftID,
                        CheckIn=check_in,
                        CheckOut=check_out,
                        WorkingHours=4.0,
                        LateMinutes=0,
                        OvertimeHours=0,
                        Status='Half Day'
                    )
                    db.session.add(r)
                    
        db.session.commit()
        print("Successfully generated bulk sample reports!")

if __name__ == '__main__':
    generate_bulk_reports()
