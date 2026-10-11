-- Attendance Management System - Database Schema
-- Compatible with Microsoft SQL Server

-- 1. Departments Table
CREATE TABLE [dbo].[Department] (
    [DepartmentID] INT IDENTITY(1,1) NOT NULL,
    [DepartmentName] NVARCHAR(100) NOT NULL UNIQUE,
    [Description] NVARCHAR(255) NULL,
    [IsActive] BIT NOT NULL DEFAULT (1),
    [CreatedAt] DATETIME NOT NULL DEFAULT (GETDATE()),
    PRIMARY KEY CLUSTERED ([DepartmentID] ASC)
);

-- 2. Positions Table
CREATE TABLE [dbo].[Positions] (
    [PositionID] INT IDENTITY(1,1) NOT NULL,
    [PositionName] NVARCHAR(100) NOT NULL UNIQUE,
    [Description] NVARCHAR(255) NULL,
    [IsActive] BIT NOT NULL DEFAULT (1),
    [CreatedAt] DATETIME NOT NULL DEFAULT (GETDATE()),
    PRIMARY KEY CLUSTERED ([PositionID] ASC)
);

-- 3. Shifts Table
CREATE TABLE [dbo].[Shift] (
    [ShiftID] INT IDENTITY(1,1) NOT NULL,
    [ShiftName] NVARCHAR(50) NOT NULL,
    [StartTime] TIME(7) NOT NULL,
    [EndTime] TIME(7) NOT NULL,
    [GracePeriod] INT NULL DEFAULT (0),
    [WorkingHours] DECIMAL(4, 2) NOT NULL,
    PRIMARY KEY CLUSTERED ([ShiftID] ASC)
);

-- 4. Devices Table
CREATE TABLE [dbo].[Device] (
    [DeviceID] INT IDENTITY(1,1) NOT NULL,
    [DeviceName] NVARCHAR(100) NOT NULL,
    [SerialNumber] NVARCHAR(100) NOT NULL UNIQUE,
    [DeviceType] NVARCHAR(50) NULL,
    [IPAddress] NVARCHAR(50) NULL,
    [Port] INT NULL,
    [Location] NVARCHAR(150) NULL,
    [Model] NVARCHAR(100) NULL,
    [Status] BIT NULL DEFAULT (1),
    [Notes] NVARCHAR(500) NULL,
    [CreatedAt] DATETIME NULL DEFAULT (GETDATE()),
    PRIMARY KEY CLUSTERED ([DeviceID] ASC)
);

-- 5. Employees Table
CREATE TABLE [dbo].[Employees] (
    [EmployeeID] INT IDENTITY(1,1) NOT NULL,
    [EmployeeCode] NVARCHAR(40) NOT NULL UNIQUE,
    [CardNumber] NVARCHAR(40) NULL,
    [FirstName] NVARCHAR(100) NOT NULL,
    [LastName] NVARCHAR(100) NULL,
    [NickName] NVARCHAR(100) NULL,
    [CNIC] NVARCHAR(20) NULL,
    [Passport] NVARCHAR(30) NULL,
    [Gender] NVARCHAR(10) NULL,
    [DateOfBirth] DATE NULL,
    [Nationality] NVARCHAR(100) NULL,
    [Religion] NVARCHAR(40) NULL,
    [Photo] NVARCHAR(255) NULL,
    [Mobile] NVARCHAR(20) NULL,
    [OfficePhone] NVARCHAR(20) NULL,
    [Email] NVARCHAR(100) NULL,
    [Address] NVARCHAR(255) NULL,
    [City] NVARCHAR(50) NULL,
    [PostalCode] NVARCHAR(20) NULL,
    [HireDate] DATE NULL,
    [DepartmentID] INT NULL,
    [PositionID] INT NULL,
    [ShiftID] INT NULL,
    [SupervisorID] INT NULL,
    [EmploymentType] SMALLINT NULL,
    [Status] BIT NOT NULL DEFAULT (1),
    [DevicePassword] NVARCHAR(40) NULL,
    [DeviceSerialNumber] NVARCHAR(40) NULL,
    [FingerprintEnrolled] BIT NOT NULL DEFAULT (0),
    [FaceEnrolled] BIT NOT NULL DEFAULT (0),
    [CreatedAt] DATETIME2(7) NOT NULL DEFAULT (GETDATE()),
    [UpdatedAt] DATETIME2(7) NULL,
    PRIMARY KEY CLUSTERED ([EmployeeID] ASC),
    CONSTRAINT [FK_Employees_Shifts] FOREIGN KEY ([ShiftID]) REFERENCES [dbo].[Shift] ([ShiftID]),
    CONSTRAINT [FK_Employees_Department] FOREIGN KEY ([DepartmentID]) REFERENCES [dbo].[Department] ([DepartmentID]),
    CONSTRAINT [FK_Employees_Position] FOREIGN KEY ([PositionID]) REFERENCES [dbo].[Positions] ([PositionID])
);

-- 6. Raw Transactions (Biometric device punches)
CREATE TABLE [dbo].[RawTransactions] (
    [id] INT NOT NULL,
    [emp_code] NVARCHAR(40) NOT NULL,
    [punch_time] DATETIME2(7) NOT NULL,
    [punch_state] NVARCHAR(10) NOT NULL,
    [verify_type] INT NOT NULL,
    [work_code] NVARCHAR(40) NULL,
    [terminal_sn] NVARCHAR(100) NULL,
    [terminal_alias] NVARCHAR(100) NULL,
    [area_alias] NVARCHAR(200) NULL,
    [longitude] FLOAT NULL,
    [latitude] FLOAT NULL,
    [gps_location] NVARCHAR(MAX) NULL,
    [mobile] NVARCHAR(100) NULL,
    [source] SMALLINT NULL,
    [purpose] SMALLINT NULL,
    [crc] NVARCHAR(200) NULL,
    [is_attendance] SMALLINT NULL,
    [reserved] NVARCHAR(200) NULL,
    [upload_time] DATETIME2(7) NULL,
    [sync_status] SMALLINT NULL,
    [sync_time] DATETIME2(7) NULL,
    [is_mask] SMALLINT NULL,
    [temperature] NUMERIC(4, 1) NULL,
    [emp_id] INT NULL,
    [terminal_id] INT NULL,
    [company_code] NVARCHAR(100) NULL,
    PRIMARY KEY CLUSTERED ([id] ASC)
);

-- 7. Attendance Table
CREATE TABLE [dbo].[Attendance] (
    [AttendanceID] INT IDENTITY(1,1) NOT NULL,
    [EmployeeID] NVARCHAR(40) NOT NULL,
    [PunchTime] DATETIME2(7) NOT NULL,
    [ZKBioTransactionID] INT NULL,
    [Source] NVARCHAR(20) NOT NULL,
    PRIMARY KEY CLUSTERED ([AttendanceID] ASC),
    CONSTRAINT [FK_Attendance_Transaction] FOREIGN KEY ([ZKBioTransactionID]) REFERENCES [dbo].[RawTransactions] ([id])
);

-- 8. Report Table
CREATE TABLE [dbo].[Report] (
    [ReportID] INT IDENTITY(1,1) NOT NULL,
    [EmployeeID] INT NOT NULL,
    [AttendanceDate] DATE NOT NULL,
    [ShiftID] INT NOT NULL,
    [CheckIn] TIME(7) NULL,
    [CheckOut] TIME(7) NULL,
    [WorkingHours] DECIMAL(4, 2) NULL,
    [LateMinutes] INT NULL DEFAULT (0),
    [OvertimeHours] DECIMAL(4, 2) NULL DEFAULT (0),
    [Status] NVARCHAR(20) NULL,
    PRIMARY KEY CLUSTERED ([ReportID] ASC),
    CONSTRAINT [FK_Report_Shift] FOREIGN KEY ([ShiftID]) REFERENCES [dbo].[Shift] ([ShiftID]),
    CONSTRAINT [FK_Report_Employee] FOREIGN KEY ([EmployeeID]) REFERENCES [dbo].[Employees] ([EmployeeID])
);

-- 9. Roster Table
CREATE TABLE [dbo].[Roster] (
    [RosterID] INT IDENTITY(1,1) NOT NULL,
    [StartDate] DATE NOT NULL,
    [EndDate] DATE NOT NULL,
    [ShiftID] INT NOT NULL,
    [OffDays] NVARCHAR(100) NULL,
    [TeamName] NVARCHAR(100) NULL,
    [Notes] NVARCHAR(255) NULL,
    [CreatedAt] DATETIME NOT NULL DEFAULT (GETDATE()),
    PRIMARY KEY CLUSTERED ([RosterID] ASC),
    CONSTRAINT [FK_Roster_Shift] FOREIGN KEY ([ShiftID]) REFERENCES [dbo].[Shift] ([ShiftID])
);

-- 10. Roster Assignments Table
CREATE TABLE [dbo].[RosterAssignment] (
    [RosterAssignmentID] INT IDENTITY(1,1) NOT NULL,
    [RosterID] INT NOT NULL,
    [EmployeeID] INT NOT NULL,
    PRIMARY KEY CLUSTERED ([RosterAssignmentID] ASC),
    CONSTRAINT [UQ_RosterAssignment_RosterEmployee] UNIQUE ([RosterID], [EmployeeID]),
    CONSTRAINT [FK_RosterAssignment_Roster] FOREIGN KEY ([RosterID]) REFERENCES [dbo].[Roster] ([RosterID]),
    CONSTRAINT [FK_RosterAssignment_Employee] FOREIGN KEY ([EmployeeID]) REFERENCES [dbo].[Employees] ([EmployeeID])
);

-- 11. Sync Log Table
CREATE TABLE [dbo].[SyncLog] (
    [LastTransactionID] BIGINT NULL
);
