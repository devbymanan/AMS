USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[SyncLog]    Script Date: 8/11/2026 1:12:15 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[SyncLog](
	[LastTransactionID] [bigint] NULL
) ON [PRIMARY]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Positions]    Script Date: 8/11/2026 1:11:46 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Positions](
	[PositionID] [int] IDENTITY(1,1) NOT NULL,
	[PositionName] [nvarchar](100) NOT NULL,
	[Description] [nvarchar](255) NULL,
	[IsActive] [bit] NOT NULL,
	[CreatedAt] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[PositionID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[PositionName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Positions] ADD  DEFAULT ((1)) FOR [IsActive]
GO

ALTER TABLE [dbo].[Positions] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[personnel_employee]    Script Date: 8/11/2026 1:11:38 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[personnel_employee](
	[id] [int] NOT NULL,
	[create_time] [datetime2](7) NULL,
	[create_user] [nvarchar](150) NULL,
	[change_time] [datetime2](7) NULL,
	[change_user] [nvarchar](150) NULL,
	[status] [smallint] NOT NULL,
	[emp_code] [nvarchar](20) NOT NULL,
	[first_name] [nvarchar](100) NULL,
	[last_name] [nvarchar](100) NULL,
	[nickname] [nvarchar](100) NULL,
	[passport] [nvarchar](30) NULL,
	[driver_license_automobile] [nvarchar](30) NULL,
	[driver_license_motorcycle] [nvarchar](30) NULL,
	[photo] [nvarchar](200) NULL,
	[self_password] [nvarchar](128) NULL,
	[device_password] [nvarchar](20) NULL,
	[dev_privilege] [int] NULL,
	[card_no] [nvarchar](20) NULL,
	[acc_group] [nvarchar](5) NULL,
	[acc_timezone] [nvarchar](20) NULL,
	[gender] [nvarchar](1) NULL,
	[birthday] [date] NULL,
	[address] [nvarchar](200) NULL,
	[postcode] [nvarchar](10) NULL,
	[office_tel] [nvarchar](20) NULL,
	[contact_tel] [nvarchar](20) NULL,
	[mobile] [nvarchar](20) NULL,
	[national] [nvarchar](50) NULL,
	[religion] [nvarchar](20) NULL,
	[title] [nvarchar](20) NULL,
	[enroll_sn] [nvarchar](20) NULL,
	[ssn] [nvarchar](20) NULL,
	[update_time] [datetime2](7) NULL,
	[hire_date] [date] NULL,
	[verify_mode] [int] NULL,
	[city] [nvarchar](20) NULL,
	[emp_type] [smallint] NULL,
	[enable_payroll] [bit] NOT NULL,
	[app_status] [smallint] NULL,
	[app_role] [smallint] NULL,
	[email] [nvarchar](50) NULL,
	[last_login] [datetime2](7) NULL,
	[is_active] [bit] NOT NULL,
	[session_key] [nvarchar](32) NULL,
	[login_ip] [nvarchar](32) NULL,
	[department_id] [int] NULL,
	[position_id] [int] NULL,
	[leave_group] [int] NULL,
	[emp_code_digit] [bigint] NULL,
	[superior_id] [int] NULL,
	[company_id] [int] NOT NULL,
	[password_reset] [datetime2](7) NULL,
 CONSTRAINT [PK_personnel_employee] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Employees]    Script Date: 8/11/2026 1:11:20 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Employees](
	[EmployeeID] [int] IDENTITY(1,1) NOT NULL,
	[EmployeeCode] [nvarchar](40) NOT NULL,
	[CardNumber] [nvarchar](40) NULL,
	[FirstName] [nvarchar](100) NOT NULL,
	[LastName] [nvarchar](100) NULL,
	[NickName] [nvarchar](100) NULL,
	[CNIC] [nvarchar](20) NULL,
	[Passport] [nvarchar](30) NULL,
	[Gender] [nvarchar](10) NULL,
	[DateOfBirth] [date] NULL,
	[Nationality] [nvarchar](100) NULL,
	[Religion] [nvarchar](40) NULL,
	[Photo] [nvarchar](255) NULL,
	[Mobile] [nvarchar](20) NULL,
	[OfficePhone] [nvarchar](20) NULL,
	[Email] [nvarchar](100) NULL,
	[Address] [nvarchar](255) NULL,
	[City] [nvarchar](50) NULL,
	[PostalCode] [nvarchar](20) NULL,
	[HireDate] [date] NULL,
	[DepartmentID] [int] NULL,
	[PositionID] [int] NULL,
	[ShiftID] [int] NULL,
	[SupervisorID] [int] NULL,
	[EmploymentType] [smallint] NULL,
	[Status] [bit] NOT NULL,
	[DevicePassword] [nvarchar](40) NULL,
	[DeviceSerialNumber] [nvarchar](40) NULL,
	[FingerprintEnrolled] [bit] NOT NULL,
	[FaceEnrolled] [bit] NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[UpdatedAt] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[EmployeeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[EmployeeCode] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Employees] ADD  DEFAULT ((1)) FOR [Status]
GO

ALTER TABLE [dbo].[Employees] ADD  DEFAULT ((0)) FOR [FingerprintEnrolled]
GO

ALTER TABLE [dbo].[Employees] ADD  DEFAULT ((0)) FOR [FaceEnrolled]
GO

ALTER TABLE [dbo].[Employees] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[Employees]  WITH CHECK ADD  CONSTRAINT [FK_Employees_Shifts] FOREIGN KEY([ShiftID])
REFERENCES [dbo].[Shift] ([ShiftID])
GO

ALTER TABLE [dbo].[Employees] CHECK CONSTRAINT [FK_Employees_Shifts]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Device]    Script Date: 8/11/2026 1:11:02 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Device](
	[DeviceID] [int] IDENTITY(1,1) NOT NULL,
	[DeviceName] [nvarchar](100) NOT NULL,
	[SerialNumber] [nvarchar](100) NOT NULL,
	[DeviceType] [nvarchar](50) NULL,
	[IPAddress] [nvarchar](50) NULL,
	[Port] [int] NULL,
	[Location] [nvarchar](150) NULL,
	[Model] [nvarchar](100) NULL,
	[Status] [bit] NULL,
	[Notes] [nvarchar](500) NULL,
	[CreatedAt] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[DeviceID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[SerialNumber] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Device] ADD  DEFAULT ((1)) FOR [Status]
GO

ALTER TABLE [dbo].[Device] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Department]    Script Date: 8/11/2026 1:10:48 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Department](
	[DepartmentID] [int] IDENTITY(1,1) NOT NULL,
	[DepartmentName] [nvarchar](100) NOT NULL,
	[Description] [nvarchar](255) NULL,
	[IsActive] [bit] NOT NULL,
	[CreatedAt] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[DepartmentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[DepartmentName] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Department] ADD  DEFAULT ((1)) FOR [IsActive]
GO

ALTER TABLE [dbo].[Department] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Attendance]    Script Date: 8/11/2026 1:10:39 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Attendance](
	[AttendanceID] [int] IDENTITY(1,1) NOT NULL,
	[EmployeeID] [nvarchar](40) NOT NULL,
	[PunchTime] [datetime2](7) NOT NULL,
	[ZKBioTransactionID] [int] NULL,
	[Source] [nvarchar](20) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[AttendanceID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Attendance]  WITH CHECK ADD  CONSTRAINT [FK_Attendance_Transaction] FOREIGN KEY([ZKBioTransactionID])
REFERENCES [dbo].[RawTransactions] ([id])
GO

ALTER TABLE [dbo].[Attendance] CHECK CONSTRAINT [FK_Attendance_Transaction]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[RawTransactions]    Script Date: 8/11/2026 1:11:52 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[RawTransactions](
	[id] [int] NOT NULL,
	[emp_code] [nvarchar](40) NOT NULL,
	[punch_time] [datetime2](7) NOT NULL,
	[punch_state] [nvarchar](10) NOT NULL,
	[verify_type] [int] NOT NULL,
	[work_code] [nvarchar](40) NULL,
	[terminal_sn] [nvarchar](100) NULL,
	[terminal_alias] [nvarchar](100) NULL,
	[area_alias] [nvarchar](200) NULL,
	[longitude] [float] NULL,
	[latitude] [float] NULL,
	[gps_location] [nvarchar](max) NULL,
	[mobile] [nvarchar](100) NULL,
	[source] [smallint] NULL,
	[purpose] [smallint] NULL,
	[crc] [nvarchar](200) NULL,
	[is_attendance] [smallint] NULL,
	[reserved] [nvarchar](200) NULL,
	[upload_time] [datetime2](7) NULL,
	[sync_status] [smallint] NULL,
	[sync_time] [datetime2](7) NULL,
	[is_mask] [smallint] NULL,
	[temperature] [numeric](4, 1) NULL,
	[emp_id] [int] NULL,
	[terminal_id] [int] NULL,
	[company_code] [nvarchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Report]    Script Date: 8/11/2026 1:11:59 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Report](
	[ReportID] [int] IDENTITY(1,1) NOT NULL,
	[EmployeeID] [int] NOT NULL,
	[AttendanceDate] [date] NOT NULL,
	[ShiftID] [int] NOT NULL,
	[CheckIn] [time](7) NULL,
	[CheckOut] [time](7) NULL,
	[WorkingHours] [decimal](4, 2) NULL,
	[LateMinutes] [int] NULL,
	[OvertimeHours] [decimal](4, 2) NULL,
	[Status] [nvarchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[ReportID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Report] ADD  DEFAULT ((0)) FOR [LateMinutes]
GO

ALTER TABLE [dbo].[Report] ADD  DEFAULT ((0)) FOR [OvertimeHours]
GO

ALTER TABLE [dbo].[Report]  WITH CHECK ADD FOREIGN KEY([ShiftID])
REFERENCES [dbo].[Shift] ([ShiftID])
GO

ALTER TABLE [dbo].[Report]  WITH CHECK ADD  CONSTRAINT [FK_Report_Employee] FOREIGN KEY([EmployeeID])
REFERENCES [dbo].[Employees] ([EmployeeID])
GO

ALTER TABLE [dbo].[Report] CHECK CONSTRAINT [FK_Report_Employee]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Shift]    Script Date: 8/11/2026 1:12:05 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Shift](
	[ShiftID] [int] IDENTITY(1,1) NOT NULL,
	[ShiftName] [nvarchar](50) NOT NULL,
	[StartTime] [time](7) NOT NULL,
	[EndTime] [time](7) NOT NULL,
	[GracePeriod] [int] NULL,
	[WorkingHours] [decimal](4, 2) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ShiftID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Shift] ADD  DEFAULT ((0)) FOR [GracePeriod]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[Roster]    A date-specific shift assignment for a team ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Roster](
	[RosterID] [int] IDENTITY(1,1) NOT NULL,
	[RosterDate] [date] NOT NULL,
	[ShiftID] [int] NOT NULL,
	[TeamName] [nvarchar](100) NULL,
	[Notes] [nvarchar](255) NULL,
	[CreatedAt] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[RosterID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Roster] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[Roster]  WITH CHECK ADD  CONSTRAINT [FK_Roster_Shift] FOREIGN KEY([ShiftID])
REFERENCES [dbo].[Shift] ([ShiftID])
GO

ALTER TABLE [dbo].[Roster] CHECK CONSTRAINT [FK_Roster_Shift]
GO


USE [AttendanceManagementSystem]
GO

/****** Object:  Table [dbo].[RosterAssignment]    Links employees to a Roster entry (the "team") ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[RosterAssignment](
	[RosterAssignmentID] [int] IDENTITY(1,1) NOT NULL,
	[RosterID] [int] NOT NULL,
	[EmployeeID] [int] NOT NULL,
PRIMARY KEY CLUSTERED
(
	[RosterAssignmentID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
CONSTRAINT [UQ_RosterAssignment_RosterEmployee] UNIQUE NONCLUSTERED
(
	[RosterID] ASC, [EmployeeID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[RosterAssignment]  WITH CHECK ADD  CONSTRAINT [FK_RosterAssignment_Roster] FOREIGN KEY([RosterID])
REFERENCES [dbo].[Roster] ([RosterID])
GO

ALTER TABLE [dbo].[RosterAssignment] CHECK CONSTRAINT [FK_RosterAssignment_Roster]
GO

ALTER TABLE [dbo].[RosterAssignment]  WITH CHECK ADD  CONSTRAINT [FK_RosterAssignment_Employee] FOREIGN KEY([EmployeeID])
REFERENCES [dbo].[Employees] ([EmployeeID])
GO

ALTER TABLE [dbo].[RosterAssignment] CHECK CONSTRAINT [FK_RosterAssignment_Employee]
GO
