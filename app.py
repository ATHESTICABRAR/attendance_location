from flask import Flask, request, jsonify, send_from_directory
from datetime import date
import math
import os

app = Flask(__name__)

# ---------------- CONFIG ----------------
CAMPUS_LAT = 18.336389     # change to your campus latitude (converted from degrees, minutes, seconds)
CAMPUS_LON = 78.347139     # change to your campus longitude (converted from degrees, minutes, seconds)
RADIUS_KM = 100        

CR_PASSWORD = "8464940297"       # CHANGE CR PASSWORD
# =========================================


# -------- Distance Calculation --------
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111


# -------- Home Page --------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# -------- Mark Attendance --------
@app.route("/mark", methods=["POST"])
def mark_attendance():
    data = request.json
    reg_no = data.get("regNo")
    lat = float(data.get("lat"))
    lon = float(data.get("lon"))

    today = str(date.today())

    # Load students
    if not os.path.exists("students.txt"):
        return jsonify({"message": "students.txt not found ❌"})

    with open("students.txt", "r") as f:
        students = [s.strip() for s in f.readlines()]

    if reg_no not in students:
        return jsonify({"message": "Invalid registration number ❌"})

    # Location check
    dist = distance(lat, lon, CAMPUS_LAT, CAMPUS_LON)
    if dist > RADIUS_KM:
        return jsonify({"message": "You are not inside campus ❌"})

    # Create attendance file if missing
    if not os.path.exists("attendance.txt"):
        open("attendance.txt", "w").close()

    with open("attendance.txt", "r") as f:
        records = f.readlines()

    for r in records:
        if r.strip() == f"{reg_no},{today}":
            return jsonify({"message": "Attendance already marked ⚠️"})

    with open("attendance.txt", "a") as f:
        f.write(f"{reg_no},{today}\n")

    return jsonify({"message": "Attendance marked successfully ✅"})


# -------- WhatsApp Formatter --------
def whatsapp_format(present_list, absent_list, total):
    present = len(present_list)
    absent = len(absent_list)
    percentage = round((present / total) * 100, 2)

    now = datetime.now()
    time_str = now.strftime("%I:%M %p").lower()
    date_str = now.strftime("%d %B %Y")

    message = f"""|| CSE E Attendance {date_str}
Morning (9:30 - 12:00) {time_str}

Present ({present}/{total}) - {percentage}%:
{", ".join(present_list)}

Absent ({absent}):
{", ".join(absent_list)}
"""
    return message


# -------- CR Login --------
@app.route("/cr-login", methods=["POST"])
def cr_login():
    data = request.json
    if data.get("password") == CR_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid CR password ❌"})


# -------- CR Report (Protected) --------
@app.route("/report")
def report():
    today = str(date.today())

    if not os.path.exists("students.txt"):
        return "<pre>students.txt not found</pre>"

    with open("students.txt", "r") as f:
        students = [s.strip()[-2:] for s in f.readlines()]

    present = []
    if os.path.exists("attendance.txt"):
        with open("attendance.txt", "r") as f:
            for line in f:
                reg, d = line.strip().split(",")
                if d == today:
                    present.append(reg[-2:])

    absent = list(set(students) - set(present))

    whatsapp_text = whatsapp_format(present, absent, len(students))
    return f"<pre>{whatsapp_text}</pre>"


# -------- Run App --------
if __name__ == "__main__":
    app.run(debug=True)