CREATE DATABASE AttendanceManagementSystem;
GO

USE AttendanceManagementSystem;
GO


CREATE TABLE Shift (
    ShiftID INT IDENTITY(1,1) PRIMARY KEY,
    ShiftName NVARCHAR(50) NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    GracePeriod INT DEFAULT 0,      
    WorkingHours DECIMAL(4,2) NOT NULL
);


CREATE TABLE Employee (
    EmployeeID INT IDENTITY(1,1) PRIMARY KEY,
    ZKBioEmployeeID INT,
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100),
    Address NVARCHAR(200),
    ShiftID INT,

    FOREIGN KEY (ShiftID)
        REFERENCES Shift(ShiftID)
);



CREATE TABLE Attendance (
    AttendanceID INT IDENTITY(1,1) PRIMARY KEY,
    ZKBioTransactionID BIGINT,
    EmployeeID INT,
    PunchTime DATETIME NOT NULL,

    FOREIGN KEY (EmployeeID)
        REFERENCES Employee(EmployeeID)
);


CREATE TABLE Report (
    ReportID INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeID INT NOT NULL,
    AttendanceDate DATE NOT NULL,
    ShiftID INT NOT NULL,
    CheckIn TIME,
    CheckOut TIME,
    WorkingHours DECIMAL(4,2),
    LateMinutes INT DEFAULT 0,
    OvertimeHours DECIMAL(4,2) DEFAULT 0,
    Status NVARCHAR(20),

    FOREIGN KEY (EmployeeID)
        REFERENCES Employee(EmployeeID),

    FOREIGN KEY (ShiftID)
        REFERENCES Shift(ShiftID)
);


CREATE TABLE SyncLog (
    LastTransactionID BIGINT
);

INSERT INTO SyncLog VALUES (0);