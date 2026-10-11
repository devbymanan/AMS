from flask import Blueprint, render_template, request, redirect, url_for
from models.models import Device, RawTransaction
from extensions import db
from sqlalchemy import func

bp = Blueprint("devices", __name__)


@bp.route("/devices")
def devices():
    devices_data = (
        db.session.query(
            Device,
            func.count(RawTransaction.id).label("PunchCount"),
            func.max(RawTransaction.punch_time).label("LastSeen"),
        )
        .outerjoin(RawTransaction, RawTransaction.terminal_sn == Device.SerialNumber)
        .group_by(
            Device.DeviceID,
            Device.DeviceName,
            Device.SerialNumber,
            Device.DeviceType,
            Device.IPAddress,
            Device.Port,
            Device.Location,
            Device.Model,
            Device.Status,
            Device.Notes,
            Device.CreatedAt,
        )
        .order_by(Device.DeviceName)
        .all()
    )

    devices_list = []
    for device, punch_count, last_seen in devices_data:
        devices_list.append(
            {
                "DeviceID": device.DeviceID,
                "DeviceName": device.DeviceName,
                "SerialNumber": device.SerialNumber,
                "DeviceType": device.DeviceType,
                "IPAddress": device.IPAddress,
                "Port": device.Port,
                "Location": device.Location,
                "Model": device.Model,
                "Status": device.Status,
                "Notes": device.Notes,
                "CreatedAt": device.CreatedAt,
                "PunchCount": punch_count,
                "LastSeen": last_seen,
            }
        )

    return render_template("devices.html", active_page="devices", devices=devices_list)


@bp.route("/add_device", methods=["GET", "POST"])
def add_device():
    if request.method == "POST":
        new_device = Device(
            DeviceName=request.form.get("device_name"),
            SerialNumber=request.form.get("serial_number"),
            DeviceType=request.form.get("device_type"),
            IPAddress=request.form.get("ip_address"),
            Port=request.form.get("port") or None,
            Location=request.form.get("location"),
            Model=request.form.get("model"),
            Status=bool(request.form.get("status")),
            Notes=request.form.get("notes"),
        )
        db.session.add(new_device)
        db.session.commit()
        return redirect(url_for("devices.devices"))

    return render_template("add_device.html", active_page="devices")


@bp.route("/edit_device/<int:device_id>", methods=["GET", "POST"])
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)

    if request.method == "POST":
        device.DeviceName = request.form.get("device_name")
        device.SerialNumber = request.form.get("serial_number")
        device.DeviceType = request.form.get("device_type")
        device.IPAddress = request.form.get("ip_address")
        device.Port = request.form.get("port") or None
        device.Location = request.form.get("location")
        device.Model = request.form.get("model")
        device.Status = bool(request.form.get("status"))
        device.Notes = request.form.get("notes")

        db.session.commit()
        return redirect(url_for("devices.devices"))

    return render_template("edit_device.html", active_page="devices", device=device)


@bp.route("/delete_device/<int:device_id>", methods=["POST"])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
    return redirect(url_for("devices.devices"))
