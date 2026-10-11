import os
from datetime import datetime, timedelta, date
from main import create_app
from extensions import db
from models.models import Department, Position, Shift, Device, Employee, Attendance, RawTransaction, Report, Roster, RosterAssignment

def seed_data():
    app = create_app()
    with app.app_context():
        # Always insert departments
        d1 = Department(DepartmentName='Engineering', IsActive=True)
        d2 = Department(DepartmentName='Human Resources', IsActive=True)
        d3 = Department(DepartmentName='Sales', IsActive=True)
        db.session.add_all([d1, d2, d3])
        try:
            db.session.commit()
        except:
            db.session.rollback()
            
        p1 = Position(PositionName='Software Engineer')
        p2 = Position(PositionName='HR Manager')
        p3 = Position(PositionName='Sales Representative')
        db.session.add_all([p1, p2, p3])
        try:
            db.session.commit()
        except:
            db.session.rollback()
            
        s1 = Shift(
            ShiftName='Morning Shift', 
            StartTime=datetime.strptime('09:00:00', '%H:%M:%S').time(),
            EndTime=datetime.strptime('17:00:00', '%H:%M:%S').time(),
            GracePeriod=15,
            WorkingHours=8
        )
        s2 = Shift(
            ShiftName='Night Shift', 
            StartTime=datetime.strptime('21:00:00', '%H:%M:%S').time(),
            EndTime=datetime.strptime('05:00:00', '%H:%M:%S').time(),
            GracePeriod=15,
            WorkingHours=8
        )
        db.session.add_all([s1, s2])
        try:
            db.session.commit()
        except:
            db.session.rollback()

        dev1 = Device(DeviceName='Main Entrance Terminal', SerialNumber='ZK123456', DeviceType='Face', Status=True)
        dev2 = Device(DeviceName='Back Door Terminal', SerialNumber='ZK654321', DeviceType='Fingerprint', Status=True)
        db.session.add_all([dev1, dev2])
        try:
            db.session.commit()
        except:
            db.session.rollback()

        dept_eng = Department.query.filter_by(DepartmentName='Engineering').first()
        dept_hr = Department.query.filter_by(DepartmentName='Human Resources').first()
        pos_se = Position.query.filter_by(PositionName='Software Engineer').first()
        pos_hrm = Position.query.filter_by(PositionName='HR Manager').first()
        shift_morn = Shift.query.filter_by(ShiftName='Morning Shift').first()
        
        e1 = Employee(
            EmployeeCode='EMP001',
            FirstName='John',
            LastName='Doe',
            DepartmentID=dept_eng.DepartmentID if dept_eng else None,
            PositionID=pos_se.PositionID if pos_se else None,
            ShiftID=shift_morn.ShiftID if shift_morn else None,
            Status=True
        )
        e2 = Employee(
            EmployeeCode='EMP002',
            FirstName='Jane',
            LastName='Smith',
            DepartmentID=dept_hr.DepartmentID if dept_hr else None,
            PositionID=pos_hrm.PositionID if pos_hrm else None,
            ShiftID=shift_morn.ShiftID if shift_morn else None,
            Status=True
        )
        db.session.add_all([e1, e2])
        try:
            db.session.commit()
        except:
            db.session.rollback()

        today = date.today()
        yesterday = today - timedelta(days=1)
        
        att1 = Attendance(
            EmployeeID='EMP001',
            PunchTime=datetime.combine(yesterday, datetime.strptime('08:55:00', '%H:%M:%S').time()),
            Source='Device'
        )
        att2 = Attendance(
            EmployeeID='EMP001',
            PunchTime=datetime.combine(yesterday, datetime.strptime('17:05:00', '%H:%M:%S').time()),
            Source='Device'
        )
        att3 = Attendance(
            EmployeeID='EMP001',
            PunchTime=datetime.combine(today, datetime.strptime('09:10:00', '%H:%M:%S').time()),
            Source='Device'
        )
        
        db.session.add_all([att1, att2, att3])
        try:
            db.session.commit()
        except:
            db.session.rollback()

        emp = Employee.query.filter_by(EmployeeCode='EMP001').first()
        if emp and shift_morn:
            r1 = Report(
                EmployeeID=emp.EmployeeID,
                AttendanceDate=yesterday,
                ShiftID=shift_morn.ShiftID,
                CheckIn=datetime.combine(yesterday, datetime.strptime('08:55:00', '%H:%M:%S').time()),
                CheckOut=datetime.combine(yesterday, datetime.strptime('17:05:00', '%H:%M:%S').time()),
                WorkingHours=8.16,
                LateMinutes=0,
                Status='Present'
            )
            db.session.add(r1)
            try:
                db.session.commit()
            except:
                db.session.rollback()

        if emp and shift_morn:
            roster = Roster(
                StartDate=today,
                EndDate=today + timedelta(days=7),
                OffDays='Sat,Sun',
                ShiftID=shift_morn.ShiftID,
                TeamName='Alpha Team'
            )
            db.session.add(roster)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            
            assign = RosterAssignment(
                RosterID=roster.RosterID,
                EmployeeID=emp.EmployeeID
            )
            db.session.add(assign)
            try:
                db.session.commit()
            except:
                db.session.rollback()

        print("Database seeded successfully with sample data!")

if __name__ == '__main__':
    seed_data()
