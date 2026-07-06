CREATE DATABASE AttendanceManagementSystem;
GO

USE AttendanceManagementSystem
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


CREATE TABLE dbo.RawTransactions
(
    id              INT NOT NULL PRIMARY KEY,

    emp_code        NVARCHAR(40) NOT NULL,

    punch_time      DATETIME2(7) NOT NULL,

    punch_state     NVARCHAR(10) NOT NULL,

    verify_type     INT NOT NULL,

    work_code       NVARCHAR(40) NULL,

    terminal_sn     NVARCHAR(100) NULL,

    terminal_alias  NVARCHAR(100) NULL,

    area_alias      NVARCHAR(200) NULL,

    longitude       FLOAT NULL,

    latitude        FLOAT NULL,

    gps_location    NVARCHAR(MAX) NULL,

    mobile          NVARCHAR(100) NULL,

    source          SMALLINT NULL,

    purpose         SMALLINT NULL,

    crc             NVARCHAR(200) NULL,

    is_attendance   SMALLINT NULL,

    reserved        NVARCHAR(200) NULL,

    upload_time     DATETIME2(7) NULL,

    sync_status     SMALLINT NULL,

    sync_time       DATETIME2(7) NULL,

    is_mask         SMALLINT NULL,

    temperature     NUMERIC(4,1) NULL,

    emp_id          INT NULL,

    terminal_id     INT NULL,

    company_code    NVARCHAR(100) NULL
);
GO

CREATE UNIQUE INDEX UX_RawTransactions
ON dbo.RawTransactions
(
    company_code,
    emp_code,
    punch_time
);

CREATE INDEX IX_RawTransactions_EmpID
ON dbo.RawTransactions(emp_id);

CREATE INDEX IX_RawTransactions_TerminalID
ON dbo.RawTransactions(terminal_id);
GO


INSERT INTO dbo.RawTransactions
SELECT *
FROM zkbiotime.dbo.iclock_transaction;

CREATE TRIGGER trg_iclock_transaction_insert
ON zkbiotime.dbo.iclock_transaction
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.RawTransactions
    (
        id,
        emp_code,
        punch_time,
        punch_state,
        verify_type,
        work_code,
        terminal_sn,
        terminal_alias,
        area_alias,
        longitude,
        latitude,
        gps_location,
        mobile,
        source,
        purpose,
        crc,
        is_attendance,
        reserved,
        upload_time,
        sync_status,
        sync_time,
        is_mask,
        temperature,
        emp_id,
        terminal_id,
        company_code
    )
    SELECT
        id,
        emp_code,
        punch_time,
        punch_state,
        verify_type,
        work_code,
        terminal_sn,
        terminal_alias,
        area_alias,
        longitude,
        latitude,
        gps_location,
        mobile,
        source,
        purpose,
        crc,
        is_attendance,
        reserved,
        upload_time,
        sync_status,
        sync_time,
        is_mask,
        temperature,
        emp_id,
        terminal_id,
        company_code
    FROM inserted;
END;
GO




