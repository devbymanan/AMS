"""
device_sync.py -- Pulls attendance punches from a ZKTeco TM F650 terminal via
the SBXPC SDK (SBXPCDLL.dll / SBXPCDLL64.dll) and writes them into AttendanceMS's
`Attendance` table.

REQUIREMENTS
  - Must run on Windows. The SDK is a native Win32/x64 DLL, not portable.
  - Copy SBXPCDLL64.dll (for 64-bit Python) next to this file, or point
    SBXPC_DLL_PATH at it. It's in the SDK zip at:
      Sample_M50/Java_SBXPCSample/SBXPCSample/SBXPCDLL64.dll
    Use SBXPCDLL.dll instead if you're running 32-bit Python.
  - Same .env this project's app.py already uses (AMS_DB_DRIVER/SERVER/NAME/
    USER/PASSWORD), plus these additional keys (all optional, shown with
    their defaults):
      SBXPC_DLL_PATH=SBXPCDLL64.dll
      DEVICE_IP=192.168.1.201
      DEVICE_PORT=4370
      DEVICE_PASSWORD=0          # comm key set on the device; 0 if none
      DEVICE_MACHINE_NUMBER=1

HOW IT MAPS PUNCHES TO EMPLOYEES
  The device only knows an EnrollNumber (the ID it was enrolled with). This
  script matches that against employees.EmployeeCode -- so whatever code the
  employee was enrolled with on the terminal must match what's stored in
  their AMS record. Unmapped punches are reported, not silently dropped.

USAGE
  python device_sync.py

  Run it by hand first to confirm it connects and maps correctly, then wire
  it up to Windows Task Scheduler to run every few minutes.
"""

import os
import sys
import ctypes
from datetime import datetime

import pyodbc
from dotenv import load_dotenv

load_dotenv()

if sys.platform != "win32":
    sys.exit("device_sync.py must run on Windows -- the SBXPC SDK is a native Win32/x64 DLL.")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SBXPC_DLL_PATH = os.getenv(
    "SBXPC_DLL_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "SBXPCDLL64.dll")
)
DEVICE_IP = os.getenv("DEVICE_IP", "192.168.1.201")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "4370"))
DEVICE_PASSWORD = int(os.getenv("DEVICE_PASSWORD", "0"))
MACHINE_NUMBER = int(os.getenv("DEVICE_MACHINE_NUMBER", "1"))

AMS_DB_DRIVER = os.getenv("AMS_DB_DRIVER")
AMS_DB_SERVER = os.getenv("AMS_DB_SERVER")
AMS_DB_NAME = os.getenv("AMS_DB_NAME")
AMS_DB_USER = os.getenv("AMS_DB_USER")
AMS_DB_PASSWORD = os.getenv("AMS_DB_PASSWORD")


def db_connect():
    return pyodbc.connect(
        f"DRIVER={AMS_DB_DRIVER};"
        f"SERVER={AMS_DB_SERVER};"
        f"DATABASE={AMS_DB_NAME};"
        f"UID={AMS_DB_USER};"
        f"PWD={AMS_DB_PASSWORD}"
    )


# ---------------------------------------------------------------------------
# SBXPC SDK wrapper
#
# Signatures below are taken from the SDK's own C# sample
# (SBXPCDLLSampleCSharp/sbxpc/SBXPCDLL.cs), translated to ctypes:
#   - ConnectTcpip takes the IP as a BSTR passed by reference, so it's
#     allocated with SysAllocString/freed with SysFreeString, same as the
#     C# wrapper does with Marshal.StringToBSTR/FreeBSTR.
#   - GetGeneralLogData's ten "IntPtr" out-params are just int-sized output
#     values -- ctypes handles these natively as POINTER(c_int32) + byref(),
#     no manual allocation needed like the C#/Delphi samples require.
# ---------------------------------------------------------------------------
class SBXPCDevice:
    def __init__(self, dll_path):
        if not os.path.exists(dll_path):
            raise FileNotFoundError(
                f"Can't find {dll_path}. Copy SBXPCDLL64.dll (from the SDK's "
                f"Java_SBXPCSample/SBXPCSample folder) next to this script, "
                f"or set SBXPC_DLL_PATH in your .env."
            )
        self.dll = ctypes.WinDLL(dll_path)
        self.oleaut32 = ctypes.windll.oleaut32
        self.oleaut32.SysAllocString.restype = ctypes.c_void_p
        self.oleaut32.SysAllocString.argtypes = [ctypes.c_wchar_p]
        self.oleaut32.SysFreeString.argtypes = [ctypes.c_void_p]

        # NOTE: the DLL exports these with a leading underscore (confirmed via
        # objdump on the export table) -- the C# sample's public wrapper
        # methods (ConnectTcpip, ReadGeneralLogData, etc.) are just thin
        # renamed calls around these actual exports.
        self.dll._ConnectTcpip.argtypes = [
            ctypes.c_int32, ctypes.POINTER(ctypes.c_void_p), ctypes.c_int32, ctypes.c_int32
        ]
        self.dll._ConnectTcpip.restype = ctypes.c_ubyte

        self.dll._ReadGeneralLogData.argtypes = [ctypes.c_int32, ctypes.c_ubyte]
        self.dll._ReadGeneralLogData.restype = ctypes.c_ubyte

        self.dll._GetGeneralLogData.argtypes = (
            [ctypes.c_int32] + [ctypes.POINTER(ctypes.c_int32)] * 10
        )
        self.dll._GetGeneralLogData.restype = ctypes.c_ubyte

        # "All" variants ignore the device's internal read-mark, unlike
        # ReadGeneralLogData/GetGeneralLogData above -- needed here because
        # another client (the Yunatt cloud agent) is already pulling and
        # marking records as read, so the marked-aware call comes back empty.
        self.dll._ReadAllGLogData.argtypes = [ctypes.c_int32]
        self.dll._ReadAllGLogData.restype = ctypes.c_ubyte

        self.dll._GetAllGLogData.argtypes = (
            [ctypes.c_int32] + [ctypes.POINTER(ctypes.c_int32)] * 10
        )
        self.dll._GetAllGLogData.restype = ctypes.c_ubyte

        self.dll._Disconnect.argtypes = [ctypes.c_int32]
        self.dll._Disconnect.restype = None

        self.connected = False

    def connect(self, ip, port, password, machine_number):
        bstr = self.oleaut32.SysAllocString(ip)
        bstr_ptr = ctypes.c_void_p(bstr)
        try:
            ok = self.dll._ConnectTcpip(machine_number, ctypes.byref(bstr_ptr), port, password)
        finally:
            self.oleaut32.SysFreeString(bstr)
        self.connected = bool(ok)
        return self.connected

    def disconnect(self, machine_number):
        if self.connected:
            self.dll._Disconnect(machine_number)
            self.connected = False

    def get_general_log(self, machine_number):
        """Reads all attendance ("general") log records off the device.
        Returns a list of dicts: user_id, verify_mode, punch_time."""
        if not self.dll._ReadAllGLogData(machine_number):
            return []

        records = []
        (t_machine, enroll_no, e_machine, verify_mode,
         year, month, day, hour, minute, second) = (ctypes.c_int32() for _ in range(10))

        while self.dll._GetAllGLogData(
            machine_number,
            ctypes.byref(t_machine), ctypes.byref(enroll_no), ctypes.byref(e_machine),
            ctypes.byref(verify_mode), ctypes.byref(year), ctypes.byref(month),
            ctypes.byref(day), ctypes.byref(hour), ctypes.byref(minute), ctypes.byref(second),
        ):
            try:
                ts = datetime(year.value, month.value, day.value, hour.value, minute.value, second.value)
            except ValueError:
                continue  # skip a malformed record instead of aborting the whole sync
            records.append({
                "user_id": str(enroll_no.value),
                "verify_mode": verify_mode.value,
                "punch_time": ts,
            })
        return records


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------
def sync():
    device = SBXPCDevice(SBXPC_DLL_PATH)

    print(f"Connecting to {DEVICE_IP}:{DEVICE_PORT} ...")
    if not device.connect(DEVICE_IP, DEVICE_PORT, DEVICE_PASSWORD, MACHINE_NUMBER):
        print("Failed to connect. Check the IP/port/comm key and that the device is on the network.")
        return

    try:
        print("Reading attendance log ...")
        records = device.get_general_log(MACHINE_NUMBER)
        print(f"Device returned {len(records)} punch record(s).")
    finally:
        device.disconnect(MACHINE_NUMBER)
        # Note: we deliberately do NOT call EmptyGeneralLogData here, so the
        # device keeps holding its own copy as a safety net while you verify
        # the pipeline. Clear it manually later once you trust this script.

    if not records:
        return

    conn = db_connect()
    cursor = conn.cursor()

    # Map device user_id (EnrollNumber) -> EmployeeID via EmployeeCode
    cursor.execute("SELECT EmployeeID, EmployeeCode FROM employees WHERE EmployeeCode IS NOT NULL")
    code_to_employee = {str(row.EmployeeCode): row.EmployeeID for row in cursor.fetchall()}

    inserted, skipped_dupe, skipped_unmapped = 0, 0, 0

    for rec in records:
        employee_id = code_to_employee.get(rec["user_id"])
        if not employee_id:
            skipped_unmapped += 1
            continue

        cursor.execute(
            "SELECT 1 FROM Attendance WHERE EmployeeID = ? AND PunchTime = ?",
            (employee_id, rec["punch_time"]),
        )
        if cursor.fetchone():
            skipped_dupe += 1
            continue

        cursor.execute(
            "INSERT INTO Attendance (EmployeeID, PunchTime) VALUES (?, ?)",
            (employee_id, rec["punch_time"]),
        )
        inserted += 1

    conn.commit()
    conn.close()

    print(f"Done. Inserted {inserted}, skipped {skipped_dupe} duplicate(s), "
          f"skipped {skipped_unmapped} unmapped device user(s).")
    if skipped_unmapped:
        print("Unmapped punches mean the device's enrolled user ID doesn't match any "
              "employees.EmployeeCode -- double check employees were enrolled on the "
              "terminal with the same code stored in AMS.")


if __name__ == "__main__":
    sync()
