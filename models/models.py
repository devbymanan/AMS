from extensions import db
from flask_login import UserMixin


class Shift(db.Model):
    __tablename__ = "Shift"
    ShiftID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ShiftName = db.Column(db.String(50), nullable=False)
    StartTime = db.Column(db.Time, nullable=False)
    EndTime = db.Column(db.Time, nullable=False)
    GracePeriod = db.Column(db.Integer, default=0)
    WorkingHours = db.Column(db.Numeric(4, 2), nullable=False)

    employees = db.relationship("Employee", backref="shift", lazy=True)


class Department(db.Model):
    __tablename__ = "Department"
    DepartmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DepartmentName = db.Column(db.String(100), unique=True, nullable=False)
    Description = db.Column(db.String(255))
    IsActive = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, server_default=db.func.now())


class Position(db.Model):
    __tablename__ = "Positions"
    PositionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    PositionName = db.Column(db.String(100), unique=True, nullable=False)
    Description = db.Column(db.String(255))
    IsActive = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, server_default=db.func.now())


class Employee(db.Model):
    __tablename__ = "Employees"
    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeCode = db.Column(db.String(40), unique=True, nullable=False)
    CardNumber = db.Column(db.String(40))
    FirstName = db.Column(db.String(100), nullable=False)
    LastName = db.Column(db.String(100))
    NickName = db.Column(db.String(100))
    CNIC = db.Column(db.String(20))
    Passport = db.Column(db.String(30))
    Gender = db.Column(db.String(10))
    DateOfBirth = db.Column(db.Date)
    Nationality = db.Column(db.String(100))
    Religion = db.Column(db.String(40))
    Photo = db.Column(db.String(255))
    Mobile = db.Column(db.String(20))
    OfficePhone = db.Column(db.String(20))
    Email = db.Column(db.String(100))
    Address = db.Column(db.String(255))
    City = db.Column(db.String(50))
    PostalCode = db.Column(db.String(20))
    HireDate = db.Column(db.Date)
    DepartmentID = db.Column(db.Integer, db.ForeignKey("Department.DepartmentID"))
    PositionID = db.Column(db.Integer, db.ForeignKey("Positions.PositionID"))
    ShiftID = db.Column(db.Integer, db.ForeignKey("Shift.ShiftID"))
    SupervisorID = db.Column(db.Integer)
    EmploymentType = db.Column(db.SmallInteger)
    Status = db.Column(db.Boolean, default=True)
    DevicePassword = db.Column(db.String(40))
    DeviceSerialNumber = db.Column(db.String(40))
    FingerprintEnrolled = db.Column(db.Boolean, default=False)
    FaceEnrolled = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, server_default=db.func.now())
    UpdatedAt = db.Column(db.DateTime, onupdate=db.func.now())

    department = db.relationship("Department", backref="employees", lazy=True)
    position = db.relationship("Position", backref="employees", lazy=True)


class Device(db.Model):
    __tablename__ = "Device"
    DeviceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DeviceName = db.Column(db.String(100), nullable=False)
    SerialNumber = db.Column(db.String(100), unique=True, nullable=False)
    DeviceType = db.Column(db.String(50))
    IPAddress = db.Column(db.String(50))
    Port = db.Column(db.Integer)
    Location = db.Column(db.String(150))
    Model = db.Column(db.String(100))
    Status = db.Column(db.Boolean, default=True)
    Notes = db.Column(db.String(500))
    CreatedAt = db.Column(db.DateTime, server_default=db.func.now())


class RawTransaction(db.Model):
    __tablename__ = "RawTransactions"
    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(40), nullable=False)
    punch_time = db.Column(db.DateTime, nullable=False)
    punch_state = db.Column(db.String(10), nullable=False)
    verify_type = db.Column(db.Integer, nullable=False)
    terminal_sn = db.Column(db.String(100))
    terminal_alias = db.Column(db.String(100))


class Attendance(db.Model):
    __tablename__ = "Attendance"
    __table_args__ = {"implicit_returning": False}
    AttendanceID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.String(40), nullable=False)
    PunchTime = db.Column(db.DateTime, nullable=False)
    ZKBioTransactionID = db.Column(db.Integer, db.ForeignKey("RawTransactions.id"))
    Source = db.Column(db.String(20), nullable=False, default="Device")


class Report(db.Model):
    __tablename__ = "Report"
    __table_args__ = {"implicit_returning": False}
    ReportID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(
        db.Integer, db.ForeignKey("Employees.EmployeeID"), nullable=False
    )
    AttendanceDate = db.Column(db.Date, nullable=False)
    ShiftID = db.Column(db.Integer, db.ForeignKey("Shift.ShiftID"), nullable=False)
    CheckIn = db.Column(db.Time)
    CheckOut = db.Column(db.Time)
    WorkingHours = db.Column(db.Numeric(4, 2))
    LateMinutes = db.Column(db.Integer, default=0)
    OvertimeHours = db.Column(db.Numeric(4, 2), default=0)
    Status = db.Column(db.String(20))


class Roster(db.Model):
    __tablename__ = "Roster"
    RosterID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    OffDays = db.Column(db.String(255))
    ShiftID = db.Column(db.Integer, db.ForeignKey("Shift.ShiftID"), nullable=False)
    TeamName = db.Column(db.String(100))
    Notes = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, server_default=db.func.now())

    shift = db.relationship("Shift", backref="rosters", lazy=True)


class RosterAssignment(db.Model):
    __tablename__ = "RosterAssignment"
    RosterAssignmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RosterID = db.Column(db.Integer, db.ForeignKey("Roster.RosterID"), nullable=False)
    EmployeeID = db.Column(
        db.Integer, db.ForeignKey("Employees.EmployeeID"), nullable=False
    )

    employee = db.relationship("Employee", backref="roster_assignments", lazy=True)


class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="Admin")
